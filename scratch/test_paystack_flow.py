import os
import sys
import django

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from booking.models import Service, Booking
from payments.models import Payment
from payments.views import initiate_payment, verify_payment

def test_paystack_verification_flow():
    factory = RequestFactory()
    service = Service.objects.filter(active=True).first()

    booking = Booking.objects.create(
        service=service,
        customer_name="Paystack Test User",
        customer_phone="08011112222",
        customer_email="paystacktest@example.com",
        appointment_date="2026-08-25",
        appointment_time="10:00",
        service_name_snapshot=service.name,
        service_price_snapshot=100.00,
        amount_due=100.00,
        status=Booking.STATUS_PENDING_PAYMENT,
        payment_status=Booking.PAYMENT_UNPAID
    )

    # 1. Test Initiation
    req_init = factory.get(f'/payments/initiate/{booking.reference}/')
    req_init.user = booking.user or None
    # Attach session & messages support
    from django.contrib.sessions.middleware import SessionMiddleware
    from django.contrib.messages.middleware import MessageMiddleware
    middleware = SessionMiddleware(lambda r: None)
    middleware.process_request(req_init)
    req_init.session.save()
    msg_middleware = MessageMiddleware(lambda r: None)
    msg_middleware.process_request(req_init)

    res_init = initiate_payment(req_init, booking.reference)
    assert res_init.status_code == 302, f"Expected redirect, got {res_init.status_code}"
    
    payment = Payment.objects.filter(booking=booking).last()
    assert payment is not None, "Payment object not created"
    print(f" Created Payment Reference: {payment.reference} for Booking {booking.reference} [OK]")

    # 2. Test Verification Callback
    verify_url = f"/payments/verify/?payment_ref={payment.reference}&trxref={payment.reference}"
    req_ver = factory.get(verify_url)
    middleware.process_request(req_ver)
    req_ver.session.save()
    msg_middleware.process_request(req_ver)

    res_ver = verify_payment(req_ver)
    assert res_ver.status_code == 302, f"Expected redirect after verify, got {res_ver.status_code}"

    booking.refresh_from_db()
    payment.refresh_from_db()

    assert payment.status == Payment.STATUS_PAID, f"Payment status expected PAID, got {payment.status}"
    assert booking.status == Booking.STATUS_CONFIRMED, f"Booking status expected CONFIRMED, got {booking.status}"
    assert booking.payment_status == Booking.PAYMENT_PAID, f"Booking payment status expected PAID, got {booking.payment_status}"

    print(f" Payment Verified Successfully! Booking {booking.reference} is now CONFIRMED. [OK]")

    # Clean up test
    booking.delete()
    payment.delete()

if __name__ == '__main__':
    test_paystack_verification_flow()
