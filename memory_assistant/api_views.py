from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.core.files.storage import default_storage
from django.conf import settings
from datetime import datetime, timedelta
import json
import os
import sys

from .models import Memory, UserProfile, SharedMemory, MemoryLike, MemoryComment, SmartReminder
from .serializers import (
    MemorySerializer, 
    UserSerializer, 
    MemoryCreateSerializer,
    SharedMemorySerializer,
    MemoryLikeSerializer,
    MemoryCommentSerializer,
    UserRegistrationSerializer,
    SmartReminderSerializer,
    SmartReminderCreateSerializer,
    SmartReminderAnalyzeSerializer,
    SmartReminderStatsSerializer
)
from .services import ChatGPTService
from .recommendation_service import AIRecommendationService
from .smart_reminder_service import SmartReminderService


class HealthCheckView(APIView):
    """
    Health check endpoint for Flutter app connection testing
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        # Check AI service status
        ai_status = 'unavailable'
        try:
            from .services import ChatGPTService
            ai_service = ChatGPTService()
            ai_status = 'available' if ai_service.is_available() else 'unavailable'
        except Exception:
            ai_status = 'error'
        
        return Response({
            'status': 'healthy',
            'server': 'memora_core',
            'version': '4.2.0-release',
            'timestamp': timezone.now().isoformat(),
            'database': 'connected',
            'ai_service': ai_status,
        })


class VoiceTranscribeView(APIView):
    """
    Voice transcription endpoint for Flutter voice features
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            # Get uploaded audio file
            audio_file = request.FILES.get('audio')
            if not audio_file:
                return Response(
                    {'error': 'No audio file provided'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # For now, return mock transcription
            # TODO: Integrate with actual speech-to-text service
            return Response({
                'transcription': 'Mock transcription - integrate with speech service',
                'confidence': 0.85,
                'language': request.data.get('language', 'en-US'),
                'duration': 0,
            })
            
        except Exception as e:
            return Response(
                {'error': f'Transcription failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SearchMemoriesView(APIView):
    """
    Text search endpoint for Flutter app
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            query = request.GET.get('q', '').strip()
            if not query:
                return Response(
                    {'error': 'Search query is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Search in user's memories
            memories = Memory.objects.filter(
                user=request.user,
                content__icontains=query,
                is_archived=False
            ).order_by('-created_at')
            
            results = []
            for memory in memories:
                results.append(MemorySerializer(memory, context={'request': request}).data)
            
            return Response({
                'results': results,
                'total': len(results),
                'query': query,
            })
            
        except Exception as e:
            return Response(
                {'error': f'Search failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SemanticSearchView(APIView):
    """
    Semantic search endpoint for Flutter advanced search
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            query = request.data.get('query', '')
            limit = request.data.get('limit', 20)
            min_relevance = request.data.get('min_relevance', 0.5)
            
            if not query:
                return Response(
                    {'error': 'Query is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # For now, fall back to regular text search
            # TODO: Implement actual semantic/vector search
            memories = Memory.objects.filter(
                user=request.user,
                content__icontains=query,
                is_archived=False
            )[:limit]
            
            results = []
            for memory in memories:
                results.append({
                    'memory': MemorySerializer(memory, context={'request': request}).data,
                    'relevance_score': 0.8,  # Mock relevance
                    'highlights': [query],
                })
            
            return Response({
                'results': results,
                'total': len(results),
                'query': query,
            })
            
        except Exception as e:
            return Response(
                {'error': f'Semantic search failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VoiceSearchView(APIView):
    """
    Voice search endpoint for Flutter voice search
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            # Get uploaded audio file
            audio_file = request.FILES.get('audio')
            if not audio_file:
                return Response(
                    {'error': 'No audio file provided'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # For now, return mock search results
            # TODO: Integrate transcription + search
            return Response({
                'results': [],
                'transcription': 'Mock voice search - integrate with speech service',
                'total': 0,
            })
            
        except Exception as e:
            return Response(
                {'error': f'Voice search failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MemoryStatsView(APIView):
    """
    Memory statistics endpoint for Flutter app
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            user = request.user
            now = timezone.now()
            
            # Get all user memories
            memories = Memory.objects.filter(user=user, is_archived=False)
            
            # Calculate statistics
            week_ago = now - timedelta(days=7)
            month_ago = now - timedelta(days=30)
            
            stats = {
                'total': memories.count(),
                'this_week': memories.filter(created_at__gte=week_ago).count(),
                'this_month': memories.filter(created_at__gte=month_ago).count(),
                'important': memories.filter(importance__gte=8).count(),
                'scheduled': memories.filter(delivery_date__gt=now).count(),
                'today': memories.filter(delivery_date__date=now.date()).count(),
                'categories': {},
            }
            
            # Add category counts
            from django.db.models import Count
            category_counts = memories.values('memory_type').annotate(count=Count('memory_type'))
            for item in category_counts:
                stats['categories'][item['memory_type']] = item['count']
            
            return Response(stats)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch stats: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AIStatusView(APIView):
    """
    Enhanced AI service status endpoint with cost monitoring and cache stats
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            from .services import ChatGPTService
            from .recommendation_service import AIRecommendationService
            from .ai_cache_service import get_cache_service
            from .ai_cost_monitor import get_cost_monitor
            
            # Check ChatGPT service
            chatgpt_service = ChatGPTService()
            chatgpt_available = chatgpt_service.is_available()
            
            # Check recommendation service
            recommendation_service = AIRecommendationService()
            recommendation_available = recommendation_service.is_available()
            
            # Get cache statistics
            try:
                cache_service = get_cache_service()
                cache_stats = cache_service.get_stats()
            except Exception as e:
                cache_stats = {'error': str(e)}
            
            # Get cost monitoring statistics
            try:
                cost_monitor = get_cost_monitor()
                cost_stats = cost_monitor.get_summary_stats()
                limits_status = cost_monitor.check_limits(user_id=request.user.id)
            except Exception as e:
                cost_stats = {'error': str(e)}
                limits_status = {'can_proceed': True}
            
            # Test AI functionality (only if available and under limits)
            test_result = None
            if chatgpt_available and limits_status.get('can_proceed', False):
                try:
                    # Test with a simple categorization
                    test_response = chatgpt_service.categorize_memory("Test memory for AI functionality")
                    test_result = {
                        'success': test_response.get('success', False),
                        'memory_type': test_response.get('memory_type', 'unknown'),
                        'reasoning': test_response.get('reasoning', 'No reasoning provided')[:100]
                    }
                except Exception as e:
                    test_result = {
                        'success': False,
                        'error': str(e)
                    }
            
            return Response({
                'available': chatgpt_available,  # Main availability flag for mobile app
                'chatgpt_service': {
                    'available': chatgpt_available,
                    'model': 'gpt-3.5-turbo' if chatgpt_available else None,
                    'status': 'online' if chatgpt_available else 'offline'
                },
                'recommendation_service': {
                    'available': recommendation_available,
                    'status': 'online' if recommendation_available else 'offline'
                },
                'cache': {
                    'enabled': True,
                    'stats': cache_stats
                },
                'cost_monitoring': {
                    'enabled': True,
                    'today_stats': cost_stats.get('today', {}),
                    'limits_status': limits_status,
                    'total_lifetime_cost': cost_stats.get('total_lifetime_cost', 0.0)
                },
                'features': {
                    'categorization': chatgpt_available,
                    'summarization': chatgpt_available,
                    'tagging': chatgpt_available,
                    'suggestions': recommendation_available,
                    'semantic_search': chatgpt_available
                },
                'fallback_available': True,  # Basic functionality always works
                'test_result': test_result,
                'environment': {
                    'openai_api_key_configured': bool(os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != 'your_openai_api_key_here'),
                    'python_version': sys.version,
                },
                'timestamp': timezone.now().isoformat(),
                'message': 'AI services fully operational' if chatgpt_available else 'AI services unavailable - using fallback logic'
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to check AI status: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token view that includes user information
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Add user information to the response
            data = response.data
            # During token obtain, request.user is Anonymous.
            # Look up the user based on submitted credentials instead.
            username_or_email = request.data.get('username') or request.data.get('email')
            user = None
            if username_or_email:
                # Try username first
                user = User.objects.filter(username=username_or_email).first()
                if user is None:
                    # Fallback to email lookup
                    user = User.objects.filter(email=username_or_email).first()
            if user is None:
                # As an ultimate fallback, do not attempt to access attributes
                return response
            
            # Add user ID and basic info
            data['user_id'] = user.id
            data['username'] = user.username
            data['email'] = user.email
            
            # Create user profile if it doesn't exist
            UserProfile.objects.get_or_create(user=user)
        
        return response


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint for mobile app
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create user profile
            UserProfile.objects.get_or_create(user=user)
            return Response(
                {'message': 'User created successfully', 'user_id': user.id},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    
    def perform_create(self, serializer):
        """Create memory and generate smart reminders similar to web flow."""
        # Ensure memory is owned by the authenticated user
        memory = serializer.save(user=self.request.user)
        
        # Create smart reminders based on the memory content and scheduling
        try:
            reminder_service = SmartReminderService()
            # For scheduled memories, create the scheduled reminder first
            if getattr(memory, 'delivery_date', None):
                reminder_service.create_scheduled_memory_reminder(memory, self.request.user)
            
            # Analyze content for additional reminders
            suggestions = reminder_service.analyze_memory_for_reminders(memory) or []
            for suggestion in suggestions:
                try:
                    reminder_service.create_smart_reminder(memory, self.request.user, suggestion)
                except Exception:
                    # Skip any invalid suggestion without failing the request
                    continue
        except Exception:
            # Do not block creation if reminder generation fails
            pass
    
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
        
        # Create smart reminders for quick-add memory as well
        try:
            reminder_service = SmartReminderService()
            if getattr(memory, 'delivery_date', None):
                reminder_service.create_scheduled_memory_reminder(memory, request.user)
            suggestions = reminder_service.analyze_memory_for_reminders(memory) or []
            for suggestion in suggestions:
                try:
                    reminder_service.create_smart_reminder(memory, request.user, suggestion)
                except Exception:
                    continue
        except Exception:
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
        try:
            user = request.user
            print(f'📊 Stats requested for user: {user.username} (ID: {user.id})')
            now = timezone.now()
            
            # Get all user memories
            memories = Memory.objects.filter(user=user, is_archived=False)
            print(f'📊 Found {memories.count()} memories for user')
            
            # Calculate statistics for Flutter app
            week_ago = now - timedelta(days=7)
            month_ago = now - timedelta(days=30)
            
            # Safe queries to avoid potential issues
            total_count = memories.count()
            this_week_count = memories.filter(created_at__gte=week_ago).count()
            this_month_count = memories.filter(created_at__gte=month_ago).count()
            important_count = memories.filter(importance__gte=8).count()
            
            # Safe delivery date queries
            scheduled_count = 0
            todays_count = 0
            try:
                scheduled_count = memories.filter(delivery_date__isnull=False, delivery_date__gt=now).count()
                todays_count = memories.filter(delivery_date__date=now.date()).count()
            except Exception as e:
                print(f'⚠️ Date filtering error: {e}')
            
            # Get recent memories
            recent_memories_data = []
            try:
                recent_memories = memories.order_by('-created_at')[:6]
                recent_memories_data = MemorySerializer(
                    recent_memories, 
                    many=True,
                    context={'request': request}
                ).data
                print(f'📊 Serialized {len(recent_memories_data)} recent memories')
            except Exception as e:
                print(f'⚠️ Recent memories serialization error: {e}')
            
            stats = {
                'total': total_count,
                'thisWeek': this_week_count,
                'thisMonth': this_month_count,
                'voiceMemories': 0,  # Simplified for now
                'categories': {},
                'total_memories': total_count,
                'important_memories': important_count,
                'scheduled_memories_count': scheduled_count,
                'todays_memories_count': todays_count,
                'recent_memories': recent_memories_data
            }
            
            # Add category counts
            from django.db.models import Count
            try:
                category_counts = memories.values('memory_type').annotate(count=Count('memory_type'))
                for item in category_counts:
                    stats['categories'][item['memory_type']] = item['count']
            except Exception as e:
                print(f'⚠️ Category counting error: {e}')
            
            print(f'📊 Returning stats: {stats}')
            return Response(stats)
            
        except Exception as e:
            print(f'❌ Stats endpoint error: {e}')
            # Return basic stats to avoid 500 error
            return Response({
                'total': 0,
                'thisWeek': 0,
                'thisMonth': 0,
                'voiceMemories': 0,
                'categories': {},
                'total_memories': 0,
                'important_memories': 0,
                'scheduled_memories_count': 0,
                'todays_memories_count': 0,
                'recent_memories': []
            })
    
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
    
    @action(detail=True, methods=['post'])
    def upload_voice(self, request, pk=None):
        """Upload voice file to memory"""
        memory = self.get_object()
        voice_file = request.FILES.get('voice_file')
        
        if not voice_file:
            return Response(
                {'error': 'No voice file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save voice file (you can implement actual file storage here)
        # For now, just return success
        return Response({
            'message': 'Voice file uploaded successfully',
            'voice_file_url': f'/media/voices/{memory.id}_{voice_file.name}'
        })
    
    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        """Find similar memories"""
        memory = self.get_object()
        
        # Simple similarity based on tags and content
        similar_memories = Memory.objects.filter(
            user=request.user,
            is_archived=False
        ).exclude(id=memory.id)
        
        # Filter by similar tags if any
        if memory.tags:
            similar_memories = similar_memories.filter(
                tags__overlap=memory.tags
            )
        
        # Limit to 5 similar memories
        similar_memories = similar_memories[:5]
        
        results = []
        for sim_memory in similar_memories:
            results.append({
                'memory': MemorySerializer(sim_memory, context={'request': request}).data,
                'relevance_score': 0.7,  # Mock relevance score
                'similarity_reason': 'Similar tags and content'
            })
        
        return Response({
            'results': results,
            'total': len(results)
        })


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
            profile = user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user)
        
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        """Update user profile"""
        user = request.user
        try:
            profile = user.profile
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
            print(f'🤖 AI suggestions requested for user: {request.user.username} (ID: {request.user.id})')
            ai_service = AIRecommendationService()
            print(f'🤖 AI service available: {ai_service.is_available()}')
            
            if ai_service.is_available():
                recommendations = ai_service.get_personalized_recommendations(request.user)
                print(f'🤖 AI recommendations received: {recommendations}')
                # Convert the complex AI response to simple suggestion list
                suggestions = []
                
                # Add memory prompts as suggestions
                for prompt in recommendations.get('memory_prompts', []):
                    suggestions.append({
                        'text': prompt,
                        'type': 'prompt',
                        'reason': 'Memory prompt suggestion'
                    })
                
                # Add content suggestions
                for content in recommendations.get('content_suggestions', []):
                    suggestions.append({
                        'text': content.get('description', content.get('title', str(content))),
                        'type': 'content',
                        'reason': 'Content suggestion'
                    })
                
                # Add improvement tips
                for tip in recommendations.get('improvement_tips', []):
                    suggestions.append({
                        'text': tip,
                        'type': 'tip',
                        'reason': 'Improvement tip'
                    })
                
                if suggestions:
                    return Response(suggestions)
            
            # Fallback path when AI is unavailable or returned nothing
            print(f'🤖 Using fallback suggestions for user: {request.user.username}')
            recent = Memory.objects.filter(user=request.user, is_archived=False).order_by('-created_at')[:5]
            print(f'🤖 Found {recent.count()} recent memories for fallback')
            fallback = [
                {
                    'text': (m.summary or m.content[:120] + ('...' if len(m.content) > 120 else '')),
                    'memory_id': m.id,
                    'type': 'recent',
                    'reason': 'Recent activity',
                }
                for m in recent
            ]
            print(f'🤖 Returning {len(fallback)} fallback suggestions')
            return Response(fallback, status=status.HTTP_200_OK)
        except Exception as e:
            # Final fallback to avoid breaking the client: return recent memories as suggestions
            try:
                recent = Memory.objects.filter(user=request.user, is_archived=False).order_by('-created_at')[:6]
                fallback = [
                    {
                        'text': (m.summary or m.content[:120] + ('...' if len(m.content) > 120 else '')),
                        'memory_id': m.id,
                        'type': 'recent',
                        'reason': 'Recent activity',
                    }
                    for m in recent
                ]
                return Response(fallback, status=status.HTTP_200_OK)
            except Exception:
                return Response([], status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='suggestions/live')
    def live_suggestions(self, request):
        """Always return fresh AI-generated suggestions - EXACT COPY of web dashboard debug_ai_suggestions logic."""
        try:
            # EXACT COPY from debug_ai_suggestions endpoint in views.py
            from .services import ChatGPTService
            
            # Get recent memories (EXACT same query as web dashboard)
            recent_memories = Memory.objects.filter(
                user=request.user, 
                is_archived=False
            ).order_by('-created_at')[:6]
            
            # Prepare memory data (EXACT same format as web dashboard)
            recent_memory_data = [
                {
                    'content': memory.content,
                    'tags': memory.tags or []
                } for memory in recent_memories
            ]
            
            # Test ChatGPTService (EXACT same as web dashboard)
            chatgpt_service = ChatGPTService()
            is_available = chatgpt_service.is_available()
            
            if not is_available:
                resp = Response([], status=status.HTTP_200_OK)
                resp["Cache-Control"] = "no-store"
                return resp

            if not recent_memories.exists():
                resp = Response([], status=status.HTTP_200_OK)
                resp["Cache-Control"] = "no-store"
                return resp
            
            # Generate suggestions (EXACT same call as web dashboard)
            suggestions = chatgpt_service.generate_memory_suggestions(recent_memory_data)
            
            # Format for mobile API (convert strings to objects with text field)
            formatted_suggestions = [
                {
                    'text': suggestion,
                    'type': 'prompt',
                    'source': 'ai'
                } for suggestion in suggestions
            ]

            resp = Response(formatted_suggestions, status=status.HTTP_200_OK)
            resp["Cache-Control"] = "no-store"
            return resp
            
        except Exception as e:
            print(f"Error in live_suggestions: {e}")
            resp = Response([], status=status.HTTP_200_OK)
            resp["Cache-Control"] = "no-store"
            return resp
    
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
    
    @action(detail=False, methods=['post'])
    def categorize(self, request):
        """Categorize content with AI"""
        content = request.data.get('content', '').strip()
        if not content:
            return Response(
                {'error': 'Content is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            ai_service = ChatGPTService()
            if ai_service.is_available():
                response = ai_service.categorize_memory(content)
                if response.get('success'):
                    return Response({
                        'category': response.get('memory_type', 'general'),
                        'importance': response.get('importance', 5),
                        'reasoning': response.get('reasoning', '')
                    })
            
            # Fallback categorization
            return Response({
                'category': 'general',
                'importance': 5,
                'reasoning': 'AI categorization unavailable'
            })
            
        except Exception as e:
            return Response(
                {'error': f'Categorization failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def summarize(self, request):
        """Summarize content with AI"""
        content = request.data.get('content', '').strip()
        max_length = request.data.get('max_length', 200)
        
        if not content:
            return Response(
                {'error': 'Content is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            ai_service = ChatGPTService()
            if ai_service.is_available():
                response = ai_service.generate_summary(content, max_length=max_length)
                if response.get('success'):
                    return Response({
                        'summary': response.get('summary', ''),
                        'original_length': len(content),
                        'summary_length': len(response.get('summary', ''))
                    })
            
            # Fallback summary
            fallback_summary = content[:max_length] + ('...' if len(content) > max_length else '')
            return Response({
                'summary': fallback_summary,
                'original_length': len(content),
                'summary_length': len(fallback_summary)
            })
            
        except Exception as e:
            return Response(
                {'error': f'Summarization failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def tags(self, request):
        """Generate tags for content with AI"""
        content = request.data.get('content', '').strip()
        
        if not content:
            return Response(
                {'error': 'Content is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            ai_service = ChatGPTService()
            if ai_service.is_available():
                response = ai_service.generate_tags(content)
                if response.get('success'):
                    return Response({
                        'tags': response.get('tags', []),
                        'confidence': response.get('confidence', 0.8)
                    })
            
            # Fallback tags - simple keyword extraction
            words = content.lower().split()
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'was', 'are', 'were'}
            keywords = [word for word in words if len(word) > 3 and word not in common_words]
            fallback_tags = list(set(keywords[:5]))  # Get unique keywords, max 5
            
            return Response({
                'tags': fallback_tags,
                'confidence': 0.5
            })
            
        except Exception as e:
            return Response(
                {'error': f'Tag generation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RegisterView(APIView):
    """
    User registration endpoint for Flutter app
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                return Response({
                    'message': 'User registered successfully',
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': f'Registration failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token obtain pair view that returns additional user information
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Get user information
            username = request.data.get('username')
            try:
                user = User.objects.get(username=username)
                response.data.update({
                    'userId': user.id,
                    'username': user.username,
                    'email': user.email,
                })
            except User.DoesNotExist:
                pass
        return response


class SmartReminderViewSet(viewsets.ModelViewSet):
    """ViewSet for Smart Reminders"""
    serializer_class = SmartReminderSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_queryset(self):
        """Get reminders for the current user"""
        return SmartReminder.objects.filter(user=self.request.user).select_related('memory')
    
    def create(self, request):
        """Create a smart reminder"""
        serializer = SmartReminderCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            reminder = serializer.save()
            response_serializer = SmartReminderSerializer(reminder)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """Analyze a memory and suggest smart reminders"""
        serializer = SmartReminderAnalyzeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            memory_id = serializer.validated_data['memory_id']
            memory = Memory.objects.get(id=memory_id, user=request.user)
            
            service = SmartReminderService()
            suggestions = service.analyze_memory_for_reminders(memory)
            
            return Response({
                'memory_id': memory_id,
                'suggestions': suggestions
            })
        except Memory.DoesNotExist:
            return Response(
                {'error': 'Memory not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Analysis failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def scheduled(self, request):
        """Get reminders for scheduled memories"""
        try:
            service = SmartReminderService()
            reminders = service.get_scheduled_memory_reminders(request.user)
            serializer = SmartReminderSerializer(reminders, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Failed to get scheduled reminders: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def check(self, request):
        """Check and trigger due reminders"""
        try:
            service = SmartReminderService()
            triggered = service.check_and_trigger_reminders(request.user)
            
            return Response({
                'triggered_count': len(triggered),
                'reminders': [
                    {
                        'id': item['reminder'].id,
                        'memory_id': item['reminder'].memory.id,
                        'description': item['reminder'].memory.content[:100],
                        'priority': item['reminder'].priority,
                        'trigger_reason': item['trigger'].trigger_reason
                    }
                    for item in triggered
                ]
            })
        except Exception as e:
            return Response(
                {'error': f'Check failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get reminder statistics for the user"""
        try:
            user_reminders = SmartReminder.objects.filter(user=request.user)
            
            # Calculate statistics
            total = user_reminders.count()
            active = user_reminders.filter(is_active=True).count()
            
            # Triggered today
            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            triggered_today = user_reminders.filter(
                last_triggered__gte=today_start
            ).count()
            
            # Upcoming (next 24 hours)
            next_24h = timezone.now() + timedelta(hours=24)
            upcoming = user_reminders.filter(
                is_active=True,
                next_trigger__lte=next_24h,
                next_trigger__gte=timezone.now()
            ).count()
            
            # By type
            by_type = {}
            for reminder_type, _ in SmartReminder.REMINDER_TYPES:
                count = user_reminders.filter(reminder_type=reminder_type).count()
                if count > 0:
                    by_type[reminder_type] = count
            
            # By priority
            by_priority = {}
            for priority, _ in SmartReminder.PRIORITY_LEVELS:
                count = user_reminders.filter(priority=priority).count()
                if count > 0:
                    by_priority[priority] = count
            
            stats_data = {
                'total_reminders': total,
                'active_reminders': active,
                'triggered_today': triggered_today,
                'upcoming_count': upcoming,
                'by_type': by_type,
                'by_priority': by_priority
            }
            
            serializer = SmartReminderStatsSerializer(stats_data)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get stats: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """Dismiss a reminder"""
        try:
            reminder = self.get_object()
            service = SmartReminderService()
            success = service.dismiss_reminder(reminder.id, request.user)
            
            if success:
                return Response({'message': 'Reminder dismissed'})
            else:
                return Response(
                    {'error': 'Failed to dismiss reminder'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': f'Dismiss failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def snooze(self, request, pk=None):
        """Snooze a reminder"""
        try:
            reminder = self.get_object()
            hours = request.data.get('hours', 1)
            
            service = SmartReminderService()
            success = service.snooze_reminder(reminder.id, request.user, hours)
            
            if success:
                return Response({'message': f'Reminder snoozed for {hours} hours'})
            else:
                return Response(
                    {'error': 'Failed to snooze reminder'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': f'Snooze failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def update_scheduled(self, request):
        """Update reminders for a scheduled memory"""
        memory_id = request.data.get('memory_id')
        
        if not memory_id:
            return Response(
                {'error': 'memory_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            memory = Memory.objects.get(id=memory_id, user=request.user)
            service = SmartReminderService()
            service.update_scheduled_memory_reminders(memory)
            
            # Return updated reminders
            reminders = SmartReminder.objects.filter(memory=memory, user=request.user)
            serializer = SmartReminderSerializer(reminders, many=True)
            
            return Response({
                'message': 'Reminders updated',
                'reminders': serializer.data
            })
        except Memory.DoesNotExist:
            return Response(
                {'error': 'Memory not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Update failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
