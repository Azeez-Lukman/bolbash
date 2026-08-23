from django.urls import path
from . import views

app_name = 'academy'

urlpatterns = [
    path('', views.academy_landing, name='academy_landing'),
    path('courses/', views.course_list, name='course_list'),
    path('register/', views.student_register, name='register'),
    path('login/', views.student_login, name='login'),
    path('logout/', views.student_logout, name='logout'),
    path('my-learning/', views.my_learning, name='my_learning'),
    path('verify-certificate/', views.verify_certificate, name='verify_certificate'),
    path('verify-certificate/<str:certificate_id>/', views.verify_certificate, name='verify_certificate_detail'),
    path('certificates/<str:certificate_id>/', views.view_certificate, name='view_certificate'),
    path('certificates/<str:certificate_id>/pdf/', views.download_certificate_pdf, name='download_certificate_pdf'),
    path('courses/<slug:slug>/enroll/', views.course_enroll, name='course_enroll'),
    path('courses/<slug:slug>/pay/', views.course_pay_initiate, name='course_pay_initiate'),
    path('courses/<slug:slug>/enrollment-confirmation/', views.enrollment_confirmation, name='enrollment_confirmation'),
    path('courses/<slug:slug>/learn/', views.course_learn, name='course_learn'),
    path('courses/<slug:course_slug>/lessons/<slug:lesson_slug>/', views.lesson_detail, name='lesson_detail'),
    path('lessons/<int:lesson_id>/toggle-complete/', views.lesson_toggle_complete, name='lesson_toggle_complete'),
    path('courses/<slug:slug>/', views.course_detail, name='course_detail'),
    path('<slug:slug>/', views.course_detail, name='course_detail_alias'),
]


