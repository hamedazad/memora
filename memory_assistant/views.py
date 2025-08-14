from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime, timedelta
import json
import os
import re
from .models import Memory, MemorySearch, UserProfile
from .forms import MemoryForm, QuickMemoryForm, SearchForm, UserRegistrationForm
from .services import ChatGPTService
from .voice_service import voice_service
from .recommendation_service import AIRecommendationService
from .smart_reminder_service import SmartReminderService


def home(request):
    """Landing page for non-authenticated users"""
    if request.user.is_authenticated:
        return redirect('memory_assistant:dashboard')
    return render(request, 'memory_assistant/home.html')


@login_required
def dashboard(request):
    """Main dashboard view"""
    # Get user's own memories
    memories = Memory.objects.filter(user=request.user, is_archived=False)
    
    # Get shared memories for dashboard
    from .models import SharedMemory
    shared_memory_objects = SharedMemory.objects.filter(
        Q(shared_with_user=request.user) | 
        Q(shared_with_organization__in=request.user.organization_memberships.filter(is_active=True).values_list('organization', flat=True)),
        is_active=True
    ).select_related('memory').values_list('memory', flat=True)
    
    # Combine own and shared memories for recent list using Q objects
    all_memories = Memory.objects.filter(
        Q(user=request.user) | Q(id__in=shared_memory_objects),
        is_archived=False
    ).order_by('-created_at')
    recent_memories = all_memories[:5]
    
    # Create shared memory info for dashboard
    shared_memory_info = {}
    for shared in SharedMemory.objects.filter(
        Q(shared_with_user=request.user) | 
        Q(shared_with_organization__in=request.user.organization_memberships.filter(is_active=True).values_list('organization', flat=True)),
        is_active=True
    ).select_related('memory', 'shared_by'):
        shared_memory_info[shared.memory.id] = {
            'shared_by': shared.shared_by,
            'share_type': shared.share_type,
            'organization': shared.shared_with_organization if shared.share_type == 'organization' else None
        }
    
    # Get memory statistics
    total_memories = memories.count()
    important_memories = memories.filter(importance__gte=8).count()
    
    # Only count future scheduled memories
    from django.utils import timezone
    now = timezone.now()
    scheduled_memories_count = memories.filter(delivery_date__gt=now).count()
    todays_memories_count = memories.filter(delivery_date__date=datetime.now().date()).count()

    
    # Get memory suggestions
    chatgpt_service = ChatGPTService()
    recent_memory_data = [
        {
            'content': memory.content,
            'tags': memory.tags
        } for memory in recent_memories
    ]
    suggestions = chatgpt_service.generate_memory_suggestions(recent_memory_data)
    
    # Check for triggered reminders
    reminder_service = SmartReminderService()
    triggered_reminders = reminder_service.check_and_trigger_reminders(request.user)
    
    # Format triggered reminders for display
    reminder_notifications = []
    for item in triggered_reminders:
        reminder = item['reminder']
        trigger = item['trigger']
        reminder_notifications.append({
            'id': reminder.id,
            'memory_id': reminder.memory.id,
            'title': f"Reminder: {reminder.memory.content[:50]}...",
            'message': trigger.trigger_reason,
            'memory_content': reminder.memory.content,
            'triggered_at': trigger.triggered_at,
            'priority': reminder.priority
        })
    
    context = {
        'recent_memories': recent_memories,
        'total_memories': total_memories,
        'important_memories': important_memories,
        'shared_memory_info': shared_memory_info,
        'scheduled_memories_count': scheduled_memories_count,
        'todays_memories_count': todays_memories_count,
        'suggestions': suggestions,
        'ai_available': chatgpt_service.is_available(),
        'reminder_notifications': reminder_notifications,
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
    # Get both own and shared memories in a single query
    from .models import SharedMemory
    shared_memory_objects = SharedMemory.objects.filter(
        Q(shared_with_user=request.user) | 
        Q(shared_with_organization__in=request.user.organization_memberships.filter(is_active=True).values_list('organization', flat=True)),
        is_active=True
    ).select_related('memory').values_list('memory', flat=True)
    
    # Combine own and shared memories using Q objects
    memories = Memory.objects.filter(
        Q(user=request.user) | Q(id__in=shared_memory_objects),
        is_archived=False
    )
    
    # Get filter parameters
    memory_type = request.GET.get('type')
    importance = request.GET.get('importance')
    search_query = request.GET.get('q', '').strip()
    date_filter = request.GET.get('date_filter', '').strip()
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
    
    # Apply date filter
    if date_filter:
        try:
            from datetime import datetime
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            # Filter memories created on the specified date
            memories = memories.filter(created_at__date=filter_date)
        except ValueError:
            pass  # Ignore invalid date values
    
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
    
    # Add prefetching for comments and likes
    memories = memories.prefetch_related('comments__user__profile', 'likes__user')
    
    # Pagination
    paginator = Paginator(memories, 12)  # Show more items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get statistics for the current filter
    total_memories = Memory.objects.filter(user=request.user, is_archived=False).count()
    filtered_count = memories.count()
    
    # Create shared memory info for template
    shared_memory_info = {}
    for shared in SharedMemory.objects.filter(
        Q(shared_with_user=request.user) | 
        Q(shared_with_organization__in=request.user.organization_memberships.filter(is_active=True).values_list('organization', flat=True)),
        is_active=True
    ).select_related('memory', 'shared_by'):
        shared_memory_info[shared.memory.id] = {
            'shared_by': shared.shared_by,
            'share_type': shared.share_type,
            'message': shared.message,
            'created_at': shared.created_at,
            'organization': shared.shared_with_organization if shared.share_type == 'organization' else None
        }
    
    context = {
        'page_obj': page_obj,
        'memory_types': Memory.memory_type.field.choices,
        'search_query': search_query,
        'selected_date': date_filter,
        'selected_type': memory_type,
        'selected_importance': importance,
        'selected_sort': sort_by,
        'total_memories': total_memories,
        'filtered_count': filtered_count,
        'has_filters': bool(search_query or date_filter or memory_type or importance),
        'shared_memory_info': shared_memory_info,
        'now': timezone.now(),
    }
    
    return render(request, 'memory_assistant/memory_list.html', context)


@login_required
def create_memory(request):
    """Create a new memory with date parsing"""
    if request.method == 'POST':
        form = MemoryForm(request.POST, request.FILES)
        if form.is_valid():
            memory = form.save(commit=False)
            memory.user = request.user
            
            # Process with ChatGPT for auto-categorization and date parsing
            chatgpt_service = ChatGPTService()
            processed_data = chatgpt_service.process_memory(memory.content)
            
            # Apply AI-generated categorization
            memory.summary = processed_data.get('summary', '')
            memory.ai_reasoning = processed_data.get('reasoning', '')
            memory.tags = processed_data.get('tags', [])
            memory.memory_type = processed_data.get('memory_type', 'general')
            memory.importance = processed_data.get('importance', 5)
            
            # Apply date parsing results
            delivery_date = processed_data.get('delivery_date')
            if delivery_date and delivery_date != "None" and delivery_date is not None:
                # Handle both string and datetime objects
                if isinstance(delivery_date, str):
                    try:
                        from datetime import datetime
                        memory.delivery_date = datetime.fromisoformat(delivery_date.replace('Z', '+00:00'))
                    except (ValueError, TypeError):
                        # If parsing fails, don't set delivery_date
                        pass
                else:
                    memory.delivery_date = delivery_date
                memory.delivery_type = processed_data.get('delivery_type', 'scheduled')
            

            
            memory.save()
            
            # Auto-create smart reminders based on memory content
            try:
                reminder_service = SmartReminderService()
                suggestions = reminder_service.analyze_memory_for_reminders(memory)
                
                # Create smart reminders for time-based suggestions
                reminders_created = 0
                for suggestion in suggestions:
                    if suggestion['type'] == 'time_based':
                        reminder = reminder_service.create_smart_reminder(memory, request.user, suggestion)
                        if reminder:  # Only count if reminder was actually created
                            reminders_created += 1
                
                # Add reminder info to success message if reminders were created
                if reminders_created > 0:
                    success_msg = f'Memory created successfully! Categorized as: {memory.get_memory_type_display()} | {reminders_created} smart reminder{"s" if reminders_created != 1 else ""} created'
                else:
                    success_msg = f'Memory created successfully! Categorized as: {memory.get_memory_type_display()}'
            except Exception as e:
                # If smart reminder creation fails, don't break the memory creation
                success_msg = f'Memory created successfully! Categorized as: {memory.get_memory_type_display()}'
            
            # Auto-share with friends if privacy level is set to friends
            if memory.privacy_level == 'friends':
                from .models import Friendship, SharedMemory, Notification
                friends = Friendship.get_user_friends(request.user)
                for friend in friends:
                    shared_memory = SharedMemory.objects.create(
                        memory=memory,
                        shared_by=request.user,
                        shared_with_user=friend,
                        share_type='user',
                        message=f"Shared a new {memory.get_memory_type_display().lower()} memory",
                        can_reshare=True
                    )
                    # Create notification
                    Notification.objects.create(
                        recipient=friend,
                        sender=request.user,
                        notification_type='memory_shared',
                        title='New Memory Shared',
                        message=f'{request.user.username} shared a {memory.get_memory_type_display().lower()} memory with you',
                        action_url=f'/memora/memories/{memory.id}/',
                        related_object_id=memory.id,
                        related_object_type='memory'
                    )
            
            # Auto-share with organization members if privacy level is organization
            elif memory.privacy_level == 'organization':
                from .models import OrganizationMembership, SharedMemory, Notification
                user_orgs = request.user.organization_memberships.filter(is_active=True)
                for membership in user_orgs:
                    shared_memory = SharedMemory.objects.create(
                        memory=memory,
                        shared_by=request.user,
                        shared_with_organization=membership.organization,
                        share_type='organization',
                        message=f"Shared a new {memory.get_memory_type_display().lower()} memory with {membership.organization.name}",
                        can_reshare=True
                    )
                    # Create notifications for all organization members
                    org_members = User.objects.filter(
                        organization_memberships__organization=membership.organization,
                        organization_memberships__is_active=True
                    ).exclude(id=request.user.id)
                    for member in org_members:
                        Notification.objects.create(
                            recipient=member,
                            sender=request.user,
                            notification_type='memory_shared',
                            title='New Memory Shared',
                            message=f'{request.user.username} shared a {memory.get_memory_type_display().lower()} memory with {membership.organization.name}',
                            action_url=f'/memora/memories/{memory.id}/',
                            related_object_id=memory.id,
                            related_object_type='memory'
                        )
            
            # Add date info to success message if delivery date exists
            if memory.delivery_date:
                success_msg += f' | Scheduled for: {memory.delivery_date.strftime("%B %d, %Y at %I:%M %p")}'
            
            # Add sharing info to success message
            if memory.privacy_level == 'friends':
                friends_count = len(Friendship.get_user_friends(request.user))
                if friends_count > 0:
                    success_msg += f' | Shared with {friends_count} friend{"s" if friends_count != 1 else ""}'
            elif memory.privacy_level == 'organization':
                orgs_count = request.user.organization_memberships.filter(is_active=True).count()
                if orgs_count > 0:
                    success_msg += f' | Shared with {orgs_count} organization{"s" if orgs_count != 1 else ""}'
            

            
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
    memory = get_object_or_404(
        Memory.objects.prefetch_related(
            'comments__user__profile',
            'likes__user',
            'user__profile'
        ), 
        id=memory_id
    )
    
    # Check if user can view this memory based on privacy settings
    if not memory.can_be_viewed_by(request.user):
        return render(request, 'memory_assistant/memory_not_accessible.html', {
            'memory_id': memory_id,
            'reason': 'privacy'
        }, status=403)
    
    # Get smart reminders for this memory
    smart_reminders = memory.smart_reminders.filter(is_active=True).order_by('-created_at')
    
    context = {
        'memory': memory,
        'smart_reminders': smart_reminders,
        'now': timezone.now(),
    }
    
    return render(request, 'memory_assistant/memory_detail.html', context)


@login_required
def edit_memory(request, memory_id):
    """Edit a memory"""
    memory = get_object_or_404(Memory, id=memory_id, user=request.user)
    
    if request.method == 'POST':
        form = MemoryForm(request.POST, request.FILES, instance=memory)
        if form.is_valid():
            # Handle image removal
            if request.POST.get('clear-image'):
                if memory.image:
                    # Delete the old image file
                    if os.path.isfile(memory.image.path):
                        os.remove(memory.image.path)
                    memory.image = None
            
            # Get the old privacy level before saving changes
            old_privacy_level = Memory.objects.get(id=memory.id).privacy_level
            
            memory = form.save(commit=False)
            
            # Reprocess with ChatGPT if content changed to update AI-generated fields
            # but preserve user's manual selections for memory_type and importance
            chatgpt_service = ChatGPTService()
            processed_data = chatgpt_service.process_memory(memory.content)
            
            # Only update AI-generated fields, preserve user's manual selections
            memory.summary = processed_data.get('summary', '')
            memory.tags = processed_data.get('tags', [])
            memory.ai_reasoning = processed_data.get('reasoning', '')
            
            # Don't override user's manual selections for memory_type and importance
            # These are handled by the form and should be preserved
            
            memory.save()
            
            # Handle privacy level changes for sharing
            if old_privacy_level != memory.privacy_level:
                from .models import SharedMemory
                # Remove old shares if privacy changed
                SharedMemory.objects.filter(memory=memory).delete()
                
                # Create new shares based on new privacy level
                if memory.privacy_level == 'friends':
                    from .models import Friendship
                    friends = Friendship.get_user_friends(request.user)
                    for friend in friends:
                        SharedMemory.objects.create(
                            memory=memory,
                            shared_by=request.user,
                            shared_with_user=friend,
                            share_type='user',
                            message=f"Updated privacy settings - now shared with friends",
                            can_reshare=True
                        )
                elif memory.privacy_level == 'organization':
                    from .models import OrganizationMembership
                    user_orgs = request.user.organization_memberships.filter(is_active=True)
                    for membership in user_orgs:
                        SharedMemory.objects.create(
                            memory=memory,
                            shared_by=request.user,
                            shared_with_organization=membership.organization,
                            share_type='organization',
                            message=f"Updated privacy settings - now shared with {membership.organization.name}",
                            can_reshare=True
                        )
            
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
    """Delete a memory - only the owner can delete"""
    memory = get_object_or_404(Memory, id=memory_id)
    
    # Only the owner of the memory can delete it
    if memory.user != request.user:
        messages.error(request, 'You can only delete your own memories.')
        return redirect('memory_assistant:memory_detail', memory_id=memory_id)
    
    if request.method == 'POST':
        memory.delete()
        messages.success(request, 'Memory deleted successfully!')
        return redirect('memory_assistant:memory_list')
    
    context = {
        'memory': memory,
    }
    
    return render(request, 'memory_assistant/delete_memory.html', context)


@login_required
@csrf_exempt
def mark_memory_done(request, memory_id):
    """Mark a scheduled memory as completed"""
    if request.method == 'POST':
        try:
            memory = get_object_or_404(Memory, id=memory_id, user=request.user)
            
            # Only allow marking scheduled memories as done
            if memory.delivery_date and memory.delivery_date > timezone.now():
                memory.is_completed = True
                memory.completed_at = timezone.now()
                memory.is_delivered = True  # Mark as delivered since it's done
                memory.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Memory marked as completed!'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Only scheduled memories can be marked as done.'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


@login_required
@csrf_exempt
def snooze_memory(request, memory_id):
    """Snooze a scheduled memory"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            snooze_option = data.get('snooze_option')
            custom_date = data.get('custom_date')
            
            memory = get_object_or_404(Memory, id=memory_id, user=request.user)
            
            # Only allow snoozing scheduled memories
            if not (memory.delivery_date and memory.delivery_date > timezone.now()):
                return JsonResponse({
                    'success': False,
                    'error': 'Only scheduled memories can be snoozed.'
                })
            
            # Calculate new delivery date based on snooze option
            now = timezone.now()
            if snooze_option == '1_hour':
                new_date = now + timedelta(hours=1)
            elif snooze_option == '3_hours':
                new_date = now + timedelta(hours=3)
            elif snooze_option == 'tomorrow_morning':
                new_date = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
            elif snooze_option == 'next_week':
                new_date = now + timedelta(weeks=1)
            elif snooze_option == 'custom' and custom_date:
                try:
                    new_date = timezone.make_aware(datetime.fromisoformat(custom_date.replace('Z', '+00:00')))
                except:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid custom date format.'
                    })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid snooze option.'
                })
            
            # Update memory
            memory.delivery_date = new_date
            memory.snooze_count += 1
            memory.last_snoozed_at = now
            memory.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Memory snoozed until {new_date.strftime("%B %d, %Y at %I:%M %p")}',
                'new_date': new_date.isoformat()
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
@csrf_exempt
def decline_memory(request, memory_id):
    """Decline a scheduled memory"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            decline_reason = data.get('decline_reason', '')
            
            memory = get_object_or_404(Memory, id=memory_id, user=request.user)
            
            # Only allow declining scheduled memories
            if not (memory.delivery_date and memory.delivery_date > timezone.now()):
                return JsonResponse({
                    'success': False,
                    'error': 'Only scheduled memories can be declined.'
                })
            
            # Update memory
            memory.declined_at = timezone.now()
            memory.decline_reason = decline_reason
            memory.is_delivered = True  # Mark as delivered since it's handled
            memory.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Memory declined successfully!'
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
def search_memories(request):
    """Enhanced search memories with AI-powered semantic search"""
    query = request.GET.get('q', '').strip()
    date_filter = request.GET.get('date_filter', '').strip()
    memories = []
    search_method = "basic"
    
    # Get all memories for the user
    all_memories = Memory.objects.filter(
        user=request.user,
        is_archived=False
    )
    
    # Apply date filter if specified (works independently of search query)
    if date_filter:
        try:
            from datetime import datetime
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            # Filter memories created on the specified date
            all_memories = all_memories.filter(created_at__date=filter_date)
        except ValueError:
            pass  # Ignore invalid date values
    
    # If only date filter is provided (no search query), return all memories for that date
    if not query and date_filter:
        memories = all_memories
        search_method = "date_filter_only"
    
    # If search query is provided
    elif query:
        
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
                        'memory_type': memory.memory_type,
                        'delivery_date': memory.delivery_date.isoformat() if memory.delivery_date else None
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
            
            # Check for date-specific queries first
            query_lower = query.lower()
            date_keywords = {
                'today': 'today',
                'tonight': 'today',
                'tomorrow': 'tomorrow', 
                'yesterday': 'yesterday',
                'this week': 'this week',
                'next week': 'next week',
                'this month': 'this month',
                'next month': 'next month'
            }
            
            # Check if query contains date references
            detected_date = None
            for keyword, date_type in date_keywords.items():
                if keyword in query_lower:
                    detected_date = date_type
                    break
            
            # If date detected, add delivery date filtering
            if detected_date:
                today = datetime.now().date()
                if detected_date == 'today':
                    search_conditions |= Q(delivery_date__date=today)
                elif detected_date == 'tomorrow':
                    search_conditions |= Q(delivery_date__date=today + timedelta(days=1))
                elif detected_date == 'yesterday':
                    search_conditions |= Q(delivery_date__date=today - timedelta(days=1))
                elif detected_date == 'this week':
                    # Find memories scheduled for this week (next 7 days)
                    end_of_week = today + timedelta(days=7)
                    search_conditions |= Q(delivery_date__date__gte=today, delivery_date__date__lte=end_of_week)
                elif detected_date == 'next week':
                    # Find memories scheduled for next week (7-14 days from now)
                    start_of_next_week = today + timedelta(days=7)
                    end_of_next_week = today + timedelta(days=14)
                    search_conditions |= Q(delivery_date__date__gte=start_of_next_week, delivery_date__date__lte=end_of_next_week)
            
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
        
        # If no results found, use contextual AI suggestions
        if not memories:
            # Get user's memories for context
            user_memories = all_memories.order_by('-created_at')[:10]
            
            memory_data = [
                {
                    'content': memory.content,
                    'tags': memory.tags or [],
                    'delivery_date': memory.delivery_date.isoformat() if memory.delivery_date else None
                } for memory in user_memories
            ]
            
            # Use contextual suggestions
            chatgpt_service = ChatGPTService()
            contextual_suggestions = chatgpt_service.generate_contextual_suggestions(query, memory_data)
            
            if contextual_suggestions:
                # Store contextual suggestions in context
                context = {
                    'search_results': [],
                    'results_count': 0,
                    'query': query,
                    'date_filter': date_filter,
                    'search_method': "contextual_suggestions",
                    'ai_available': chatgpt_service.is_available(),
                    'contextual_suggestions': contextual_suggestions,
                    'message': f'No memories found for "{query}". Here are some suggestions:'
                }
            else:
                # Fall back to recent memories
                memories = user_memories[:5]
                search_method = "suggestions"
                context = {
                    'search_results': memories,
                    'results_count': len(memories),
                    'query': query,
                    'date_filter': date_filter,
                    'search_method': search_method,
                    'ai_available': chatgpt_service.is_available(),
                    'message': f'No memories found for "{query}". Here are your recent memories:'
                }
            
            return render(request, 'memory_assistant/search_results.html', context)
    
    context = {
        'search_results': memories,
        'results_count': len(memories),
        'query': query,
        'date_filter': date_filter,
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
            
            # Handle delivery_date properly
            delivery_date = processed_data.get('delivery_date')
            if delivery_date and delivery_date != "None" and delivery_date is not None:
                if isinstance(delivery_date, str):
                    try:
                        from datetime import datetime
                        delivery_date = datetime.fromisoformat(delivery_date.replace('Z', '+00:00'))
                    except (ValueError, TypeError):
                        delivery_date = None
            else:
                delivery_date = None
            
            # Create memory with AI categorization and date parsing
            memory = Memory.objects.create(
                user=request.user,
                content=content,
                memory_type=processed_data.get('memory_type', 'general'),
                importance=processed_data.get('importance', 5),
                # Only keep summary if it's Work and long content (service already enforces this)
                summary=processed_data.get('summary', ''),
                ai_reasoning=processed_data.get('reasoning', ''),
                tags=processed_data.get('tags', []),
                delivery_date=delivery_date,
                delivery_type=processed_data.get('delivery_type', 'immediate')
            )
            
            # Auto-create smart reminders based on memory content
            reminder_count = 0
            try:
                reminder_service = SmartReminderService()
                suggestions = reminder_service.analyze_memory_for_reminders(memory)
                
                # Create smart reminders for time-based suggestions
                for suggestion in suggestions:
                    if suggestion['type'] == 'time_based':
                        reminder = reminder_service.create_smart_reminder(memory, request.user, suggestion)
                        if reminder:  # Only count if reminder was actually created
                            reminder_count += 1
            except Exception as e:
                # If smart reminder creation fails, don't break the memory creation
                pass
            
            # Create success message with date info
            success_msg = f'Memory added successfully! Categorized as: {memory.get_memory_type_display()}'
            if memory.delivery_date:
                success_msg += f' | Scheduled for: {memory.delivery_date.strftime("%B %d, %Y at %I:%M %p")}'
            if reminder_count > 0:
                success_msg += f' | {reminder_count} smart reminder{"s" if reminder_count != 1 else ""} created'
            
            return JsonResponse({
                'success': True,
                'memory_id': memory.id,
                'message': success_msg,
                'category': memory.memory_type,
                'importance': memory.importance,
                'scheduled_date': memory.delivery_date.isoformat() if memory.delivery_date else None
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
                
                # Auto-create smart reminders based on memory content
                reminder_count = 0
                try:
                    reminder_service = SmartReminderService()
                    suggestions = reminder_service.analyze_memory_for_reminders(memory)
                    
                    # Create smart reminders for time-based suggestions
                    for suggestion in suggestions:
                        if suggestion['type'] == 'time_based':
                            reminder = reminder_service.create_smart_reminder(memory, request.user, suggestion)
                            if reminder:  # Only count if reminder was actually created
                                reminder_count += 1
                except Exception as e:
                    # If smart reminder creation fails, don't break the memory creation
                    pass
                
                return JsonResponse({
                    'success': True,
                    'content': text,
                    'memory_id': memory.id,
                    'category': categorization.get('category', 'general'),
                    'confidence': categorization.get('confidence', 50),
                    'summary': categorization.get('summary', ''),
                    'tags': categorization.get('tags', []),
                    'importance': categorization.get('importance', 5),
                    'reminders_created': reminder_count
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
            
            # Search memories with more flexible matching - include both own and shared memories
            from .models import SharedMemory
            
            # Get shared memory IDs first
            shared_memory_objects = SharedMemory.objects.filter(
                Q(shared_with_user=request.user) | 
                Q(shared_with_organization__memberships__user=request.user, shared_with_organization__memberships__is_active=True)
            ).select_related('memory').values_list('memory', flat=True)
            
            # Create a single query that includes both own and shared memories
            memories = Memory.objects.filter(
                Q(user=request.user) | Q(id__in=shared_memory_objects),
                is_archived=False
            ).order_by('-created_at')
            
            print(f"DEBUG: Total memories for user: {memories.count()}")  # Debug log
            
            # Show all memories for debugging
            for memory in memories[:5]:
                print(f"DEBUG: Memory {memory.id}: {memory.content[:100]}...")
            
            # Split query into words for better matching
            query_words = query.lower().split()
            print(f"DEBUG: Query words: {query_words}")  # Debug log
            
            # Create a more flexible search - try multiple approaches
            search_conditions = Q()
            
            # CHECK FOR DATE FILTERING FIRST (like regular search function)
            query_lower = query.lower()
            date_patterns = {
                r'\b(today|tonight)\b': 'today',
                r'\b(tomorrow)\b': 'tomorrow',
                r'\b(yesterday)\b': 'yesterday',
                r'\b(this week)\b': 'this_week',
                r'\b(next week)\b': 'next_week'
            }
            
            # Special handling for "plan for today" queries
            if 'plan' in query_lower and 'today' in query_lower:
                print(f"DEBUG: Detected 'plan for today' query")
                # First, try to find memories scheduled for today
                today = datetime.now().date()
                today_scheduled = memories.filter(delivery_date__date=today)
                print(f"DEBUG: Found {today_scheduled.count()} memories scheduled for today")
                
                if today_scheduled.count() > 0:
                    # Return today's scheduled memories as the primary results
                    results = []
                    for memory in today_scheduled.order_by('delivery_date'):
                        results.append({
                            'id': memory.id,
                            'content': memory.content[:100] + '...' if len(memory.content) > 100 else memory.content,
                            'summary': memory.summary,
                            'created_at': memory.created_at.strftime('%Y-%m-%d %H:%M'),
                            'recency': 'Today',
                            'scheduled_time': memory.delivery_date.strftime('%I:%M %p') if memory.delivery_date else None
                        })
                    
                    return JsonResponse({
                        'success': True,
                        'query': query,
                        'results': results,
                        'message': f'Here are your plans for today ({today.strftime("%B %d, %Y")}):'
                    })
                else:
                    # No scheduled memories for today, but user asked for plans
                    # Look for recent memories that might be plans or tasks
                    recent_plan_memories = memories.filter(
                        Q(content__icontains='plan') | 
                        Q(content__icontains='task') | 
                        Q(content__icontains='todo') | 
                        Q(content__icontains='meeting') | 
                        Q(content__icontains='appointment') |
                        Q(memory_type='reminder')
                    ).order_by('-created_at')[:5]
                    
                    if recent_plan_memories.count() > 0:
                        results = []
                        for memory in recent_plan_memories:
                            results.append({
                                'id': memory.id,
                                'content': memory.content[:100] + '...' if len(memory.content) > 100 else memory.content,
                                'summary': memory.summary,
                                'created_at': memory.created_at.strftime('%Y-%m-%d %H:%M'),
                                'recency': 'Recent',
                                'note': 'No specific plans scheduled for today, but here are recent planning-related memories:'
                            })
                        
                        return JsonResponse({
                            'success': True,
                            'query': query,
                            'results': results,
                            'message': f'No specific plans scheduled for today ({today.strftime("%B %d, %Y")}). Here are recent planning-related memories:'
                        })
                    else:
                        return JsonResponse({
                            'success': True,
                            'query': query,
                            'results': [],
                            'message': f'No plans found for today ({today.strftime("%B %d, %Y")}). You can create new memories and schedule them for today!'
                        })
            
            detected_date = None
            for pattern, date_type in date_patterns.items():
                if re.search(pattern, query_lower):
                    detected_date = date_type
                    print(f"DEBUG: Detected date reference: {detected_date}")
                    break
            
            # If date detected, prioritize DATE FILTERING with content search
            if detected_date:
                today = datetime.now().date()
                date_filter = Q()
                
                if detected_date == 'today':
                    date_filter = Q(delivery_date__date=today)
                    print(f"DEBUG: Added today filter for date: {today}")
                elif detected_date == 'tomorrow':
                    date_filter = Q(delivery_date__date=today + timedelta(days=1))
                elif detected_date == 'yesterday':
                    date_filter = Q(delivery_date__date=today - timedelta(days=1))
                elif detected_date == 'this_week':
                    # Find memories scheduled for this week (next 7 days)
                    end_of_week = today + timedelta(days=7)
                    date_filter = Q(delivery_date__date__gte=today, delivery_date__date__lte=end_of_week)
                elif detected_date == 'next_week':
                    # Find memories scheduled for next week (7-14 days from now)
                    start_of_next_week = today + timedelta(days=7)
                    end_of_next_week = today + timedelta(days=14)
                    date_filter = Q(delivery_date__date__gte=start_of_next_week, delivery_date__date__lte=end_of_next_week)
                
                # Create content search conditions
                content_search = Q()
                content_search |= Q(content__icontains=query)
                content_search |= Q(summary__icontains=query)
                content_search |= Q(tags__contains=[query])
                content_search |= Q(ai_reasoning__icontains=query)
                
                # Filter out common stop words that shouldn't be searched individually
                stop_words = {
                    'what', 'should', 'i', 'you', 'we', 'they', 'he', 'she', 'it', 'the', 'a', 'an', 
                    'and', 'or', 'but', 'to', 'for', 'of', 'in', 'on', 'at', 'by', 'with', 'from',
                    'say', 'tell', 'ask', 'do', 'be', 'is', 'are', 'was', 'were', 'have', 'has', 'had',
                    'will', 'would', 'could', 'should', 'may', 'might', 'can', 'about', 'how', 'when',
                    'where', 'why', 'who', 'that', 'this', 'these', 'those', 'my', 'your', 'his', 'her',
                    'today', 'tomorrow', 'yesterday'  # Include date words
                }
                
                # Individual meaningful word matches
                meaningful_words = []
                for word in query_words:
                    word_clean = word.lower().strip('.,!?;:"()[]{}')
                    if len(word_clean) >= 3 and word_clean not in stop_words:
                        meaningful_words.append(word_clean)
                
                print(f"DEBUG: Meaningful words for date search: {meaningful_words}")
                
                # Only search for meaningful words
                for word in meaningful_words:
                    content_search |= Q(content__icontains=word)
                    content_search |= Q(summary__icontains=word)
                    content_search |= Q(tags__contains=[word])
                
                # Combine date filter AND content search (both must be true)
                search_conditions = date_filter & content_search
                print(f"DEBUG: Using date-filtered search for {detected_date}")
                
            else:
                # No date detected, use regular content search
                search_conditions |= Q(content__icontains=query)
                search_conditions |= Q(summary__icontains=query)
                search_conditions |= Q(tags__contains=[query])
                search_conditions |= Q(ai_reasoning__icontains=query)
                
                # Filter out common stop words that shouldn't be searched individually
                stop_words = {
                    'what', 'should', 'i', 'you', 'we', 'they', 'he', 'she', 'it', 'the', 'a', 'an', 
                    'and', 'or', 'but', 'to', 'for', 'of', 'in', 'on', 'at', 'by', 'with', 'from',
                    'say', 'tell', 'ask', 'do', 'be', 'is', 'are', 'was', 'were', 'have', 'has', 'had',
                    'will', 'would', 'could', 'should', 'may', 'might', 'can', 'about', 'how', 'when',
                    'where', 'why', 'who', 'that', 'this', 'these', 'those', 'my', 'your', 'his', 'her'
                }
                
                # Individual word matches (more targeted)
                meaningful_words = []
                for word in query_words:
                    word_clean = word.lower().strip('.,!?;:"()[]{}')
                    if len(word_clean) >= 3 and word_clean not in stop_words:
                        meaningful_words.append(word_clean)
                
                print(f"DEBUG: Meaningful words for search: {meaningful_words}")
                
                # Only search for meaningful words
                for word in meaningful_words:
                    search_conditions |= Q(content__icontains=word)
                    search_conditions |= Q(summary__icontains=word)
                    search_conditions |= Q(tags__contains=[word])
                
                # Partial matches for common meaningful words
                common_words = ['plan', 'meeting', 'work', 'home', 'buy', 'need', 'project', 'task']
                for word in common_words:
                    if word in query.lower():
                        search_conditions |= Q(content__icontains=word)
                        search_conditions |= Q(summary__icontains=word)
            
            memories = memories.filter(search_conditions)
            
            print(f"DEBUG: Memories after filtering: {memories.count()}")  # Debug log
            
            # If no memories found with date filter and it was a date-specific query, provide clear feedback
            if detected_date and memories.count() == 0:
                print(f"DEBUG: No memories found for {detected_date} with content matching query")
                # Check if there are any memories scheduled for that date (without content filter)
                # Include both own and shared memories
                date_only_memories = Memory.objects.filter(
                    Q(user=request.user) | Q(id__in=shared_memory_objects),
                    is_archived=False
                )
                if detected_date == 'today':
                    date_only_memories = date_only_memories.filter(delivery_date__date=datetime.now().date())
                
                print(f"DEBUG: Total memories scheduled for {detected_date}: {date_only_memories.count()}")
                
                if date_only_memories.count() > 0:
                    # There are memories for today, but none match the content search
                    # Show the actual memories scheduled for today as suggestions
                    suggestions = []
                    for memory in date_only_memories[:5]:  # Show up to 5 memories
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
                        'message': f'No memories found matching "{query}" for {detected_date}. You have {date_only_memories.count()} other memories scheduled for {detected_date}.',
                        'suggestions': suggestions
                    })
                else:
                    # No memories at all for today
                    return JsonResponse({
                        'success': True,
                        'query': query,
                        'results': [],
                        'message': f'No memories scheduled for {detected_date}.',
                        'suggestions': []
                    })
            
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
                    
                    # For "plan" related queries, be more flexible - include memories that might be plans even without explicit plan words
                    elif 'plan' in query_lower:
                        plan_indicators = ['plan', 'schedule', 'arrange', 'organize', 'prepare', 'meeting', 'appointment', 'task', 'todo', 'reminder']
                        # Also include memories that are scheduled for today/tomorrow as they might be plans
                        if not any(indicator in content_lower for indicator in plan_indicators):
                            # Check if this memory is scheduled for today/tomorrow (which could be a plan)
                            if memory.delivery_date:
                                today = datetime.now().date()
                                tomorrow = today + timedelta(days=1)
                                if memory.delivery_date.date() in [today, tomorrow]:
                                    is_relevant = True
                                else:
                                    is_relevant = False
                            else:
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
            
            # If still no results, use contextual AI suggestions
            if len(memories) == 0:
                print("DEBUG: No memories found, using contextual AI suggestions")
                
                # Get user's memories for context (including shared ones)
                user_memories = Memory.objects.filter(
                    Q(user=request.user) | Q(id__in=shared_memory_objects),
                    is_archived=False
                ).order_by('-created_at')[:10]
                
                memory_data = [
                    {
                        'content': memory.content,
                        'tags': memory.tags or [],
                        'delivery_date': memory.delivery_date.isoformat() if memory.delivery_date else None
                    } for memory in user_memories
                ]
                
                # Use contextual suggestions
                chatgpt_service = ChatGPTService()
                contextual_suggestions = chatgpt_service.generate_contextual_suggestions(query, memory_data)
                
                # If no contextual suggestions, fall back to recent memories
                if not contextual_suggestions:
                    recent_memories = user_memories[:5]
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
                else:
                    # Return contextual suggestions
                    return JsonResponse({
                        'success': True,
                        'query': query,
                        'results': [],
                        'message': f'No memories found for "{query}". Here are some suggestions:',
                        'suggestions': contextual_suggestions,
                        'contextual': True
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
                    
                    # Special boost for "plan for today" queries - prioritize memories scheduled for today
                    if 'plan' in query.lower() and 'today' in query.lower():
                        if memory.delivery_date and memory.delivery_date.date() == datetime.now().date():
                            score += 100  # Significant boost for today's scheduled memories
                        elif memory.delivery_date and memory.delivery_date.date() == datetime.now().date() + timedelta(days=1):
                            score += 50   # Moderate boost for tomorrow's scheduled memories
                
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
def debug_comments(request, memory_id):
    """Debug endpoint to check comments for a specific memory"""
    if request.method == 'GET':
        try:
            memory = get_object_or_404(Memory, id=memory_id)
            
            # Check if user can view this memory
            if not memory.can_be_viewed_by(request.user):
                return JsonResponse({
                    'success': False,
                    'error': 'Permission denied'
                })
            
            comments = memory.comments.all()
            
            debug_info = {
                'memory_id': memory.id,
                'memory_content': memory.content[:100] + '...' if len(memory.content) > 100 else memory.content,
                'allow_comments': memory.allow_comments,
                'total_comments': comments.count(),
                'comments': []
            }
            
            for comment in comments:
                debug_info['comments'].append({
                    'id': comment.id,
                    'user': comment.user.username,
                    'content': comment.content,
                    'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
                    'is_edited': comment.is_edited
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


@login_required
def important_memories(request):
    """Show all important memories (importance >= 8)"""
    memories = Memory.objects.filter(
        user=request.user, 
        is_archived=False,
        importance__gte=8
    ).order_by('-created_at')
    
    # Get filter parameters
    search_query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort', '-created_at')
    
    # Apply search filter
    if search_query:
        search_conditions = Q()
        search_conditions |= Q(content__icontains=search_query)
        search_conditions |= Q(summary__icontains=search_query)
        search_conditions |= Q(tags__contains=[search_query])
        memories = memories.filter(search_conditions)
    
    # Apply sorting
    if sort_by in ['created_at', '-created_at', 'importance', '-importance', 'updated_at', '-updated_at']:
        memories = memories.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(memories, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'memories': page_obj,
        'total_count': memories.count(),
        'filter_type': 'important',
        'search_query': search_query,
        'sort_by': sort_by,
    }
    
    return render(request, 'memory_assistant/filtered_memories.html', context)


@login_required
def scheduled_memories(request):
    """Show future scheduled memories (with delivery_date in the future)"""
    from django.utils import timezone
    now = timezone.now()
    
    memories = Memory.objects.filter(
        user=request.user, 
        is_archived=False,
        delivery_date__gt=now  # Only show memories scheduled for the future
    ).order_by('delivery_date')
    
    # Get filter parameters
    search_query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort', 'delivery_date')
    
    # Apply search filter
    if search_query:
        search_conditions = Q()
        search_conditions |= Q(content__icontains=search_query)
        search_conditions |= Q(summary__icontains=search_query)
        search_conditions |= Q(tags__contains=[search_query])
        memories = memories.filter(search_conditions)
    
    # Apply sorting
    if sort_by in ['delivery_date', '-delivery_date', 'created_at', '-created_at', 'importance', '-importance']:
        memories = memories.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(memories, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'memories': page_obj,
        'total_count': memories.count(),
        'filter_type': 'scheduled',
        'search_query': search_query,
        'sort_by': sort_by,
        'now': now,
    }
    
    return render(request, 'memory_assistant/filtered_memories.html', context)


@login_required
def todays_memories(request):
    """Show memories scheduled for today"""
    today = datetime.now().date()
    memories = Memory.objects.filter(
        user=request.user, 
        is_archived=False,
        delivery_date__date=today
    ).order_by('delivery_date')
    
    # Get filter parameters
    search_query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort', 'delivery_date')
    
    # Apply search filter
    if search_query:
        search_conditions = Q()
        search_conditions |= Q(content__icontains=search_query)
        search_conditions |= Q(summary__icontains=search_query)
        search_conditions |= Q(tags__contains=[search_query])
        memories = memories.filter(search_conditions)
    
    # Apply sorting
    if sort_by in ['delivery_date', '-delivery_date', 'created_at', '-created_at', 'importance', '-importance']:
        memories = memories.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(memories, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'memories': page_obj,
        'total_count': memories.count(),
        'filter_type': 'today',
        'search_query': search_query,
        'sort_by': sort_by,
        'today_date': today,
    }
    
    return render(request, 'memory_assistant/filtered_memories.html', context)





@login_required
def all_memories(request):
    """Show all memories (same as memory_list but with different template)"""
    # Get both own and shared memories in a single query
    from .models import SharedMemory
    shared_memory_objects = SharedMemory.objects.filter(
        Q(shared_with_user=request.user) | 
        Q(shared_with_organization__in=request.user.organization_memberships.filter(is_active=True).values_list('organization', flat=True)),
        is_active=True
    ).select_related('memory').values_list('memory', flat=True)
    
    # Combine own and shared memories using Q objects
    memories = Memory.objects.filter(
        Q(user=request.user) | Q(id__in=shared_memory_objects),
        is_archived=False
    )
    
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
            pass
    
    # Enhanced search functionality
    if search_query:
        search_conditions = Q()
        search_conditions |= Q(content__icontains=search_query)
        search_conditions |= Q(summary__icontains=search_query)
        search_conditions |= Q(tags__contains=[search_query])
        memories = memories.filter(search_conditions)
    
    # Apply sorting
    if sort_by in ['created_at', '-created_at', 'importance', '-importance', 'updated_at', '-updated_at']:
        memories = memories.order_by(sort_by)
    
    # Add prefetching for comments and likes
    memories = memories.prefetch_related('comments__user__profile', 'likes__user')
    
    # Pagination
    paginator = Paginator(memories, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Create shared memory info for template
    shared_memory_info = {}
    for shared in SharedMemory.objects.filter(
        Q(shared_with_user=request.user) | 
        Q(shared_with_organization__in=request.user.organization_memberships.filter(is_active=True).values_list('organization', flat=True)),
        is_active=True
    ).select_related('memory', 'shared_by'):
        shared_memory_info[shared.memory.id] = {
            'shared_by': shared.shared_by,
            'share_type': shared.share_type,
            'message': shared.message,
            'created_at': shared.created_at,
            'organization': shared.shared_with_organization if shared.share_type == 'organization' else None
        }
    
    context = {
        'memories': page_obj,
        'total_count': memories.count(),
        'filter_type': 'all',
        'search_query': search_query,
        'sort_by': sort_by,
        'memory_type': memory_type,
        'importance': importance,
        'shared_memory_info': shared_memory_info,
    }
    
    return render(request, 'memory_assistant/filtered_memories.html', context)








def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Get the selected country and set the user's timezone
            country_code = form.cleaned_data.get('country')
            if country_code:
                from .timezone_utils import get_timezone_for_country
                timezone_name = get_timezone_for_country(country_code)
                
                # Create or update user profile with timezone
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.user_timezone = timezone_name
                profile.save()
                
                messages.success(
                    request, 
                    f'Account created successfully for {user.username}! '
                    f'Your timezone has been set to {timezone_name}. You can now log in.'
                )
            else:
                messages.success(request, f'Account created successfully for {user.username}! You can now log in.')
            
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'memory_assistant/register.html', {'form': form}) 


@login_required
def smart_reminders(request):
    """View and manage smart reminders"""
    reminder_service = SmartReminderService()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        reminder_id = request.POST.get('reminder_id')
        
        if action == 'dismiss' and reminder_id:
            reminder_service.dismiss_reminder(reminder_id, request.user)
            messages.success(request, 'Reminder dismissed successfully!')
        elif action == 'snooze' and reminder_id:
            hours = int(request.POST.get('hours', 1))
            reminder_service.snooze_reminder(reminder_id, request.user, hours)
            messages.success(request, f'Reminder snoozed for {hours} hour(s)!')
    
    # Get user's reminders
    reminders = reminder_service.get_user_reminders(request.user)
    
    # Check for triggered reminders for this user only
    triggered_reminders = reminder_service.check_and_trigger_reminders(request.user)
    
    context = {
        'reminders': reminders,
        'triggered_reminders': triggered_reminders,
    }
    
    return render(request, 'memory_assistant/smart_reminders.html', context)


@login_required
def create_smart_reminder(request, memory_id):
    """Create a smart reminder for a specific memory"""
    memory = get_object_or_404(Memory, id=memory_id)
    
    # Check if user can view this memory
    if not memory.can_be_viewed_by(request.user):
        messages.error(request, "You don't have permission to create reminders for this memory.")
        return redirect('memory_assistant:dashboard')
    
    reminder_service = SmartReminderService()
    
    if request.method == 'POST':
        reminder_type = request.POST.get('reminder_type')
        priority = request.POST.get('priority', 'medium')
        
        # Create reminder based on type
        if reminder_type == 'time_based':
            offset_minutes = int(request.POST.get('offset_minutes', 15))
            suggestion = {
                'type': 'time_based',
                'priority': priority,
                'description': f"Reminder in {offset_minutes} minutes",
                'trigger_conditions': {
                    'offset_minutes': offset_minutes,
                    'reason': f"Manual time-based reminder"
                }
            }
        elif reminder_type == 'date_based':
            target_date = request.POST.get('target_date')
            suggestion = {
                'type': 'date_based',
                'priority': priority,
                'description': f"Reminder on {target_date}",
                'trigger_conditions': {
                    'target_date': target_date,
                    'reason': f"Manual date-based reminder"
                }
            }
        elif reminder_type == 'frequency_based':
            frequency = request.POST.get('frequency', 'daily')
            suggestion = {
                'type': 'frequency_based',
                'priority': priority,
                'description': f"Recurring reminder ({frequency})",
                'trigger_conditions': {
                    'frequency': frequency,
                    'reason': f"Manual frequency-based reminder"
                }
            }
        else:
            messages.error(request, "Invalid reminder type.")
            return redirect('memory_assistant:memory_detail', memory_id=memory.id)
        
        # Create the reminder
        reminder = reminder_service.create_smart_reminder(memory, request.user, suggestion)
        messages.success(request, 'Smart reminder created successfully!')
        
        return redirect('memory_assistant:memory_detail', memory_id=memory.id)
    
    # Get AI suggestions for this memory
    suggestions = reminder_service.analyze_memory_for_reminders(memory)
    
    context = {
        'memory': memory,
        'suggestions': suggestions,
    }
    
    return render(request, 'memory_assistant/create_smart_reminder.html', context)


@login_required
def auto_create_reminders(request, memory_id):
    """Automatically create smart reminders based on AI analysis"""
    memory = get_object_or_404(Memory, id=memory_id)
    
    # Check if user can view this memory
    if not memory.can_be_viewed_by(request.user):
        messages.error(request, "You don't have permission to create reminders for this memory.")
        return redirect('memory_assistant:dashboard')
    
    reminder_service = SmartReminderService()
    
    # Get AI suggestions
    suggestions = reminder_service.analyze_memory_for_reminders(memory)
    
    created_reminders = []
    for suggestion in suggestions:
        reminder = reminder_service.create_smart_reminder(memory, request.user, suggestion)
        created_reminders.append(reminder)
    
    if created_reminders:
        messages.success(request, f'Created {len(created_reminders)} smart reminder(s)!')
    else:
        messages.info(request, 'No smart reminders were suggested for this memory.')
    
    return redirect('memory_assistant:memory_detail', memory_id=memory.id)


@login_required
def reminder_actions(request, reminder_id):
    """Handle reminder actions (dismiss, snooze, etc.) via AJAX"""
    if request.method == 'POST':
        action = request.POST.get('action')
        reminder_service = SmartReminderService()
        
        if action == 'dismiss':
            success = reminder_service.dismiss_reminder(reminder_id, request.user)
            if success:
                return JsonResponse({'success': True, 'message': 'Reminder dismissed'})
            else:
                return JsonResponse({'success': False, 'message': 'Reminder not found'})
        
        elif action == 'snooze':
            hours = int(request.POST.get('hours', 1))
            success = reminder_service.snooze_reminder(reminder_id, request.user, hours)
            if success:
                return JsonResponse({'success': True, 'message': f'Reminder snoozed for {hours} hour(s)'})
            else:
                return JsonResponse({'success': False, 'message': 'Reminder not found'})
    
    return JsonResponse({'success': False, 'message': 'Invalid action'}) 

# Smart Reminder Notification Views
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import SmartReminder

def check_reminders(request):
    """Check for active reminders that should be shown to the user"""
    if not request.user.is_authenticated:
        return JsonResponse({'has_reminders': False})
    
    now = timezone.now()
    
    # Find reminders that should be triggered now
    active_reminders = SmartReminder.objects.filter(
        user=request.user,
        is_active=True,
        next_trigger__lte=now,
        last_triggered__isnull=True  # Only show if not already triggered
    ).select_related('memory').order_by('priority', 'next_trigger')[:1]  # Get the most important one
    
    if active_reminders.exists():
        reminder = active_reminders.first()
        
        # Mark as triggered
        reminder.last_triggered = now
        reminder.save()
        
        return JsonResponse({
            'has_reminders': True,
            'reminder': {
                'id': reminder.id,
                'memory_content': reminder.memory.content[:100] + '...' if len(reminder.memory.content) > 100 else reminder.memory.content,
                'reason': reminder.trigger_conditions.get('reason', 'Time-based reminder'),
                'priority': reminder.get_priority_display(),
                'memory_id': reminder.memory.id
            }
        })
    
    return JsonResponse({'has_reminders': False})

def mark_reminder_done(request, reminder_id):
    """Mark a reminder as done"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    try:
        reminder = SmartReminder.objects.get(
            id=reminder_id,
            user=request.user
        )
        reminder.is_active = False
        reminder.save()
        return JsonResponse({'success': True})
    except SmartReminder.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Reminder not found'})

def snooze_reminder(request, reminder_id):
    """Snooze a reminder for 1 hour"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    try:
        reminder = SmartReminder.objects.get(
            id=reminder_id,
            user=request.user
        )
        reminder.next_trigger = timezone.now() + timedelta(hours=1)
        reminder.last_triggered = None  # Reset so it can be triggered again
        reminder.save()
        return JsonResponse({'success': True})
    except SmartReminder.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Reminder not found'})

def dismiss_reminder(request, reminder_id):
    """Dismiss a reminder permanently"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    try:
        reminder = SmartReminder.objects.get(
            id=reminder_id,
            user=request.user
        )
        reminder.is_active = False
        reminder.save()
        return JsonResponse({'success': True})
    except SmartReminder.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Reminder not found'})

@login_required
def timezone_test(request):
    """Test view to demonstrate timezone functionality"""
    from django.utils import timezone
    import pytz
    
    # Get current time in different timezones
    now = timezone.now()
    
    timezone_times = {}
    common_timezones = [
        'UTC',
        'America/New_York',
        'America/Chicago', 
        'America/Denver',
        'America/Los_Angeles',
        'Europe/London',
        'Europe/Paris',
        'Asia/Tokyo',
        'Australia/Sydney'
    ]
    
    for tz_name in common_timezones:
        try:
            tz = pytz.timezone(tz_name)
            local_time = now.astimezone(tz)
            timezone_times[tz_name] = local_time.strftime('%Y-%m-%d %H:%M:%S %Z')
        except:
            timezone_times[tz_name] = 'Error'
    
    # Get user's current timezone
    user_timezone = 'UTC'
    if hasattr(request.user, 'profile') and request.user.profile.user_timezone:
        user_timezone = request.user.profile.user_timezone
    
    context = {
        'timezone_times': timezone_times,
        'user_timezone': user_timezone,
        'current_time': now.strftime('%Y-%m-%d %H:%M:%S %Z'),
    }
    
    return render(request, 'memory_assistant/timezone_test.html', context)