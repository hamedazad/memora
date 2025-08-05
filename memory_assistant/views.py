from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import json
import os
from datetime import datetime, timedelta

from .models import Memory, MemorySearch
from .services import ChatGPTService
from .forms import MemoryForm, UserRegistrationForm
from .voice_service import voice_service
from .recommendation_service import AIRecommendationService


@login_required
def dashboard(request):
    """Main dashboard view"""
    memories = Memory.objects.filter(user=request.user, is_archived=False)
    
    # Get recent memories
    recent_memories = memories[:5]
    
    # Get memory statistics
    total_memories = memories.count()
    important_memories = memories.filter(importance__gte=8).count()
    
    # Get memory suggestions
    chatgpt_service = ChatGPTService()
    recent_memory_data = [
        {
            'content': memory.content,
            'tags': memory.tags
        } for memory in recent_memories
    ]
    suggestions = chatgpt_service.generate_memory_suggestions(recent_memory_data)
    
    context = {
        'recent_memories': recent_memories,
        'total_memories': total_memories,
        'important_memories': important_memories,
        'suggestions': suggestions,
        'ai_available': chatgpt_service.is_available(),
    }
    
    return render(request, 'memory_assistant/dashboard.html', context)


def safe_delete_file(file_path):
    """Safely delete a file with proper error handling"""
    import time
    try:
        if file_path and os.path.exists(file_path):
            # Add a small delay to ensure file is not in use
            time.sleep(0.1)
            os.unlink(file_path)
    except (OSError, PermissionError):
        pass  # File might be locked, ignore error





@login_required
def memory_list(request):
    """List all memories with enhanced filtering and search"""
    memories = Memory.objects.filter(user=request.user, is_archived=False)
    
    # Get filter parameters
    memory_type = request.GET.get('type')
    importance = request.GET.get('importance')
    search_query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort', '-created_at')
    
    # Apply filters
    if memory_type:
        memories = memories.filter(memory_type=memory_type)
    
    if importance:
        try:
            importance_val = int(importance)
            memories = memories.filter(importance__gte=importance_val)
        except ValueError:
            pass  # Ignore invalid importance values
    
    # Enhanced search functionality
    if search_query:
        # Create a comprehensive search query
        search_conditions = Q()
        
        # Search in content and summary
        search_conditions |= Q(content__icontains=search_query)
        search_conditions |= Q(summary__icontains=search_query)
        
        # Search in tags (JSON field)
        search_conditions |= Q(tags__contains=[search_query])
        
        # Search in AI reasoning
        search_conditions |= Q(ai_reasoning__icontains=search_query)
        
        # Split query into words for more flexible matching
        query_words = search_query.split()
        for word in query_words:
            if len(word) >= 2:  # Only search for words with 2+ characters
                search_conditions |= Q(content__icontains=word)
                search_conditions |= Q(summary__icontains=word)
                search_conditions |= Q(tags__contains=[word])
        
        memories = memories.filter(search_conditions)
    
    # Apply sorting
    valid_sort_fields = ['created_at', '-created_at', 'importance', '-importance', 'memory_type', '-memory_type']
    if sort_by in valid_sort_fields:
        memories = memories.order_by(sort_by)
    else:
        memories = memories.order_by('-created_at')  # Default sort
    
    # Pagination
    paginator = Paginator(memories, 12)  # Show more items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get statistics for the current filter
    total_memories = Memory.objects.filter(user=request.user, is_archived=False).count()
    filtered_count = memories.count()
    
    context = {
        'page_obj': page_obj,
        'memory_types': Memory.memory_type.field.choices,
        'search_query': search_query,
        'selected_type': memory_type,
        'selected_importance': importance,
        'selected_sort': sort_by,
        'total_memories': total_memories,
        'filtered_count': filtered_count,
        'has_filters': bool(search_query or memory_type or importance),
    }
    
    return render(request, 'memory_assistant/memory_list.html', context)


