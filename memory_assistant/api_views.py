from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import Memory, UserProfile, SharedMemory, MemoryLike, MemoryComment
from .serializers import (
    MemorySerializer, 
    UserSerializer, 
    MemoryCreateSerializer,
    SharedMemorySerializer,
    MemoryLikeSerializer,
    MemoryCommentSerializer
)
from .services import ChatGPTService
from .recommendation_service import AIRecommendationService


class MemoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for memory management
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get memories for the authenticated user (own + shared)"""
        user = self.request.user
        
        # Get shared memory IDs
        shared_memory_ids = SharedMemory.objects.filter(
            Q(shared_with_user=user) | 
            Q(shared_with_organization__in=user.organization_memberships.filter(is_active=True).values_list('organization', flat=True)),
            is_active=True
        ).values_list('memory_id', flat=True)
        
        # Get all accessible memories
        return Memory.objects.filter(
            Q(user=user) | Q(id__in=shared_memory_ids),
            is_archived=False
        ).select_related('user').prefetch_related(
            'shares__shared_by',
            'shares__shared_with_organization',
            'likes__user',
            'comments__user'
        ).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MemoryCreateSerializer
        return MemorySerializer
    
    @action(detail=False, methods=['post'])
    def quick_add(self, request):
        """Quick add memory endpoint"""
        content = request.data.get('content', '').strip()
        if len(content) < 10:
            return Response(
                {'error': 'Memory content must be at least 10 characters long.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create memory with AI processing
        memory = Memory.objects.create(
            user=request.user,
            content=content,
            importance=5,
            memory_type='general'
        )
        
        # Process with AI
        try:
            ai_service = ChatGPTService()
            if ai_service.is_available():
                # Auto-categorize
                ai_response = ai_service.categorize_memory(content)
                if ai_response.get('success'):
                    memory.memory_type = ai_response.get('memory_type', 'general')
                    memory.importance = ai_response.get('importance', 5)
                    memory.tags = ai_response.get('tags', [])
                    memory.ai_reasoning = ai_response.get('reasoning', '')
                
                # Generate summary
                summary_response = ai_service.generate_summary(content)
                if summary_response.get('success'):
                    memory.summary = summary_response.get('summary', '')
                
                memory.save()
        except Exception as e:
            # Continue even if AI fails
            pass
        
        serializer = MemorySerializer(memory)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search memories endpoint"""
        query = request.GET.get('q', '').strip()
        mode = request.GET.get('mode', 'fast')
        page = request.GET.get('page', 1)
        
        if not query:
            return Response(
                {'error': 'Search query is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset()
        
        # Apply search filters
        if mode == 'semantic':
            # AI semantic search
            try:
                ai_service = ChatGPTService()
                if ai_service.is_available():
                    semantic_results = ai_service.semantic_search(query, queryset)
                    if semantic_results.get('success'):
                        memory_ids = semantic_results.get('memory_ids', [])
                        queryset = queryset.filter(id__in=memory_ids)
            except:
                # Fallback to text search
                search_conditions = Q(content__icontains=query) | Q(summary__icontains=query)
                queryset = queryset.filter(search_conditions)
        else:
            # Fast text search
            search_conditions = Q(content__icontains=query) | Q(summary__icontains=query)
            queryset = queryset.filter(search_conditions)
        
        # Pagination
        paginator = Paginator(queryset, 20)
        page_obj = paginator.get_page(page)
        
        serializer = MemorySerializer(page_obj, many=True)
        return Response({
            'results': serializer.data,
            'pagination': {
                'page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        })
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get dashboard statistics"""
        user = request.user
        now = timezone.now()
        
        # Get all user memories
        memories = Memory.objects.filter(user=user, is_archived=False)
        
        # Calculate statistics
        stats = {
            'total_memories': memories.count(),
            'important_memories': memories.filter(importance__gte=8).count(),
            'scheduled_memories_count': memories.filter(delivery_date__gt=now).count(),
            'todays_memories_count': memories.filter(delivery_date__date=now.date()).count(),
            'recent_memories': MemorySerializer(
                memories.order_by('-created_at')[:5], 
                many=True
            ).data
        }
        
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like/unlike a memory"""
        memory = self.get_object()
        user = request.user
        
        # Check if user can like this memory
        if memory.user == user:
            return Response(
                {'error': 'You cannot like your own memory.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Toggle like
        like, created = MemoryLike.objects.get_or_create(
            memory=memory,
            user=user,
            defaults={'reaction_type': 'like'}
        )
        
        if not created:
            like.delete()
            action = 'unliked'
        else:
            action = 'liked'
        
        return Response({
            'action': action,
            'like_count': memory.likes.count()
        })
    
    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        """Add comment to memory"""
        memory = self.get_object()
        content = request.data.get('content', '').strip()
        
        if not content:
            return Response(
                {'error': 'Comment content is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not memory.allow_comments:
            return Response(
                {'error': 'Comments are not allowed on this memory.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        comment = MemoryComment.objects.create(
            memory=memory,
            user=request.user,
            content=content
        )
        
        serializer = MemoryCommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user management
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
    
    def get_serializer_class(self):
        return UserSerializer
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Get user profile"""
        user = request.user
        try:
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user)
        
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        """Update user profile"""
        user = request.user
        try:
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user)
        
        # Update profile fields
        profile.user_timezone = request.data.get('timezone', profile.user_timezone)
        profile.bio = request.data.get('bio', profile.bio)
        profile.save()
        
        serializer = UserSerializer(user)
        return Response(serializer.data)


class AIViewSet(viewsets.ViewSet):
    """
    API endpoint for AI features
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        """Get AI memory suggestions"""
        try:
            ai_service = AIRecommendationService()
            if ai_service.is_available():
                suggestions = ai_service.get_personalized_recommendations(request.user)
                return Response(suggestions)
            else:
                return Response(
                    {'error': 'AI service is currently unavailable.'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
        except Exception as e:
            return Response(
                {'error': 'Failed to get AI suggestions.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def enhance_memory(self, request):
        """Enhance memory with AI"""
        content = request.data.get('content', '').strip()
        if not content:
            return Response(
                {'error': 'Memory content is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            ai_service = ChatGPTService()
            if ai_service.is_available():
                # Generate summary
                summary_response = ai_service.generate_summary(content)
                # Generate tags
                tags_response = ai_service.generate_tags(content)
                # Categorize
                categorize_response = ai_service.categorize_memory(content)
                
                result = {
                    'summary': summary_response.get('summary', '') if summary_response.get('success') else '',
                    'tags': tags_response.get('tags', []) if tags_response.get('success') else [],
                    'memory_type': categorize_response.get('memory_type', 'general') if categorize_response.get('success') else 'general',
                    'importance': categorize_response.get('importance', 5) if categorize_response.get('success') else 5,
                    'ai_reasoning': categorize_response.get('reasoning', '') if categorize_response.get('success') else ''
                }
                
                return Response(result)
            else:
                return Response(
                    {'error': 'AI service is currently unavailable.'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
        except Exception as e:
            return Response(
                {'error': 'Failed to enhance memory.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
