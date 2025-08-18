"""
URL configuration for memora_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from memory_assistant.forms import UserLoginForm
from memory_assistant import views as memory_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('home') if not request.user.is_authenticated else redirect('memory_assistant:dashboard'), name='root'),
    path('home/', memory_views.home, name='home'),
    path('memora/', include('memory_assistant.urls')),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='memory_assistant/login.html', form_class=UserLoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login', http_method_names=['post']), name='logout'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
