from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from django import forms

from .models import Posts, CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'username',)

class CreationPosts(forms.ModelForm):
    class Meta:
        model = Posts
        fields = ['title', 'content', 'photo']
    
    widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'content': forms.Textarea(attrs={'cols': 60, 'rows': 10}),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 200:
            raise ValidationError('Длина превышает 200 символов')

        return title


class AdminCreationPosts(CreationPosts): # форма для админа
    class Meta:
        model = Posts
        fields = ['title', 'content', 'photo', 'is_published']

class EditPostsForm(forms.ModelForm):
    class Meta:
        model = Posts
        fields = ['title', 'content', 'photo']


class EditUserInfoForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name',
            'email', 'picture',
        ]