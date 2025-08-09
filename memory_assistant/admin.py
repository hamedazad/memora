from django.contrib import admin
from .models import (
    Memory, MemorySearch, UserProfile, FriendRequest, Friendship,
    Organization, OrganizationMembership, OrganizationInvitation,
    SharedMemory, MemoryComment, MemoryLike, Notification
)


@admin.register(Memory)
class MemoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'content', 'memory_type', 'importance', 'has_image', 'created_at', 'is_archived']
    list_filter = ['memory_type', 'importance', 'is_archived', 'created_at']
    search_fields = ['content', 'summary', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20
    
    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = 'Has Image'


@admin.register(MemorySearch)
class MemorySearchAdmin(admin.ModelAdmin):
    list_display = ['user', 'query', 'results_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['query', 'user__username']
    readonly_fields = ['created_at']
    list_per_page = 20


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'privacy_level', 'location', 'created_at']
    list_filter = ['privacy_level', 'created_at']
    search_fields = ['user__username', 'user__email', 'location']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['from_user__username', 'to_user__username']
    readonly_fields = ['created_at', 'responded_at']


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ['user1', 'user2', 'created_at']
    search_fields = ['user1__username', 'user2__username']
    readonly_fields = ['created_at']


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'org_type', 'privacy', 'created_by', 'member_count', 'created_at']
    list_filter = ['org_type', 'privacy', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def member_count(self, obj):
        return obj.memberships.filter(is_active=True).count()
    member_count.short_description = 'Active Members'


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'role', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active', 'joined_at']
    search_fields = ['user__username', 'organization__name']
    readonly_fields = ['joined_at']


@admin.register(SharedMemory)
class SharedMemoryAdmin(admin.ModelAdmin):
    list_display = ['memory', 'shared_by', 'share_type', 'get_recipient', 'is_active', 'created_at']
    list_filter = ['share_type', 'is_active', 'created_at']
    search_fields = ['memory__content', 'shared_by__username']
    readonly_fields = ['created_at']
    
    def get_recipient(self, obj):
        if obj.shared_with_user:
            return obj.shared_with_user.username
        elif obj.shared_with_organization:
            return obj.shared_with_organization.name
        return "Public"
    get_recipient.short_description = 'Shared With'


@admin.register(MemoryComment)
class MemoryCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'memory', 'content_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'content']
    readonly_fields = ['created_at', 'updated_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Comment'


@admin.register(MemoryLike)
class MemoryLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'memory', 'reaction_type', 'created_at']
    list_filter = ['reaction_type', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['recipient__username', 'title', 'message']
    readonly_fields = ['created_at']



