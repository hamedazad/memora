"""
Enhanced Error Handler

Provides user-friendly error messages with actionable steps.
"""

from typing import Dict, Any, Optional
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class ErrorHandler:
    """
    Centralized error handling with user-friendly messages
    """
    
    # Error codes and messages
    ERROR_MESSAGES = {
        # Authentication errors
        'AUTH_001': {
            'message': 'Invalid credentials',
            'user_message': 'Username or password is incorrect',
            'actionable_steps': [
                'Check your username and password',
                'Make sure Caps Lock is off',
                'Try resetting your password if you forgot it'
            ],
            'retry_possible': True
        },
        'AUTH_002': {
            'message': 'Token expired',
            'user_message': 'Your session has expired',
            'actionable_steps': [
                'Please log in again',
                'Enable "Remember me" to stay logged in longer'
            ],
            'retry_possible': False
        },
        'AUTH_003': {
            'message': 'Token invalid',
            'user_message': 'Your session is invalid',
            'actionable_steps': [
                'Please log out and log in again',
                'Clear app data if problem persists'
            ],
            'retry_possible': False
        },
        
        # Network errors
        'NET_001': {
            'message': 'Connection timeout',
            'user_message': 'Could not connect to server',
            'actionable_steps': [
                'Check your internet connection',
                'Try again in a moment',
                'Check if server is running (for developers)'
            ],
            'retry_possible': True
        },
        'NET_002': {
            'message': 'Connection error',
            'user_message': 'Network error occurred',
            'actionable_steps': [
                'Check your internet connection',
                'Switch between WiFi and mobile data',
                'Try again when connection is stable'
            ],
            'retry_possible': True
        },
        'NET_003': {
            'message': 'Server unavailable',
            'user_message': 'Server is temporarily unavailable',
            'actionable_steps': [
                'Try again in a few minutes',
                'Server may be undergoing maintenance',
                'Check status page (if available)'
            ],
            'retry_possible': True
        },
        
        # Validation errors
        'VAL_001': {
            'message': 'Missing required field',
            'user_message': 'Please fill in all required fields',
            'actionable_steps': [
                'Check for fields marked with *',
                'Ensure all required information is provided'
            ],
            'retry_possible': True
        },
        'VAL_002': {
            'message': 'Invalid data format',
            'user_message': 'Some information is not in the correct format',
            'actionable_steps': [
                'Check date formats (YYYY-MM-DD)',
                'Check number fields contain only numbers',
                'Review error details below'
            ],
            'retry_possible': True
        },
        'VAL_003': {
            'message': 'File too large',
            'user_message': 'File size exceeds maximum allowed',
            'actionable_steps': [
                'Choose a smaller file',
                'Compress the image before uploading',
                'Maximum size: 10MB'
            ],
            'retry_possible': True
        },
        
        # AI errors
        'AI_001': {
            'message': 'AI service unavailable',
            'user_message': 'AI features are temporarily unavailable',
            'actionable_steps': [
                'Using basic functionality instead',
                'AI features will be restored automatically',
                'Your request will still complete successfully'
            ],
            'retry_possible': True
        },
        'AI_002': {
            'message': 'AI quota exceeded',
            'user_message': 'Daily AI usage limit reached',
            'actionable_steps': [
                'Limit resets at midnight',
                'Basic functionality still available',
                'Consider upgrading plan for more AI usage'
            ],
            'retry_possible': False
        },
        
        # Database errors
        'DB_001': {
            'message': 'Database error',
            'user_message': 'Could not save data',
            'actionable_steps': [
                'Try again in a moment',
                'Contact support if problem persists',
                'Your data may not have been saved'
            ],
            'retry_possible': True
        },
        'DB_002': {
            'message': 'Duplicate entry',
            'user_message': 'This item already exists',
            'actionable_steps': [
                'Check if you already created this',
                'Try updating the existing item instead',
                'Use a different name or identifier'
            ],
            'retry_possible': False
        },
        
        # Permission errors
        'PERM_001': {
            'message': 'Permission denied',
            'user_message': 'You don\'t have permission for this action',
            'actionable_steps': [
                'Make sure you\'re logged in',
                'Check if you own this resource',
                'Contact owner for access'
            ],
            'retry_possible': False
        },
        
        # Resource errors
        'RES_001': {
            'message': 'Resource not found',
            'user_message': 'The requested item was not found',
            'actionable_steps': [
                'Check if the item was deleted',
                'Refresh the page',
                'Go back and try again'
            ],
            'retry_possible': False
        },
    }
    
    @classmethod
    def get_error_response(
        cls,
        error_code: str,
        details: Optional[str] = None,
        field: Optional[str] = None,
        http_status: int = status.HTTP_400_BAD_REQUEST
    ) -> Response:
        """
        Get formatted error response with user-friendly message
        
        Args:
            error_code: Error code (e.g., 'AUTH_001')
            details: Additional error details
            field: Field name if validation error
            http_status: HTTP status code
            
        Returns:
            DRF Response object
        """
        error_info = cls.ERROR_MESSAGES.get(error_code, {
            'message': 'Unknown error',
            'user_message': 'An unexpected error occurred',
            'actionable_steps': ['Try again', 'Contact support if problem persists'],
            'retry_possible': True
        })
        
        response_data = {
            'error': True,
            'error_code': error_code,
            'message': error_info['user_message'],
            'actionable_steps': error_info['actionable_steps'],
            'retry_possible': error_info['retry_possible'],
        }
        
        if details:
            response_data['details'] = details
        
        if field:
            response_data['field'] = field
        
        # Log error
        logger.error(f"Error {error_code}: {error_info['message']}" + 
                    (f" - {details}" if details else ""))
        
        return Response(response_data, status=http_status)
    
    @classmethod
    def get_validation_error_response(cls, serializer_errors: Dict) -> Response:
        """
        Convert DRF serializer errors to user-friendly format
        
        Args:
            serializer_errors: Django REST Framework serializer.errors
            
        Returns:
            DRF Response with friendly error messages
        """
        # Extract first error for main message
        first_field = list(serializer_errors.keys())[0]
        first_error = serializer_errors[first_field]
        
        if isinstance(first_error, list):
            first_error = first_error[0]
        
        # Convert field errors to actionable messages
        field_errors = []
        for field, errors in serializer_errors.items():
            if isinstance(errors, list):
                for error in errors:
                    field_errors.append({
                        'field': field,
                        'message': str(error)
                    })
            else:
                field_errors.append({
                    'field': field,
                    'message': str(errors)
                })
        
        return Response({
            'error': True,
            'error_code': 'VAL_001',
            'message': 'Please check your input and try again',
            'field_errors': field_errors,
            'actionable_steps': [
                'Review the fields highlighted below',
                'Correct any invalid values',
                'Try submitting again'
            ],
            'retry_possible': True
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @classmethod
    def handle_exception(cls, exception: Exception, context: Optional[str] = None) -> Response:
        """
        Handle generic exceptions with appropriate error response
        
        Args:
            exception: The exception that occurred
            context: Context where error occurred (e.g., 'create_memory')
            
        Returns:
            DRF Response with error details
        """
        error_type = type(exception).__name__
        error_message = str(exception)
        
        # Log the full exception
        logger.exception(f"Exception in {context}: {error_type} - {error_message}")
        
        # Determine appropriate error code and message
        if 'connection' in error_message.lower():
            return cls.get_error_response('NET_002', details=error_message)
        elif 'timeout' in error_message.lower():
            return cls.get_error_response('NET_001', details=error_message)
        elif 'permission' in error_message.lower():
            return cls.get_error_response('PERM_001', details=error_message)
        elif 'not found' in error_message.lower():
            return cls.get_error_response('RES_001', details=error_message)
        else:
            # Generic error
            return Response({
                'error': True,
                'error_code': 'SYS_001',
                'message': 'An unexpected error occurred',
                'actionable_steps': [
                    'Try again in a moment',
                    'Contact support if problem persists',
                    f'Error type: {error_type}'
                ],
                'retry_possible': True,
                'details': error_message if context else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




























