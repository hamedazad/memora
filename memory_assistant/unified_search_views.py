"""
Unified Search API Views for Flutter Mobile App

Supports 4 search modes:
1. Fast Search (mode=fast) - Traditional keyword-based search
2. Semantic Search (mode=semantic) - AI-powered semantic search
3. Hybrid Search (mode=hybrid) - Combines semantic + keyword
4. Default - Comprehensive search across all fields

All modes support filtering by:
- memory_type
- importance_min/max
- date_from/to
- delivery_type
- pagination (page, page_size)
"""

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime
import re

from .models import Memory
from .serializers import MemorySerializer
from .services import ChatGPTService
from .semantic_search_service import SemanticSearchService


class UnifiedSearchView(APIView):
    """
    Unified search endpoint supporting multiple search modes
    
    Query Parameters:
    - q (required): Search query string
    - mode (optional): Search mode - 'fast', 'semantic', 'hybrid' (default: 'fast')
    - page (optional): Page number (default: 1)
    - page_size (optional): Results per page (default: 20, max: 100)
    - memory_type (optional): Filter by memory type
    - importance_min (optional): Minimum importance (1-10)
    - importance_max (optional): Maximum importance (1-10)
    - date_from (optional): Filter memories from date (YYYY-MM-DD)
    - date_to (optional): Filter memories to date (YYYY-MM-DD)
    - delivery_type (optional): Filter by delivery type
    - semantic_weight (optional): For hybrid mode (default: 0.7)
    - keyword_weight (optional): For hybrid mode (default: 0.3)
    
    Modes:
    - fast: Fast keyword-based search (default)
    - semantic: AI-powered semantic search (requires OpenAI API)
    - hybrid: Combines semantic + keyword search with weighted scoring
    - comprehensive: Search across all fields (content, summary, tags, reasoning)
    """
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            # Extract query parameters
            query = request.GET.get('q', '').strip()
            mode = request.GET.get('mode', 'fast').lower()
            page = int(request.GET.get('page', 1))
            page_size = min(int(request.GET.get('page_size', 20)), 100)
            
            # Validate query
            if not query:
                return Response(
                    {'error': 'Search query (q) is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if len(query) < 2:
                return Response(
                    {'error': 'Search query must be at least 2 characters'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate mode
            valid_modes = ['fast', 'semantic', 'hybrid', 'comprehensive']
            if mode not in valid_modes:
                return Response(
                    {'error': f'Invalid mode. Must be one of: {", ".join(valid_modes)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Base queryset - user's non-archived memories
            queryset = Memory.objects.filter(
                user=request.user,
                is_archived=False
            )
            
            # Apply filters
            queryset = self._apply_filters(queryset, request.GET)
            
            # Execute search based on mode
            if mode == 'fast':
                results = self._fast_search(queryset, query)
            elif mode == 'semantic':
                results = self._semantic_search(queryset, query)
            elif mode == 'hybrid':
                semantic_weight = float(request.GET.get('semantic_weight', 0.7))
                keyword_weight = float(request.GET.get('keyword_weight', 0.3))
                results = self._hybrid_search(queryset, query, semantic_weight, keyword_weight)
            else:  # comprehensive
                results = self._comprehensive_search(queryset, query)
            
            # Paginate results
            paginator = Paginator(results, page_size)
            page_obj = paginator.get_page(page)
            
            # Serialize results
            serialized_results = []
            for memory in page_obj:
                serialized_results.append(
                    MemorySerializer(memory, context={'request': request}).data
                )
            
            # Build response
            response_data = {
                'results': serialized_results,
                'total': paginator.count,
                'query': query,
                'mode': mode,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_pages': paginator.num_pages,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                }
            }
            
            # Add mode-specific metadata
            if mode == 'hybrid':
                response_data['weights'] = {
                    'semantic': semantic_weight,
                    'keyword': keyword_weight
                }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response(
                {'error': f'Invalid parameter value: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Search failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _apply_filters(self, queryset, params):
        """Apply common filters to queryset"""
        
        # Filter by memory type
        memory_type = params.get('memory_type')
        if memory_type:
            queryset = queryset.filter(memory_type=memory_type)
        
        # Filter by importance range
        importance_min = params.get('importance_min')
        if importance_min:
            queryset = queryset.filter(importance__gte=int(importance_min))
        
        importance_max = params.get('importance_max')
        if importance_max:
            queryset = queryset.filter(importance__lte=int(importance_max))
        
        # Filter by date range
        date_from = params.get('date_from')
        if date_from:
            try:
                date_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=date_obj)
            except ValueError:
                pass  # Invalid date format, skip filter
        
        date_to = params.get('date_to')
        if date_to:
            try:
                date_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=date_obj)
            except ValueError:
                pass  # Invalid date format, skip filter
        
        # Filter by delivery type
        delivery_type = params.get('delivery_type')
        if delivery_type:
            queryset = queryset.filter(delivery_type=delivery_type)
        
        return queryset
    
    def _fast_search(self, queryset, query):
        """
        Fast keyword-based search
        Searches in: content, summary, tags
        """
        # Build search query using Q objects
        search_filter = (
            Q(content__icontains=query) |
            Q(summary__icontains=query) |
            Q(tags__contains=[query])  # JSONField contains
        )
        
        # Apply filter and order by relevance (created_at as proxy)
        results = queryset.filter(search_filter).order_by('-created_at')
        
        return list(results)
    
    def _semantic_search(self, queryset, query):
        """
        AI-powered semantic search
        Uses OpenAI embeddings or similar for meaning-based search
        Falls back to enhanced keyword search if AI unavailable
        """
        try:
            # Try semantic search service
            semantic_service = SemanticSearchService()
            if semantic_service.is_available():
                # Convert queryset to list for semantic search
                memories_list = list(queryset.values('id', 'content', 'summary', 'tags', 'importance'))
                
                # Search and get IDs
                try:
                    results_with_scores = semantic_service.semantic_search(
                        query=query,
                        memories=memories_list,
                        top_k=100
                    )
                    
                    # Extract memory IDs from results
                    memory_ids = [result['memory']['id'] for result in results_with_scores]
                    
                    # Return memories in order of semantic relevance
                    memory_dict = {m.id: m for m in queryset.filter(id__in=memory_ids)}
                    ordered_memories = [memory_dict[mid] for mid in memory_ids if mid in memory_dict]
                    
                    return ordered_memories
                except Exception as e:
                    print(f"Semantic search failed: {e}")
                    # Fall through to fallback
        except Exception as e:
            print(f"Semantic search service error: {e}")
        
        # Fallback: Enhanced keyword search with synonyms
        # Break query into words
        query_words = query.lower().split()
        
        # Build complex search with OR conditions
        search_filter = Q()
        for word in query_words:
            search_filter |= (
                Q(content__icontains=word) |
                Q(summary__icontains=word) |
                Q(ai_reasoning__icontains=word) |
                Q(tags__contains=[word])
            )
        
        results = queryset.filter(search_filter).distinct().order_by('-importance', '-created_at')
        
        return list(results)
    
    def _hybrid_search(self, queryset, query, semantic_weight=0.7, keyword_weight=0.3):
        """
        Hybrid search combining semantic and keyword search
        Uses weighted scoring to rank results
        """
        # Get semantic search results
        semantic_results = self._semantic_search(queryset, query)
        semantic_ids = {m.id: idx for idx, m in enumerate(semantic_results)}
        
        # Get keyword search results
        keyword_results = self._fast_search(queryset, query)
        keyword_ids = {m.id: idx for idx, m in enumerate(keyword_results)}
        
        # Combine results with weighted scoring
        all_ids = set(semantic_ids.keys()) | set(keyword_ids.keys())
        scored_results = []
        
        for memory_id in all_ids:
            # Calculate normalized scores (lower position = higher score)
            semantic_score = 0
            if memory_id in semantic_ids:
                position = semantic_ids[memory_id]
                semantic_score = 1.0 - (position / max(len(semantic_results), 1))
            
            keyword_score = 0
            if memory_id in keyword_ids:
                position = keyword_ids[memory_id]
                keyword_score = 1.0 - (position / max(len(keyword_results), 1))
            
            # Calculate weighted score
            final_score = (semantic_score * semantic_weight) + (keyword_score * keyword_weight)
            
            # Get memory object
            memory = queryset.get(id=memory_id)
            scored_results.append((memory, final_score))
        
        # Sort by score (highest first)
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
        # Return sorted memories
        return [memory for memory, score in scored_results]
    
    def _comprehensive_search(self, queryset, query):
        """
        Comprehensive search across ALL fields
        Searches in: content, summary, tags, ai_reasoning, memory_type
        """
        query_lower = query.lower()
        
        # Build comprehensive search filter
        search_filter = (
            Q(content__icontains=query) |
            Q(summary__icontains=query) |
            Q(tags__contains=[query]) |
            Q(ai_reasoning__icontains=query) |
            Q(memory_type__icontains=query)
        )
        
        # Apply filter and order by relevance
        results = queryset.filter(search_filter).order_by('-importance', '-created_at')
        
        return list(results.distinct())


class SearchSuggestionsView(APIView):
    """
    Provides search suggestions based on user's search history
    """
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            query = request.GET.get('q', '').strip()
            limit = min(int(request.GET.get('limit', 10)), 20)
            
            if not query:
                # Return recent searches
                from .models import MemorySearch
                recent_searches = MemorySearch.objects.filter(
                    user=request.user
                ).order_by('-created_at')[:limit]
                
                suggestions = [search.query for search in recent_searches]
                
                return Response({
                    'suggestions': suggestions,
                    'type': 'recent'
                })
            
            # Return suggestions based on partial query
            # Get unique tags that match
            memories = Memory.objects.filter(
                user=request.user,
                is_archived=False
            )
            
            # Extract matching tags
            matching_tags = set()
            for memory in memories:
                for tag in memory.tags:
                    if query.lower() in tag.lower():
                        matching_tags.add(tag)
            
            # Get matching memory types
            matching_types = []
            type_choices = ['general', 'work', 'personal', 'learning', 'idea', 'reminder']
            for t in type_choices:
                if query.lower() in t.lower():
                    matching_types.append(t)
            
            # Combine suggestions
            suggestions = list(matching_tags)[:5] + matching_types[:3]
            
            return Response({
                'suggestions': suggestions[:limit],
                'type': 'autocomplete',
                'query': query
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get suggestions: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

