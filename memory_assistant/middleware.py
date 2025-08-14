from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
import pytz


class TimezoneMiddleware(MiddlewareMixin):
    """
    Middleware to set the timezone based on user preference or default.
    """
    
    def process_request(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Check if user has a timezone preference in their profile
            try:
                if hasattr(request.user, 'profile') and request.user.profile.user_timezone:
                    timezone.activate(request.user.profile.user_timezone)
                else:
                    # Use default timezone from settings
                    timezone.activate(timezone.get_default_timezone())
            except (pytz.exceptions.UnknownTimeZoneError, AttributeError):
                # Fallback to default timezone if user's timezone is invalid
                timezone.activate(timezone.get_default_timezone())
        else:
            # For anonymous users, use default timezone
            timezone.activate(timezone.get_default_timezone())
