from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse, HttpRequest
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseNotFound
from django.template.loader import render_to_string

from .models import *
from .forms import *
from .utils import DataMixin
from config.settings import MEDIA_URL

import os

TITLE = 'TALKTROVE'

class HomePageView(DataMixin, ListView):
    model = Posts
    template_name = 'index.html'
    context_object_name = 'posts'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cat_selected'] = 0
        context['title'] ="TALKTROVE"
        
        comments_dict = {}
        for post in context['posts']:
            comments_dict[post] = UserComments.objects.filter(post=post).count()

        context['comments_dict'] = comments_dict

        return context
    
    def get_queryset(self):
        return Posts.objects.filter(is_published=True)
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            sort_by = self.request.GET.get('sort_by')
            queryset = self.get_queryset()

            if sort_by == 'date':
                queryset = queryset.order_by('-time_create')
            elif sort_by == 'alpha':
                queryset = queryset.order_by('title')

            comments_dict = {}
            for post in context['posts']:
                comments_dict[post] = UserComments.objects.filter(post=post).count()

            context['comments_dict'] = comments_dict

            render_context = {'posts': queryset, 'comments_dict': comments_dict}
            html = render_to_string('posts_partial.html', render_context)  # Здесь используется отдельный шаблон для постов
            return JsonResponse({'html': html})
        else:
            return super().render_to_response(context, **response_kwargs)
    
    
class PostsCategory(DataMixin, ListView):
    template_name = 'index.html'
    context_object_name = 'posts'
    allow_empty = True

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        if slug:
            return Posts.objects.filter(cat__slug=slug, is_published=True)
        return Posts.objects.none()

    def get_context_data(self, *, object_list=None, **kwargs):
        print(f'{kwargs=}')
        print(f'{self.kwargs=}')
        context = super().get_context_data(**kwargs)
        context['title'] ="TALKTROVE"
        if context['posts']:
            context['title'] = context['title'] + ' - ' + str(context['posts'][0].cat.name)
            print(f"это: {context['posts'][0]}")
            context['cat_selected'] = context['posts'][0].cat.pk
            print(context['cat_selected'])
        else:
            context['title'] = context['title'] + ' - ' + str(Category.objects.get(slug=self.kwargs['slug']).name)
            context['cat_selected'] = Category.objects.get(slug=self.kwargs['slug']).pk
        return context
    

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('account_login')
    else:
        form = UserCreationForm()
    return render(request, 'account/signup.html', {
        'title': TITLE + ' || Войти',
        'form': form,
    })

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

    posts_instance = get_object_or_404(Posts, id=posts_id)
    if request.user != posts_instance.creater and request.user.is_superuser != True and request.user.is_admin != True:
        return redirect('home')

    posts_instance.delete()
    return redirect('home')

@login_required
def public_posts(request, posts_id):

    posts_instance = get_object_or_404(Posts, id=posts_id)
    if request.user != posts_instance.creater and request.user.is_superuser != True and request.user.is_admin != True:
        return redirect('home')

    posts_instance.is_published = True
    posts_instance.save()
    return redirect('home')


@login_required
def check_message(request):
    if request.user.is_superuser or request.user.is_admin:
        title = TITLE + ' || Админ панель'
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
        'title': TITLE + ' || Новое сообщение',
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
        'title': TITLE + ' || Редактировать сообщение',
        'form': form, 
        'post_instance': post_instance
    }
    return render(request, 'edit_post.html', context)

@login_required
def show_user_profile(request, username):
    if request.user.username == username:
        title = TITLE + ' || Личный кабинет'
    else:
        title = TITLE + f' || Профиль пользователя {username}'
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
        'title': TITLE + ' || Редактировать профиль',
        'form': form, 
        'user_instance': user_instance
    }
    return render(request, 'edit_user.html', context)

def show_posts(request, slug):
    post = Posts.objects.get(slug=slug)

    views = post.views.count()
    likes = post.like_set.count()
    like = False
    comments = UserComments.objects.filter(post=post).order_by('-time_create')

    if request.user.is_authenticated:
        if post.like_set.filter(user=request.user).exists():
            like = True

    context = {
        'title': TITLE + ' || Сообщение',
        'post': post,
        'views': views,
        'likes': likes,
        'is_auth': request.user.is_authenticated,
        'user_like': like,
        'user_r': request.user,
        'comments': comments,
    }
    return render(request, 'show_posts.html', context)

@login_required
def grant_admin_privileges(request, username):
    if request.user.is_superuser:
        user = get_object_or_404(CustomUser, username=username)
        user.is_admin = True
        user.save()
        return redirect('home')
    else:
        return redirect('home')

@login_required
def revoke_admin_privileges(request, username):
    if request.user.is_superuser:
        user = get_object_or_404(CustomUser, username=username)
        user.is_admin = False
        user.save()
        return redirect('home')
    else:
        return redirect('home')
    
@login_required
def show_category(request):
    if not (request.user.is_admin or request.user.is_superuser):
        return redirect('home')

    category = Category.objects.all()

    context = {
        'title': TITLE + ' || Все категории',
        'category': category,
    }
    return render(request, 'show_category.html', context)

@login_required
def new_category(request):
    if not (request.user.is_admin or request.user.is_superuser):
        return redirect('home')
    
    if request.method == 'POST':
        form = NewCategory(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('show_category')
    else:
        form = NewCategory()

    context = {
        'title': TITLE + ' || Добавить категорию',
        'form': form, 
    }
    return render(request, 'new_category.html', context)
    
@login_required
def delete_category(request, cat_id):
    if not (request.user.is_admin or request.user.is_superuser):
        return redirect('home')

    category = get_object_or_404(Category, id=cat_id)
    category.delete()

    return redirect('show_category')

@login_required
def make_comments(request, pk):
    if request.method == 'POST':
        form = MakeComments(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.creater_id = request.user.id  # Установите пользователя
            comment.post_id = pk # ид поста
            comment.save()
            form.save()
            return redirect('show_posts', pk=pk)  # Перенаправление на страницу успешного создания
    else:
        form = MakeComments()

    context = {
        'title': TITLE + ' || Оставить комментарий',
        'form': form
    }
    return render(request, 'make_comments.html', context)



class SearchView(ListView):

    template_name = 'search_view.html'
    count = 0
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = TITLE + ' || Результаты поиска'
        context['count'] = self.count or 0
        context['query'] = self.request.GET.get('q')
        return context

    def get_queryset(self):

        from itertools import chain # для объединения нескольких итерируемых объектов

        request = self.request
        query = request.GET.get('q', None)
        
        if query is not None:
            posts_events_results  = Posts.objects.search(query)
            comments_results      = UserComments.objects.search(query)
            category_results = Category.objects.search(query)
            
            # объединяем запросы 
            queryset_chain = chain(
                    posts_events_results,
                    comments_results,
                    category_results,
            )        
            qs = sorted(queryset_chain, 
                        key=lambda instance: instance.pk, 
                        reverse=True)
            self.count = len(qs) 
            return qs
        return Posts.objects.none()