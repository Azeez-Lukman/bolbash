from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('', views.booking_form, name='booking_form'),
    path('submit/', views.booking_submit, name='booking_submit'),
    path('lookup/', views.booking_lookup, name='booking_lookup'),
    path('confirmation/<str:reference>/', views.booking_confirmation, name='booking_confirmation'),
    path('api/available-slots/', views.api_available_slots, name='api_available_slots'),
]
