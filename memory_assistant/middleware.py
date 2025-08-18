from django.utils import timezone
from .models import UserProfile


class TimezoneMiddleware:
    """Middleware to set user's timezone preference."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                # Get user's timezone preference
                profile = UserProfile.objects.get(user=request.user)
                if profile.user_timezone:
                    timezone.activate(profile.user_timezone)
            except UserProfile.DoesNotExist:
                pass
        
        response = self.get_response(request)
        return response



