from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os


def memory_image_path(instance, filename):
    """Generate upload path for memory images"""
    # Get file extension
    ext = filename.split('.')[-1]
    # Create new filename with memory id and timestamp
    filename = f"memory_{instance.user.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    return os.path.join('memories', 'images', str(instance.user.id), filename)


class Memory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memories')
    content = models.TextField(help_text="The memory content")
    image = models.ImageField(upload_to=memory_image_path, blank=True, null=True, 
                             help_text="Optional image to attach to this memory")
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
    
    # Delivery and encryption fields
    delivery_date = models.DateTimeField(null=True, blank=True, help_text="When to deliver this memory")
    delivery_type = models.CharField(max_length=50, default='immediate', 
                                   choices=[
                                       ('immediate', 'Immediate'),
                                       ('scheduled', 'Scheduled'),
                                       ('conditional', 'Conditional')
                                   ],
                                   help_text="How this memory should be delivered")
    encrypted_content = models.TextField(default='', help_text="Encrypted version of the content")
    is_delivered = models.BooleanField(default=False, help_text="Whether this memory has been delivered")
    is_time_locked = models.BooleanField(default=False, help_text="Whether this memory is time-locked")
    
    # Privacy and Sharing fields
    privacy_level = models.CharField(
        max_length=20,
        choices=[
            ('private', 'Private - Only me'),
            ('friends', 'Friends Only'),
            ('organization', 'Organization Members'),
            ('public', 'Public')
        ],
        default='private',
        help_text="Who can see this memory"
    )
    allow_comments = models.BooleanField(default=True, help_text="Allow comments on this memory")
    allow_likes = models.BooleanField(default=True, help_text="Allow likes/reactions on this memory")
    shared_count = models.PositiveIntegerField(default=0, help_text="Number of times this memory has been shared")
    

    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Memories"
    
    def __str__(self):
        return f"{self.user.username} - {self.content[:50]}..."
    
    def delete(self, *args, **kwargs):
        # Delete the image file when the memory is deleted
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)
    
    def can_be_viewed_by(self, user):
        """Check if a user can view this memory based on privacy settings"""
        if self.user == user:
            return True
        
        if self.privacy_level == 'private':
            return False
        elif self.privacy_level == 'public':
            return True
        elif self.privacy_level == 'friends':
            return Friendship.are_friends(self.user, user)
        elif self.privacy_level == 'organization':
            # Check if both users are in the same organization
            user_orgs = user.organization_memberships.filter(is_active=True).values_list('organization', flat=True)
            memory_user_orgs = self.user.organization_memberships.filter(is_active=True).values_list('organization', flat=True)
            return bool(set(user_orgs) & set(memory_user_orgs))
        
        return False
    
    def get_likes_count(self):
        """Get total number of likes for this memory"""
        return self.likes.count()
    
    def get_comments_count(self):
        """Get total number of comments for this memory"""
        return self.comments.count()
    
    def is_liked_by(self, user):
        """Check if user has liked this memory"""
        return self.likes.filter(user=user).exists()
    
    def get_user_reaction(self, user):
        """Get user's reaction to this memory"""
        try:
            return self.likes.get(user=user).reaction_type
        except:
            return None
    

    



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


# Social Features Models

