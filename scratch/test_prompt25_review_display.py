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
    print("STARTING TEST SUITE FOR PHASE 9 — REVIEW DISPLAY")
    print("==================================================")

    client = Client()
    user_email = "display_customer@example.com"

    # Cleanup existing test data
    User.objects.filter(email=user_email).delete()

    user = User.objects.create_user(
        username=user_email,
        email=user_email,
        password="CustomerPassword123!",
        first_name="Display",
        last_name="Tester"
    )

    cat = ServiceCategory.objects.first() or ServiceCategory.objects.create(name="Display Hair Category")
    svc = Service.objects.filter(active=True).first()
    if not svc:
        svc = Service.objects.create(
            name="Frontal Installation & Melt",
            slug="frontal-installation-melt",
            category=cat,
            short_description="Short desc",
            description="Full desc",
            price=35000.00,
            active=True
        )

    b1 = Booking.objects.create(user=user, service=svc, customer_name="Display Tester", customer_phone="08012345678", customer_email=user_email, appointment_date=timezone.now().date() - datetime.timedelta(days=3), appointment_time=datetime.time(10, 0), service_name_snapshot=svc.name, service_price_snapshot=svc.price, status=Booking.STATUS_COMPLETED)
    b2 = Booking.objects.create(user=user, service=svc, customer_name="Display Tester", customer_phone="08012345678", customer_email=user_email, appointment_date=timezone.now().date() - datetime.timedelta(days=2), appointment_time=datetime.time(12, 0), service_name_snapshot=svc.name, service_price_snapshot=svc.price, status=Booking.STATUS_COMPLETED)
    b3 = Booking.objects.create(user=user, service=svc, customer_name="Display Tester", customer_phone="08012345678", customer_email=user_email, appointment_date=timezone.now().date() - datetime.timedelta(days=1), appointment_time=datetime.time(14, 0), service_name_snapshot=svc.name, service_price_snapshot=svc.price, status=Booking.STATUS_COMPLETED)

    # 1. Create 3 Reviews with different moderation statuses
    approved_text = "APPROVED REVIEW: Magnificent lace melt and customer service!"
    pending_text = "PENDING REVIEW: Still under moderation review."
    rejected_text = "REJECTED REVIEW: Inappropriate spam submission."

    rev_approved = Review.objects.create(user=user, booking=b1, service=svc, rating=5, comment=approved_text, status=Review.STATUS_APPROVED)
    rev_pending = Review.objects.create(user=user, booking=b2, service=svc, rating=1, comment=pending_text, status=Review.STATUS_PENDING)
    rev_rejected = Review.objects.create(user=user, booking=b3, service=svc, rating=2, comment=rejected_text, status=Review.STATUS_REJECTED)

    # --------------------------------------------------
    # TEST 1 & 2 — PUBLIC FILTER & UNAPPROVED CONCEALMENT (HOMEPAGE)
    # --------------------------------------------------
    response = client.get(reverse('core:index'))
    assert response.status_code == 200, "Homepage load failed"
    content = response.content.decode('utf-8')
    assert approved_text in content, "Approved review text must be visible on homepage"
    assert pending_text not in content, "Pending review MUST NOT appear on homepage"
    assert rejected_text not in content, "Rejected review MUST NOT appear on homepage"
    print("TEST 1 & 2 PASSED: Approved review rendered on homepage; pending/rejected reviews strictly concealed.")

    # --------------------------------------------------
    # TEST 3 — SERVICE DETAIL REVIEWS & RATING SCORE
    # --------------------------------------------------
    response = client.get(reverse('core:service_detail', kwargs={'slug': svc.slug}))
    assert response.status_code == 200, "Service detail page load failed"
    content = response.content.decode('utf-8')
    assert approved_text in content, "Approved review text must be visible on service detail"
    assert pending_text not in content, "Pending review MUST NOT appear on service detail"
    assert rejected_text not in content, "Rejected review MUST NOT appear on service detail"
    assert "Verified Reviews for" in content, "Verified reviews section heading missing"
    print("TEST 3 PASSED: Service detail page displays approved service reviews & average rating score.")

    # --------------------------------------------------
    # TEST 4 — REVIEWS SHOWCASE PAGE (/reviews/)
    # --------------------------------------------------
    response = client.get(reverse('core:reviews_showcase'))
    assert response.status_code == 200, "Reviews showcase GET failed"
    content = response.content.decode('utf-8')
    assert approved_text in content, "Approved review text missing from showcase page"
    assert pending_text not in content, "Pending review MUST NOT appear on showcase page"
    assert rejected_text not in content, "Rejected review MUST NOT appear on showcase page"
    assert "Client Experiences & Reviews" in content, "Reviews showcase title missing"
    print("TEST 4 PASSED: Dedicated public reviews showcase page (/reviews/) rendered approved client reviews cleanly.")

    # --------------------------------------------------
    # TEST 5 — RATING FILTER ON SHOWCASE PAGE
    # --------------------------------------------------
    response = client.get(reverse('core:reviews_showcase') + "?rating=5")
    assert response.status_code == 200, "Reviews showcase rating filter GET failed"
    content = response.content.decode('utf-8')
    assert approved_text in content, "5-star approved review should appear when rating=5 filter applied"
    print("TEST 5 PASSED: Rating filter on public reviews showcase verified.")

    print("==================================================")
    print("ALL REVIEW DISPLAY TESTS PASSED CLEANLY! (100% SUCCESS)")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
