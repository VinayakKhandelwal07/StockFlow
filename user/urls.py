from django.urls import path
from dashboard.views import RegisterCompanyAndAdminView

from django.contrib.auth import views as auth_views
from . import views 
from .views import CustomLogoutView , CustomLoginView


app_name = 'user'

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),  # changed name here

    path('login/', CustomLoginView.as_view(template_name='user/login.html'), name='login'),
    path('logout/', CustomLogoutView.as_view(template_name='user/logout.html'), name='logout'),
    path('register/', RegisterCompanyAndAdminView.as_view(), name='register'),

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='user/password_reset.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='user/password_reset_done.html'), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='user/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='user/password_reset_complete.html'), name='password_reset_complete'),
]
