import os
import sys
import django
from io import StringIO

# Setup Django environment
sys.path.insert(0, r'c:\Users\USER\Documents\bolbash-beautyspot')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.management import call_command
import datetime

from booking.models import ServiceCategory, Service, Booking
from notifications.models import NotificationLog
from notifications.services import NotificationDispatcher


def run_tests():
    print("==================================================")
    print("STARTING TEST SUITE FOR PHASE 9 — POST-APPOINTMENT REVIEW REQUEST")
    print("==================================================")

    client = Client()
    admin_email = "req_admin@example.com"
    client_email = "req_client@example.com"

    # Cleanup test data
    User.objects.filter(email__in=[admin_email, client_email]).delete()

    admin_user = User.objects.create_superuser(
        username=admin_email,
        email=admin_email,
        password="AdminPassword123!",
        first_name="Req",
        last_name="Admin"
    )

    cat = ServiceCategory.objects.first() or ServiceCategory.objects.create(name="Req Category")
    svc = Service.objects.filter(active=True).first()
    if not svc:
        svc = Service.objects.create(
            name="Bridal Styling Session",
            slug="bridal-styling-session",
            category=cat,
            short_description="Short desc",
            description="Full desc",
            price=50000.00,
            active=True
        )

    b1 = Booking.objects.create(
        service=svc,
        customer_name="Review Request Client",
        customer_phone="08022223333",
        customer_email=client_email,
        appointment_date=timezone.now().date() - datetime.timedelta(days=1),
        appointment_time=datetime.time(11, 0),
        service_name_snapshot=svc.name,
        service_price_snapshot=svc.price,
        status=Booking.STATUS_COMPLETED
    )

    # 1. Dispatcher Review Request & Log Creation
    res = NotificationDispatcher.send_post_appointment_review_request(b1)
    assert res.get('email') or res.get('whatsapp'), "Dispatcher output should report sent channels"

    logs = NotificationLog.objects.filter(booking=b1, notification_type=NotificationLog.TYPE_POST_APPOINTMENT_REVIEW)
    assert logs.exists(), "NotificationLog record for POST_APPOINTMENT_REVIEW must exist"
    assert logs.filter(channel=NotificationLog.CHANNEL_EMAIL).exists(), "Email notification log entry missing"
    assert logs.filter(channel=NotificationLog.CHANNEL_WHATSAPP).exists(), "WhatsApp notification log entry missing"
    print("Step 1: NotificationDispatcher post-appointment review request & multi-channel logging verified.")

    # 2. Idempotency Check
    initial_log_count = logs.count()
    idempotent_res = NotificationDispatcher.send_post_appointment_review_request(b1)
    new_log_count = NotificationLog.objects.filter(booking=b1, notification_type=NotificationLog.TYPE_POST_APPOINTMENT_REVIEW).count()
    assert new_log_count == initial_log_count, "Duplicate review request notification logs MUST NOT be created"
    print("Step 2: Review request idempotency protection verified.")

    # 3. Staff Booking Status Change Trigger
    b2 = Booking.objects.create(
        service=svc,
        customer_name="Staff Status Client",
        customer_phone="08033334444",
        customer_email="status_client@example.com",
        appointment_date=timezone.now().date(),
        appointment_time=datetime.time(14, 0),
        service_name_snapshot=svc.name,
        service_price_snapshot=svc.price,
        status=Booking.STATUS_CONFIRMED
    )

    client.login(username=admin_email, password="AdminPassword123!")
    response = client.post(reverse('admin_panel:appointment_detail', kwargs={'reference': b2.reference}), {
        'status': Booking.STATUS_COMPLETED,
        'payment_status': b2.payment_status,
        'customer_note': '',
    })
    assert response.status_code in [200, 302], "Status update POST failed"
    b2.refresh_from_db()
    assert b2.status == Booking.STATUS_COMPLETED, "Booking status should be updated to COMPLETED"

    b2_logs = NotificationLog.objects.filter(booking=b2, notification_type=NotificationLog.TYPE_POST_APPOINTMENT_REVIEW)
    assert b2_logs.exists(), "Staff marking booking COMPLETED must automatically trigger review request notification"
    print("Step 3: Staff status update trigger for review request verified.")

    # 4. Management Command Test
    b3 = Booking.objects.create(
        service=svc,
        customer_name="Cmd Client",
        customer_phone="08044445555",
        customer_email="cmd_client@example.com",
        appointment_date=timezone.now().date() - datetime.timedelta(days=2),
        appointment_time=datetime.time(15, 0),
        service_name_snapshot=svc.name,
        service_price_snapshot=svc.price,
        status=Booking.STATUS_COMPLETED
    )

    out = StringIO()
    call_command('send_post_appointment_review_requests', stdout=out)
    command_output = out.getvalue()
    assert "Review request" in command_output or "Processed" in command_output, "Management command output mismatch"

    b3_logs = NotificationLog.objects.filter(booking=b3, notification_type=NotificationLog.TYPE_POST_APPOINTMENT_REVIEW)
    assert b3_logs.exists(), "Management command must dispatch review request for un-notified completed bookings"
    print("Step 4: Management command send_post_appointment_review_requests verified.")

    print("==================================================")
    print("ALL POST-APPOINTMENT REVIEW REQUEST TESTS PASSED CLEANLY! (100% SUCCESS)")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
