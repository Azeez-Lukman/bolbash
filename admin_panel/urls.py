from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Appointment Management
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/<str:reference>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<str:reference>/reschedule/', views.appointment_reschedule, name='appointment_reschedule'),
    path('availability/', views.availability_management, name='availability'),
    path('blocked-dates/', views.blocked_dates_management, name='blocked_dates'),

    # Customer Management
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:user_id>/', views.customer_detail, name='customer_detail'),

    # Academy Management
    path('academy/courses/', views.academy_course_list, name='academy_course_list'),
    path('academy/courses/create/', views.academy_course_create, name='academy_course_create'),
    path('academy/courses/<int:course_id>/edit/', views.academy_course_edit, name='academy_course_edit'),
    path('academy/modules/', views.academy_module_list, name='academy_module_list'),
    path('academy/modules/course/<int:course_id>/', views.academy_module_list, name='academy_module_list_by_course'),
    path('academy/lessons/', views.academy_lesson_list, name='academy_lesson_list'),
    path('academy/lessons/module/<int:module_id>/', views.academy_lesson_list, name='academy_lesson_list_by_module'),
    path('academy/students/', views.academy_student_list, name='academy_student_list'),
    path('academy/certificates/', views.academy_certificate_list, name='academy_certificates'),

    # Shop & Inventory Management
    path('shop/products/', views.shop_product_list, name='shop_product_list'),
    path('shop/products/create/', views.shop_product_create, name='shop_product_create'),
    path('shop/products/<int:product_id>/edit/', views.shop_product_edit, name='shop_product_edit'),
    path('shop/inventory/', views.shop_inventory_list, name='shop_inventory'),
    path('shop/orders/', views.shop_order_list, name='shop_order_list'),
    path('shop/orders/<str:order_number>/', views.shop_order_detail, name='shop_order_detail'),

    # Notification Management Dashboard
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:pk>/retry/', views.notification_retry, name='notification_retry'),

    # Customer Enquiry Management Dashboard
    path('enquiries/', views.enquiry_list, name='enquiry_list'),
    path('enquiries/<int:pk>/update-status/', views.enquiry_update_status, name='enquiry_update_status'),

    # Customer Review Moderation Dashboard
    path('reviews/', views.review_list, name='review_list'),
    path('reviews/<int:pk>/update-status/', views.review_update_status, name='review_update_status'),

    # Customer Feedback Resolution Dashboard
    path('feedback/', views.feedback_list, name='feedback_list'),
    path('feedback/<int:pk>/update-status/', views.feedback_update_status, name='feedback_update_status'),
]
