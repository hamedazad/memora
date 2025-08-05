from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Memory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memories')
    content = models.TextField(help_text="The memory content")
    summary = models.TextField(blank=True, help_text="AI-generated summary of the memory")
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
    
    # Delivery and encryption fields
    delivery_date = models.DateTimeField(null=True, blank=True, help_text="When to deliver this memory")
    delivery_type = models.CharField(max_length=50, default='immediate', 
                                   choices=[
                                       ('immediate', 'Immediate'),
                                       ('scheduled', 'Scheduled'),
                                       ('recurring', 'Recurring'),
                                       ('conditional', 'Conditional')
                                   ],
                                   help_text="How this memory should be delivered")
    encrypted_content = models.TextField(default='', help_text="Encrypted version of the content")
    is_delivered = models.BooleanField(default=False, help_text="Whether this memory has been delivered")
    is_time_locked = models.BooleanField(default=False, help_text="Whether this memory is time-locked")
    
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
