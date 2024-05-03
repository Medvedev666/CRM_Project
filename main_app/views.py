from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView
from django.contrib.auth import authenticate, login, logout

from .models import *
from .forms import *
from config.settings import MEDIA_URL

import os

class HomePageView(ListView):
    model = Posts
    template_name = 'index.html'
    context_object_name = 'posts'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] ="TalkTrove"
        return context
    
    def get_queryset(self):
        return Posts.objects.filter(is_published=True)

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('account_login')
    else:
        form = UserCreationForm()
    return render(request, 'account/signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Замените 'home' на имя вашего URL-адреса для переадресации после входа
    else:
        form = AuthenticationForm()
    return render(request, 'account/login.html', {'form': form})

class CustomPasswordResetView(PasswordResetView):
    template_name = 'account/password_reset.html'  # указываем имя вашего HTML-шаблона для смены пароля
    email_template_name = 'account/password_reset_email.html'  # имя HTML-шаблона для отправки письма со ссылкой для смены пароля
    subject_template_name = 'password_reset_subject.txt'  # имя текстового шаблона для темы письма
    success_url = '/password_reset/done/'

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'account/password_reset_done.html'  # ваш шаблон для страницы успешного сброса пароля

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def delete_posts(request, posts_id):
    try:
        posts_instance = get_object_or_404(Posts, id=posts_id)
        if request.user != posts_instance.creater and request.user.is_superuser != True and request.user.is_admin != True:
            return redirect('home')

        posts_instance.delete()
        return redirect('home')
    except Posts.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Пост не найтен'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def public_posts(request, posts_id):
    try:
        posts_instance = get_object_or_404(Posts, id=posts_id)
        if request.user != posts_instance.creater and request.user.is_superuser != True and request.user.is_admin != True:
            return redirect('home')

        posts_instance.is_published = True
        posts_instance.save()
        return redirect('home')
    except Posts.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Пост не найтен'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def check_message(request):
    if request.user.is_superuser or request.user.is_admin:
        title = 'Админ панель'
    else:
        return redirect('home')
    
    new_posts = Posts.objects.filter(is_published=False)
    
    context = {
        'title': title,
        'new_posts': new_posts,
    }
    return render(request, 'check_posts.html', context)

@login_required
def create_posts(request):
    if request.method == 'POST':
        form = CreationPosts(request.POST, request.FILES)
        if form.is_valid():
            creater = form.save(commit=False)
            creater.creater_id = request.user.id  # Установите пользователя
            creater.save()
            form.save()
            return redirect('home')  # Перенаправление на страницу успешного создания
    else:
        form = CreationPosts()

    context = {
        'title': 'Новое сообщение',
        'form': form
    }
    return render(request, 'new_posts.html', context)

@login_required
def edit_post(request, post_id):
    post_instance = get_object_or_404(Posts, id=post_id)
    # проверяем принадлежит ли объявление обратившемуся пользователю
    if request.user != post_instance.creater:
        return redirect('home')

    if request.method == 'POST':
        form = EditPostsForm(request.POST, instance=post_instance)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = EditPostsForm(instance=post_instance)

    context = {
        'title': 'Редактировать сообщение',
        'form': form, 
        'post_instance': post_instance
    }
    return render(request, 'edit_post.html', context)

@login_required
def show_user_profile(request, username):
    if request.user.username == username:
        title = 'Личный кабинет'
    else:
        title = f'Профиль пользователя {username}'
    user_model = CustomUser.objects.get(username=username)
    user_ad = Posts.objects.filter(creater=user_model)
    
    context = {
        'title': title,
        'user_model': user_model,
        'request_user': request.user,
        'user_ad': user_ad,
    }
    return render(request, 'show_user_profile.html', context)

@login_required
def edit_user_profile(request, username):
    user_instance = get_object_or_404(CustomUser, username=username)
    # проверяем принадлежит ли объявление обратившемуся пользователю
    if request.user != user_instance:
        return redirect('user_profile', username=username)

    if request.method == 'POST':
        form = EditUserInfoForm(request.POST, request.FILES, instance=user_instance)
        if form.is_valid():
            form.save()
            return redirect('user_profile', username=username)
    else:
        form = EditUserInfoForm(instance=user_instance)

    context = {
        'title': 'Редактировать профиль',
        'form': form, 
        'user_instance': user_instance
    }
    return render(request, 'edit_user.html', context)

def show_posts(request, pk):
    post = Posts.objects.get(pk=pk)
    context = {
        'title': 'Сообщение',
        'post': post,
    }
    return render(request, 'show_posts.html', context)