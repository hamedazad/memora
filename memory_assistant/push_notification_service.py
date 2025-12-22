#!/usr/bin/env python
"""
Push Notification Service for Smart Reminders
Handles sending push notifications to mobile devices when reminders are triggered
"""

import requests
import json
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from .models import SmartReminder, ReminderTrigger
import logging

logger = logging.getLogger(__name__)

class PushNotificationService:
    """
    Service for sending push notifications for smart reminders
    """
    
    def __init__(self):
        self.firebase_server_key = getattr(settings, 'FIREBASE_SERVER_KEY', None)
        self.firebase_url = 'https://fcm.googleapis.com/fcm/send'
        
    def send_reminder_notification(self, reminder, trigger):
        """
        Send push notification for a triggered reminder
        
        Args:
            reminder: SmartReminder instance
            trigger: ReminderTrigger instance
        """
        try:
            # Get user's FCM token from UserProfile
            user = reminder.user
            try:
                profile = user.profile
                fcm_token = profile.fcm_token
                if not profile.push_notifications_enabled:
                    logger.info(f"Push notifications disabled for user {user.username}")
                    return False
            except:
                fcm_token = None
            
            if not fcm_token:
                logger.warning(f"No FCM token found for user {user.username}")
                return False
            
            # Prepare notification payload
            notification_data = {
                'to': fcm_token,
                'notification': {
                    'title': '⏰ Memora Reminder',
                    'body': self._format_reminder_message(reminder, trigger),
                    'icon': 'ic_notification',
                    'sound': 'default',
                    'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                },
                'data': {
                    'type': 'smart_reminder',
                    'reminder_id': str(reminder.id),
                    'memory_id': str(reminder.memory.id),
                    'memory_content': reminder.memory.content[:100],
                    'reminder_type': reminder.reminder_type,
                    'priority': reminder.priority,
                    'trigger_reason': trigger.trigger_reason,
                    'triggered_at': trigger.triggered_at.isoformat(),
                    'actions': self._get_available_actions(reminder)
                },
                'priority': 'high',
                'time_to_live': 3600  # 1 hour
            }
            
            # Send notification
            headers = {
                'Authorization': f'key={self.firebase_server_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                self.firebase_url,
                headers=headers,
                data=json.dumps(notification_data),
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success', 0) > 0:
                    logger.info(f"Push notification sent successfully for reminder {reminder.id}")
                    return True
                else:
                    logger.error(f"Failed to send push notification: {result}")
                    return False
            else:
                logger.error(f"Push notification request failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending push notification: {str(e)}")
            return False
    
    def send_scheduled_memory_notification(self, memory, reminder):
        """
        Send push notification for a scheduled memory
        
        Args:
            memory: Memory instance with delivery_type='scheduled'
            reminder: SmartReminder instance
        """
        try:
            user = memory.user
            try:
                profile = user.profile
                fcm_token = profile.fcm_token
                if not profile.push_notifications_enabled:
                    logger.info(f"Push notifications disabled for user {user.username}")
                    return False
            except:
                fcm_token = None
            
            if not fcm_token:
                logger.warning(f"No FCM token found for user {user.username}")
                return False
            
            # Prepare notification payload for scheduled memory
            notification_data = {
                'to': fcm_token,
                'notification': {
                    'title': '📅 Scheduled Memory',
                    'body': f"Time for: {memory.content[:80]}...",
                    'icon': 'ic_scheduled',
                    'sound': 'default',
                    'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                },
                'data': {
                    'type': 'scheduled_memory',
                    'memory_id': str(memory.id),
                    'reminder_id': str(reminder.id),
                    'memory_content': memory.content[:100],
                    'delivery_date': memory.delivery_date.isoformat() if memory.delivery_date else None,
                    'snooze_count': memory.snooze_count,
                    'can_snooze': memory.snooze_count < 5,
                    'can_decline': not memory.is_completed,
                    'can_mark_done': not memory.is_completed,
                    'actions': ['snooze', 'mark_done', 'decline']
                },
                'priority': 'high',
                'time_to_live': 3600
            }
            
            # Send notification
            headers = {
                'Authorization': f'key={self.firebase_server_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                self.firebase_url,
                headers=headers,
                data=json.dumps(notification_data),
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success', 0) > 0:
                    logger.info(f"Scheduled memory notification sent successfully for memory {memory.id}")
                    return True
                else:
                    logger.error(f"Failed to send scheduled memory notification: {result}")
                    return False
            else:
                logger.error(f"Scheduled memory notification request failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending scheduled memory notification: {str(e)}")
            return False
    
    def _format_reminder_message(self, reminder, trigger):
        """
        Format the reminder message for the notification
        """
        memory_content = reminder.memory.content[:60]
        if len(reminder.memory.content) > 60:
            memory_content += "..."
        
        if trigger.trigger_reason:
            return f"{trigger.trigger_reason}: {memory_content}"
        else:
            return f"Reminder: {memory_content}"
    
    def _get_available_actions(self, reminder):
        """
        Get available actions for the reminder based on its type and state
        """
        actions = ['dismiss']
        
        if reminder.reminder_type == 'time_based':
            actions.append('snooze')
        
        if reminder.memory.delivery_type == 'scheduled':
            actions.extend(['mark_done', 'decline'])
        
        return actions
    
    def send_bulk_notifications(self, reminders_and_triggers):
        """
        Send multiple notifications efficiently
        
        Args:
            reminders_and_triggers: List of tuples (reminder, trigger)
        """
        success_count = 0
        for reminder, trigger in reminders_and_triggers:
            if self.send_reminder_notification(reminder, trigger):
                success_count += 1
        
        logger.info(f"Sent {success_count}/{len(reminders_and_triggers)} push notifications")
        return success_count
    
    def send_test_notification(self, user, message="Test notification from Memora"):
        """
        Send a test notification to verify FCM setup
        """
        try:
            try:
                profile = user.profile
                fcm_token = profile.fcm_token
            except:
                fcm_token = None
            
            if not fcm_token:
                return False, "No FCM token found for user"
            
            notification_data = {
                'to': fcm_token,
                'notification': {
                    'title': '🧪 Test Notification',
                    'body': message,
                    'icon': 'ic_notification',
                    'sound': 'default'
                },
                'data': {
                    'type': 'test',
                    'timestamp': timezone.now().isoformat()
                },
                'priority': 'normal'
            }
            
            headers = {
                'Authorization': f'key={self.firebase_server_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                self.firebase_url,
                headers=headers,
                data=json.dumps(notification_data),
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success', 0) > 0:
                    return True, "Test notification sent successfully"
                else:
                    return False, f"Failed to send test notification: {result}"
            else:
                return False, f"Test notification request failed: {response.status_code}"
                
        except Exception as e:
            return False, f"Error sending test notification: {str(e)}"


# Global instance
push_notification_service = PushNotificationService()
