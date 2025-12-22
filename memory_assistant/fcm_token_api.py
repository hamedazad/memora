#!/usr/bin/env python
"""
FCM Token Management API for Flutter app
Handles FCM token registration and management
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_fcm_token(request):
    """
    Register or update FCM token for push notifications
    
    Expected payload:
    {
        "fcm_token": "firebase_cloud_messaging_token_here",
        "device_type": "android",  # android, ios, web
        "push_notifications_enabled": true
    }
    """
    try:
        fcm_token = request.data.get('fcm_token')
        device_type = request.data.get('device_type', 'android')
        push_notifications_enabled = request.data.get('push_notifications_enabled', True)
        
        if not fcm_token:
            return Response(
                {'error': 'FCM token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'fcm_token': fcm_token,
                'device_type': device_type,
                'push_notifications_enabled': push_notifications_enabled,
                'last_notification_sent': None
            }
        )
        
        if not created:
            # Update existing profile
            profile.fcm_token = fcm_token
            profile.device_type = device_type
            profile.push_notifications_enabled = push_notifications_enabled
            profile.updated_at = timezone.now()
            profile.save()
        
        logger.info(f"FCM token registered for user {request.user.username}")
        
        return Response({
            'success': True,
            'message': 'FCM token registered successfully',
            'device_type': device_type,
            'push_notifications_enabled': push_notifications_enabled,
            'created': created
        })
        
    except Exception as e:
        logger.error(f"Error registering FCM token: {str(e)}")
        return Response(
            {'error': f'Failed to register FCM token: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_notification_settings(request):
    """
    Update push notification settings
    
    Expected payload:
    {
        "push_notifications_enabled": true
    }
    """
    try:
        push_notifications_enabled = request.data.get('push_notifications_enabled')
        
        if push_notifications_enabled is None:
            return Response(
                {'error': 'push_notifications_enabled is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'push_notifications_enabled': push_notifications_enabled
            }
        )
        
        if not created:
            profile.push_notifications_enabled = push_notifications_enabled
            profile.updated_at = timezone.now()
            profile.save()
        
        return Response({
            'success': True,
            'message': 'Notification settings updated successfully',
            'push_notifications_enabled': push_notifications_enabled
        })
        
    except Exception as e:
        logger.error(f"Error updating notification settings: {str(e)}")
        return Response(
            {'error': f'Failed to update notification settings: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notification_settings(request):
    """
    Get current notification settings for the user
    """
    try:
        try:
            profile = request.user.profile
            return Response({
                'fcm_token_registered': bool(profile.fcm_token),
                'device_type': profile.device_type,
                'push_notifications_enabled': profile.push_notifications_enabled,
                'last_notification_sent': profile.last_notification_sent.isoformat() if profile.last_notification_sent else None,
                'created_at': profile.created_at.isoformat(),
                'updated_at': profile.updated_at.isoformat()
            })
        except UserProfile.DoesNotExist:
            return Response({
                'fcm_token_registered': False,
                'device_type': 'android',
                'push_notifications_enabled': True,
                'last_notification_sent': None,
                'created_at': None,
                'updated_at': None
            })
        
    except Exception as e:
        logger.error(f"Error getting notification settings: {str(e)}")
        return Response(
            {'error': f'Failed to get notification settings: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_notification(request):
    """
    Send a test notification to verify FCM setup
    """
    try:
        from .push_notification_service import push_notification_service
        
        message = request.data.get('message', 'Test notification from Memora')
        success, result_message = push_notification_service.send_test_notification(request.user, message)
        
        if success:
            return Response({
                'success': True,
                'message': result_message
            })
        else:
            return Response(
                {'error': result_message},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    except Exception as e:
        logger.error(f"Error sending test notification: {str(e)}")
        return Response(
            {'error': f'Failed to send test notification: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )











































