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

from core.models import CustomerFeedback


def run_tests():
    print("==================================================")
    print("STARTING TEST SUITE FOR PHASE 9 — CUSTOMER FEEDBACK")
    print("==================================================")

    client = Client()
    customer_email = "feedback_client@example.com"
    admin_email = "feedback_admin@example.com"

    # Cleanup test users & data
    User.objects.filter(email__in=[customer_email, admin_email]).delete()
    CustomerFeedback.objects.filter(email=customer_email).delete()

    customer_user = User.objects.create_user(
        username=customer_email,
        email=customer_email,
        password="CustomerPassword123!",
        first_name="Feedback",
        last_name="Client"
    )
    admin_user = User.objects.create_superuser(
        username=admin_email,
        email=admin_email,
        password="AdminPassword123!",
        first_name="Feedback",
        last_name="Admin"
    )

    # 1. Guest Feedback Submission
    response = client.post(reverse('core:feedback'), {
        'category': 'SALON',
        'rating': 5,
        'name': 'Guest Customer',
        'email': 'guest_feedback@example.com',
        'phone': '08099998888',
        'subject': 'Salon Ambiance & Service Quality',
        'message': 'Loved the calm environment and precise wig styling!',
        'website_url': '',  # empty honeypot
    })
    assert response.status_code == 200, "Guest feedback POST failed"
    guest_fb = CustomerFeedback.objects.get(email='guest_feedback@example.com')
    assert guest_fb.status == CustomerFeedback.STATUS_NEW, "Default status must be NEW"
    assert guest_fb.category == 'SALON', "Category mismatch"
    print("Step 1: Guest customer feedback submission verified.")

    # 2. Authenticated Customer Submission & Auto-linking
    client.login(username=customer_email, password="CustomerPassword123!")
    response = client.post(reverse('core:feedback'), {
        'category': 'ACADEMY',
        'rating': 4,
        'name': 'Feedback Client',
        'email': customer_email,
        'phone': '08011112222',
        'subject': 'Wig Making Course Suggestion',
        'message': 'Great course! Would love additional lace melt practice modules.',
        'website_url': '',
    })
    assert response.status_code == 200, "Authenticated customer feedback POST failed"
    auth_fb = CustomerFeedback.objects.get(email=customer_email)
    assert auth_fb.user == customer_user, "User relation auto-link failed"
    print("Step 2: Authenticated customer submission & user auto-link verified.")

    # 3. Honeypot Anti-Spam Protection
    response = client.post(reverse('core:feedback'), {
        'category': 'GENERAL',
        'rating': 1,
        'name': 'Spam Bot',
        'email': 'bot@spam.com',
        'subject': 'Spam subject',
        'message': 'Spam message',
        'website_url': 'http://spambot-link.com',  # filled honeypot!
    })
    assert response.status_code == 200, "Honeypot request failed"
    assert not CustomerFeedback.objects.filter(email='bot@spam.com').exists(), "Spam bot feedback MUST NOT be created in DB"
    print("Step 3: Honeypot anti-spam protection verified.")

    # 4. Admin Staff Resolution & Notes Update
    client.logout()
    client.login(username=admin_email, password="AdminPassword123!")

    response = client.get(reverse('admin_panel:feedback_list'))
    assert response.status_code == 200, "Admin feedback_list GET failed"
    assert "Customer Feedback & Suggestions" in response.content.decode('utf-8'), "Feedback list dashboard title missing"

    response = client.post(reverse('admin_panel:feedback_update_status', kwargs={'pk': auth_fb.pk}), {
        'status': 'RESOLVED',
        'admin_notes': 'Contacted client via WhatsApp and provided supplementary module guide.',
    }, follow=True)
    assert response.status_code == 200, "Feedback resolution POST failed"

    auth_fb.refresh_from_db()
    assert auth_fb.status == CustomerFeedback.STATUS_RESOLVED, "Status should be RESOLVED"
    assert "WhatsApp" in auth_fb.admin_notes, "Admin resolution notes mismatch"
    print("Step 4: Admin staff status & resolution notes update verified.")

    # 5. Customer Access Control Security
    client.logout()
    client.login(username=customer_email, password="CustomerPassword123!")
    response = client.post(reverse('admin_panel:feedback_update_status', kwargs={'pk': guest_fb.pk}), {
        'status': 'CLOSED',
    })
    assert response.status_code in [302, 403], "Normal customer must be denied access to feedback update"
    guest_fb.refresh_from_db()
    assert guest_fb.status == CustomerFeedback.STATUS_NEW, "Status must remain NEW"
    print("Step 5: Customer access control security verified.")

    print("==================================================")
    print("ALL CUSTOMER FEEDBACK TESTS PASSED CLEANLY! (100% SUCCESS)")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
