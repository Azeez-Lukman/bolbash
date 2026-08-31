import os
import sys
import django

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from booking.models import Service, Booking
from payments.models import Payment
from payments.services import PaystackService

def test_checkout_redirect():
    service = Service.objects.filter(active=True).first()
    booking = Booking.objects.create(
        service=service,
        customer_name="Paystack Live Test User",
        customer_phone="08123456789",
        customer_email="paystacklive@example.com",
        appointment_date="2026-08-28",
        appointment_time="11:00",
        service_name_snapshot=service.name,
        service_price_snapshot=100.00,
        amount_due=100.00,
        status=Booking.STATUS_PENDING_PAYMENT,
        payment_status=Booking.PAYMENT_UNPAID
    )

    res = PaystackService.initialize_transaction(
        email=booking.customer_email,
        amount_kobo=10000,
        reference=f"PAY-{booking.reference}",
        callback_url=f"http://127.0.0.1:8000/payments/verify/?payment_ref=PAY-{booking.reference}"
    )

    print("Initialize Response:", res)
    assert res.get('status') == True
    url = res['data']['authorization_url']
    print(f" Official Paystack Gateway URL generated: {url}")
    assert 'checkout.paystack.com' in url

    booking.delete()

if __name__ == '__main__':
    test_checkout_redirect()
