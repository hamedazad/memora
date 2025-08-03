from django.contrib import admin
from .models import Memory, MemorySearch


@admin.register(Memory)
class MemoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_preview', 'memory_type', 'importance', 'created_at', 'is_archived']
    list_filter = ['memory_type', 'importance', 'is_archived', 'created_at']
    search_fields = ['content', 'summary', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['importance', 'is_archived']
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'content', 'memory_type', 'importance')
        }),
        ('AI Analysis', {
            'fields': ('summary', 'tags'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'is_archived'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MemorySearch)
class MemorySearchAdmin(admin.ModelAdmin):
    list_display = ['user', 'query_preview', 'results_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['query', 'user__username']
    readonly_fields = ['created_at']
    
    def query_preview(self, obj):
        return obj.query[:50] + '...' if len(obj.query) > 50 else obj.query
    query_preview.short_description = 'Query'
