import os
import sys
import django

# Setup Django environment
sys.path.insert(0, r'c:\Users\USER\Documents\bolbash-beautyspot')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from accounts.models import CustomerProfile
from booking.models import ServiceCategory, Service, Booking
from core.models import Review, CustomerFeedback, ContactSubmission


def run_tests():
    print("==================================================")
    print("STARTING PHASE 11 — FORM VALIDATION AUDIT")
    print("==================================================")

    client = Client()

    # Clean up previous test users
    User.objects.filter(username__startswith="formtest_").delete()

    # ----------------------------------------------------
    # 1. Customer Registration Form Validation
    # ----------------------------------------------------
    print("\n--- 1. Customer Registration Form Validation ---")
    
    # Missing required fields
    res_missing = client.post('/accounts/register/', {
        'first_name': '',
        'last_name': '',
        'email': '',
        'phone_number': '',
        'password': '',
        'confirm_password': '',
    })
    assert res_missing.status_code == 200
    assert '_auth_user_id' not in client.session, "Invalid registration allowed login!"

    # Malformed email
    res_bad_email = client.post('/accounts/register/', {
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'not-an-email',
        'phone_number': '08012345678',
        'password': 'Password123!',
        'confirm_password': 'Password123!',
    })
    assert res_bad_email.status_code == 200
    assert '_auth_user_id' not in client.session

    # Password mismatch
    res_mismatch = client.post('/accounts/register/', {
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'formtest_user1@example.com',
        'phone_number': '08012345678',
        'password': 'Password123!',
        'confirm_password': 'DifferentPassword123!',
    })
    assert res_mismatch.status_code == 200
    assert '_auth_user_id' not in client.session

    print("  [OK] Customer registration form cleanly rejects missing, malformed, and mismatch inputs.")

    # ----------------------------------------------------
    # 2. Academy Student Registration Form Validation
    # ----------------------------------------------------
    print("\n--- 2. Academy Student Registration Form Validation ---")
    
    # Weak password rejection via validate_password()
    res_weak_pass = client.post('/academy/register/', {
        'first_name': 'Student',
        'last_name': 'Test',
        'email': 'formtest_student1@example.com',
        'phone_number': '08012345678',
        'password': '123',
        'confirm_password': '123',
    })
    assert res_weak_pass.status_code == 200
    assert '_auth_user_id' not in client.session, "Weak password allowed student registration!"

    print("  [OK] Student registration form enforces Django validate_password() strength rules.")

    # ----------------------------------------------------
    # 3. Appointment Booking Form & API Validation
    # ----------------------------------------------------
    print("\n--- 3. Appointment Booking Form & API Validation ---")
    
    # API available slots: invalid date format
    res_api_bad_date = client.get('/booking/api/available-slots/?service_id=1&date=invalid-date')
    assert res_api_bad_date.status_code == 200
    json_bad_date = res_api_bad_date.json()
    assert json_bad_date.get('slots') == [] and 'Invalid date' in json_bad_date.get('message')

    # API available slots: past date
    res_api_past = client.get('/booking/api/available-slots/?service_id=1&date=2020-01-01')
    assert res_api_past.status_code == 200
    json_past = res_api_past.json()
    assert json_past.get('slots') == [] and 'Past dates' in json_past.get('message')

    # Submit booking with missing fields
    res_book_missing = client.post('/booking/submit/', {
        'service_id': '',
        'appointment_date': '',
        'appointment_time': '',
        'customer_name': '',
        'customer_phone': '',
        'customer_email': '',
    }, follow=True)
    assert res_book_missing.status_code == 200
    assert 'fill in all required fields' in res_book_missing.content.decode('utf-8').lower()

    print("  [OK] Appointment booking form & API endpoints reject invalid date formats, past dates, and missing fields.")

    # ----------------------------------------------------
    # 4. Review & Feedback Form Validation & Anti-Spam
    # ----------------------------------------------------
    print("\n--- 4. Review & Feedback Form Validation & Anti-Spam ---")
    
    # Feedback Form Honeypot Spam Check
    res_spam_fb = client.post('/feedback/', {
        'category': 'GENERAL',
        'rating': 5,
        'message': 'Spam message test',
        'website_url': 'http://spam-bot.com',  # Honeypot filled!
    })
    assert res_spam_fb.status_code == 200
    assert not CustomerFeedback.objects.filter(message='Spam message test').exists(), \
        "Honeypot anti-spam failed! Spam feedback record created in DB."

    print("  [OK] Customer feedback honeypot anti-spam protection verified.")

    # ----------------------------------------------------
    # 5. Contact Us Form Validation & Anti-Spam
    # ----------------------------------------------------
    print("\n--- 5. Contact Us Form Validation & Anti-Spam ---")
    
    # Contact Form Honeypot Spam Check
    res_spam_contact = client.post('/contact/', {
        'name': 'Spam Bot',
        'email': 'spambot@example.com',
        'subject': 'Spam Subject',
        'message': 'Spam Contact Message',
        'website_url': 'http://spam-bot.com',  # Honeypot filled!
    })
    assert res_spam_contact.status_code == 200
    assert not ContactSubmission.objects.filter(message='Spam Contact Message').exists(), \
        "Honeypot anti-spam failed! Spam contact record created in DB."

    # Contact Form Invalid Email
    res_contact_bad_email = client.post('/contact/', {
        'name': 'Valid Name',
        'email': 'not-an-email',
        'subject': 'Valid Subject',
        'message': 'Valid Message',
        'website_url': '',
    })
    assert res_contact_bad_email.status_code == 200
    assert not ContactSubmission.objects.filter(name='Valid Name').exists()

    print("  [OK] Contact form invalid email and honeypot anti-spam protection verified.")

    # Cleanup test users
    User.objects.filter(username__startswith="formtest_").delete()

    print("==================================================")
    print("FORM VALIDATION & ANTI-SPAM AUDIT PASSED! (100% SUCCESS)")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
