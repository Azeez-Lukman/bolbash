import os
import sys
import django

# Setup Django environment
sys.path.insert(0, r'c:\Users\USER\Documents\bolbash-beautyspot')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
import datetime

from core.models import Review
from booking.models import ServiceCategory, Service, Booking


def run_tests():
    print("==================================================")
    print("STARTING TEST SUITE FOR PHASE 9 — REVIEW MODERATION")
    print("==================================================")

    client = Client()
    admin_email = "admin_moderator@example.com"
    customer_email = "normal_customer@example.com"

    # Cleanup test users
    User.objects.filter(email__in=[admin_email, customer_email]).delete()

    admin_user = User.objects.create_superuser(
        username=admin_email,
        email=admin_email,
        password="AdminPassword123!",
        first_name="Admin",
        last_name="Moderator"
    )
    customer_user = User.objects.create_user(
        username=customer_email,
        email=customer_email,
        password="CustomerPassword123!",
        first_name="Normal",
        last_name="Customer"
    )

    cat = ServiceCategory.objects.first() or ServiceCategory.objects.create(name="Beauty Category")
    svc = Service.objects.first() or Service.objects.create(
        name="Bridal Styling",
        category=cat,
        short_description="Short desc",
        description="Full desc",
        price=50000.00
    )

    booking_1 = Booking.objects.create(
        user=customer_user,
        service=svc,
        customer_name="Normal Customer",
        customer_phone="08022223333",
        customer_email=customer_email,
        appointment_date=timezone.now().date() - datetime.timedelta(days=2),
        appointment_time=datetime.time(10, 0),
        service_name_snapshot=svc.name,
        service_price_snapshot=svc.price,
        status=Booking.STATUS_COMPLETED
    )

    booking_2 = Booking.objects.create(
        user=customer_user,
        service=svc,
        customer_name="Normal Customer",
        customer_phone="08022223333",
        customer_email=customer_email,
        appointment_date=timezone.now().date() - datetime.timedelta(days=1),
        appointment_time=datetime.time(12, 0),
        service_name_snapshot=svc.name,
        service_price_snapshot=svc.price,
        status=Booking.STATUS_COMPLETED
    )

    # --------------------------------------------------
    # TEST 1 — NEW REVIEW STATUS
    # --------------------------------------------------
    client.login(username=customer_email, password="CustomerPassword123!")
    response = client.post(reverse('accounts:submit_review', kwargs={'booking_id': booking_1.id}), {
        'rating': 5,
        'comment': 'Exceptional bridal styling experience! Recommended 100%.',
    }, follow=True)
    assert response.status_code == 200, "Review submission failed"

    review_1 = Review.objects.get(booking=booking_1)
    assert review_1.status == Review.STATUS_PENDING, "New review must default to PENDING status"
    print("TEST 1 PASSED: New review created with status = PENDING.")
    client.logout()

    # --------------------------------------------------
    # TEST 2 — ADMIN APPROVAL
    # --------------------------------------------------
    client.login(username=admin_email, password="AdminPassword123!")
    response = client.post(reverse('admin_panel:review_update_status', kwargs={'pk': review_1.pk}), {
        'status': 'APPROVED',
    }, follow=True)
    assert response.status_code == 200, "Admin status update POST failed"

    review_1.refresh_from_db()
    assert review_1.status == Review.STATUS_APPROVED, "Review status should be APPROVED"
    print("TEST 2 PASSED: Admin approval changed review status to APPROVED.")

    # --------------------------------------------------
    # TEST 3 — ADMIN REJECTION
    # --------------------------------------------------
    client.logout()
    client.login(username=customer_email, password="CustomerPassword123!")
    response = client.post(reverse('accounts:submit_review', kwargs={'booking_id': booking_2.id}), {
        'rating': 1,
        'comment': 'Inappropriate test content.',
    }, follow=True)
    review_2 = Review.objects.get(booking=booking_2)
    client.logout()

    client.login(username=admin_email, password="AdminPassword123!")
    response = client.post(reverse('admin_panel:review_update_status', kwargs={'pk': review_2.pk}), {
        'status': 'REJECTED',
    }, follow=True)
    review_2.refresh_from_db()
    assert review_2.status == Review.STATUS_REJECTED, "Review status should be REJECTED"
    print("TEST 3 PASSED: Admin rejection changed review status to REJECTED.")
    client.logout()

    # --------------------------------------------------
    # TEST 4 — CUSTOMER SECURITY
    # --------------------------------------------------
    client.login(username=customer_email, password="CustomerPassword123!")
    response = client.post(reverse('admin_panel:review_update_status', kwargs={'pk': review_2.pk}), {
        'status': 'APPROVED',
    })
    # Normal customer must be denied access to admin views
    assert response.status_code in [302, 403], "Customer must be denied access to moderation endpoint"
    review_2.refresh_from_db()
    assert review_2.status == Review.STATUS_REJECTED, "Customer should NOT be able to change status to APPROVED"
    print("TEST 4 PASSED: Customer security check prevented unauthorized moderation status change.")
    client.logout()

    # --------------------------------------------------
    # TEST 5 — INVALID STATUS VALIDATION
    # --------------------------------------------------
    client.login(username=admin_email, password="AdminPassword123!")
    response = client.post(reverse('admin_panel:review_update_status', kwargs={'pk': review_1.pk}), {
        'status': 'HACKED_INVALID_STATUS',
    }, follow=True)
    assert "Invalid moderation status choice selected." in response.content.decode('utf-8'), "Invalid status error message missing"
    review_1.refresh_from_db()
    assert review_1.status == Review.STATUS_APPROVED, "Review status must remain unchanged on invalid status input"
    print("TEST 5 PASSED: Invalid status input rejected by backend server-side validation.")

    # --------------------------------------------------
    # TEST 6 — DATABASE INTEGRITY
    # --------------------------------------------------
    assert Review.objects.get(pk=review_1.pk).status == Review.STATUS_APPROVED, "Target review 1 status intact"
    assert Review.objects.get(pk=review_2.pk).status == Review.STATUS_REJECTED, "Target review 2 status intact"
    print("TEST 6 PASSED: Database record integrity verified.")

    # --------------------------------------------------
    # TEST 7 — MULTIPLE REVIEWS ISOLATION
    # --------------------------------------------------
    client.post(reverse('admin_panel:review_update_status', kwargs={'pk': review_1.pk}), {'status': 'PENDING'})
    review_1.refresh_from_db()
    review_2.refresh_from_db()
    assert review_1.status == Review.STATUS_PENDING, "Review 1 updated to PENDING"
    assert review_2.status == Review.STATUS_REJECTED, "Review 2 remained REJECTED"
    print("TEST 7 PASSED: Updating one review does not affect unrelated reviews.")

    print("==================================================")
    print("ALL REVIEW MODERATION TESTS PASSED CLEANLY! (100% SUCCESS)")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
