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

    # регистрация / авторизация
    path('signup/', signup, name='account_signup'),
    path('login/', user_login, name='account_login'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='account_reset_password'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('logout/', user_logout, name='account_logout'),
]