@login_required
def create_memory(request):
    """Create a new memory"""
    if request.method == 'POST':
        form = MemoryForm(request.POST)
        if form.is_valid():
            memory = form.save(commit=False)
            memory.user = request.user
            
            # Process with ChatGPT for auto-categorization
            chatgpt_service = ChatGPTService()
            processed_data = chatgpt_service.process_memory(memory.content)
            
            # Apply AI-generated categorization
            memory.summary = processed_data.get('summary', '')
            memory.ai_reasoning = processed_data.get('reasoning', '')
            memory.tags = processed_data.get('tags', [])
            memory.memory_type = processed_data.get('memory_type', 'general')
            memory.importance = processed_data.get('importance', 5)
            memory.save()
            
            messages.success(request, f'Memory created successfully! Categorized as: {memory.get_memory_type_display()}')
            return redirect('memory_assistant:memory_detail', memory_id=memory.id)
    else:
        form = MemoryForm()
    
    context = {
        'form': form,
        'ai_available': ChatGPTService().is_available(),
    }
    
    return render(request, 'memory_assistant/create_memory.html', context)


@login_required
def create_test_memory(request):
    """Create a test memory for demonstration purposes"""
    if request.method == 'POST':
        try:
            # Create multiple test memories
            memories_created = []
            
            # Memory 1: Today's plan
            memory1 = Memory.objects.create(
                user=request.user,
                content="Today's plan: 1) Morning meeting with team at 10 AM, 2) Lunch with client at 1 PM, 3) Review project documents in the afternoon, 4) Gym workout at 6 PM, 5) Dinner with family at 8 PM.",
                memory_type='reminder',
                importance=8,
                summary="Today's schedule including meetings, work tasks, and personal activities",
                tags=['today', 'plan', 'schedule', 'meeting', 'workout', 'dinner']
            )
            memories_created.append(memory1.id)
            
            # Memory 2: Shopping list
            memory2 = Memory.objects.create(
                user=request.user,
                content="Shopping list for today: milk, bread, eggs, vegetables, and cat food for my cat.",
                memory_type='shopping',
                importance=6,
                summary="Grocery shopping list including pet supplies",
                tags=['shopping', 'today', 'grocery', 'cat']
            )
            memories_created.append(memory2.id)
            
            # Memory 3: Work reminder
            memory3 = Memory.objects.create(
                user=request.user,
                content="Important work reminder: submit the quarterly report by Friday, prepare presentation for next week's meeting.",
                memory_type='reminder',
                importance=9,
                summary="Work deadlines and meeting preparation",
                tags=['work', 'deadline', 'meeting', 'report']
            )
            memories_created.append(memory3.id)
            
            return JsonResponse({
                'success': True,
                'message': f'Created {len(memories_created)} test memories successfully!',
                'memory_ids': memories_created
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def memory_detail(request, memory_id):
    """View a specific memory"""
    memory = get_object_or_404(Memory, id=memory_id, user=request.user)
    
    context = {
        'memory': memory,
    }
    
    return render(request, 'memory_assistant/memory_detail.html', context)


@login_required
def edit_memory(request, memory_id):
    """Edit a memory"""
    memory = get_object_or_404(Memory, id=memory_id, user=request.user)
    
    if request.method == 'POST':
        form = MemoryForm(request.POST, instance=memory)
        if form.is_valid():
            memory = form.save(commit=False)
            
            # Reprocess with ChatGPT if content changed
            chatgpt_service = ChatGPTService()
            processed_data = chatgpt_service.process_memory(memory.content)
            
            memory.summary = processed_data.get('summary', '')
            memory.tags = processed_data.get('tags', [])
            memory.save()
            
            messages.success(request, 'Memory updated successfully!')
            return redirect('memory_assistant:memory_detail', memory_id=memory.id)
    else:
        form = MemoryForm(instance=memory)
    
    context = {
        'form': form,
        'memory': memory,
        'ai_available': ChatGPTService().is_available(),
    }
    
    return render(request, 'memory_assistant/edit_memory.html', context)


@login_required
def delete_memory(request, memory_id):
    """Delete a memory"""
    memory = get_object_or_404(Memory, id=memory_id, user=request.user)
    
    if request.method == 'POST':
        memory.delete()
        messages.success(request, 'Memory deleted successfully!')
        return redirect('memory_assistant:memory_list')
    
    context = {
        'memory': memory,
    }
    
    return render(request, 'memory_assistant/delete_memory.html', context)


@login_required
def search_memories(request):
    """Enhanced search memories with AI-powered semantic search"""
    query = request.GET.get('q', '').strip()
    memories = []
    search_method = "basic"
    
    if query:
        # Get all memories for the user
        all_memories = Memory.objects.filter(
            user=request.user,
            is_archived=False
        )
        
        # Try AI-powered semantic search first
        try:
            chatgpt_service = ChatGPTService()
            if chatgpt_service.is_available():
                # Use AI to find semantically related memories
                memory_data = [
                    {
                        'id': memory.id,
                        'content': memory.content,
                        'summary': memory.summary or '',
                        'tags': memory.tags or [],
                        'memory_type': memory.memory_type
                    }
                    for memory in all_memories
                ]
                
                ai_results = chatgpt_service.search_memories(query, memory_data)
                if ai_results:
                    # Get the memory IDs from AI results
                    ai_memory_ids = [result.get('id') for result in ai_results if result.get('id')]
                    memories = all_memories.filter(id__in=ai_memory_ids)
                    search_method = "ai_semantic"
        except Exception as e:
            print(f"AI search failed, falling back to basic search: {e}")
        
        # If AI search didn't work or returned no results, use enhanced basic search
        if not memories:
            search_conditions = Q()
            
            # Search in content and summary
            search_conditions |= Q(content__icontains=query)
            search_conditions |= Q(summary__icontains=query)
            
            # Search in tags (JSON field)
            search_conditions |= Q(tags__contains=[query])
            
            # Search in AI reasoning
            search_conditions |= Q(ai_reasoning__icontains=query)
            
            # Split query into words for more flexible matching
            query_words = query.split()
            for word in query_words:
                if len(word) >= 2:  # Only search for words with 2+ characters
                    search_conditions |= Q(content__icontains=word)
                    search_conditions |= Q(summary__icontains=word)
                    search_conditions |= Q(tags__contains=[word])
            
            memories = all_memories.filter(search_conditions)
            search_method = "enhanced_basic"
        
        # If still no results, try fuzzy matching
        if not memories:
            # Try searching for partial matches
            for word in query.split():
                if len(word) >= 3:
                    memories = all_memories.filter(
                        Q(content__icontains=word) |
                        Q(summary__icontains=word) |
                        Q(tags__contains=[word])
                    )
                    if memories.exists():
                        search_method = "fuzzy"
                        break
        
        # If no results found, show recent memories as suggestions
        if not memories:
            memories = all_memories.order_by('-created_at')[:5]
            search_method = "suggestions"
    
    context = {
        'search_results': memories,
        'results_count': len(memories),
        'query': query,
        'search_method': search_method,
        'ai_available': ChatGPTService().is_available(),
    }
    
    return render(request, 'memory_assistant/search_results.html', context)


@login_required
@csrf_exempt
def quick_add_memory(request):
    """Quick add memory via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()
            
            if len(content) < 10:
                return JsonResponse({
                    'success': False,
                    'error': 'Memory content must be at least 10 characters long.'
                })
            
            # Process with ChatGPT first to get categorization
            chatgpt_service = ChatGPTService()
            processed_data = chatgpt_service.process_memory(content)
            
            # Create memory with AI categorization
            memory = Memory.objects.create(
                user=request.user,
                content=content,
                memory_type=processed_data.get('memory_type', 'general'),
                importance=processed_data.get('importance', 5),
                summary=processed_data.get('summary', ''),
                ai_reasoning=processed_data.get('reasoning', ''),
                tags=processed_data.get('tags', [])
            )
            
            return JsonResponse({
                'success': True,
                'memory_id': memory.id,
                'message': f'Memory added successfully! Categorized as: {memory.get_memory_type_display()}',
                'category': memory.memory_type,
                'importance': memory.importance
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


@login_required
def archive_memory(request, memory_id):
    """Archive a memory"""
    memory = get_object_or_404(Memory, id=memory_id, user=request.user)
    
    if request.method == 'POST':
        memory.is_archived = True
        memory.save()
        messages.success(request, 'Memory archived successfully!')
        return redirect('memory_assistant:memory_list')
    
    context = {
        'memory': memory,
    }
    
    return render(request, 'memory_assistant/archive_memory.html', context)


# Voice-related views
@login_required
def voice_create_memory(request):
    """Create memory using voice input"""
    if request.method == 'POST':
        try:
            # Check if text input was provided (for testing)
            if request.POST.get('text'):
                text = request.POST.get('text')
                
                # Use AI to categorize the audio memory
                from .voice_service import voice_service
                categorization = voice_service.categorize_audio_memory(text)
                
                # Create the memory with AI categorization
                memory = Memory.objects.create(
                    user=request.user,
                    content=text,
                    summary=categorization.get('summary', ''),
                    ai_reasoning=categorization.get('reasoning', ''),
                    tags=categorization.get('tags', []),
                    memory_type=categorization.get('category', 'general'),
                    importance=categorization.get('importance', 5)
                )
                
                return JsonResponse({
                    'success': True,
                    'content': text,
                    'memory_id': memory.id,
                    'category': categorization.get('category', 'general'),
                    'confidence': categorization.get('confidence', 50),
                    'summary': categorization.get('summary', ''),
                    'tags': categorization.get('tags', []),
                    'importance': categorization.get('importance', 5)
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'No text provided'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return render(request, 'memory_assistant/voice_create_memory.html')


@login_required
def voice_read_memory(request, memory_id):
    """Read memory content using text-to-speech"""
    memory = get_object_or_404(Memory, id=memory_id, user=request.user)
    
    if request.method == 'POST':
        try:
            # Speak the memory content
            text_to_speak = f"Memory: {memory.content}"
            if memory.summary:
                text_to_speak += f" Summary: {memory.summary}"
            
            success = voice_service.speak_text(text_to_speak)
            
            return JsonResponse({
                'success': success,
                'message': 'Memory read aloud' if success else 'Failed to read memory'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def voice_search_memories(request):
    """Search memories using voice input"""
    if request.method == 'POST':
        try:
            # Check if text input was provided
            if request.POST.get('text'):
                query = request.POST.get('text')
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'No search query provided'
                })
            
            print(f"DEBUG: Searching for query: '{query}'")  # Debug log
            
            # Search memories with more flexible matching
            memories = Memory.objects.filter(
                user=request.user,
                is_archived=False
            )
            
            print(f"DEBUG: Total memories for user: {memories.count()}")  # Debug log
            
            # Show all memories for debugging
            for memory in memories[:5]:
                print(f"DEBUG: Memory {memory.id}: {memory.content[:100]}...")
            
            # Split query into words for better matching
            query_words = query.lower().split()
            print(f"DEBUG: Query words: {query_words}")  # Debug log
            
            # Create a more flexible search - try multiple approaches
            search_conditions = Q()
            
            # First try: exact phrase match
            search_conditions |= Q(content__icontains=query)
            search_conditions |= Q(summary__icontains=query)
            
            # Second try: individual word matches (more lenient)
            for word in query_words:
                if len(word) >= 2:  # Allow shorter words
                    search_conditions |= Q(content__icontains=word)
                    search_conditions |= Q(summary__icontains=word)
            
            # Third try: partial matches for common words
            common_words = ['plan', 'today', 'meeting', 'work', 'home', 'buy', 'need']
            for word in common_words:
                if word in query.lower():
                    search_conditions |= Q(content__icontains=word)
                    search_conditions |= Q(summary__icontains=word)
            
            memories = memories.filter(search_conditions)
            
            print(f"DEBUG: Memories after filtering: {memories.count()}")  # Debug log
            
            # Apply contextual filtering to remove irrelevant results
            if memories.count() > 0:
                filtered_memories = []
                query_lower = query.lower()
                
                for memory in memories:
                    content_lower = memory.content.lower()
                    summary_lower = memory.summary.lower() if memory.summary else ""
                    
                    # Context-specific filtering
                    is_relevant = True
                    
                    # Time-based filtering - be more precise about time context
                    if 'today' in query_lower:
                        # If searching for "today", exclude memories that mention other days
                        time_indicators = ['tomorrow', 'yesterday', 'next week', 'next month', 'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
                        if any(indicator in content_lower for indicator in time_indicators):
                            # Check if it's actually about today or a different day
                            if 'today' not in content_lower and 'now' not in content_lower:
                                is_relevant = False
                    
                    elif 'tomorrow' in query_lower:
                        # If searching for "tomorrow", exclude memories that mention other days
                        time_indicators = ['today', 'yesterday', 'next week', 'next month', 'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
                        if any(indicator in content_lower for indicator in time_indicators):
                            # Check if it's actually about tomorrow or a different day
                            if 'tomorrow' not in content_lower:
                                is_relevant = False
                    
                    # For "call" related queries, ensure the memory is actually about calling someone
                    elif 'call' in query_lower:
                        call_indicators = ['call', 'phone', 'contact', 'dial', 'ring']
                        if not any(indicator in content_lower for indicator in call_indicators):
                            is_relevant = False
                    
                    # For "plan" related queries, ensure it's about planning or scheduling
                    elif 'plan' in query_lower:
                        plan_indicators = ['plan', 'schedule', 'arrange', 'organize', 'prepare']
                        if not any(indicator in content_lower for indicator in plan_indicators):
                            is_relevant = False
                    
                    # For "buy" or "shopping" related queries
                    elif any(word in query_lower for word in ['buy', 'purchase', 'shop', 'shopping']):
                        shopping_indicators = ['buy', 'purchase', 'shop', 'shopping', 'list', 'store', 'market']
                        if not any(indicator in content_lower for indicator in shopping_indicators):
                            is_relevant = False
                    
                    # For "meeting" related queries
                    elif 'meeting' in query_lower:
                        meeting_indicators = ['meeting', 'appointment', 'conference', 'discussion', 'session']
                        if not any(indicator in content_lower for indicator in meeting_indicators):
                            is_relevant = False
                
                    if is_relevant:
                        filtered_memories.append(memory)
                
                memories = filtered_memories
                print(f"DEBUG: Memories after contextual filtering: {len(memories)}")  # Debug log
            
            # If still no results, return all recent memories as suggestions
            if len(memories) == 0:
                print("DEBUG: No memories found, returning recent memories as suggestions")
                recent_memories = Memory.objects.filter(
                    user=request.user,
                    is_archived=False
                ).order_by('-created_at')[:5]
                
                suggestions = []
                for memory in recent_memories:
                    days_old = (datetime.now() - memory.created_at.replace(tzinfo=None)).days
                    if days_old == 0:
                        recency = "Today"
                    elif days_old == 1:
                        recency = "Yesterday"
                    elif days_old <= 7:
                        recency = f"{days_old} days ago"
                    else:
                        recency = memory.created_at.strftime('%Y-%m-%d')
                    
                    suggestions.append({
                        'id': memory.id,
                        'content': memory.content[:100] + '...' if len(memory.content) > 100 else memory.content,
                        'summary': memory.summary,
                        'created_at': memory.created_at.strftime('%Y-%m-%d %H:%M'),
                        'recency': recency
                    })
                
                return JsonResponse({
                    'success': True,
                    'query': query,
                    'results': [],
                    'message': f'No memories found for "{query}". Here are your recent memories:',
                    'suggestions': suggestions
                })
            
            # Score and rank results based on relevance
            scored_memories = []
            
            for memory in memories:
                score = 0
                content_lower = memory.content.lower()
                summary_lower = memory.summary.lower() if memory.summary else ""
                
                # Time-based relevance scoring
                days_old = (datetime.now() - memory.created_at.replace(tzinfo=None)).days
                
                # Recent memories get higher scores
                if days_old == 0:  # Today
                    score += 50
                elif days_old <= 7:  # This week
                    score += 30
                elif days_old <= 30:  # This month
                    score += 15
                elif days_old <= 90:  # Last 3 months
                    score += 5
                else:  # Older memories get penalty
                    score -= 20
                
                # Exact phrase match gets highest score
                if query.lower() in content_lower:
                    score += 100
                if query.lower() in summary_lower:
                    score += 80
                
                # Word-by-word scoring
                for word in query_words:
                    if len(word) >= 2:
                        # Multiple occurrences get higher score
                        word_count = content_lower.count(word)
                        score += word_count * 10
                        
                        if word in summary_lower:
                            score += 5
                
                # Context-specific boosting
                
                # Time-related queries (today, now, today's plan, etc.)
                time_words = ['today', 'now', 'tonight', 'tomorrow', 'this week', 'plan', 'schedule']
                if any(word in query.lower() for word in time_words):
                    # Boost recent memories significantly
                    if days_old <= 7:
                        score += 40
                    # Penalize old memories more heavily
                    elif days_old > 30:
                        score -= 50
                
                # Shopping-related queries
                shopping_words = ['buy', 'purchase', 'shop', 'shopping', 'list', 'need', 'want']
                if any(word in query.lower() for word in shopping_words):
                    if any(word in content_lower for word in ['buy', 'purchase', 'shop', 'shopping', 'list']):
                        score += 20
                
                # Pet-related queries
                pet_words = ['cat', 'dog', 'pet', 'animal']
                if any(word in query.lower() for word in pet_words):
                    if any(word in content_lower for word in ['cat', 'dog', 'pet', 'animal']):
                        score += 30
                
                # Appointment/meeting queries
                appointment_words = ['appointment', 'meeting', 'schedule', 'meet', 'call']
                if any(word in query.lower() for word in appointment_words):
                    if any(word in content_lower for word in ['appointment', 'meeting', 'schedule', 'meet', 'call']):
                        score += 25
                        # Boost recent appointments
                        if days_old <= 7:
                            score += 30
                
                # Filter out very old memories for time-sensitive queries
                if any(word in query.lower() for word in ['today', 'now', 'tonight', 'tomorrow', 'this week']):
                    if days_old > 30:  # Skip memories older than 30 days for time queries
                        continue
                
                if score > 0:
                    scored_memories.append((memory, score))
                    print(f"DEBUG: Memory {memory.id} scored {score}: {memory.content[:50]}...")  # Debug log
            
            print(f"DEBUG: Scored memories: {len(scored_memories)}")  # Debug log
            
            # Sort by relevance score (highest first)
            scored_memories.sort(key=lambda x: x[1], reverse=True)
            
            # Take top 10 results
            top_memories = [memory for memory, score in scored_memories[:10]]
            
            results = []
            for memory in top_memories:
                # Add recency indicator
                days_old = (datetime.now() - memory.created_at.replace(tzinfo=None)).days
                if days_old == 0:
                    recency = "Today"
                elif days_old == 1:
                    recency = "Yesterday"
                elif days_old <= 7:
                    recency = f"{days_old} days ago"
                elif days_old <= 30:
                    recency = f"{days_old} days ago"
                else:
                    recency = memory.created_at.strftime('%Y-%m-%d')
                
                results.append({
                    'id': memory.id,
                    'content': memory.content[:100] + '...' if len(memory.content) > 100 else memory.content,
                    'summary': memory.summary,
                    'created_at': memory.created_at.strftime('%Y-%m-%d %H:%M'),
                    'recency': recency
                })
            
            print(f"DEBUG: Final results count: {len(results)}")  # Debug log
            
            return JsonResponse({
                'success': True,
                'query': query,
                'results': results
            })
                
        except Exception as e:
            print(f"DEBUG: Error in voice_search_memories: {str(e)}")  # Debug log
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return render(request, 'memory_assistant/voice_search.html')


@login_required
def debug_memories(request):
    """Debug endpoint to check memories in database"""
    if request.method == 'GET':
        try:
            memories = Memory.objects.filter(user=request.user, is_archived=False)
            
            debug_info = {
                'total_memories': memories.count(),
                'recent_memories': []
            }
            
            for memory in memories.order_by('-created_at')[:5]:
                debug_info['recent_memories'].append({
                    'id': memory.id,
                    'content': memory.content[:100] + '...' if len(memory.content) > 100 else memory.content,
                    'created_at': memory.created_at.strftime('%Y-%m-%d %H:%M'),
                    'memory_type': memory.memory_type,
                    'importance': memory.importance
                })
            
            return JsonResponse({
                'success': True,
                'debug_info': debug_info
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def ai_recommendations(request):
    """Get AI-powered personalized recommendations"""
    if request.method == 'GET':
        try:
            recommendation_service = AIRecommendationService()
            
            if not recommendation_service.is_available():
                return JsonResponse({
                    'success': False,
                    'error': 'AI recommendations are not available. Please check your OpenAI API key.',
                    'ai_available': False
                })
            
            recommendations = recommendation_service.get_personalized_recommendations(request.user)
            
            return JsonResponse({
                'success': True,
                'ai_available': True,
                'recommendations': recommendations
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'ai_available': False
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def ai_insights(request):
    """Get AI-powered insights about user's memory patterns"""
    if request.method == 'GET':
        try:
            recommendation_service = AIRecommendationService()
            
            if not recommendation_service.is_available():
                return JsonResponse({
                    'success': False,
                    'error': 'AI insights are not available. Please check your OpenAI API key.',
                    'ai_available': False
                })
            
            insights = recommendation_service.get_memory_insights(request.user)
            
            return JsonResponse({
                'success': True,
                'ai_available': True,
                'insights': insights
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'ai_available': False
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def smart_search_suggestions(request):
    """Get smart search suggestions based on user's memories"""
    if request.method == 'GET':
        query = request.GET.get('q', '')
        
        if not query:
            return JsonResponse({
                'success': False,
                'error': 'Query parameter is required'
            })
        
        try:
            recommendation_service = AIRecommendationService()
            
            if not recommendation_service.is_available():
                return JsonResponse({
                    'success': False,
                    'error': 'Smart search suggestions are not available.',
                    'ai_available': False
                })
            
            suggestions = recommendation_service.get_smart_search_suggestions(request.user, query)
            
            return JsonResponse({
                'success': True,
                'ai_available': True,
                'suggestions': suggestions
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'ai_available': False
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})





def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Account created successfully for {user.username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'memory_assistant/register.html', {'form': form}) 