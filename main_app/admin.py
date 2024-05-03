from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import *
from .models import Posts



CustomUser = get_user_model()
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm 
    model = CustomUser
    list_display = [
        'username', 'email', 'is_superuser', 'is_admin', 'is_active'
    ]

class PostsAdmin(admin.ModelAdmin):
    add_form = AdminCreationPosts
    form = AdminCreationPosts
    model = Posts
    list_display = [
        'title', 'content', 'photo', 'is_published', 'creater'
    ]

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Posts, PostsAdmin)