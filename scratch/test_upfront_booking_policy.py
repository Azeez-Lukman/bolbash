import os
import sys
import datetime
import django

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from django.utils import timezone
from booking.models import Service, Booking
from core.context_processors import bank_details

def test_upfront_booking_policy():
    print("=== TEST 1: Bank Details Context Processor ===")
    ctx = bank_details(None)
    assert 'BANK_NAME' in ctx, "BANK_NAME missing"
    assert 'ACCOUNT_NUMBER' in ctx, "ACCOUNT_NUMBER missing"
    assert 'ACCOUNT_NAME' in ctx, "ACCOUNT_NAME missing"
    print(f" Context Processor Bank Info: {ctx['BANK_NAME']} | Acc: {ctx['ACCOUNT_NUMBER']} | Name: {ctx['ACCOUNT_NAME']} [OK]")

    print("\n=== TEST 2: Booking Expiration & Seconds Remaining ===")
    service = Service.objects.filter(active=True).first()
    
    # Create fresh pending booking
    b_fresh = Booking.objects.create(
        service=service,
        customer_name="Test Fresh Client",
        customer_phone="08012345678",
        customer_email="fresh@example.com",
        appointment_date=timezone.now().date() + datetime.timedelta(days=1),
        appointment_time=datetime.time(10, 0),
        service_name_snapshot=service.name,
        service_price_snapshot=service.price or 5000,
        status=Booking.STATUS_PENDING_PAYMENT,
        payment_status=Booking.PAYMENT_UNPAID,
        amount_due=service.price or 5000,
    )

    assert not b_fresh.is_expired, "Fresh booking should not be expired"
    assert b_fresh.seconds_remaining > 0, "Fresh booking should have seconds remaining"
    print(f" Fresh Booking ({b_fresh.reference}): Expired={b_fresh.is_expired}, Secs Left={b_fresh.seconds_remaining} [OK]")

    # Create old expired pending booking (created 20 mins ago)
    b_old = Booking.objects.create(
        service=service,
        customer_name="Test Old Client",
        customer_phone="08087654321",
        customer_email="old@example.com",
        appointment_date=timezone.now().date() + datetime.timedelta(days=1),
        appointment_time=datetime.time(11, 0),
        service_name_snapshot=service.name,
        service_price_snapshot=service.price or 5000,
        status=Booking.STATUS_PENDING_PAYMENT,
        payment_status=Booking.PAYMENT_UNPAID,
        amount_due=service.price or 5000,
    )
    # Manually backdate created_at to 20 minutes ago
    twenty_mins_ago = timezone.now() - datetime.timedelta(minutes=20)
    Booking.objects.filter(id=b_old.id).update(created_at=twenty_mins_ago)
    b_old.refresh_from_db()

    assert b_old.is_expired, "Old unpaid booking (>15 mins) should be marked as expired"
    assert b_old.seconds_remaining == 0, "Expired booking should have 0 seconds remaining"
    print(f" Expired Booking ({b_old.reference}): Expired={b_old.is_expired}, Secs Left={b_old.seconds_remaining} [OK]")

    # Clean up test records
    b_fresh.delete()
    b_old.delete()
    print("\n=== ALL UPFRONT BOOKING POLICY TESTS PASSED SUCCESSFULLY! ===")

if __name__ == '__main__':
    test_upfront_booking_policy()
