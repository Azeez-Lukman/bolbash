from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('initiate/<str:booking_reference>/', views.initiate_payment, name='initiate_payment'),
    path('sandbox/<str:payment_reference>/', views.paystack_sandbox_checkout, name='sandbox_checkout'),
    path('verify/', views.verify_payment, name='verify_payment'),
    path('failed/<str:booking_reference>/', views.payment_failed, name='payment_failed'),
    path('webhook/', views.paystack_webhook, name='paystack_webhook'),
]
