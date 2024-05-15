from django.urls import path
from django.contrib.auth import views as auth_views

from .views import *

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('check_message/', check_message, name='check_message'),
    path('new_message/', create_posts, name='new_message'),
    path('delete_posts/<int:posts_id>/', delete_posts, name='delete_posts'),
    path('public_posts/<int:posts_id>/', public_posts, name='public_posts'),
    path('edit_post/<int:post_id>/', edit_post, name='edit_post'),
    path('user_profile/<str:username>/', show_user_profile, name='user_profile'),
    path('user_profile/edit/<str:username>/', edit_user_profile, name='edit_profile'),
    path('show_post/<slug>/', show_posts, name='show_posts'),
    path('show_post/make_comments/<int:pk>/', make_comments, name='make_comments'),

    # управление категориями
    path('category/<slug>', PostsCategory.as_view(), name='category'),
    path('show_category/', show_category, name='show_category'),
    path('show_category/new_category', new_category, name='new_category'),
    path('category/delete_category/<int:cat_id>', delete_category, name='delete_category'),

    # дать права администратора
    path('grant_admin/<str:username>/', grant_admin_privileges, name='grant_admin'),
    path('revoke_admin/<str:username>/', revoke_admin_privileges, name='revoke_admin'),

    # регистрация / авторизация
    path('signup/', signup, name='account_signup'),
    path('login/', user_login, name='account_login'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='account_reset_password'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('logout/', user_logout, name='account_logout'),

    # поиск
    path('search/', SearchView.as_view(), name='query'), 
]