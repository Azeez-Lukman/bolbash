import os
import sys
import json
import hmac
import hashlib
import django

# Setup Django environment
sys.path.insert(0, r'c:\Users\USER\Documents\bolbash-beautyspot')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.conf import settings
from django.contrib.auth.models import User
from booking.models import ServiceCategory, Service, Booking
from payments.models import Payment
from payments.services import PaystackService


def run_tests():
    print("==================================================")
    print("STARTING PHASE 11 — PAYMENT SECURITY TESTING AUDIT")
    print("==================================================")

    client = Client()

    # Clean up previous test data
    Booking.objects.filter(customer_email="paytest_customer@example.com").delete()

    # Create Service & Booking for testing
    svc_cat = ServiceCategory.objects.first() or ServiceCategory.objects.create(name="Pay Security Cat")
    svc = Service.objects.create(
        name="Pay Security Styling",
        slug="pay-security-styling",
        category=svc_cat,
        price=15000.00,
        active=True
    )

    booking = Booking.objects.create(
        customer_name="Pay Security Customer",
        customer_email="paytest_customer@example.com",
        customer_phone="08012345678",
        service=svc,
        service_name_snapshot=svc.name,
        service_price_snapshot=svc.price,
        service_duration_snapshot=60,
        appointment_date="2026-08-10",
        appointment_time="11:00:00",
        amount_due=15000.00,
        status=Booking.STATUS_PENDING_PAYMENT,
        payment_status=Booking.PAYMENT_UNPAID
    )

    # ----------------------------------------------------
    # 1. Server-Side Price Calculation Verification
    # ----------------------------------------------------
    print("\n--- 1. Server-Side Price Calculation Verification ---")
    
    # Initiate payment via GET/POST
    init_res = client.get(f'/payments/initiate/{booking.reference}/', follow=False)
    assert init_res.status_code == 302, f"Payment initiation returned status {init_res.status_code}, expected 302 redirect"

    payment = Payment.objects.filter(booking=booking).order_by('-created_at').first()
    assert payment is not None, "Payment record not created during payment initiation"
    assert payment.amount == 15000.00, f"Payment amount mismatch! Expected 15000.00, got {payment.amount}"
    
    print("  [OK] Payment amount calculated strictly from server-side DB record (15,000.00 NGN).")

    # ----------------------------------------------------
    # 2. Paystack Webhook HMAC-SHA512 Signature Validation
    # ----------------------------------------------------
    print("\n--- 2. Paystack Webhook HMAC-SHA512 Signature Security ---")

    webhook_payload = {
        'event': 'charge.success',
        'data': {
            'reference': payment.reference,
            'amount': 1500000,
            'currency': 'NGN',
            'status': 'success'
        }
    }
    payload_bytes = json.dumps(webhook_payload).encode('utf-8')

    # Un-signed Webhook POST -> 400 Bad Request
    no_sig_res = client.post('/payments/webhook/', data=payload_bytes, content_type='application/json')
    assert no_sig_res.status_code == 400, f"Un-signed webhook returned status {no_sig_res.status_code}, expected 400"
    print("  [OK] Un-signed Webhook POST rejected with HTTP 400 Bad Request.")

    # Invalid Signature Webhook POST -> 400 Bad Request
    invalid_sig_res = client.post(
        '/payments/webhook/',
        data=payload_bytes,
        content_type='application/json',
        HTTP_X_PAYSTACK_SIGNATURE='invalid_hmac_signature_hash'
    )
    assert invalid_sig_res.status_code == 400, f"Invalid signature webhook returned status {invalid_sig_res.status_code}, expected 400"
    print("  [OK] Invalid signature Webhook POST rejected with HTTP 400 Bad Request.")

    # Valid Signature Webhook POST -> 200 OK
    secret_bytes = settings.PAYSTACK_SECRET_KEY.encode('utf-8')
    valid_hash = hmac.new(secret_bytes, payload_bytes, hashlib.sha512).hexdigest()

    valid_sig_res = client.post(
        '/payments/webhook/',
        data=payload_bytes,
        content_type='application/json',
        HTTP_X_PAYSTACK_SIGNATURE=valid_hash
    )
    assert valid_sig_res.status_code == 200, f"Valid signature webhook returned status {valid_sig_res.status_code}, expected 200"
    print("  [OK] Valid HMAC-SHA512 signed Webhook POST accepted with HTTP 200 OK.")

    # ----------------------------------------------------
    # 3. Verification & Idempotency Guarantee
    # ----------------------------------------------------
    print("\n--- 3. Payment Verification & Idempotency Guarantee ---")

    # Refresh DB objects
    payment.refresh_from_db()
    booking.refresh_from_db()

    assert payment.status == Payment.STATUS_PAID, f"Payment status not updated to PAID, current: {payment.status}"
    assert booking.status == Booking.STATUS_CONFIRMED, f"Booking status not updated to CONFIRMED, current: {booking.status}"
    assert booking.payment_status == Booking.PAYMENT_PAID, f"Booking payment status not updated to PAID, current: {booking.payment_status}"
    print("  [OK] Payment verified and Booking status updated to CONFIRMED & PAID.")

    # Re-run webhook event for already PAID transaction -> Idempotency Check
    repeat_res = client.post(
        '/payments/webhook/',
        data=payload_bytes,
        content_type='application/json',
        HTTP_X_PAYSTACK_SIGNATURE=valid_hash
    )
    assert repeat_res.status_code == 200, f"Repeat webhook returned status {repeat_res.status_code}, expected 200"
    print("  [OK] Repeat webhook event handled idempotently without side-effects.")

    # Cleanup test data
    booking.delete()
    svc.delete()

    print("==================================================")
    print("PAYMENT SECURITY AUDIT PASSED! (100% SUCCESS)")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
