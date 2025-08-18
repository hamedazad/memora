"""
AI-Powered Views for Memory Assistant

This module provides AI-enhanced views for the memory assistant app.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

from .models import Memory
from .ai_services import get_ai_service

@login_required
def ai_dashboard(request):
    """AI-powered dashboard with insights and suggestions."""
    try:
        # Force reload environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        ai_service = get_ai_service()
        if not ai_service:
            # Check if API key is available
            import os
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                context = {
                    'error': 'OpenAI API key not found. Please check your .env file.',
                    'ai_enabled': False
                }
                return render(request, 'memory_assistant/ai_dashboard.html', context)
            else:
                context = {
                    'error': 'AI service initialization failed. Please check your API key.',
                    'ai_enabled': False
                }
                return render(request, 'memory_assistant/ai_dashboard.html', context)
        
        # Get user's recent memories
        user_memories = Memory.objects.filter(user=request.user).order_by('-created_at')[:10]
        
        # Get memory statistics (similar to main dashboard)
        from django.db.models import Count, Case, When, IntegerField
        from django.utils import timezone
        now = timezone.now()
        
        all_user_memories = Memory.objects.filter(user=request.user, is_archived=False)
        stats = all_user_memories.aggregate(
            total_memories=Count('id'),
            important_memories=Count(Case(When(importance__gte=8, then=1), output_field=IntegerField())),
            scheduled_memories_count=Count(Case(When(delivery_date__isnull=False, then=1), output_field=IntegerField())),
            today_memories=Count(Case(When(delivery_date__date=now.date(), then=1), output_field=IntegerField()))
        )
        
        # Generate AI insights
        memories_data = [
            {
                'content': memory.content,
                'created_at': memory.created_at.strftime('%Y-%m-%d %H:%M')
            }
            for memory in user_memories
        ]
        
        # Get AI analysis
        analysis = ai_service.analyze_productivity_patterns(memories_data)
        
        # Get memory suggestions
        memory_contents = [m.content for m in user_memories]
        suggestions = ai_service.generate_memory_suggestions(memory_contents)
        
        context = {
            'analysis': analysis,
            'suggestions': suggestions,
            'memory_count': len(user_memories),
            'total_memories': stats['total_memories'],
            'important_memories': stats['important_memories'],
            'scheduled_memories_count': stats['scheduled_memories_count'],
            'todays_memories_count': stats['today_memories'],
            'ai_enabled': True
        }
        
        return render(request, 'memory_assistant/ai_dashboard.html', context)
        
    except Exception as e:
        context = {
            'error': str(e),
            'ai_enabled': False
        }
        return render(request, 'memory_assistant/ai_dashboard.html', context)

@login_required
@require_POST
@csrf_exempt
def ai_enhance_memory(request):
    """AI-powered memory enhancement."""
    try:
        data = json.loads(request.body)
        content = data.get('content', '')
        
        ai_service = get_ai_service()
        if not ai_service:
            return JsonResponse({'error': 'AI service not available'}, status=400)
        
        # Get AI suggestions
        enhancement = ai_service.enhance_memory(content)
        categories = ai_service.auto_categorize(content)
        tags = ai_service.generate_tags(content)
        summary = ai_service.summarize_memory(content)
        
        return JsonResponse({
            'enhancement': enhancement,
            'categories': categories,
            'tags': tags,
            'summary': summary
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_POST
@csrf_exempt
def ai_auto_categorize(request):
    """Auto-categorize memory content."""
    try:
        data = json.loads(request.body)
        content = data.get('content', '')
        
        ai_service = get_ai_service()
        if not ai_service:
            return JsonResponse({'error': 'AI service not available'}, status=400)
        
        categories = ai_service.auto_categorize(content)
        
        return JsonResponse({
            'categories': categories
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_POST
@csrf_exempt
def ai_generate_tags(request):
    """Generate tags for memory content."""
    try:
        data = json.loads(request.body)
        content = data.get('content', '')
        
        ai_service = get_ai_service()
        if not ai_service:
            return JsonResponse({'error': 'AI service not available'}, status=400)
        
        tags = ai_service.generate_tags(content)
        
        return JsonResponse({
            'tags': tags
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def ai_memory_suggestions(request):
    """Get AI-generated memory suggestions."""
    try:
        ai_service = get_ai_service()
        if not ai_service:
            return JsonResponse({'error': 'AI service not available'}, status=400)
        
        # Get user's recent memories
        user_memories = Memory.objects.filter(user=request.user).order_by('-created_at')[:5]
        memory_contents = [memory.content for memory in user_memories]
        
        suggestions = ai_service.generate_memory_suggestions(memory_contents)
        
        return JsonResponse({
            'suggestions': suggestions
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def ai_related_memories(request, memory_id):
    """Find related memories using AI."""
    try:
        ai_service = get_ai_service()
        if not ai_service:
            return JsonResponse({'error': 'AI service not available'}, status=400)
        
        # Get the current memory
        current_memory = Memory.objects.get(id=memory_id, user=request.user)
        
        # Get user's other memories
        other_memories = Memory.objects.filter(user=request.user).exclude(id=memory_id)[:10]
        
        # Find related topics
        related_topics = ai_service.find_related_topics(current_memory.content)
        
        # Find memories with similar topics (simple keyword matching for now)
        related_memories = []
        for memory in other_memories:
            for topic in related_topics:
                if topic.lower() in memory.content.lower():
                    related_memories.append({
                        'id': memory.id,
                        'title': memory.title,
                        'content': memory.content[:100] + '...' if len(memory.content) > 100 else memory.content,
                        'created_at': memory.created_at.strftime('%Y-%m-%d')
                    })
                    break
        
        return JsonResponse({
            'related_topics': related_topics,
            'related_memories': related_memories[:5]  # Limit to 5 related memories
        })
        
    except Memory.DoesNotExist:
        return JsonResponse({'error': 'Memory not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 