from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.root_redirect),
    path('login/', views.custom_login, name='login'),
       path('register/', views.register, name='register'),


    path('logout/', views.logout_view, name='logout'),

    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='password_reset.html',
        extra_context={'no_menu': True}
    ), name='password_reset'),

    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'), name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html'), name='password_reset_confirm'),

    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'), name='password_reset_complete'),

    path('home/', views.home, name='home'),
    path('accounts/', views.account_management, name='account_management'),

    path('staff/', views.staff_management, name='staff_management'),
    path('prices/', views.price_management, name='price_management'),
    path('areas/', views.area_management, name='area_management'),
    path('check-in/', views.vehicle_check_in, name='vehicle_check_in'),
    path('recognize-plate/', views.recognize_license_plate, name='recognize_license_plate'),
    path('available-parking-areas/', views.get_available_parking_areas, name='get_available_parking_areas'),
    path('check-out/', views.check_out, name='check_out'),
    
]
