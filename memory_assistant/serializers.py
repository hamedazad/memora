from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Memory, UserProfile, SharedMemory, MemoryLike, MemoryComment, SmartReminder, ReminderTrigger


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = ['id']
    
    def get_profile(self, obj):
        try:
            profile = obj.profile
            return {
                'timezone': profile.user_timezone,
                'bio': profile.bio,
                'avatar': profile.avatar.url if profile.avatar else None
            }
        except UserProfile.DoesNotExist:
            return {
                'timezone': 'UTC',
                'bio': '',
                'avatar': None
            }


class MemoryCommentSerializer(serializers.ModelSerializer):
    """Serializer for MemoryComment model"""
    user = UserSerializer(read_only=True)
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    
    class Meta:
        model = MemoryComment
        fields = ['id', 'memory', 'user', 'content', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class MemoryLikeSerializer(serializers.ModelSerializer):
    """Serializer for MemoryLike model"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = MemoryLike
        fields = ['id', 'memory', 'user', 'reaction_type', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class SharedMemorySerializer(serializers.ModelSerializer):
    """Serializer for SharedMemory model"""
    shared_by = UserSerializer(read_only=True)
    shared_with_user = UserSerializer(read_only=True)
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    
    class Meta:
        model = SharedMemory
        fields = ['id', 'memory', 'shared_by', 'shared_with_user', 'message', 'share_type', 'created_at']
        read_only_fields = ['id', 'shared_by', 'created_at']


class MemorySerializer(serializers.ModelSerializer):
    """Serializer for Memory model"""
    user = UserSerializer(read_only=True)
    comments = MemoryCommentSerializer(many=True, read_only=True)
    likes = MemoryLikeSerializer(many=True, read_only=True)
    shares = SharedMemorySerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    delivery_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', allow_null=True)
    
    # Computed fields
    title = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    share_count = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Memory
        fields = [
            'id', 'user', 'title', 'content', 'image', 'image_url', 'summary', 'ai_reasoning',
            'tags', 'importance', 'memory_type', 'created_at', 'updated_at',
            'delivery_date', 'delivery_type', 'is_delivered', 'is_time_locked',
            'privacy_level', 'allow_comments', 'allow_likes', 'shared_count',
            'is_completed', 'completed_at', 'declined_at', 'decline_reason',
            'snooze_count', 'last_snoozed_at', 'language', 'is_archived',
            'comments', 'likes', 'shares', 'comment_count', 'like_count',
            'share_count', 'is_liked_by_user'
        ]
        read_only_fields = [
            'id', 'user', 'created_at', 'updated_at', 'ai_reasoning',
            'shared_count', 'is_delivered', 'snooze_count', 'last_snoozed_at'
        ]
    
    def get_title(self, obj):
        """Extract title from content (first line before double newline)"""
        content = obj.content or ''
        lines = content.split('\n\n')
        if lines:
            title = lines[0].strip()
            return title if title else 'Untitled Memory'
        return 'Untitled Memory'
    
    def get_comment_count(self, obj):
        return obj.comments.count()
    
    def get_like_count(self, obj):
        return obj.likes.count()
    
    def get_share_count(self, obj):
        return obj.shares.filter(is_active=True).count()
    
    def get_is_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def validate_content(self, value):
        """Validate memory content"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Memory content must be at least 10 characters long.")
        return value
    
    def validate_importance(self, value):
        """Validate importance level"""
        if not 1 <= value <= 10:
            raise serializers.ValidationError("Importance must be between 1 and 10.")
        return value


class MemoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating memories"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Memory
        fields = [
            'id', 'user', 'content', 'image', 'summary', 'tags', 'importance',
            'memory_type', 'delivery_date', 'delivery_type', 'privacy_level',
            'allow_comments', 'allow_likes', 'language'
        ]
        read_only_fields = ['id', 'user']
    
    def create(self, validated_data):
        """Create memory with user from request"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate_content(self, value):
        """Validate memory content"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Memory content must be at least 10 characters long.")
        return value
    
    def validate_importance(self, value):
        """Validate importance level"""
        if not 1 <= value <= 10:
            raise serializers.ValidationError("Importance must be between 1 and 10.")
        return value


class MemoryUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating memories"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Memory
        fields = [
            'id', 'user', 'content', 'image', 'summary', 'tags', 'importance',
            'memory_type', 'delivery_date', 'delivery_type', 'privacy_level',
            'allow_comments', 'allow_likes', 'language'
        ]
        read_only_fields = ['id', 'user']
    
    def validate_content(self, value):
        """Validate memory content"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Memory content must be at least 10 characters long.")
        return value
    
    def validate_importance(self, value):
        """Validate importance level"""
        if not 1 <= value <= 10:
            raise serializers.ValidationError("Importance must be between 1 and 10.")
        return value


class SearchSerializer(serializers.Serializer):
    """Serializer for search requests"""
    query = serializers.CharField(max_length=500, required=True)
    mode = serializers.ChoiceField(
        choices=[('fast', 'Fast'), ('semantic', 'Semantic'), ('hybrid', 'Hybrid')],
        default='fast'
    )
    page = serializers.IntegerField(min_value=1, default=1)
    memory_type = serializers.CharField(required=False, allow_blank=True)
    importance_min = serializers.IntegerField(min_value=1, max_value=10, required=False)
    importance_max = serializers.IntegerField(min_value=1, max_value=10, required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    
    def validate(self, data):
        """Validate search parameters"""
        if 'importance_min' in data and 'importance_max' in data:
            if data['importance_min'] > data['importance_max']:
                raise serializers.ValidationError("Minimum importance cannot be greater than maximum importance.")
        
        if 'date_from' in data and 'date_to' in data:
            if data['date_from'] > data['date_to']:
                raise serializers.ValidationError("Start date cannot be after end date.")
        
        return data


class QuickAddSerializer(serializers.Serializer):
    """Serializer for quick add memory"""
    content = serializers.CharField(max_length=10000, required=True)
    fast = serializers.BooleanField(default=True)
    
    def validate_content(self, value):
        """Validate memory content"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Memory content must be at least 10 characters long.")
        return value


class AIEnhanceSerializer(serializers.Serializer):
    """Serializer for AI enhancement requests"""
    content = serializers.CharField(max_length=10000, required=True)
    enhance_type = serializers.ChoiceField(
        choices=[('summary', 'Summary'), ('tags', 'Tags'), ('categorize', 'Categorize'), ('all', 'All')],
        default='all'
    )


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    class Meta:
        model = UserProfile
        fields = ['user_timezone', 'bio', 'avatar']
    
    def validate_user_timezone(self, value):
        """Validate timezone"""
        import pytz
        try:
            pytz.timezone(value)
            return value
        except pytz.exceptions.UnknownTimeZoneError:
            raise serializers.ValidationError("Invalid timezone.")


class ReminderTriggerSerializer(serializers.ModelSerializer):
    """Serializer for ReminderTrigger model"""
    
    class Meta:
        model = ReminderTrigger
        fields = ['id', 'reminder', 'triggered_at', 'trigger_reason', 'was_dismissed', 
                 'was_acted_upon', 'action_taken']
        read_only_fields = ['id', 'triggered_at']


class SmartReminderSerializer(serializers.ModelSerializer):
    """Serializer for SmartReminder model"""
    memory = MemorySerializer(read_only=True)
    user = UserSerializer(read_only=True)
    triggers = ReminderTriggerSerializer(many=True, read_only=True)
    memory_id = serializers.IntegerField(source='memory.id', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    
    class Meta:
        model = SmartReminder
        fields = ['id', 'memory_id', 'user_id', 'memory', 'user', 'reminder_type', 'priority', 
                 'trigger_conditions', 'is_active', 'created_at', 
                 'last_triggered', 'next_trigger', 'triggers']
        read_only_fields = ['id', 'memory_id', 'user_id', 'created_at', 'last_triggered', 'next_trigger']


class SmartReminderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating smart reminders"""
    memory_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = SmartReminder
        fields = ['memory_id', 'reminder_type', 'priority', 'trigger_conditions']
    
    def create(self, validated_data):
        memory_id = validated_data.pop('memory_id')
        user = self.context['request'].user
        
        # Validate memory exists and belongs to user
        try:
            memory = Memory.objects.get(id=memory_id, user=user)
        except Memory.DoesNotExist:
            raise serializers.ValidationError({'memory_id': 'Memory not found or access denied'})
        
        # Check for duplicate reminder
        existing_reminder = SmartReminder.objects.filter(
            memory=memory,
            user=user,
            reminder_type=validated_data.get('reminder_type')
        ).first()
        
        if existing_reminder:
            # Update existing reminder instead of creating duplicate
            existing_reminder.priority = validated_data.get('priority', existing_reminder.priority)
            existing_reminder.trigger_conditions = validated_data.get('trigger_conditions', existing_reminder.trigger_conditions)
            existing_reminder.is_active = True
            existing_reminder.calculate_next_trigger()
            existing_reminder.save()
            return existing_reminder
        
        reminder = SmartReminder.objects.create(
            memory=memory,
            user=user,
            **validated_data
        )
        reminder.calculate_next_trigger()
        reminder.save()
        return reminder


class SmartReminderAnalyzeSerializer(serializers.Serializer):
    """Serializer for analyzing memory for reminders"""
    memory_id = serializers.IntegerField(required=True)
    
    def validate_memory_id(self, value):
        try:
            Memory.objects.get(id=value)
            return value
        except Memory.DoesNotExist:
            raise serializers.ValidationError("Memory not found.")


class SmartReminderStatsSerializer(serializers.Serializer):
    """Serializer for reminder statistics"""
    total_reminders = serializers.IntegerField()
    active_reminders = serializers.IntegerField()
    triggered_today = serializers.IntegerField()
    upcoming_count = serializers.IntegerField()
    by_type = serializers.DictField()
    by_priority = serializers.DictField()
