import os
import sys
import django

# Setup Django environment
sys.path.insert(0, r'c:\Users\USER\Documents\bolbash-beautyspot')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
import datetime

from core.models import Review
from booking.models import ServiceCategory, Service, Booking


def run_tests():
    print("==================================================")
    print("STARTING TEST SUITE FOR PHASE 9 — CUSTOMER REVIEWS FOUNDATION")
    print("==================================================")

    test_email = "review_tester@example.com"

    # Cleanup existing test user and data
    User.objects.filter(email__iexact=test_email).delete()

    user = User.objects.create_user(
        username=test_email,
        email=test_email,
        password="TestPassword123!",
        first_name="Review",
        last_name="Tester"
    )

    cat = ServiceCategory.objects.first() or ServiceCategory.objects.create(name="Review Category")
    svc = Service.objects.first() or Service.objects.create(
        name="Lace Melt & Install",
        category=cat,
        short_description="Short desc",
        description="Full desc",
        price=25000.00
    )

    booking = Booking.objects.create(
        user=user,
        service=svc,
        customer_name="Review Tester",
        customer_phone="08011112222",
        customer_email=test_email,
        appointment_date=timezone.now().date(),
        appointment_time=datetime.time(14, 0),
        service_name_snapshot=svc.name,
        service_price_snapshot=svc.price,
        status=Booking.STATUS_COMPLETED
    )

    # 1. Test Valid Review Creation & Defaults
    review = Review(
        user=user,
        booking=booking,
        service=svc,
        rating=5,
        comment="Absolutely stunning wig installation! Highly professional experience."
    )
    review.full_clean()
    review.save()

    assert review.pk is not None, "Review failed to save"
    assert review.rating == 5, "Rating mismatch"
    assert review.status == Review.STATUS_PENDING, "Default status must be PENDING"
    assert review.user == user, "User relation mismatch"
    assert review.booking == booking, "Booking relation mismatch"
    print("Step 1: Valid Review Creation & Default PENDING status verified.")

    # 2. Test Invalid Rating Validation (0 Stars)
    review_zero = Review(
        user=user,
        rating=0,
        comment="Zero rating test"
    )
    try:
        review_zero.full_clean()
        assert False, "Should fail full_clean() for 0 rating"
    except ValidationError as e:
        assert 'rating' in e.message_dict, "Validation error should contain rating field"
    print("Step 2: 0 star rating server-side validation error verified.")

    # 3. Test Invalid Rating Validation (> 5 Stars)
    review_six = Review(
        user=user,
        rating=6,
        comment="Six rating test"
    )
    try:
        review_six.full_clean()
        assert False, "Should fail full_clean() for rating > 5"
    except ValidationError as e:
        assert 'rating' in e.message_dict, "Validation error should contain rating field"
    print("Step 3: >5 star rating server-side validation error verified.")

    # 4. Test Empty Comment Validation
    review_empty = Review(
        user=user,
        rating=4,
        comment="   "
    )
    try:
        review_empty.full_clean()
        assert False, "Should fail full_clean() for empty comment"
    except ValidationError as e:
        assert 'comment' in e.message_dict, "Validation error should contain comment field"
    print("Step 4: Empty review comment validation error verified.")

    # 5. Test Duplicate Review Prevention on Same Booking
    duplicate_review = Review(
        user=user,
        booking=booking,
        service=svc,
        rating=4,
        comment="Attempting duplicate review on same completed booking."
    )
    try:
        duplicate_review.save()
        assert False, "Database should prevent duplicate review for same booking"
    except IntegrityError:
        print("Step 5: Database-level duplicate review prevention verified (IntegrityError raised).")

    print("==================================================")
    print("ALL REVIEW ARCHITECTURE TESTS PASSED CLEANLY!")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
