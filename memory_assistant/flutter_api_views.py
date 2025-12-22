#!/usr/bin/env python
"""
Optimized API views specifically designed for Flutter app integration
with smart reminders functionality.
"""

from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import Memory, SmartReminder, ReminderTrigger
from .serializers import (
    MemorySerializer, 
    MemoryCreateSerializer,
    SmartReminderSerializer,
    SmartReminderCreateSerializer
)
from .services import ChatGPTService
from .smart_reminder_service import SmartReminderService


class FlutterMemoryAPIView(APIView):
    """
    Optimized memory creation API for Flutter app
    Automatically creates smart reminders when memory is created
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Create a new memory with automatic smart reminder generation and scheduled memory support
        
        Expected payload:
        {
            "content": "Team meeting tomorrow at 2 PM",
            "memory_type": "task",  # optional: general, task, idea, learning, etc.
            "importance": 8,        # optional: 1-10 scale
            "delivery_date": "2024-01-15T14:00:00Z",  # optional: ISO format
            "delivery_type": "scheduled",  # optional: immediate, scheduled, conditional
            "tags": ["work", "meeting"],   # optional: array of strings
            "privacy_level": "private",    # optional: private, friends, public
            "allow_comments": true,        # optional: boolean
            "allow_likes": true,           # optional: boolean
            "is_time_locked": false,       # optional: boolean
            "recurring_pattern": {         # optional: for recurring memories
                "type": "daily",           # daily, weekly, monthly, yearly
                "interval": 1,             # every N days/weeks/months/years
                "end_date": "2024-12-31T23:59:59Z",  # optional end date
                "days_of_week": [1, 3, 5]  # for weekly: 0=Monday, 6=Sunday
            }
        }
        """
        try:
            # Validate required fields
            content = request.data.get('content', '').strip()
            if len(content) < 10:
                return Response(
                    {'error': 'Memory content must be at least 10 characters long.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Parse delivery_date if provided
            delivery_date = None
            delivery_date_str = request.data.get('delivery_date')
            if delivery_date_str:
                try:
                    from django.utils.dateparse import parse_datetime
                    delivery_date = parse_datetime(delivery_date_str)
                    if not delivery_date:
                        return Response(
                            {'error': 'Invalid delivery_date format. Use ISO format: YYYY-MM-DDTHH:MM:SSZ'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                except Exception:
                    return Response(
                        {'error': 'Invalid delivery_date format. Use ISO format: YYYY-MM-DDTHH:MM:SSZ'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Validate delivery_type
            delivery_type = request.data.get('delivery_type', 'immediate')
            valid_delivery_types = ['immediate', 'scheduled', 'conditional']
            if delivery_type not in valid_delivery_types:
                return Response(
                    {'error': f'Invalid delivery_type. Must be one of: {", ".join(valid_delivery_types)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Inference: if not explicitly scheduled or missing time, infer for vague future phrases
            try:
                from django.conf import settings
                import pytz
                content_lower = content.lower()

                # Determine user's timezone
                user_tz_name = getattr(getattr(request.user, 'profile', None), 'user_timezone', None) or getattr(settings, 'TIME_ZONE', 'UTC')
                user_tz = pytz.timezone(user_tz_name)
                now_utc = timezone.now()
                now_local = now_utc.astimezone(user_tz)

                def set_delivery_local(hour: int, minute: int = 0, day_offset: int = 0):
                    local_dt = (now_local + timedelta(days=day_offset)).replace(hour=hour, minute=minute, second=0, microsecond=0)
                    # If time already passed today with day_offset=0, push to next day
                    if day_offset == 0 and local_dt <= now_local:
                        local_dt = local_dt + timedelta(days=1)
                    return local_dt.astimezone(pytz.UTC)

                # Only infer if delivery_date not provided
                if delivery_date is None:
                    inferred = None
                    # Morning / breakfast → 09:00
                    if any(k in content_lower for k in ['tomorrow morning', 'morning tomorrow']):
                        inferred = set_delivery_local(9, 0, day_offset=1)
                    elif 'tomorrow' in content_lower and any(k in content_lower for k in ['morning']):
                        inferred = set_delivery_local(9, 0, day_offset=1)
                    elif 'tomorrow' in content_lower:
                        # default tomorrow at 09:00 if vague tomorrow without time
                        inferred = set_delivery_local(9, 0, day_offset=1)
                    # Afternoon → 13:00
                    elif any(k in content_lower for k in ['tomorrow afternoon', 'afternoon tomorrow']):
                        inferred = set_delivery_local(13, 0, day_offset=1)
                    elif 'tomorrow' in content_lower and any(k in content_lower for k in ['afternoon']):
                        inferred = set_delivery_local(13, 0, day_offset=1)
                    # Evening / tonight → 19:00
                    elif any(k in content_lower for k in ['tonight']):
                        inferred = set_delivery_local(19, 0, day_offset=0)
                    elif 'tomorrow' in content_lower and any(k in content_lower for k in ['evening']):
                        inferred = set_delivery_local(19, 0, day_offset=1)

                    # Week-based phrases and weekdays
                    if inferred is None:
                        import re
                        weekdays = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
                        # next <weekday>
                        m = re.search(r"next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)", content_lower)
                        if m:
                            target_name = m.group(1)
                            target_idx = weekdays.index(target_name)
                            # Python weekday(): Monday=0 ... Sunday=6
                            diff = (target_idx - now_local.weekday()) % 7
                            if diff == 0:
                                diff = 7
                            inferred = set_delivery_local(9, 0, day_offset=diff)
                        else:
                            # plain weekday → next occurrence (today->next week)
                            for idx, name in enumerate(weekdays):
                                if name in content_lower:
                                    diff = (idx - now_local.weekday()) % 7
                                    if diff == 0:
                                        diff = 7
                                    inferred = set_delivery_local(9, 0, day_offset=diff)
                                    break

                    if inferred is not None:
                        delivery_date = inferred
                        delivery_type = 'scheduled'
            except Exception:
                # Non-fatal: continue without inference
                pass
            
            # Validate scheduled memory requirements (after inference)
            if delivery_type == 'scheduled' and not delivery_date:
                return Response(
                    {'error': 'delivery_date is required when delivery_type is "scheduled"'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create memory
            memory_data = {
                'user': request.user,
                'content': content,
                'memory_type': request.data.get('memory_type', 'general'),
                'importance': request.data.get('importance', 5),
                'delivery_date': delivery_date,
                'delivery_type': delivery_type,
                'tags': request.data.get('tags', []),
                'privacy_level': request.data.get('privacy_level', 'private'),
                'allow_comments': request.data.get('allow_comments', True),
                'allow_likes': request.data.get('allow_likes', True),
                'language': request.data.get('language', 'en'),
                'is_time_locked': request.data.get('is_time_locked', False),
            }
            
            # Handle recurring pattern if provided
            recurring_pattern = request.data.get('recurring_pattern')
            if recurring_pattern and delivery_type == 'scheduled':
                memory_data['recurring_pattern'] = recurring_pattern
            
            # Remove None values
            memory_data = {k: v for k, v in memory_data.items() if v is not None}
            
            memory = Memory.objects.create(**memory_data)
            
            # AI Enhancement (optional, non-blocking)
            try:
                ai_service = ChatGPTService()
                if ai_service.is_available():
                    # Auto-categorize and enhance
                    ai_response = ai_service.categorize_memory(content)
                    if ai_response.get('success'):
                        memory.memory_type = ai_response.get('memory_type', memory.memory_type)
                        memory.importance = ai_response.get('importance', memory.importance)
                        memory.tags = ai_response.get('tags', memory.tags)
                        memory.ai_reasoning = ai_response.get('reasoning', '')
                    
                    # Generate summary
                    summary_response = ai_service.generate_summary(content)
                    if summary_response.get('success'):
                        memory.summary = summary_response.get('summary', '')
                    
                    memory.save()
            except Exception:
                # Continue even if AI fails
                pass
            
            # Create Smart Reminders (automatic)
            reminder_service = SmartReminderService()
            created_reminders = []
            
            try:
                # For scheduled memories, create the scheduled reminder first
                if memory.delivery_type == 'scheduled' and memory.delivery_date:
                    scheduled_reminder = reminder_service.create_scheduled_memory_reminder(memory, request.user)
                    if scheduled_reminder:
                        created_reminders.append({
                            'id': scheduled_reminder.id,
                            'type': scheduled_reminder.reminder_type,
                            'priority': scheduled_reminder.priority,
                            'next_trigger': scheduled_reminder.next_trigger.isoformat() if scheduled_reminder.next_trigger else None,
                            'description': f'Scheduled reminder for {memory.delivery_date.strftime("%Y-%m-%d %H:%M")}',
                            'is_scheduled': True
                        })
                
                # For time-locked memories, create appropriate reminders
                if memory.is_time_locked and memory.delivery_date:
                    time_locked_reminder = reminder_service.create_time_locked_reminder(memory, request.user)
                    if time_locked_reminder:
                        created_reminders.append({
                            'id': time_locked_reminder.id,
                            'type': time_locked_reminder.reminder_type,
                            'priority': time_locked_reminder.priority,
                            'next_trigger': time_locked_reminder.next_trigger.isoformat() if time_locked_reminder.next_trigger else None,
                            'description': 'Time-locked memory reminder',
                            'is_time_locked': True
                        })
                
                # Analyze content for additional contextual reminders
                suggestions = reminder_service.analyze_memory_for_reminders(memory) or []
                for suggestion in suggestions:
                    try:
                        reminder = reminder_service.create_smart_reminder(memory, request.user, suggestion)
                        created_reminders.append({
                            'id': reminder.id,
                            'type': reminder.reminder_type,
                            'priority': reminder.priority,
                            'next_trigger': reminder.next_trigger.isoformat() if reminder.next_trigger else None,
                            'description': suggestion.get('description', ''),
                            'is_contextual': True
                        })
                    except Exception:
                        # Skip any invalid suggestion without failing the request
                        continue
            except Exception:
                # Do not block creation if reminder generation fails
                pass
            
            # Return memory with created reminders
            memory_serializer = MemorySerializer(memory)
            response_data = memory_serializer.data
            response_data['created_reminders'] = created_reminders
            response_data['reminder_count'] = len(created_reminders)
            
            # Add scheduled memory specific information
            if memory.delivery_type == 'scheduled':
                response_data['scheduled_info'] = {
                    'delivery_date': memory.delivery_date.isoformat() if memory.delivery_date else None,
                    'delivery_type': memory.delivery_type,
                    'is_time_locked': memory.is_time_locked,
                    'recurring_pattern': memory.recurring_pattern if hasattr(memory, 'recurring_pattern') else None,
                    'is_delivered': memory.is_delivered,
                    'is_completed': memory.is_completed,
                    'snooze_count': memory.snooze_count,
                    'last_snoozed_at': memory.last_snoozed_at.isoformat() if memory.last_snoozed_at else None,
                }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to create memory: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FlutterQuickAddMemoryAPIView(APIView):
    """
    Quick add memory API for Flutter app
    Applies the same time inference to set scheduled delivery when possible
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            content = request.data.get('content', '').strip()
            if len(content) < 3:
                return Response({'error': 'content is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Defaults
            delivery_date = None
            delivery_type = 'immediate'
            
            # Inference (same logic as in FlutterMemoryAPIView)
            try:
                import pytz, re
                content_lower = content.lower()
                user_tz_name = getattr(getattr(request.user, 'profile', None), 'user_timezone', None) or getattr(timezone, 'get_current_timezone_name', lambda: 'UTC')()
                try:
                    user_tz = pytz.timezone(user_tz_name)
                except Exception:
                    user_tz = pytz.UTC
                now_utc = timezone.now()
                now_local = now_utc.astimezone(user_tz)
                
                def set_delivery_local(hour: int, minute: int = 0, day_offset: int = 0):
                    local_dt = (now_local + timedelta(days=day_offset)).replace(hour=hour, minute=minute, second=0, microsecond=0)
                    if day_offset == 0 and local_dt <= now_local:
                        local_dt = local_dt + timedelta(days=1)
                    return local_dt.astimezone(pytz.UTC)
                
                inferred = None
                # tomorrow variants
                if any(k in content_lower for k in ['tomorrow morning', 'morning tomorrow']):
                    inferred = set_delivery_local(9, 0, day_offset=1)
                elif 'tomorrow' in content_lower and 'afternoon' in content_lower:
                    inferred = set_delivery_local(13, 0, day_offset=1)
                elif 'tomorrow' in content_lower and 'evening' in content_lower:
                    inferred = set_delivery_local(19, 0, day_offset=1)
                elif 'tomorrow' in content_lower:
                    inferred = set_delivery_local(9, 0, day_offset=1)
                # tonight
                elif 'tonight' in content_lower:
                    inferred = set_delivery_local(19, 0, day_offset=0)
                
                # next <weekday> or plain weekday
                if inferred is None:
                    weekdays = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
                    m = re.search(r"next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)", content_lower)
                    if m:
                        target_idx = weekdays.index(m.group(1))
                        diff = (target_idx - now_local.weekday()) % 7
                        if diff == 0:
                            diff = 7
                        inferred = set_delivery_local(9, 0, day_offset=diff)
                    else:
                        for idx, name in enumerate(weekdays):
                            if name in content_lower:
                                diff = (idx - now_local.weekday()) % 7
                                if diff == 0:
                                    diff = 7
                                inferred = set_delivery_local(9, 0, day_offset=diff)
                                break
                
                if inferred is not None:
                    delivery_date = inferred
                    delivery_type = 'scheduled'
            except Exception:
                pass
            
            # Create the memory
            memory = Memory.objects.create(
                user=request.user,
                content=content,
                memory_type=request.data.get('memory_type', 'general'),
                importance=request.data.get('importance', 5),
                delivery_date=delivery_date,
                delivery_type=delivery_type,
                tags=request.data.get('tags', []),
                privacy_level=request.data.get('privacy_level', 'private'),
                allow_comments=request.data.get('allow_comments', True),
                allow_likes=request.data.get('allow_likes', True),
                language=request.data.get('language', 'en'),
                is_time_locked=request.data.get('is_time_locked', False),
            )
            
            # Create reminders similarly to the main create endpoint
            created_reminders = []
            try:
                service = SmartReminderService()
                if memory.delivery_type == 'scheduled' and memory.delivery_date:
                    scheduled_reminder = service.create_scheduled_memory_reminder(memory, request.user)
                    if scheduled_reminder:
                        created_reminders.append({'id': scheduled_reminder.id})
                suggestions = service.analyze_memory_for_reminders(memory) or []
                for s in suggestions:
                    try:
                        r = service.create_smart_reminder(memory, request.user, s)
                        created_reminders.append({'id': r.id})
                    except Exception:
                        continue
            except Exception:
                pass
            
            data = MemorySerializer(memory).data
            data['created_reminders'] = created_reminders
            if memory.delivery_type == 'scheduled':
                data['scheduled_info'] = {
                    'delivery_date': memory.delivery_date.isoformat() if memory.delivery_date else None,
                    'delivery_type': memory.delivery_type,
                    'is_time_locked': memory.is_time_locked,
                    'is_delivered': memory.is_delivered,
                    'is_completed': memory.is_completed,
                }
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': f'Quick add failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FlutterSmartReminderAPIView(APIView):
    """
    Optimized smart reminder API for Flutter app
    Provides all necessary endpoints for reading and managing reminders
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Get smart reminders for the user
        
        Query parameters:
        - status: active, triggered, all (default: active)
        - type: time_based, date_based, frequency_based, etc.
        - priority: low, medium, high, critical
        - memory_id: filter by specific memory ID
        - memoryId: alternative parameter name for memory_id
        - memory: alternative parameter name for memory_id
        - limit: number of results (default: 50)
        - offset: pagination offset (default: 0)
        """
        try:
            # Get query parameters
            print(f"🔍 Server: All GET parameters: {dict(request.GET)}")
            status_filter = request.GET.get('status', 'active')
            type_filter = request.GET.get('type')
            priority_filter = request.GET.get('priority')
            memory_id = request.GET.get('memory_id') or request.GET.get('memoryId') or request.GET.get('memory')
            limit = int(request.GET.get('limit', 50))
            offset = int(request.GET.get('offset', 0))
            print(f"🔍 Server: Extracted memory_id: {memory_id}")
            
            # Build queryset
            queryset = SmartReminder.objects.filter(user=request.user).select_related('memory')
            
            # Apply memory_id filter if provided
            if memory_id:
                try:
                    memory_id_int = int(memory_id)
                    print(f"🔍 Server: Filtering reminders by memory_id={memory_id_int}")
                    queryset = queryset.filter(memory_id=memory_id_int)
                    print(f"🔍 Server: After filtering, queryset count: {queryset.count()}")
                except (ValueError, TypeError):
                    return Response(
                        {'error': 'Invalid memory_id parameter. Must be an integer.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                print(f"🔍 Server: No memory_id filter provided, returning all reminders for user")
            
            # Apply filters
            if status_filter == 'active':
                queryset = queryset.filter(is_active=True)
            elif status_filter == 'triggered':
                # Get reminders that have been triggered recently
                recent_time = timezone.now() - timedelta(hours=24)
                queryset = queryset.filter(
                    triggers__triggered_at__gte=recent_time
                ).distinct()
            
            if type_filter:
                queryset = queryset.filter(reminder_type=type_filter)
            
            if priority_filter:
                queryset = queryset.filter(priority=priority_filter)
            
            # Order by next trigger time
            queryset = queryset.order_by('next_trigger', '-created_at')
            
            # Apply pagination
            total_count = queryset.count()
            reminders = queryset[offset:offset + limit]
            
            # Serialize reminders
            serializer = SmartReminderSerializer(reminders, many=True)
            
            print(f"🔍 Server: Returning {len(serializer.data)} reminders")
            for reminder_data in serializer.data:
                print(f"  - Reminder {reminder_data.get('id')}: memoryId={reminder_data.get('memory_id')}")
            
            return Response({
                'reminders': serializer.data,
                'total_count': total_count,
                'has_more': offset + limit < total_count,
                'next_offset': offset + limit if offset + limit < total_count else None
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get reminders: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """
        Create a new smart reminder manually
        
        Expected payload:
        {
            "memory_id": 123,
            "reminder_type": "time_based",
            "priority": "high",
            "trigger_conditions": {
                "target_time": "2024-01-15T14:00:00Z",
                "offset_minutes": 30,
                "reason": "Meeting reminder"
            }
        }
        """
        try:
            serializer = SmartReminderCreateSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                reminder = serializer.save()
                response_serializer = SmartReminderSerializer(reminder)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to create reminder: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def patch(self, request, reminder_id=None):
        """
        Update a smart reminder
        
        Expected payload:
        {
            "reminder_type": "time_based",
            "priority": "high",
            "trigger_conditions": {...},
            "is_active": true
        }
        """
        try:
            # Get the reminder
            try:
                reminder = SmartReminder.objects.get(id=reminder_id, user=request.user)
            except SmartReminder.DoesNotExist:
                return Response(
                    {'error': 'Reminder not found or access denied'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Update fields if provided
            if 'reminder_type' in request.data:
                reminder.reminder_type = request.data['reminder_type']
            if 'priority' in request.data:
                reminder.priority = request.data['priority']
            if 'trigger_conditions' in request.data:
                reminder.trigger_conditions = request.data['trigger_conditions']
            if 'is_active' in request.data:
                reminder.is_active = request.data['is_active']
            
            # Recalculate next trigger if conditions changed
            if 'trigger_conditions' in request.data:
                reminder.calculate_next_trigger()
            
            reminder.save()
            
            serializer = SmartReminderSerializer(reminder)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to update reminder: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, reminder_id=None):
        """
        Delete a smart reminder
        """
        try:
            # Get the reminder
            try:
                reminder = SmartReminder.objects.get(id=reminder_id, user=request.user)
            except SmartReminder.DoesNotExist:
                return Response(
                    {'error': 'Reminder not found or access denied'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            reminder.delete()
            
            return Response(
                {'message': 'Reminder deleted successfully'}, 
                status=status.HTTP_204_NO_CONTENT
            )
            
        except Exception as e:
            return Response(
                {'error': f'Failed to delete reminder: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FlutterRemindersForMemoryAPIView(APIView):
    """
    Get reminders for a specific memory
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, memory_id):
        """
        Get all smart reminders for a specific memory
        
        Query parameters:
        - status: active, triggered, all (default: active)
        - type: time_based, date_based, frequency_based, etc.
        - priority: low, medium, high, critical
        - limit: number of results (default: 50)
        - offset: pagination offset (default: 0)
        """
        try:
            # Verify the memory exists and belongs to the user
            try:
                memory = Memory.objects.get(id=memory_id, user=request.user)
            except Memory.DoesNotExist:
                return Response(
                    {'error': 'Memory not found or access denied'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get query parameters
            status_filter = request.GET.get('status', 'active')
            type_filter = request.GET.get('type')
            priority_filter = request.GET.get('priority')
            limit = int(request.GET.get('limit', 50))
            offset = int(request.GET.get('offset', 0))
            
            # Build queryset for this specific memory
            print(f"🔍 Server: Getting reminders for memory_id={memory_id}, user={request.user.id}")
            queryset = SmartReminder.objects.filter(
                user=request.user,
                memory_id=memory_id
            ).select_related('memory')
            print(f"🔍 Server: Found {queryset.count()} reminders for memory {memory_id}")
            
            # Apply filters
            if status_filter == 'active':
                queryset = queryset.filter(is_active=True)
            elif status_filter == 'triggered':
                # Get reminders that have been triggered recently
                recent_time = timezone.now() - timedelta(hours=24)
                queryset = queryset.filter(
                    triggers__triggered_at__gte=recent_time
                ).distinct()
            
            if type_filter:
                queryset = queryset.filter(reminder_type=type_filter)
            
            if priority_filter:
                queryset = queryset.filter(priority=priority_filter)
            
            # Order by next trigger time
            queryset = queryset.order_by('next_trigger', '-created_at')
            
            # Apply pagination
            total_count = queryset.count()
            reminders = queryset[offset:offset + limit]
            
            # Serialize reminders
            serializer = SmartReminderSerializer(reminders, many=True)
            
            return Response({
                'reminders': serializer.data,
                'total_count': total_count,
                'has_more': offset + limit < total_count,
                'next_offset': offset + limit if offset + limit < total_count else None,
                'memory_id': memory_id,
                'memory_content': memory.content[:100] + '...' if len(memory.content) > 100 else memory.content
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get reminders for memory: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FlutterReminderActionsAPIView(APIView):
    """
    Handle reminder actions (snooze, dismiss, mark done)
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, reminder_id):
        """
        Perform action on a reminder
        
        Expected payload:
        {
            "action": "snooze",  # snooze, dismiss, mark_done
            "hours": 2,          # for snooze action (optional, default: 1)
            "reason": "Busy now" # optional reason
        }
        """
        try:
            # Get reminder
            try:
                reminder = SmartReminder.objects.get(id=reminder_id, user=request.user)
            except SmartReminder.DoesNotExist:
                return Response(
                    {'error': 'Reminder not found or access denied'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            action = request.data.get('action')
            
            if action == 'snooze':
                hours = int(request.data.get('hours', 1))
                reminder.next_trigger = timezone.now() + timedelta(hours=hours)
                reminder.save()
                
                return Response({
                    'success': True,
                    'message': f'Reminder snoozed for {hours} hour(s)',
                    'next_trigger': reminder.next_trigger.isoformat()
                })
            
            elif action == 'dismiss':
                reminder.is_active = False
                reminder.save()
                
                return Response({
                    'success': True,
                    'message': 'Reminder dismissed'
                })
            
            elif action == 'mark_done':
                # For now, just dismiss the reminder
                # You can extend this to mark the associated memory as completed
                reminder.is_active = False
                reminder.save()
                
                # Optionally mark memory as completed
                if hasattr(reminder.memory, 'is_completed'):
                    reminder.memory.is_completed = True
                    reminder.memory.completed_at = timezone.now()
                    reminder.memory.save()
                
                return Response({
                    'success': True,
                    'message': 'Reminder marked as done'
                })
            
            else:
                return Response(
                    {'error': 'Invalid action. Use: snooze, dismiss, or mark_done'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': f'Failed to perform action: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FlutterReminderCheckAPIView(APIView):
    """
    Check for triggered reminders (for background sync)
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Check and return triggered reminders
        
        Expected payload (optional):
        {
            "last_check": "2024-01-15T10:00:00Z"  # ISO format, only get reminders after this time
        }
        """
        try:
            # Get last check time
            last_check_str = request.data.get('last_check')
            if last_check_str:
                try:
                    last_check = datetime.fromisoformat(last_check_str.replace('Z', '+00:00'))
                except:
                    last_check = timezone.now() - timedelta(hours=1)
            else:
                last_check = timezone.now() - timedelta(hours=1)
            
            # Check for triggered reminders
            service = SmartReminderService()
            triggered = service.check_and_trigger_reminders(request.user)
            
            # Filter by last check time
            recent_triggered = []
            for item in triggered:
                if item['trigger'].triggered_at >= last_check:
                    recent_triggered.append({
                        'id': item['reminder'].id,
                        'memory_id': item['reminder'].memory.id,
                        'memory_content': item['reminder'].memory.content[:100],
                        'memory_type': item['reminder'].memory.memory_type,
                        'reminder_type': item['reminder'].reminder_type,
                        'priority': item['reminder'].priority,
                        'trigger_reason': item['trigger'].trigger_reason,
                        'triggered_at': item['trigger'].triggered_at.isoformat(),
                        'next_trigger': item['reminder'].next_trigger.isoformat() if item['reminder'].next_trigger else None
                    })
            
            return Response({
                'triggered_count': len(recent_triggered),
                'reminders': recent_triggered,
                'check_time': timezone.now().isoformat()
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to check reminders: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FlutterReminderStatsAPIView(APIView):
    """
    Get reminder statistics for dashboard
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Get comprehensive reminder statistics
        """
        try:
            user_reminders = SmartReminder.objects.filter(user=request.user)
            
            # Basic stats
            total = user_reminders.count()
            active = user_reminders.filter(is_active=True).count()
            
            # Upcoming reminders (next 24 hours)
            next_24h = timezone.now() + timedelta(hours=24)
            upcoming = user_reminders.filter(
                is_active=True,
                next_trigger__lte=next_24h,
                next_trigger__gte=timezone.now()
            ).count()
            
            # Triggered today
            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            triggered_today = ReminderTrigger.objects.filter(
                reminder__user=request.user,
                triggered_at__gte=today_start
            ).count()
            
            # By type
            type_stats = {}
            for reminder_type, _ in SmartReminder.REMINDER_TYPES:
                count = user_reminders.filter(reminder_type=reminder_type).count()
                if count > 0:
                    type_stats[reminder_type] = count
            
            # By priority
            priority_stats = {}
            for priority, _ in SmartReminder.PRIORITY_LEVELS:
                count = user_reminders.filter(priority=priority).count()
                if count > 0:
                    priority_stats[priority] = count
            
            return Response({
                'total_reminders': total,
                'active_reminders': active,
                'upcoming_count': upcoming,
                'triggered_today': triggered_today,
                'by_type': type_stats,
                'by_priority': priority_stats,
                'generated_at': timezone.now().isoformat()
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get stats: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FlutterMemoryWithRemindersAPIView(APIView):
    """
    Get memories with their associated reminders
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Get memories with their smart reminders
        
        Query parameters:
        - memory_id: specific memory ID (optional)
        - with_reminders: include reminders in response (default: true)
        - limit: number of results (default: 20)
        - offset: pagination offset (default: 0)
        """
        try:
            memory_id = request.GET.get('memory_id')
            with_reminders = request.GET.get('with_reminders', 'true').lower() == 'true'
            limit = int(request.GET.get('limit', 20))
            offset = int(request.GET.get('offset', 0))
            
            if memory_id:
                # Get specific memory
                try:
                    memory = Memory.objects.get(id=memory_id, user=request.user)
                    memories = [memory]
                except Memory.DoesNotExist:
                    return Response(
                        {'error': 'Memory not found or access denied'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # Get user's memories
                memories = Memory.objects.filter(user=request.user).order_by('-created_at')
                total_count = memories.count()
                memories = memories[offset:offset + limit]
            
            # Serialize memories
            memory_serializer = MemorySerializer(memories, many=True)
            memory_data = memory_serializer.data
            
            if with_reminders:
                # Add reminders to each memory
                for i, memory in enumerate(memories):
                    reminders = SmartReminder.objects.filter(
                        memory=memory,
                        user=request.user,
                        is_active=True
                    ).order_by('next_trigger')
                    
                    reminder_serializer = SmartReminderSerializer(reminders, many=True)
                    memory_data[i]['smart_reminders'] = reminder_serializer.data
                    memory_data[i]['reminder_count'] = reminders.count()
            
            response_data = {
                'memories': memory_data,
                'generated_at': timezone.now().isoformat()
            }
            
            if not memory_id:
                response_data.update({
                    'total_count': total_count,
                    'has_more': offset + limit < total_count,
                    'next_offset': offset + limit if offset + limit < total_count else None
                })
            
            return Response(response_data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get memories: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FlutterScheduledRemindersAPIView(APIView):
    """
    Get scheduled reminders for Flutter app
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Get scheduled reminders that are due or upcoming
        
        Query parameters:
        - due_only: only get reminders that are due now (default: false)
        - hours_ahead: get reminders due within this many hours (default: 24)
        - limit: number of results (default: 50)
        """
        try:
            due_only = request.GET.get('due_only', 'false').lower() == 'true'
            hours_ahead = int(request.GET.get('hours_ahead', 24))
            limit = int(request.GET.get('limit', 50))
            
            now = timezone.now()
            future_time = now + timedelta(hours=hours_ahead)
            
            # Get scheduled reminders
            queryset = SmartReminder.objects.filter(
                user=request.user,
                is_active=True,
                reminder_type='time_based'
            ).select_related('memory')
            
            if due_only:
                # Only get reminders that are due now or overdue
                queryset = queryset.filter(next_trigger__lte=now)
            else:
                # Get reminders due within the specified time range
                queryset = queryset.filter(
                    next_trigger__gte=now,
                    next_trigger__lte=future_time
                )
            
            # Order by next trigger time
            queryset = queryset.order_by('next_trigger')
            
            # Apply limit
            reminders = queryset[:limit]
            
            # Serialize reminders with additional scheduled memory info
            reminder_data = []
            for reminder in reminders:
                reminder_dict = SmartReminderSerializer(reminder).data
                
                # Add scheduled memory specific information
                if reminder.memory.delivery_type == 'scheduled':
                    reminder_dict['scheduled_info'] = {
                        'delivery_date': reminder.memory.delivery_date.isoformat() if reminder.memory.delivery_date else None,
                        'delivery_type': reminder.memory.delivery_type,
                        'is_time_locked': reminder.memory.is_time_locked,
                        'is_delivered': reminder.memory.is_delivered,
                        'is_completed': reminder.memory.is_completed,
                        'snooze_count': reminder.memory.snooze_count,
                        'last_snoozed_at': reminder.memory.last_snoozed_at.isoformat() if reminder.memory.last_snoozed_at else None,
                        'can_snooze': reminder.memory.snooze_count < 5,  # Max 5 snoozes
                        'can_decline': not reminder.memory.is_completed,
                        'can_mark_done': not reminder.memory.is_completed,
                    }
                
                reminder_data.append(reminder_dict)
            
            return Response({
                'scheduled_reminders': reminder_data,
                'total_count': len(reminder_data),
                'due_only': due_only,
                'hours_ahead': hours_ahead,
                'generated_at': now.isoformat()
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get scheduled reminders: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FlutterScheduledMemoryActionsAPIView(APIView):
    """
    Handle scheduled memory actions (snooze, mark done, decline)
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, memory_id):
        """
        Perform action on a scheduled memory
        
        Expected payload:
        {
            "action": "snooze",  # snooze, mark_done, decline
            "hours": 2,          # for snooze action (optional, default: 1)
            "reason": "Busy now" # optional reason for decline
        }
        """
        try:
            # Get memory
            try:
                memory = Memory.objects.get(id=memory_id, user=request.user)
            except Memory.DoesNotExist:
                return Response(
                    {'error': 'Memory not found or access denied'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if memory is scheduled
            if memory.delivery_type != 'scheduled':
                return Response(
                    {'error': 'This memory is not scheduled'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            action = request.data.get('action')
            
            if action == 'snooze':
                hours = int(request.data.get('hours', 1))
                # Update delivery_date to be hours from now
                memory.delivery_date = timezone.now() + timedelta(hours=hours)
                memory.snooze_count += 1
                memory.last_snoozed_at = timezone.now()
                memory.save()
                
                # Update associated reminders
                for reminder in memory.smart_reminders.filter(is_active=True):
                    reminder.next_trigger = memory.delivery_date - timedelta(minutes=15)  # 15 min before
                    reminder.save()
                
                return Response({
                    'success': True,
                    'message': f'Memory snoozed for {hours} hour(s)',
                    'new_delivery_date': memory.delivery_date.isoformat(),
                    'snooze_count': memory.snooze_count
                })
            
            elif action == 'mark_done':
                memory.is_completed = True
                memory.completed_at = timezone.now()
                memory.is_delivered = True
                memory.save()
                
                # Deactivate associated reminders
                memory.smart_reminders.filter(is_active=True).update(is_active=False)
                
                return Response({
                    'success': True,
                    'message': 'Memory marked as completed',
                    'completed_at': memory.completed_at.isoformat()
                })
            
            elif action == 'decline':
                reason = request.data.get('reason', '')
                memory.declined_at = timezone.now()
                memory.decline_reason = reason
                memory.is_delivered = True
                memory.save()
                
                # Deactivate associated reminders
                memory.smart_reminders.filter(is_active=True).update(is_active=False)
                
                return Response({
                    'success': True,
                    'message': 'Memory declined',
                    'declined_at': memory.declined_at.isoformat(),
                    'decline_reason': reason
                })
            
            else:
                return Response(
                    {'error': 'Invalid action. Use: snooze, mark_done, or decline'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': f'Failed to perform action: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

