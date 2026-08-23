from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('appointments/', views.upcoming_appointments, name='upcoming_appointments'),
    path('appointments/history/', views.appointment_history, name='appointment_history'),
    path('appointments/<int:booking_id>/review/', views.submit_review, name='submit_review'),
    path('payments/', views.payment_history, name='payment_history'),
    path('profile/', views.profile_view, name='profile'),
    path('security/', views.account_security, name='security'),
    
    # Password Reset URLs
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
