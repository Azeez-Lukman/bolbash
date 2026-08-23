import os
import sys
import django

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.urls import reverse, resolve
from django.core.management import call_command
from django.contrib.auth.models import User
from core.models import GalleryImage, ContactSubmission


def test_gallery_and_contact_experience():
    print("=== STARTING PHASE ROADMAP: GALLERY & CONTACT EXPERIENCE TESTS ===")
    client = Client()

    # 1. ROUTE RESOLUTION
    print("\n--- 1. Testing Gallery & Contact Route Resolution ---")
    assert reverse('core:gallery') == '/gallery/'
    assert reverse('core:contact') == '/contact/'
    assert resolve('/gallery/').url_name == 'gallery'
    assert resolve('/contact/').url_name == 'contact'
    print("[OK] Routes /gallery/ and /contact/ resolved successfully.")

    # 2. GALLERY PAGE HTTP 200 & CONTENT
    print("\n--- 2. Testing Gallery Page HTTP 200 & Lightbox Markup ---")
    response_g = client.get('/gallery/')
    assert response_g.status_code == 200
    content_g = response_g.content.decode('utf-8')
    assert "Craftsmanship in" in content_g
    assert "gallery-filter-btn" in content_g
    assert "gallery-lightbox" in content_g
    assert "navigateLightbox" in content_g
    assert "openLightboxFromCard" in content_g
    assert "Book This Look" in content_g
    print("[OK] Gallery page hero, category filters, and lightbox controls verified.")

    # 3. CONTACT PAGE HTTP 200 & BUSINESS INFO
    print("\n--- 3. Testing Contact Page Business Information ---")
    response_c = client.get('/contact/')
    assert response_c.status_code == 200
    content_c = response_c.content.decode('utf-8')
    assert "Connect With" in content_c
    assert "SIOA Plaza" in content_c
    assert "08168956606" in content_c
    assert "tel:08168956606" in content_c
    assert "wa.me/message/UW6FRPKW3STAM1" in content_c
    assert "instagram.com/hairbybolbash" in content_c
    assert "openstreetmap.org" in content_c
    print("[OK] Centralized business contact info, tel links, WhatsApp CTA, and Map embed verified.")

    # 4. CONTACT FORM VALIDATION & SUBMISSION
    print("\n--- 4. Testing Contact Form Server-Side Validation & Submission ---")
    # Invalid submission (missing required subject and message)
    invalid_resp = client.post('/contact/', {
        'name': 'Test User',
        'email': 'testuser@example.com',
        'phone': '08000000000',
    })
    assert invalid_resp.status_code == 200
    assert "Please fill in all required fields" in invalid_resp.content.decode('utf-8')

    # Valid submission
    test_subject = "Custom Wig Customization Enquiry"
    valid_resp = client.post('/contact/', {
        'name': 'Amina Bello',
        'email': 'amina.bello@example.com',
        'phone': '08123456789',
        'subject': test_subject,
        'message': 'Hello Bolbash team, I would like to inquire about booking a custom bridal wig melt consultation.',
    })
    assert valid_resp.status_code == 200
    assert "Message Sent!" in valid_resp.content.decode('utf-8')

    # Verify Database record creation
    submission = ContactSubmission.objects.filter(email='amina.bello@example.com', subject=test_subject).first()
    assert submission is not None
    assert submission.name == 'Amina Bello'
    assert submission.status == ContactSubmission.STATUS_NEW
    print("[OK] Contact form validation, DB record creation, and success banner verified.")

    # 5. ADMIN ENQUIRY MANAGEMENT PORTAL
    print("\n--- 5. Testing Admin Enquiry Management Portal ---")
    # Setup Superuser
    admin_user, created = User.objects.get_or_create(
        username='admin_test_user',
        defaults={'email': 'admin@bolbash.com', 'is_staff': True, 'is_superuser': True}
    )
    if created:
        admin_user.set_password('AdminPass123!')
        admin_user.save()

    client.force_login(admin_user)

    # View enquiry list
    response_admin = client.get('/admin-portal/enquiries/')
    assert response_admin.status_code == 200
    content_admin = response_admin.content.decode('utf-8')
    assert "Amina Bello" in content_admin
    assert "Custom Wig Customization Enquiry" in content_admin
    print("[OK] Admin enquiry list view accessible and displaying submitted enquiry.")

    # Update enquiry status
    status_update_resp = client.post(f'/admin-portal/enquiries/{submission.pk}/update-status/', {
        'status': ContactSubmission.STATUS_RESPONDED
    })
    assert status_update_resp.status_code == 302
    submission.refresh_from_db()
    assert submission.status == ContactSubmission.STATUS_RESPONDED
    print("[OK] Admin enquiry status update endpoint verified.")

    # 6. GLOBAL NAVIGATION LINKS
    print("\n--- 6. Testing Header & Footer Navigation Links ---")
    response_home = client.get('/')
    content_home = response_home.content.decode('utf-8')
    assert "/gallery/" in content_home
    assert "/contact/" in content_home
    print("[OK] Header and Footer links for Gallery and Contact verified.")

    # 7. DJANGO SYSTEM CHECK
    print("\n--- 7. Testing Django System Check ---")
    call_command('check')
    print("[OK] Django System Check identified 0 issues.")

    print("\n=== ALL GALLERY & CONTACT EXPERIENCE TESTS PASSED SUCCESSFULLY! ===")


if __name__ == '__main__':
    test_gallery_and_contact_experience()
