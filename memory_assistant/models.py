from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Memory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memories')
    content = models.TextField(help_text="The memory content")
    summary = models.TextField(blank=True, help_text="AI-generated summary of the memory")
    ai_reasoning = models.TextField(blank=True, help_text="AI reasoning for categorization")
    tags = models.JSONField(default=list, help_text="AI-generated tags for categorization")
    importance = models.IntegerField(default=5, choices=[(i, i) for i in range(1, 11)], 
                                   help_text="Importance level from 1-10")
    memory_type = models.CharField(max_length=50, default='general', 
                                 choices=[
                                     ('general', 'General'),
                                     ('work', 'Work'),
                                     ('personal', 'Personal'),
                                     ('learning', 'Learning'),
                                     ('idea', 'Idea'),
                                     ('reminder', 'Reminder')
                                 ])
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Memories"
    
    def __str__(self):
        return f"{self.user.username} - {self.content[:50]}..."


class MemorySearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='searches')
    query = models.TextField(help_text="Search query")
    results_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Memory Searches"
    
    def __str__(self):
        return f"{self.user.username} - {self.query[:30]}..."
