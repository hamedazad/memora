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
from django.utils import timezone

from .models import Memory, MemorySearch
from .services import ChatGPTService
from .forms import MemoryForm, UserRegistrationForm
from .voice_service import voice_service
from .recommendation_service import AIRecommendationService


@login_required
def dashboard(request):
    """Main dashboard view"""
    memories = Memory.objects.filter(user=request.user, is_archived=False)
    
    # Get today's scheduled memories
    today = timezone.now().date()
    todays_memories = memories.filter(scheduled_date=today).order_by('importance')
    
    # Get overdue memories
    overdue_memories = memories.filter(scheduled_date__lt=today, scheduled_date__isnull=False).order_by('scheduled_date')
    
    # Get upcoming memories (next 7 days)
    upcoming_memories = memories.filter(
        scheduled_date__gt=today,
        scheduled_date__lte=today + timedelta(days=7)
    ).order_by('scheduled_date')
    
    # Get recent memories (not scheduled for today)
    recent_memories = memories.filter(scheduled_date__isnull=True)[:5]
    
    # Get memory statistics
    total_memories = memories.count()
    important_memories = memories.filter(importance__gte=8).count()
    scheduled_memories = memories.filter(scheduled_date__isnull=False).count()
    
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
        'todays_memories': todays_memories,
        'overdue_memories': overdue_memories,
        'upcoming_memories': upcoming_memories,
        'recent_memories': recent_memories,
        'total_memories': total_memories,
        'important_memories': important_memories,
        'scheduled_memories': scheduled_memories,
        'suggestions': suggestions,
        'ai_available': chatgpt_service.is_available(),
        'today': today,
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
    date_filter = request.GET.get('date_filter', '')
    
    # Apply filters
    if memory_type:
        memories = memories.filter(memory_type=memory_type)
    
    if importance:
        try:
            importance_val = int(importance)
            memories = memories.filter(importance__gte=importance_val)
        except ValueError:
            pass  # Ignore invalid importance values
    
    # Apply date-based filtering
    today = timezone.now().date()
    if date_filter == 'today':
        memories = memories.filter(scheduled_date=today)
    elif date_filter == 'overdue':
        memories = memories.filter(scheduled_date__lt=today, scheduled_date__isnull=False)
    elif date_filter == 'upcoming':
        memories = memories.filter(scheduled_date__gt=today, scheduled_date__isnull=False)
    elif date_filter == 'scheduled':
        memories = memories.filter(scheduled_date__isnull=False)
    elif date_filter == 'unscheduled':
        memories = memories.filter(scheduled_date__isnull=True)
    
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
    valid_sort_fields = ['created_at', '-created_at', 'importance', '-importance', 'memory_type', '-memory_type', 'scheduled_date', '-scheduled_date']
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
    
    # Get date filter statistics
    todays_count = Memory.objects.filter(user=request.user, is_archived=False, scheduled_date=today).count()
    overdue_count = Memory.objects.filter(user=request.user, is_archived=False, scheduled_date__lt=today, scheduled_date__isnull=False).count()
    upcoming_count = Memory.objects.filter(user=request.user, is_archived=False, scheduled_date__gt=today, scheduled_date__isnull=False).count()
    scheduled_count = Memory.objects.filter(user=request.user, is_archived=False, scheduled_date__isnull=False).count()
    
    context = {
        'page_obj': page_obj,
        'memory_types': Memory.memory_type.field.choices,
        'search_query': search_query,
        'selected_type': memory_type,
        'selected_importance': importance,
        'selected_sort': sort_by,
        'selected_date_filter': date_filter,
        'total_memories': total_memories,
        'filtered_count': filtered_count,
        'todays_count': todays_count,
        'overdue_count': overdue_count,
        'upcoming_count': upcoming_count,
        'scheduled_count': scheduled_count,
        'has_filters': bool(search_query or memory_type or importance or date_filter),
        'today': today,
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
            
            # Process with ChatGPT for auto-categorization and date extraction
            chatgpt_service = ChatGPTService()
            processed_data = chatgpt_service.process_memory(memory.content)
            
            # Apply AI-generated categorization
            memory.summary = processed_data.get('summary', '')
            memory.ai_reasoning = processed_data.get('ai_reasoning', '')
            memory.tags = processed_data.get('tags', [])
            memory.memory_type = processed_data.get('memory_type', 'general')
            memory.importance = processed_data.get('importance', 5)
            
            # Set scheduled date if extracted
            extracted_date = processed_data.get('extracted_date')
            if extracted_date:
                memory.scheduled_date = extracted_date
            
            memory.save()
            
            # Create success message with date information
            success_msg = f'Memory created successfully! Categorized as: {memory.get_memory_type_display()}'
            if memory.scheduled_date:
                if memory.is_due_today:
                    success_msg += f' (Scheduled for today: {memory.scheduled_date.strftime("%B %d, %Y")})'
                elif memory.is_overdue:
                    success_msg += f' (Overdue from: {memory.scheduled_date.strftime("%B %d, %Y")})'
                else:
                    success_msg += f' (Scheduled for: {memory.scheduled_date.strftime("%B %d, %Y")})'
            
            messages.success(request, success_msg)
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
    """Create test memories for demonstration purposes"""
    if request.method == 'POST':
        try:
            # Create test memories that would match natural language queries
            test_memories = [
                {
                    'content': 'Meeting with the development team tomorrow at 2 PM to discuss the new feature implementation and project timeline.',
                    'memory_type': 'work',
                    'importance': 8,
                    'summary': 'Work meeting about new feature development',
                    'tags': ['meeting', 'development', 'feature', 'project', 'tomorrow'],
                    'ai_reasoning': 'This is a work-related memory about a professional meeting scheduled for tomorrow',
                    'scheduled_date': (timezone.now() + timedelta(days=1)).date()
                },
                {
                    'content': 'Need to buy groceries tomorrow: milk, bread, eggs, and vegetables. Also pick up the dry cleaning.',
                    'memory_type': 'reminder',
                    'importance': 6,
                    'summary': 'Shopping list and errands for tomorrow',
                    'tags': ['shopping', 'groceries', 'errands', 'dry cleaning', 'tomorrow'],
                    'ai_reasoning': 'This is a reminder for shopping and errands scheduled for tomorrow',
                    'scheduled_date': (timezone.now() + timedelta(days=1)).date()
                },
                {
                    'content': 'Dentist appointment tomorrow at 10 AM. Need to bring insurance card and remember to floss tonight.',
                    'memory_type': 'reminder',
                    'importance': 7,
                    'summary': 'Dentist appointment scheduled for tomorrow',
                    'tags': ['dentist', 'appointment', 'health', 'tomorrow'],
                    'ai_reasoning': 'This is a health-related reminder for a dentist appointment tomorrow',
                    'scheduled_date': (timezone.now() + timedelta(days=1)).date()
                },
                {
                    'content': 'Planning to work on the new project tomorrow. Need to review the requirements and start coding the basic structure.',
                    'memory_type': 'work',
                    'importance': 8,
                    'summary': 'Project work planned for tomorrow',
                    'tags': ['work', 'project', 'coding', 'planning', 'tomorrow'],
                    'ai_reasoning': 'This is a work-related plan for tomorrow involving project development',
                    'scheduled_date': (timezone.now() + timedelta(days=1)).date()
                },
                {
                    'content': 'Family dinner tomorrow evening. Mom is cooking her famous lasagna and we\'re all bringing side dishes.',
                    'memory_type': 'personal',
                    'importance': 9,
                    'summary': 'Family dinner planned for tomorrow evening',
                    'tags': ['family', 'dinner', 'lasagna', 'tomorrow'],
                    'ai_reasoning': 'This is a personal memory about family plans for tomorrow evening',
                    'scheduled_date': (timezone.now() + timedelta(days=1)).date()
                },
                {
                    'content': 'Call the insurance company tomorrow to update my policy. Need to discuss the new coverage options.',
                    'memory_type': 'reminder',
                    'importance': 6,
                    'summary': 'Insurance policy update call scheduled for tomorrow',
                    'tags': ['call', 'insurance', 'policy', 'tomorrow'],
                    'ai_reasoning': 'This is a reminder to call the insurance company tomorrow',
                    'scheduled_date': (timezone.now() + timedelta(days=1)).date()
                },
                {
                    'content': 'Gym workout planned for tomorrow morning. Going to focus on upper body strength training.',
                    'memory_type': 'personal',
                    'importance': 7,
                    'summary': 'Gym workout scheduled for tomorrow morning',
                    'tags': ['gym', 'workout', 'exercise', 'tomorrow'],
                    'ai_reasoning': 'This is a personal fitness plan for tomorrow morning',
                    'scheduled_date': (timezone.now() + timedelta(days=1)).date()
                },
                {
                    'content': 'Submit the quarterly report tomorrow by 5 PM. Need to finalize the data analysis and create the presentation.',
                    'memory_type': 'work',
                    'importance': 9,
                    'summary': 'Quarterly report submission deadline tomorrow',
                    'tags': ['report', 'deadline', 'work', 'tomorrow'],
                    'ai_reasoning': 'This is a work-related deadline for tomorrow',
                    'scheduled_date': (timezone.now() + timedelta(days=1)).date()
                }
            ]
            
            created_count = 0
            for memory_data in test_memories:
                memory = Memory.objects.create(
                    user=request.user,
                    content=memory_data['content'],
                    memory_type=memory_data['memory_type'],
                    importance=memory_data['importance'],
                    summary=memory_data['summary'],
                    ai_reasoning=memory_data['ai_reasoning'],
                    tags=memory_data['tags'],
                    scheduled_date=memory_data['scheduled_date']
                )
                created_count += 1
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully created {created_count} test memories!',
                'created_count': created_count
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


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
    """Enhanced search memories with improved natural language support"""
    query = request.GET.get('q', '').strip()
    
    # Initialize memories as an empty QuerySet instead of a list
    memories = Memory.objects.none()
    search_method = "basic"
    date_filter_applied = False
    extracted_date = None
    
    if query:
        # Get all memories for the user
        all_memories = Memory.objects.filter(
            user=request.user,
            is_archived=False
        )
        
        # First, check if the query contains date information
        from .date_recognition_service import date_recognition_service
        date_analysis = date_recognition_service.analyze_text_for_date_context(query)
        extracted_date = date_analysis.get('date')
        
        if extracted_date:
            print(f"DEBUG: Date extracted from query '{query}': {extracted_date}")
            # Filter memories by the extracted date
            memories = all_memories.filter(scheduled_date=extracted_date)
            date_filter_applied = True
            search_method = "date_filtered"
            
            # If no memories found for the specific date, try broader date-based search
            if not memories.exists():
                # Look for memories that mention the date in content
                date_str = extracted_date.strftime('%Y-%m-%d')
                memories = all_memories.filter(
                    Q(content__icontains=date_str) |
                    Q(summary__icontains=date_str) |
                    Q(content__icontains=extracted_date.strftime('%B %d')) |  # "August 6"
                    Q(content__icontains=extracted_date.strftime('%b %d'))    # "Aug 6"
                )
                search_method = "date_content_search"
        
        # If no date-specific results or no date found, proceed with regular search
        if not memories.exists():
            # Try AI-powered semantic search first
            try:
                chatgpt_service = ChatGPTService()
                if chatgpt_service.is_available():
                    # Use AI to find semantically related memories - create a fresh QuerySet for this
                    ai_memories = Memory.objects.filter(
                        user=request.user,
                        is_archived=False
                    )
                    memory_data = [
                        {
                            'id': memory.id,
                            'content': memory.content,
                            'summary': memory.summary or '',
                            'tags': memory.tags or [],
                            'memory_type': memory.memory_type,
                            'scheduled_date': memory.scheduled_date.isoformat() if memory.scheduled_date else None
                        }
                    for memory in ai_memories
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
            if not memories.exists():
                search_conditions = Q()
                
                # Search in content and summary
                search_conditions |= Q(content__icontains=query)
                search_conditions |= Q(summary__icontains=query)
                
                # Search in tags (JSON field)
                search_conditions |= Q(tags__contains=[query])
                
                # Search in AI reasoning
                search_conditions |= Q(ai_reasoning__icontains=query)
                
                # Split query into words for more flexible matching
                query_words = query.lower().split()
                for word in query_words:
                    if len(word) >= 1:  # Allow single character words for better matching
                        search_conditions |= Q(content__icontains=word)
                        search_conditions |= Q(summary__icontains=word)
                        search_conditions |= Q(tags__contains=[word])
                
                # Add semantic variations for common terms
                semantic_variations = {
                    'plan': ['plan', 'plans', 'planning', 'schedule', 'scheduled', 'arrange', 'arrangement'],
                    'tomorrow': ['tomorrow', 'next day', 'day after', 'upcoming'],
                    'today': ['today', 'tonight', 'this evening', 'now'],
                    'meeting': ['meeting', 'appointment', 'call', 'conference', 'discussion'],
                    'buy': ['buy', 'purchase', 'shop', 'shopping', 'get', 'pick up'],
                    'call': ['call', 'phone', 'contact', 'dial', 'ring'],
                    'work': ['work', 'job', 'office', 'professional', 'business'],
                    'family': ['family', 'home', 'personal', 'kids', 'children'],
                    'learn': ['learn', 'learning', 'study', 'education', 'tutorial'],
                    'idea': ['idea', 'concept', 'thought', 'innovation', 'creative']
                }
                
                # Add semantic variations for words in the query
                for word in query_words:
                    if word in semantic_variations:
                        for variation in semantic_variations[word]:
                            search_conditions |= Q(content__icontains=variation)
                            search_conditions |= Q(summary__icontains=variation)
                            search_conditions |= Q(tags__contains=[variation])
                
                memories = all_memories.filter(search_conditions)
                search_method = "enhanced_basic"
            
            # If still no results, try fuzzy matching with partial words
            if not memories.exists():
                search_conditions = Q()
                for word in query_words:
                    if len(word) >= 2:
                        # Try partial word matching
                        search_conditions |= Q(content__icontains=word[:3])  # First 3 characters
                        search_conditions |= Q(summary__icontains=word[:3])
                
                memories = all_memories.filter(search_conditions)
                search_method = "fuzzy_match"
            
            # If still no results, show recent memories as suggestions
            if not memories.exists():
                memories = all_memories.order_by('-created_at')
                search_method = "recent_suggestions"
        
        # Prepare results for template - convert to list only at the end
        results = []
        for memory in memories[:10]:  # Limit to 10 results here instead
            results.append({
                'id': memory.id,
                'content': memory.content,
                'summary': memory.summary,
                'memory_type': memory.memory_type,
                'importance': memory.importance,
                'created_at': memory.created_at,
                'scheduled_date': memory.scheduled_date,
                'tags': memory.tags,
                'ai_reasoning': memory.ai_reasoning,
            })
        
        context = {
            'query': query,
            'results': results,
            'search_method': search_method,
            'date_filter_applied': date_filter_applied,
            'extracted_date': extracted_date,
            'results_count': len(results),
            'ai_available': ChatGPTService().is_available(),
        }
        
        return render(request, 'memory_assistant/search_results.html', context)
    
    # If no query, show search form
    context = {
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
            
            # Process with ChatGPT first to get categorization and date extraction
            chatgpt_service = ChatGPTService()
            processed_data = chatgpt_service.process_memory(content)
            
            # Create memory with AI categorization and date extraction
            memory = Memory.objects.create(
                user=request.user,
                content=content,
                memory_type=processed_data.get('memory_type', 'general'),
                importance=processed_data.get('importance', 5),
                summary=processed_data.get('summary', ''),
                ai_reasoning=processed_data.get('ai_reasoning', ''),
                tags=processed_data.get('tags', []),
                scheduled_date=processed_data.get('extracted_date')
            )
            
            # Create success message with date information
            success_msg = f'Memory added successfully! Categorized as: {memory.get_memory_type_display()}'
            if memory.scheduled_date:
                if memory.is_due_today:
                    success_msg += f' (Scheduled for today: {memory.scheduled_date.strftime("%B %d, %Y")})'
                elif memory.is_overdue:
                    success_msg += f' (Overdue from: {memory.scheduled_date.strftime("%B %d, %Y")})'
                else:
                    success_msg += f' (Scheduled for: {memory.scheduled_date.strftime("%B %d, %Y")})'
            
            return JsonResponse({
                'success': True,
                'memory_id': memory.id,
                'message': success_msg,
                'category': memory.memory_type,
                'importance': memory.importance,
                'scheduled_date': memory.scheduled_date.isoformat() if memory.scheduled_date else None,
                'is_due_today': memory.is_due_today if memory.scheduled_date else False
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
                
                # Use AI to categorize the audio memory and extract dates
                from .voice_service import voice_service
                categorization = voice_service.categorize_audio_memory(text)
                
                # Extract date information
                from .date_recognition_service import date_recognition_service
                date_analysis = date_recognition_service.analyze_text_for_date_context(text)
                
                # Create the memory with AI categorization and date extraction
                memory = Memory.objects.create(
                    user=request.user,
                    content=text,
                    summary=categorization.get('summary', ''),
                    ai_reasoning=categorization.get('reasoning', ''),
                    tags=categorization.get('tags', []),
                    memory_type=categorization.get('category', 'general'),
                    importance=categorization.get('importance', 5),
                    scheduled_date=date_analysis.get('date')
                )
                
                # Create success message with date information
                success_msg = f"Voice memory created! Categorized as: {memory.get_memory_type_display()}"
                if memory.scheduled_date:
                    if memory.is_due_today:
                        success_msg += f' (Scheduled for today: {memory.scheduled_date.strftime("%B %d, %Y")})'
                    elif memory.is_overdue:
                        success_msg += f' (Overdue from: {memory.scheduled_date.strftime("%B %d, %Y")})'
                    else:
                        success_msg += f' (Scheduled for: {memory.scheduled_date.strftime("%B %d, %Y")})'
                
                return JsonResponse({
                    'success': True,
                    'content': text,
                    'memory_id': memory.id,
                    'category': categorization.get('category', 'general'),
                    'confidence': categorization.get('confidence', 50),
                    'summary': categorization.get('summary', ''),
                    'tags': categorization.get('tags', []),
                    'importance': categorization.get('importance', 5),
                    'scheduled_date': memory.scheduled_date.isoformat() if memory.scheduled_date else None,
                    'is_due_today': memory.is_due_today if memory.scheduled_date else False,
                    'message': success_msg
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
    """Search memories using voice input with improved natural language support"""
    if request.method == 'GET':
        # Handle GET request - show the search form
        context = {
            'ai_available': ChatGPTService().is_available(),
        }
        return render(request, 'memory_assistant/voice_search.html', context)
    
    elif request.method == 'POST':
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
            
            # Define query_words early so it's always available
            query_words = query.lower().split()
            
            # Search memories with more flexible matching
            memories = Memory.objects.filter(
                user=request.user,
                is_archived=False
            )
            
            print(f"DEBUG: Total memories for user: {memories.count()}")  # Debug log
            
            # Show all memories for debugging
            for memory in memories[:5]:
                print(f"DEBUG: Memory {memory.id}: {memory.content[:100]}...")
            
            # First, check if the query contains date information
            from .date_recognition_service import date_recognition_service
            date_analysis = date_recognition_service.analyze_text_for_date_context(query)
            extracted_date = date_analysis.get('date')
            
            if extracted_date:
                print(f"DEBUG: Date extracted from voice query '{query}': {extracted_date}")
                # Filter memories by the extracted date
                memories = memories.filter(scheduled_date=extracted_date)
                print(f"DEBUG: Memories after date filtering: {memories.count()}")
                
                # If no memories found for the specific date, try broader date-based search
                if not memories.exists():
                    # Look for memories that mention the date in content
                    date_str = extracted_date.strftime('%Y-%m-%d')
                    memories = memories.filter(
                        Q(content__icontains=date_str) |
                        Q(summary__icontains=date_str) |
                        Q(content__icontains=extracted_date.strftime('%B %d')) |  # "August 6"
                        Q(content__icontains=extracted_date.strftime('%b %d'))    # "Aug 6"
                    )
                    print(f"DEBUG: Memories after date content search: {memories.count()}")
            
            # If no date-specific results or no date found, proceed with regular search
            if not memories.exists():
                print(f"DEBUG: Query words: {query_words}")  # Debug log
                
                # Create a more flexible search - try multiple approaches
                search_conditions = Q()
                
                # First try: exact phrase match
                search_conditions |= Q(content__icontains=query)
                search_conditions |= Q(summary__icontains=query)
                search_conditions |= Q(ai_reasoning__icontains=query)
                
                # Second try: individual word matches (more lenient)
                for word in query_words:
                    if len(word) >= 1:  # Allow single character words
                        search_conditions |= Q(content__icontains=word)
                        search_conditions |= Q(summary__icontains=word)
                        search_conditions |= Q(ai_reasoning__icontains=word)
                        search_conditions |= Q(tags__contains=[word])
                
                # Third try: semantic variations for common terms
                semantic_variations = {
                    'plan': ['plan', 'plans', 'planning', 'schedule', 'scheduled', 'arrange', 'arrangement'],
                    'tomorrow': ['tomorrow', 'next day', 'day after', 'upcoming'],
                    'today': ['today', 'tonight', 'this evening', 'now'],
                    'meeting': ['meeting', 'appointment', 'call', 'conference', 'discussion'],
                    'buy': ['buy', 'purchase', 'shop', 'shopping', 'get', 'pick up'],
                    'call': ['call', 'phone', 'contact', 'dial', 'ring'],
                    'work': ['work', 'job', 'office', 'professional', 'business'],
                    'family': ['family', 'home', 'personal', 'kids', 'children'],
                    'learn': ['learn', 'learning', 'study', 'education', 'tutorial'],
                    'idea': ['idea', 'concept', 'thought', 'innovation', 'creative'],
                    'what': ['what', 'when', 'where', 'how', 'why'],
                    'the': ['the', 'a', 'an', 'this', 'that'],
                    'for': ['for', 'to', 'with', 'about', 'regarding']
                }
                
                # Add semantic variations for words in the query
                for word in query_words:
                    if word in semantic_variations:
                        for variation in semantic_variations[word]:
                            search_conditions |= Q(content__icontains=variation)
                            search_conditions |= Q(summary__icontains=variation)
                            search_conditions |= Q(tags__contains=[variation])
                            search_conditions |= Q(ai_reasoning__icontains=variation)
                
                memories = memories.filter(search_conditions)
            
            print(f"DEBUG: Memories after filtering: {memories.count()}")  # Debug log
            
            # Apply simplified contextual filtering to improve relevance
            if memories.count() > 0:
                filtered_memories = []
                query_lower = query.lower()
                
                # Define semantic variations for relevance scoring
                semantic_variations = {
                    'plan': ['plan', 'plans', 'planning', 'schedule', 'scheduled', 'arrange', 'arrangement'],
                    'tomorrow': ['tomorrow', 'next day', 'day after', 'upcoming'],
                    'today': ['today', 'tonight', 'this evening', 'now'],
                    'meeting': ['meeting', 'appointment', 'call', 'conference', 'discussion'],
                    'buy': ['buy', 'purchase', 'shop', 'shopping', 'get', 'pick up'],
                    'call': ['call', 'phone', 'contact', 'dial', 'ring'],
                    'work': ['work', 'job', 'office', 'professional', 'business'],
                    'family': ['family', 'home', 'personal', 'kids', 'children'],
                    'learn': ['learn', 'learning', 'study', 'education', 'tutorial'],
                    'idea': ['idea', 'concept', 'thought', 'innovation', 'creative'],
                    'what': ['what', 'when', 'where', 'how', 'why'],
                    'the': ['the', 'a', 'an', 'this', 'that'],
                    'for': ['for', 'to', 'with', 'about', 'regarding']
                }
                
                for memory in memories:
                    content_lower = memory.content.lower()
                    summary_lower = memory.summary.lower() if memory.summary else ""
                    reasoning_lower = memory.ai_reasoning.lower() if memory.ai_reasoning else ""
                    
                    # Calculate relevance score based on keyword matches
                    relevance_score = 0
                    
                    # Exact phrase match gets highest score
                    if query.lower() in content_lower or query.lower() in summary_lower:
                        relevance_score += 10
                    
                    # Individual word matches
                    for word in query_words:
                        if len(word) >= 2:  # Only count meaningful words
                            if word in content_lower:
                                relevance_score += 2
                            if word in summary_lower:
                                relevance_score += 1
                            if word in reasoning_lower:
                                relevance_score += 1
                    
                    # Semantic variations boost score
                    for word in query_words:
                        if word in semantic_variations:
                            for variation in semantic_variations[word]:
                                if variation in content_lower:
                                    relevance_score += 1
                                if variation in summary_lower:
                                    relevance_score += 0.5
                    
                    # Only include memories with some relevance
                    if relevance_score > 0:
                        memory.relevance_score = relevance_score
                        filtered_memories.append(memory)
                
                # Sort by relevance score
                filtered_memories.sort(key=lambda x: x.relevance_score, reverse=True)
                memories = filtered_memories[:20]  # Limit to top 20 results
            
            # If still no results, show recent memories as suggestions
            if not memories:
                memories = Memory.objects.filter(
                    user=request.user,
                    is_archived=False
                ).order_by('-created_at')[:5]
            
            # Check if this is an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Prepare results for JSON response
                results = []
                for memory in memories:
                    result = {
                        'id': memory.id,
                        'content': memory.content,
                        'summary': memory.summary or '',
                        'memory_type': memory.memory_type,
                        'importance': memory.importance,
                        'created_at': memory.created_at.strftime('%B %d, %Y'),
                        'scheduled_date': memory.scheduled_date.strftime('%B %d, %Y') if memory.scheduled_date else None,
                        'tags': memory.tags or [],
                        'ai_reasoning': memory.ai_reasoning or '',
                        'relevance_score': getattr(memory, 'relevance_score', 0)
                    }
                    results.append(result)
                
                return JsonResponse({
                    'success': True,
                    'results': results,
                    'query': query,
                    'results_count': len(results),
                    'extracted_date': extracted_date.isoformat() if extracted_date else None
                })
            else:
                # Regular form submission - render the page with results
                context = {
                    'query': query,
                    'results': memories,
                    'results_count': len(memories),
                    'extracted_date': extracted_date,
                    'ai_available': ChatGPTService().is_available(),
                }
                return render(request, 'memory_assistant/voice_search.html', context)
            
        except Exception as e:
            print(f"Error in voice search: {e}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
            else:
                context = {
                    'error': str(e),
                    'ai_available': ChatGPTService().is_available(),
                }
                return render(request, 'memory_assistant/voice_search.html', context)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


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