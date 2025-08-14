from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import (
    Memory, UserProfile, FriendRequest, Organization, 
    OrganizationInvitation, MemoryComment, SharedMemory
)
from .timezone_utils import get_country_choices, get_timezone_for_country


class MemoryForm(forms.ModelForm):
    class Meta:
        model = Memory
        fields = ['content', 'image', 'memory_type', 'importance', 'privacy_level', 'allow_comments', 'allow_likes']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'What would you like to remember?'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'memory_type': forms.Select(attrs={'class': 'form-control'}),
            'importance': forms.Select(attrs={'class': 'form-control'}),
            'privacy_level': forms.Select(attrs={'class': 'form-control'}),
            'allow_comments': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_likes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'content': 'Memory Content',
            'image': 'Image (Optional)',
            'memory_type': 'Type',
            'importance': 'Importance Level',
            'privacy_level': 'Privacy Level',
            'allow_comments': 'Allow Comments',
            'allow_likes': 'Allow Likes/Reactions'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add help text
        self.fields['content'].help_text = 'Describe what you want to remember. Be as detailed as possible for better AI processing and auto-categorization.'
        self.fields['image'].help_text = 'Upload an optional image to attach to this memory. Supported formats: JPG, PNG, GIF.'
        self.fields['memory_type'].help_text = 'Choose the category that best fits this memory. AI will also suggest a category automatically.'
        self.fields['importance'].help_text = 'Rate how important this memory is to you (1-10). AI will also suggest an importance level.'
        self.fields['privacy_level'].help_text = 'Choose who can see this memory. Private is only you, Friends are confirmed friends, Organization members, or Public for everyone.'
        self.fields['allow_comments'].help_text = 'Allow others to comment on this memory when shared.'
        self.fields['allow_likes'].help_text = 'Allow others to like or react to this memory when shared.'
        

    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or len(content.strip()) < 10:
            raise forms.ValidationError('Memory content must be at least 10 characters long.')
        return content.strip()
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Check file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image file size must be under 5MB.')
            
            # Check file type
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            ext = image.name.lower().split('.')[-1]
            if f'.{ext}' not in valid_extensions:
                raise forms.ValidationError('Only JPG, PNG, and GIF images are supported.')
        
        return image
    





class QuickMemoryForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Quick memory...',
            'style': 'resize: none;'
        }),
        label='Quick Memory',
        help_text='Write a quick memory (minimum 10 characters)'
    )
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or len(content.strip()) < 10:
            raise forms.ValidationError('Memory content must be at least 10 characters long.')
        return content.strip()


class SearchForm(forms.Form):
    query = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search your memories...',
            'type': 'search'
        }),
        label='Search',
        help_text='Search by content, tags, or use natural language'
    )
    
    memory_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Memory.memory_type.field.choices,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Filter by Type'
    )
    
    importance = forms.ChoiceField(
        choices=[('', 'All Importance')] + [(str(i), f'{i}+') for i in range(1, 11)],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Minimum Importance'
    ) 


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
    country = forms.ChoiceField(
        choices=get_country_choices(),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'country-select'
        }),
        help_text='Select your country to set your local timezone automatically'
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize password field widgets
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
        

# Social Features Forms

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'location', 'website', 'privacy_level', 'user_timezone']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Tell us about yourself...'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your location'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://your-website.com'
            }),
            'privacy_level': forms.Select(attrs={'class': 'form-control'}),
            'user_timezone': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            if avatar.size > 2 * 1024 * 1024:  # 2MB limit
                raise forms.ValidationError('Avatar file size must be under 2MB.')
        return avatar


class FriendRequestForm(forms.ModelForm):
    class Meta:
        model = FriendRequest
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional message with your friend request...'
            }),
        }


class FindUserForm(forms.Form):
    query = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search for users by username or email...',
            'type': 'search'
        }),
        label='Search Users',
        help_text='Find users to send friend requests'
    )


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'description', 'logo', 'website', 'org_type', 'privacy']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Organization name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your organization...'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://organization-website.com'
            }),
            'org_type': forms.Select(attrs={'class': 'form-control'}),
            'privacy': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo:
            if logo.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError('Logo file size must be under 5MB.')
        return logo


class OrganizationInvitationForm(forms.ModelForm):
    # Add a field to specify the user to invite
    invite_username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username to invite...'
        }),
        help_text='Enter the username of the person you want to invite'
    )
    
    class Meta:
        model = OrganizationInvitation
        fields = ['invite_username', 'role', 'message']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional message with the invitation...'
            }),
        }
        labels = {
            'role': 'Member Role',
            'message': 'Invitation Message'
        }
    
    def clean_invite_username(self):
        username = self.cleaned_data.get('invite_username')
        try:
            user = User.objects.get(username=username)
            return user
        except User.DoesNotExist:
            raise forms.ValidationError(f'User "{username}" does not exist.')


class DirectMemberAddForm(forms.Form):
    """Form for directly adding members to organization (admin only)"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username to add...'
        }),
        help_text='Enter the username of the person to add as a member'
    )
    role = forms.ChoiceField(
        choices=[
            ('admin', 'Admin'),
            ('moderator', 'Moderator'),
            ('member', 'Member'),
            ('viewer', 'Viewer')
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='member'
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        try:
            user = User.objects.get(username=username)
            return user
        except User.DoesNotExist:
            raise forms.ValidationError(f'User "{username}" does not exist.')


class MemoryCommentForm(forms.ModelForm):
    class Meta:
        model = MemoryComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add a comment...'
            }),
        }
        labels = {
            'content': 'Comment'
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or len(content.strip()) < 1:
            raise forms.ValidationError('Comment cannot be empty.')
        return content.strip()


class ShareMemoryForm(forms.Form):
    share_type = forms.ChoiceField(
        choices=[
            ('user', 'Share with Friend'),
            ('organization', 'Share with Organization'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Share With'
    )
    recipient_user = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Select Friend'
    )
    recipient_organization = forms.ModelChoiceField(
        queryset=Organization.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Select Organization'
    )
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional message when sharing...'
        }),
        label='Message'
    )
    can_reshare = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Allow recipient to reshare'
    )
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get user's friends
        from .models import Friendship
        friends = Friendship.get_user_friends(user)
        self.fields['recipient_user'].queryset = User.objects.filter(id__in=[f.id for f in friends])
        
        # Get user's organizations
        user_orgs = user.organization_memberships.filter(is_active=True).values_list('organization', flat=True)
        self.fields['recipient_organization'].queryset = Organization.objects.filter(id__in=user_orgs)
    
    def clean(self):
        cleaned_data = super().clean()
        share_type = cleaned_data.get('share_type')
        recipient_user = cleaned_data.get('recipient_user')
        recipient_organization = cleaned_data.get('recipient_organization')
        
        if share_type == 'user' and not recipient_user:
            raise forms.ValidationError('Please select a friend to share with.')
        elif share_type == 'organization' and not recipient_organization:
            raise forms.ValidationError('Please select an organization to share with.')
        
        return cleaned_data


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize field widgets
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your password'
        }) 