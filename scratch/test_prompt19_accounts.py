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

from accounts.models import CustomerProfile
from booking.models import ServiceCategory, Service, Booking
from shop.models import Order
from payments.models import Payment


def run_tests():
    print("==================================================")
    print("STARTING TEST SUITE FOR PHASE 4 — ACCOUNTS")
    print("==================================================")

    client = Client()
    test_email = "janedoe_test@example.com"
    test_password = "SecurePassword123!"

    # Cleanup any existing test data
    Payment.objects.filter(paystack_reference="PAY-TEST-REF-001").delete()
    Order.objects.filter(order_number="BBS-ORD-TEST-001").delete()
    Booking.objects.filter(customer_email__iexact=test_email).delete()
    User.objects.filter(email__iexact=test_email).delete()

    # 1. Create a guest booking and guest shop order prior to registration
    cat = ServiceCategory.objects.first()
    if not cat:
        cat = ServiceCategory.objects.create(name="Test Category")
    
    svc = Service.objects.first()
    if not svc:
        svc = Service.objects.create(
            name="Test Hair Revamp",
            category=cat,
            short_description="Short desc",
            description="Full desc",
            price=15000.00,
            duration=60
        )

    guest_booking = Booking.objects.create(
        service=svc,
        customer_name="Jane Doe",
        customer_phone="08123456789",
        customer_email=test_email,
        appointment_date=timezone.now().date() + datetime.timedelta(days=2),
        appointment_time=datetime.time(10, 0),
        service_name_snapshot=svc.name,
        service_price_snapshot=svc.price,
        service_duration_snapshot=svc.duration,
        amount_due=svc.price,
    )

    guest_order = Order.objects.create(
        order_number="BBS-ORD-TEST-001",
        customer_name="Jane Doe",
        customer_email=test_email,
        customer_phone="08123456789",
        shipping_address="123 Test Street",
        subtotal=5000.00,
        total_amount=5000.00,
    )

    payment = Payment.objects.create(
        reference="BBS-PAY-TEST001",
        paystack_reference="PAY-TEST-REF-001",
        payment_type="BOOKING",
        amount=5000.00,
        status="PAID",
        booking=guest_booking,
    )

    print("Step 1: Created guest booking, shop order, and payment record.")

    # 2. Test Customer Registration Form Submission
    response = client.post(reverse('accounts:register'), {
        'first_name': 'Jane',
        'last_name': 'Doe',
        'email': test_email,
        'phone_number': '08123456789',
        'address': '123 Test Street',
        'city': 'Ibadan',
        'state': 'Oyo State',
        'password': test_password,
        'confirm_password': test_password,
    }, follow=True)

    assert response.status_code == 200, f"Registration failed with status {response.status_code}"
    user = User.objects.get(email__iexact=test_email)
    assert user.first_name == 'Jane', "First name mismatch"
    assert user.last_name == 'Doe', "Last name mismatch"

    profile = CustomerProfile.objects.get(user=user)
    assert profile.phone_number == '08123456789', "Profile phone mismatch"
    print("Step 2: Customer registration successful & CustomerProfile created.")

    # 3. Test Auto-linking of Guest Activity
    guest_booking.refresh_from_db()
    guest_order.refresh_from_db()
    assert guest_booking.user == user, "Guest booking auto-linking failed"
    assert guest_order.user == user, "Guest order auto-linking failed"
    print("Step 3: Auto-linking guest bookings and orders to registered user verified.")

    # 4. Test Customer Dashboard
    response = client.get(reverse('accounts:dashboard'))
    assert response.status_code == 200, f"Dashboard failed with status {response.status_code}"
    assert "Welcome back, Jane!" in response.content.decode('utf-8'), "Dashboard welcome greeting missing"
    assert "BBS-ORD-TEST-001" in response.content.decode('utf-8'), "Recent order missing on dashboard"
    print("Step 4: Customer Dashboard loaded and stats verified.")

    # 5. Test Upcoming Appointments View
    response = client.get(reverse('accounts:upcoming_appointments'))
    assert response.status_code == 200, "Upcoming appointments page failed"
    assert guest_booking.reference in response.content.decode('utf-8'), "Booking reference missing from upcoming list"
    print("Step 5: Upcoming Appointments page verified.")

    # 6. Test Appointment History View
    response = client.get(reverse('accounts:appointment_history'))
    assert response.status_code == 200, "Appointment history page failed"
    print("Step 6: Appointment History page verified.")

    # 7. Test Payment History View
    response = client.get(reverse('accounts:payment_history'))
    assert response.status_code == 200, "Payment history page failed"
    assert "PAY-TEST-REF-001" in response.content.decode('utf-8'), "Payment reference missing from ledger"
    print("Step 7: Payment History Ledger verified.")

    # 8. Test Profile View & Edit
    response = client.post(reverse('accounts:profile'), {
        'first_name': 'Jane',
        'last_name': 'Smith',
        'email': test_email,
        'phone_number': '08099998888',
        'address': '456 Updated Ave',
        'city': 'Ibadan',
        'state': 'Oyo State',
    }, follow=True)

    assert response.status_code == 200, "Profile update failed"
    user.refresh_from_db()
    profile.refresh_from_db()
    assert user.last_name == 'Smith', "Last name update failed"
    assert profile.phone_number == '08099998888', "Phone update failed"
    print("Step 8: Profile view & update verified.")

    # 9. Test Security & Password Change
    new_password = "NewSecurePassword456!"
    response = client.post(reverse('accounts:security'), {
        'old_password': test_password,
        'new_password1': new_password,
        'new_password2': new_password,
    }, follow=True)

    assert response.status_code == 200, "Password change failed"
    # Verify login with new password
    client.logout()
    login_success = client.login(username=test_email, password=new_password)
    assert login_success, "Login with updated password failed"
    print("Step 9: Password change & re-authentication verified.")

    # 10. Test Logout
    response = client.get(reverse('accounts:logout'), follow=True)
    assert response.status_code == 200, "Logout failed"
    assert '_auth_user_id' not in client.session, "User still authenticated after logout"
    print("Step 10: Logout verified.")

    print("==================================================")
    print("ALL 10 TESTS PASSED CLEANLY! (100% SUCCESS)")
    print("==================================================")

if __name__ == '__main__':
    run_tests()
