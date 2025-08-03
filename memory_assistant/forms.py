from django import forms
from .models import Memory


class MemoryForm(forms.ModelForm):
    class Meta:
        model = Memory
        fields = ['content', 'memory_type', 'importance']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Write your memory here...',
                'style': 'resize: vertical;'
            }),
            'memory_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'importance': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'content': 'Memory Content',
            'memory_type': 'Type',
            'importance': 'Importance Level'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add help text
        self.fields['content'].help_text = 'Describe what you want to remember. Be as detailed as possible for better AI processing.'
        self.fields['memory_type'].help_text = 'Choose the category that best fits this memory.'
        self.fields['importance'].help_text = 'Rate how important this memory is to you (1-10).'
    
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