import os
import sys
import django
from datetime import date, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.management import call_command
from booking.models import Booking, ServiceCategory, Service
from academy.models import CourseCategory, Course, Module, Lesson, LessonProgress, Enrollment, Certificate, StudentProfile
from shop.models import ProductCategory, Product, Order, OrderItem
from payments.models import Payment
from notifications.models import NotificationLog
from notifications.services import NotificationDispatcher, EmailChannelService, WhatsAppChannelService


def test_notifications_and_automation():
    print("=== STARTING PHASE 8 NOTIFICATIONS & AUTOMATION TEST SUITE ===")
    client = Client()

    # Setup Staff Admin
    admin_user, _ = User.objects.get_or_create(username="notif_admin", email="notif_admin@test.com")
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.set_password("AdminPass123!")
    admin_user.save()
    client.force_login(admin_user)

    # Clean previous test objects for deterministic runs
    Booking.objects.filter(customer_email="notif_cust@test.com").delete()
    User.objects.filter(username="notif_student").delete()
    Order.objects.filter(customer_email="notif_shopper@test.com").delete()
    NotificationLog.objects.filter(recipient_email__in=["notif_cust@test.com", "notif_student@test.com", "notif_shopper@test.com"]).delete()

    # Setup base business records
    cat, _ = ServiceCategory.objects.get_or_create(name="Notif Category", slug="notif-cat")
    service, _ = Service.objects.get_or_create(category=cat, name="Notif Styling", slug="notif-styling", price=15000, duration=60)

    # 1. TEST BOOKING CONFIRMATION NOTIFICATION (Email + WhatsApp)
    print("\n--- 1. Testing Booking Confirmation Notification ---")
    booking = Booking.objects.create(
        service=service,
        service_name_snapshot=service.name,
        service_price_snapshot=service.price,
        customer_name="Notif Customer",
        customer_email="notif_cust@test.com",
        customer_phone="08012345678",
        appointment_date=date.today() + timedelta(days=1),
        appointment_time="10:00:00",
        amount_due=15000,
        status=Booking.STATUS_CONFIRMED,
        payment_status=Booking.PAYMENT_PAID
    )

    res1 = NotificationDispatcher.send_booking_confirmation(booking)
    assert res1.get('email') == True, "Email dispatch failed for booking confirmation"
    assert res1.get('whatsapp') == True, "WhatsApp dispatch failed for booking confirmation"

    log_count = NotificationLog.objects.filter(booking=booking, notification_type=NotificationLog.TYPE_BOOKING_CONFIRMATION).count()
    assert log_count == 2, f"Expected 2 logs (Email + WhatsApp), got {log_count}"
    print("[OK] Booking confirmation dispatched successfully to Email & WhatsApp.")

    # 2. TEST APPOINTMENT REMINDER MANAGEMENT COMMAND & IDEMPOTENCY
    print("\n--- 2. Testing 24h Appointment Reminder Command & Idempotency ---")
    call_command('send_appointment_reminders', days=1)

    reminder_logs = NotificationLog.objects.filter(booking=booking, notification_type=NotificationLog.TYPE_APPOINTMENT_REMINDER)
    assert reminder_logs.filter(channel=NotificationLog.CHANNEL_EMAIL, status=NotificationLog.STATUS_SENT).exists(), "Reminder email missing"
    assert reminder_logs.filter(channel=NotificationLog.CHANNEL_WHATSAPP, status=NotificationLog.STATUS_SENT).exists(), "Reminder WhatsApp missing"
    print("[OK] 24h appointment reminder dispatched successfully via command.")

    # Idempotency test: Re-running command should NOT duplicate logs
    call_command('send_appointment_reminders', days=1)
    reminder_count = NotificationLog.objects.filter(booking=booking, notification_type=NotificationLog.TYPE_APPOINTMENT_REMINDER).count()
    assert reminder_count == 2, f"Idempotency failed! Expected 2 reminder logs, got {reminder_count}"
    print("[OK] Duplicate reminder prevention (idempotency) verified.")

    # 3. TEST CANCELLATION NOTIFICATION
    print("\n--- 3. Testing Appointment Cancellation Notification ---")
    res_cancel = client.post(reverse('admin_panel:appointment_detail', kwargs={'reference': booking.reference}), {
        'status': Booking.STATUS_CANCELLED,
        'payment_status': Booking.PAYMENT_PAID,
        'customer_note': 'Cancelled due to emergency'
    })
    assert res_cancel.status_code == 302

    cancel_logs = NotificationLog.objects.filter(booking=booking, notification_type=NotificationLog.TYPE_APPOINTMENT_CANCELLATION)
    assert cancel_logs.filter(status=NotificationLog.STATUS_SENT).count() >= 1, "Cancellation notification missing"
    print("[OK] Appointment cancellation notification dispatched successfully.")

    # 4. TEST RESCHEDULING NOTIFICATION
    print("\n--- 4. Testing Appointment Rescheduling Notification ---")
    new_booking = Booking.objects.create(
        service=service,
        service_name_snapshot=service.name,
        service_price_snapshot=service.price,
        customer_name="Notif Reschedule Cust",
        customer_email="notif_cust@test.com",
        customer_phone="08012345678",
        appointment_date=date.today() + timedelta(days=2),
        appointment_time="14:00:00",
        amount_due=15000,
        status=Booking.STATUS_CONFIRMED,
        payment_status=Booking.PAYMENT_PAID
    )
    new_target_date = date.today() + timedelta(days=5)
    res_resched = client.post(reverse('admin_panel:appointment_reschedule', kwargs={'reference': new_booking.reference}), {
        'appointment_date': new_target_date.isoformat(),
        'appointment_time': '16:00:00'
    })
    assert res_resched.status_code == 302

    resched_logs = NotificationLog.objects.filter(booking=new_booking, notification_type=NotificationLog.TYPE_APPOINTMENT_RESCHEDULED)
    assert resched_logs.filter(status=NotificationLog.STATUS_SENT).count() >= 1, "Rescheduling notification missing"
    print("[OK] Appointment rescheduling notification dispatched successfully.")

    # 5. TEST ACADEMY ENROLMENT NOTIFICATION
    print("\n--- 5. Testing Academy Enrolment Notification ---")
    ac_user = User.objects.create_user(username="notif_student", email="notif_student@test.com", password="StudentPass123!")
    StudentProfile.objects.create(user=ac_user, phone_number="08088887777")
    ac_cat, _ = CourseCategory.objects.get_or_create(name="Notif Academy", slug="notif-academy")
    course, _ = Course.objects.get_or_create(category=ac_cat, title="Notif Masterclass", slug="notif-masterclass", price=25000)

    enrollment = Enrollment.objects.create(user=ac_user, course=course, enrollment_status=Enrollment.STATUS_ACTIVE, payment_status=Enrollment.PAYMENT_PAID)

    res_enr = NotificationDispatcher.send_academy_enrolment(enrollment, student_phone="08088887777")
    assert res_enr.get('email') == True
    assert res_enr.get('whatsapp') == True

    enr_logs = NotificationLog.objects.filter(enrollment=enrollment, notification_type=NotificationLog.TYPE_ACADEMY_ENROLMENT)
    assert enr_logs.count() == 2
    print("[OK] Academy enrolment notification dispatched successfully.")

    # 6. TEST COURSE COMPLETION NOTIFICATION
    print("\n--- 6. Testing Course Completion Notification ---")
    Module.objects.filter(course=course).delete()
    mod = Module.objects.create(course=course, title="Module 1", order=1)
    les = Lesson.objects.create(module=mod, title="Lesson 1", content="Text", order=1)
    LessonProgress.objects.create(user=ac_user, lesson=les, completed=True)

    # Server-side completion check triggers Certificate generation and notification
    enrollment.check_and_update_completion()

    cert = Certificate.objects.filter(enrollment=enrollment).first()
    assert cert is not None, "Certificate not created for completed enrollment"

    cert_logs = NotificationLog.objects.filter(certificate=cert, notification_type=NotificationLog.TYPE_COURSE_COMPLETION)
    assert cert_logs.filter(status=NotificationLog.STATUS_SENT).count() >= 1, "Course completion notification missing"
    print("[OK] Course completion notification dispatched successfully upon 100% completion.")

    # 7. TEST SHOP ORDER CONFIRMATION NOTIFICATION
    print("\n--- 7. Testing Shop Order Confirmation Notification ---")
    sh_cat, _ = ProductCategory.objects.get_or_create(name="Notif Shop", slug="notif-shop")
    product, _ = Product.objects.get_or_create(category=sh_cat, name="Notif Cream", slug="notif-cream", price=8000, stock_quantity=10)

    order = Order.objects.create(
        order_number="ORD-NOTIF-9999",
        customer_name="Notif Shopper",
        customer_email="notif_shopper@test.com",
        customer_phone="08099990000",
        shipping_address="123 Notif Street, Ibadan",
        subtotal=8000,
        delivery_fee=2000,
        total_amount=10000,
        order_status=Order.STATUS_PROCESSING,
        payment_status=Order.PAYMENT_PAID
    )
    OrderItem.objects.create(order=order, product=product, product_name_snapshot=product.name, product_price_snapshot=product.price, quantity=1, subtotal=8000)

    res_order = NotificationDispatcher.send_order_confirmation(order)
    assert res_order.get('email') == True
    assert res_order.get('whatsapp') == True

    order_logs = NotificationLog.objects.filter(order=order, notification_type=NotificationLog.TYPE_ORDER_CONFIRMATION)
    assert order_logs.count() == 2
    print("[OK] Shop order confirmation notification dispatched successfully.")

    # 8. TEST FAULT TOLERANCE (SMTP / API Failure Isolation)
    print("\n--- 8. Testing Fault Tolerance & Non-Blocking Exception Safety ---")
    # Simulate email failure with invalid recipient/SMTP
    fail_res = EmailChannelService.send_email(None, "Subject", "booking_confirmed", {})
    assert fail_res[0] == False
    print("[OK] Email failure caught safely without throwing exception.")

    # 9. TEST ADMIN NOTIFICATION LOG AUDIT DASHBOARD & RETRY ACTION
    print("\n--- 9. Testing Admin Notification Audit Log & Retry ---")
    res_log_view = client.get(reverse('admin_panel:notification_list'))
    assert res_log_view.status_code == 200
    assert b"Notification Audit Log" in res_log_view.content

    # Create a failed log entry and test retry action
    failed_log = NotificationLog.objects.create(
        channel=NotificationLog.CHANNEL_EMAIL,
        notification_type=NotificationLog.TYPE_BOOKING_CONFIRMATION,
        recipient="notif_cust@test.com",
        recipient_email="notif_cust@test.com",
        booking=booking,
        subject_or_summary="Test Failed Log",
        status=NotificationLog.STATUS_FAILED,
        error_message="Simulated Connection Timeout"
    )

    res_retry = client.get(reverse('admin_panel:notification_retry', kwargs={'pk': failed_log.pk}))
    assert res_retry.status_code == 302

    failed_log.refresh_from_db()
    assert failed_log.status == NotificationLog.STATUS_SENT, "Retry action failed to update status to SENT"
    print("[OK] Admin notification audit log viewer and manual retry action verified.")

    # 10. SYSTEM CHECK
    print("\n--- 10. Testing Django System Check ---")
    call_command('check')
    print("[OK] Django System Check identified 0 issues.")

    print("\n=== ALL PHASE 8 NOTIFICATIONS & AUTOMATION TESTS PASSED SUCCESSFULLY! ===")


if __name__ == "__main__":
    test_notifications_and_automation()
