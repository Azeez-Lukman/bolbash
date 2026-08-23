from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.shop_landing, name='shop_landing'),
    path('products/', views.product_catalogue, name='product_catalogue'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:item_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
    path('my-orders/', views.customer_orders, name='customer_orders'),
    path('my-orders/<str:order_number>/', views.customer_order_detail, name='customer_order_detail'),
]
