from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Memory


class MemoryForm(forms.ModelForm):
    class Meta:
        model = Memory
        fields = ['content', 'memory_type', 'importance']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'What would you like to remember?'
            }),
            'memory_type': forms.Select(attrs={'class': 'form-control'}),
            'importance': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'content': 'Memory Content',
            'memory_type': 'Type',
            'importance': 'Importance Level'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add help text
        self.fields['content'].help_text = 'Describe what you want to remember. Be as detailed as possible for better AI processing and auto-categorization.'
        self.fields['memory_type'].help_text = 'Choose the category that best fits this memory. AI will also suggest a category automatically.'
        self.fields['importance'].help_text = 'Rate how important this memory is to you (1-10). AI will also suggest an importance level.'
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or len(content.strip()) < 10:
            raise forms.ValidationError('Memory content must be at least 10 characters long.')
        return content.strip()


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
        
        # Customize help text
        self.fields['username'].help_text = 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
        self.fields['password1'].help_text = 'Your password must contain at least 8 characters.'
        self.fields['password2'].help_text = 'Enter the same password as before, for verification.'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email


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