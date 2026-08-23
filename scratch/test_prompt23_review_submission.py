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
    print("STARTING TEST SUITE FOR PHASE 9 — REVIEW SUBMISSION")
    print("==================================================")

    client = Client()
    user_a_email = "customer_a@example.com"
    user_b_email = "customer_b@example.com"

    # Cleanup test users
    User.objects.filter(email__in=[user_a_email, user_b_email]).delete()

    user_a = User.objects.create_user(username=user_a_email, email=user_a_email, password="Password123!", first_name="Customer", last_name="A")
    user_b = User.objects.create_user(username=user_b_email, email=user_b_email, password="Password123!", first_name="Customer", last_name="B")

    cat = ServiceCategory.objects.first() or ServiceCategory.objects.create(name="Hair Category")
    svc = Service.objects.first() or Service.objects.create(
        name="Wig Revamping & Melt",
        category=cat,
        short_description="Short desc",
        description="Full desc",
        price=30000.00
    )

    # Booking 1: Customer A's completed appointment
    completed_booking = Booking.objects.create(
        user=user_a,
        service=svc,
        customer_name="Customer A",
        customer_phone="08011111111",
        customer_email=user_a_email,
        appointment_date=timezone.now().date() - datetime.timedelta(days=1),
        appointment_time=datetime.time(11, 0),
        service_name_snapshot=svc.name,
        service_price_snapshot=svc.price,
        status=Booking.STATUS_COMPLETED
    )

    # Booking 2: Customer A's pending (uncompleted) appointment
    pending_booking = Booking.objects.create(
        user=user_a,
        service=svc,
        customer_name="Customer A",
        customer_phone="08011111111",
        customer_email=user_a_email,
        appointment_date=timezone.now().date() + datetime.timedelta(days=2),
        appointment_time=datetime.time(14, 0),
        service_name_snapshot=svc.name,
        service_price_snapshot=svc.price,
        status=Booking.STATUS_CONFIRMED
    )

    # 1. Unauthenticated Access Control Test
    response = client.get(reverse('accounts:submit_review', kwargs={'booking_id': completed_booking.id}))
    assert response.status_code == 302, "Unauthenticated user should be redirected to login"
    assert "/accounts/login/" in response.url, "Redirect URL should contain login path"
    print("Step 1: Unauthenticated access control verified.")

    # 2. Authorization Check (Customer B attempting to review Customer A's booking)
    client.login(username=user_b_email, password="Password123!")
    response = client.get(reverse('accounts:submit_review', kwargs={'booking_id': completed_booking.id}), follow=True)
    assert response.status_code == 200, "Response should succeed following redirect"
    assert "You are not authorized" in response.content.decode('utf-8'), "Unauthorized error message missing"
    client.logout()
    print("Step 2: Cross-user authorization protection verified.")

    # 3. Completion Boundary Check (Reviewing uncompleted booking)
    client.login(username=user_a_email, password="Password123!")
    response = client.get(reverse('accounts:submit_review', kwargs={'booking_id': pending_booking.id}), follow=True)
    assert "Reviews can only be submitted for completed salon appointments." in response.content.decode('utf-8'), "Uncompleted appointment review error missing"
    print("Step 3: Uncompleted appointment review boundary verified.")

    # 4. Review Submission Form Loading
    response = client.get(reverse('accounts:submit_review', kwargs={'booking_id': completed_booking.id}))
    assert response.status_code == 200, "Review submission form GET failed"
    assert "Submit Salon Experience Review" in response.content.decode('utf-8'), "Review form title missing"
    assert completed_booking.service_name_snapshot in response.content.decode('utf-8'), "Service name snapshot missing from form"
    print("Step 4: Review submission form loading verified.")

    # 5. Successful Review Submission
    response = client.post(reverse('accounts:submit_review', kwargs={'booking_id': completed_booking.id}), {
        'rating': 5,
        'comment': 'Flawless wig revamp! The lace melt was invisible and lasted perfectly.',
    }, follow=True)
    assert response.status_code == 200, "Review POST submission failed"
    assert "Thank you for your feedback!" in response.content.decode('utf-8'), "Success message missing"

    review = Review.objects.get(booking=completed_booking)
    assert review.rating == 5, "Review rating mismatch"
    assert review.status == Review.STATUS_PENDING, "Review must be PENDING moderation"
    assert review.user == user_a, "Review user mismatch"
    print("Step 5: Successful Review submission and PENDING moderation state verified.")

    # 6. Duplicate Review Prevention Check
    response = client.get(reverse('accounts:submit_review', kwargs={'booking_id': completed_booking.id}), follow=True)
    assert "already submitted a review" in response.content.decode('utf-8'), "Duplicate review notice missing"
    print("Step 6: Duplicate review prevention on reviewed booking verified.")

    print("==================================================")
    print("ALL REVIEW SUBMISSION TESTS PASSED CLEANLY! (100% SUCCESS)")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
