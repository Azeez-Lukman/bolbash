import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import GalleryImage, ContactSubmission

def run_tests():
    print("==========================================================")
    print("STARTING COMPREHENSIVE GALLERY & CONTACT TEST SUITE")
    print("==========================================================")

    client = Client()
    passed = 0
    total = 0

    # ------------------------------------------------------------------
    # TEST 1: Gallery Page Load
    # ------------------------------------------------------------------
    total += 1
    print("\n[TEST 1] Testing Gallery Page Load (/gallery/)...")
    gallery_url = reverse('core:gallery')
    res = client.get(gallery_url)
    if res.status_code == 200:
        content = res.content.decode('utf-8')
        assert "Our Masterpiece" in content or "Portfolio" in content, "Hero headline missing"
        assert "gallery-filter-btn" in content, "Category filter buttons missing"
        assert "gallery-lightbox" in content, "Lightbox modal component missing"
        print("  [OK] Gallery page loaded successfully (HTTP 200) with category filters & lightbox.")
        passed += 1
    else:
        print(f"  [FAIL] Gallery page failed with HTTP {res.status_code}")

    # ------------------------------------------------------------------
    # TEST 2: Contact Page Load & Business Context
    # ------------------------------------------------------------------
    total += 1
    print("\n[TEST 2] Testing Contact Page Load (/contact/)...")
    contact_url = reverse('core:contact')
    res = client.get(contact_url)
    if res.status_code == 200:
        content = res.content.decode('utf-8')
        assert "SIOA Plaza" in content, "Official address missing from contact page"
        assert "08168956606" in content, "Official phone number missing from contact page"
        assert "wa.me" in content, "WhatsApp CTA link missing from contact page"
        assert "map-section" in content or "google.com/maps" in content, "Location map section missing"
        assert "id_name" in content and "id_email" in content, "Contact form fields missing"
        print("  [OK] Contact page loaded successfully (HTTP 200) with address, phone, WhatsApp & map.")
        passed += 1
    else:
        print(f"  [FAIL] Contact page failed with HTTP {res.status_code}")

    # ------------------------------------------------------------------
    # TEST 3: Contact Form Successful Submission
    # ------------------------------------------------------------------
    total += 1
    print("\n[TEST 3] Testing Valid Contact Form Submission...")
    form_data = {
        'name': 'Test Client Adeola',
        'email': 'adeola.test@example.com',
        'phone': '08012345678',
        'subject': 'Bridal Styling Consultation',
        'message': 'Hello Bolbash, I would like to enquire about bridal hair styling packages for my upcoming wedding.'
    }
    res = client.post(contact_url, data=form_data, follow=True)
    if res.status_code == 200:
        content = res.content.decode('utf-8')
        assert "Message Sent" in content, "Success message not rendered"
        
        # Check DB
        sub = ContactSubmission.objects.filter(email='adeola.test@example.com').first()
        assert sub is not None, "ContactSubmission record not created in DB"
        assert sub.name == 'Test Client Adeola', "Submission name mismatch"
        assert sub.status == ContactSubmission.STATUS_NEW, "Initial status must be NEW"
        print(f"  [OK] Contact form submitted successfully! ContactSubmission ID={sub.id} created with STATUS=NEW.")
        passed += 1
    else:
        print(f"  [FAIL] Contact form submission failed with HTTP {res.status_code}")

    # ------------------------------------------------------------------
    # TEST 4: Contact Form Server-Side Validation Errors
    # ------------------------------------------------------------------
    total += 1
    print("\n[TEST 4] Testing Contact Form Validation Errors...")
    invalid_data = {
        'name': '',
        'email': 'invalid-email-format',
        'subject': '',
        'message': ''
    }
    res = client.post(contact_url, data=invalid_data, follow=True)
    content = res.content.decode('utf-8')
    if "Please fill in all required fields" in content or "Please provide your full name" in content or "Please enter a valid email address" in content:
        print("  [OK] Contact form properly rejected invalid input with server validation error messages.")
        passed += 1
    else:
        print("  [FAIL] Contact form validation test failed; error banner not found.")

    # ------------------------------------------------------------------
    # TEST 5: Honeypot Anti-Spam Protection
    # ------------------------------------------------------------------
    total += 1
    print("\n[TEST 5] Testing Contact Form Honeypot Anti-Spam Protection...")
    bot_data = {
        'website_url': 'http://spam-bot.com',
        'name': 'Bot Sender',
        'email': 'bot@spam.com',
        'subject': 'Spam subject',
        'message': 'Buy cheap crypto links'
    }
    prev_count = ContactSubmission.objects.filter(email='bot@spam.com').count()
    res = client.post(contact_url, data=bot_data, follow=True)
    new_count = ContactSubmission.objects.filter(email='bot@spam.com').count()
    if prev_count == new_count:
        print("  [OK] Spam submission intercepted cleanly by honeypot without polluting DB.")
        passed += 1
    else:
        print("  [FAIL] Honeypot anti-spam test failed; DB record created for bot.")

    # ------------------------------------------------------------------
    # TEST 6: Admin Portal Enquiry List & Status Update
    # ------------------------------------------------------------------
    total += 1
    print("\n[TEST 6] Testing Admin Portal Enquiry Management & Status Updates...")
    admin_user, _ = User.objects.get_or_create(username='admin_test_user', defaults={'is_staff': True, 'is_superuser': True})
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.set_password('password123')
    admin_user.save()

    client.force_login(admin_user)
    enquiries_url = reverse('admin_panel:enquiry_list')
    res = client.get(enquiries_url)
    if res.status_code == 200:
        content = res.content.decode('utf-8')
        assert "Customer Contact Enquiries" in content or "Customer Enquiries" in content, "Admin enquiry page header missing"
        
        target_sub = ContactSubmission.objects.first()
        if target_sub:
            update_url = reverse('admin_panel:enquiry_update_status', kwargs={'pk': target_sub.pk})
            res_update = client.post(update_url, data={'status': ContactSubmission.STATUS_RESPONDED}, follow=True)
            target_sub.refresh_from_db()
            assert target_sub.status == ContactSubmission.STATUS_RESPONDED, "Enquiry status update failed"
            print(f"  [OK] Admin Portal enquiry list loaded and status updated to RESPONDED for ID={target_sub.pk}.")
            passed += 1
        else:
            print("  [FAIL] No enquiry record found to test status update.")
    else:
        print(f"  [FAIL] Admin enquiry list failed with HTTP {res.status_code}")

    # ------------------------------------------------------------------
    # TEST 7: Navigation & Footer Integration
    # ------------------------------------------------------------------
    total += 1
    print("\n[TEST 7] Testing Global Navigation & Footer Links...")
    home_res = client.get(reverse('core:index'))
    home_content = home_res.content.decode('utf-8')
    assert reverse('core:gallery') in home_content, "Gallery URL missing from global navigation/footer"
    assert reverse('core:contact') in home_content, "Contact URL missing from global navigation/footer"
    print("  [OK] Gallery (/gallery/) and Contact (/contact/) URLs present in global navigation & footer.")
    passed += 1

    # ------------------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------------------
    print("\n==========================================================")
    print(f"TEST RESULTS: {passed}/{total} PASSED")
    print("==========================================================")
    if passed == total:
        print("ALL GALLERY AND CONTACT EXPERIENCE TESTS PASSED 100%!")

if __name__ == '__main__':
    run_tests()