class UserProfile(models.Model):
    """Extended user profile for social features"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, help_text="Brief description about yourself")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, help_text="Profile picture")
    location = models.CharField(max_length=100, blank=True, help_text="Your location")
    website = models.URLField(blank=True, help_text="Personal website or social media")
    privacy_level = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('friends', 'Friends Only'),
            ('private', 'Private')
        ],
        default='friends',
        help_text="Default privacy level for memories"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class FriendRequest(models.Model):
    """Friend request model"""
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friend_requests')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friend_requests')
    message = models.TextField(max_length=200, blank=True, help_text="Optional message with request")
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('declined', 'Declined'),
            ('cancelled', 'Cancelled')
        ],
        default='pending'
    )
    created_at = models.DateTimeField(default=timezone.now)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['from_user', 'to_user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username} ({self.status})"


class Friendship(models.Model):
    """Established friendship between users"""
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships_as_user2')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['user1', 'user2']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user1.username} ↔ {self.user2.username}"
    
    @classmethod
    def are_friends(cls, user1, user2):
        """Check if two users are friends"""
        return cls.objects.filter(
            models.Q(user1=user1, user2=user2) | models.Q(user1=user2, user2=user1)
        ).exists()
    
    @classmethod
    def get_user_friends(cls, user):
        """Get all friends of a user"""
        friendships = cls.objects.filter(
            models.Q(user1=user) | models.Q(user2=user)
        )
        friends = []
        for friendship in friendships:
            friend = friendship.user2 if friendship.user1 == user else friendship.user1
            friends.append(friend)
        return friends


class Organization(models.Model):
    """Organization/Company model"""
    name = models.CharField(max_length=100, help_text="Organization name")
    description = models.TextField(max_length=1000, blank=True, help_text="Organization description")
    logo = models.ImageField(upload_to='organization_logos/', blank=True, null=True)
    website = models.URLField(blank=True)
    org_type = models.CharField(
        max_length=20,
        choices=[
            ('company', 'Company'),
            ('team', 'Team'),
            ('project', 'Project'),
            ('community', 'Community'),
            ('family', 'Family'),
            ('other', 'Other')
        ],
        default='company'
    )
    privacy = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public - Anyone can join'),
            ('invite_only', 'Invite Only'),
            ('private', 'Private')
        ],
        default='invite_only'
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_organizations')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class OrganizationMembership(models.Model):
    """Organization membership with roles"""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organization_memberships')
    role = models.CharField(
        max_length=20,
        choices=[
            ('admin', 'Admin'),
            ('moderator', 'Moderator'),
            ('member', 'Member'),
            ('viewer', 'Viewer')
        ],
        default='member'
    )
    joined_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['organization', 'user']
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.user.username} in {self.organization.name} ({self.role})"


class OrganizationInvitation(models.Model):
    """Organization invitation model"""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='invitations')
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_org_invitations')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_org_invitations')
    role = models.CharField(
        max_length=20,
        choices=[
            ('admin', 'Admin'),
            ('moderator', 'Moderator'),
            ('member', 'Member'),
            ('viewer', 'Viewer')
        ],
        default='member'
    )
    message = models.TextField(max_length=200, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('declined', 'Declined'),
            ('cancelled', 'Cancelled')
        ],
        default='pending'
    )
    created_at = models.DateTimeField(default=timezone.now)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['organization', 'to_user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invite to {self.organization.name} for {self.to_user.username}"


class SharedMemory(models.Model):
    """Track memory sharing relationships"""
    memory = models.ForeignKey(Memory, on_delete=models.CASCADE, related_name='shares')
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_memories')
    shared_with_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_shared_memories', null=True, blank=True)
    shared_with_organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='shared_memories', null=True, blank=True)
    share_type = models.CharField(
        max_length=20,
        choices=[
            ('user', 'Shared with User'),
            ('organization', 'Shared with Organization'),
            ('public', 'Public Share')
        ]
    )
    message = models.TextField(max_length=200, blank=True, help_text="Optional message when sharing")
    can_reshare = models.BooleanField(default=False, help_text="Allow recipient to reshare this memory")
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Optional expiration date")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        # Prevent duplicate shares
        constraints = [
            models.UniqueConstraint(
                fields=['memory', 'shared_with_user'],
                condition=models.Q(shared_with_user__isnull=False),
                name='unique_user_share'
            ),
            models.UniqueConstraint(
                fields=['memory', 'shared_with_organization'],
                condition=models.Q(shared_with_organization__isnull=False),
                name='unique_org_share'
            )
        ]
    
    def __str__(self):
        if self.shared_with_user:
            return f"Memory shared with {self.shared_with_user.username}"
        elif self.shared_with_organization:
            return f"Memory shared with {self.shared_with_organization.name}"
        return "Public memory share"
    
    def is_expired(self):
        """Check if the share has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class MemoryComment(models.Model):
    """Comments on shared memories"""
    memory = models.ForeignKey(Memory, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memory_comments')
    content = models.TextField(max_length=500, help_text="Comment content")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.username} commented on memory {self.memory.id}"


class MemoryLike(models.Model):
    """Likes/reactions on shared memories"""
    memory = models.ForeignKey(Memory, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memory_likes')
    reaction_type = models.CharField(
        max_length=20,
        choices=[
            ('like', '👍 Like'),
            ('love', '❤️ Love'),
            ('laugh', '😂 Funny'),
            ('wow', '😮 Wow'),
            ('sad', '😢 Sad'),
            ('angry', '😠 Angry')
        ],
        default='like'
    )
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['memory', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} {self.reaction_type} memory {self.memory.id}"


class Notification(models.Model):
    """Notification system for social interactions"""
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    notification_type = models.CharField(
        max_length=30,
        choices=[
            ('friend_request', 'Friend Request'),
            ('friend_accepted', 'Friend Request Accepted'),
            ('memory_shared', 'Memory Shared'),
            ('memory_comment', 'Memory Comment'),
            ('memory_like', 'Memory Like'),
            ('org_invitation', 'Organization Invitation'),
            ('org_joined', 'Organization Joined'),
            ('org_memory_shared', 'Organization Memory Shared')
        ]
    )
    title = models.CharField(max_length=100)
    message = models.TextField(max_length=300)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, null=True, blank=True)
    action_url = models.CharField(max_length=200, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"
