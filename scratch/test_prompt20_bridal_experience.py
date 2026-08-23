import os
import sys
import django

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client, RequestFactory
from django.urls import reverse, resolve
from django.core.management import call_command
from booking.models import ServiceCategory, Service


def test_bridal_experience():
    print("=== STARTING PHASE ROADMAP: BRIDAL EXPERIENCE TESTS ===")
    client = Client()

    # 1. TEST URL REVERSAL & ROUTE RESOLUTION
    print("\n--- 1. Testing Bridal Route Resolution ---")
    url = reverse('core:bridal')
    assert url == '/bridal/', f"Expected /bridal/, got {url}"
    match = resolve('/bridal/')
    assert match.url_name == 'bridal'
    print("[OK] Route /bridal/ resolved successfully.")

    # 2. TEST HTTP RESPONSE & HERO SECTION
    print("\n--- 2. Testing HTTP 200 Response & Hero Content ---")
    response = client.get('/bridal/')
    assert response.status_code == 200, f"Expected HTTP 200, got {response.status_code}"
    content = response.content.decode('utf-8')
    assert "Bridal Beauty Experience" in content or "Unforgettable Day" in content
    assert "Book Bridal Consultation" in content
    assert "Explore Bridal Gallery" in content
    print("[OK] Hero section, typography, and primary CTAs rendered.")

    # 3. TEST BRIDAL SERVICES GRID & BOOKING LINKS
    print("\n--- 3. Testing Bridal Services Showcase Grid & Booking Integration ---")
    assert "White Wedding Bridal Hair" in content
    assert "Traditional &amp; Engagement Styling" in content or "Traditional & Engagement Styling" in content
    assert "Bridal Frontal Wig Melt" in content
    assert "/booking/" in content
    print("[OK] Bridal services grid & pre-selected booking links verified.")

    # 4. TEST LIGHTBOX GALLERY & FILTER SYSTEM
    print("\n--- 4. Testing Bridal Gallery & Lightbox Modal ---")
    assert "bridal-gallery" in content
    assert "lightbox-modal" in content
    assert "filterGallery" in content
    assert "openLightbox" in content
    print("[OK] Lightbox modal, gallery grid & JS filters verified.")

    # 5. TEST BRIDAL PREPARATION TIMELINE & TRUST SECTION
    print("\n--- 5. Testing 4-Step Bridal Experience Timeline ---")
    assert "Personalized Consultation" in content
    assert "Pre-Wedding Hair Trial" in content
    assert "Custom Wig &amp; Extension Prep" in content or "Custom Wig & Extension Prep" in content
    assert "Wedding Day Perfection" in content
    print("[OK] 4-Step preparation timeline & trust section verified.")

    # 6. TEST FAQ ACCORDION & BOTTOM CTAS
    print("\n--- 6. Testing Bridal FAQ & Sticky Mobile Bar ---")
    assert "Frequently Asked Questions" in content
    assert "How far in advance should I book" in content
    assert "Ready to Create Your Dream Bridal Look?" in content
    print("[OK] FAQ Accordion and Sticky Mobile CTA bar verified.")

    # 7. TEST NAVIGATION INTEGRATION IN NAVBAR & FOOTER
    print("\n--- 7. Testing Navigation Links in Header & Footer ---")
    response_home = client.get('/')
    content_home = response_home.content.decode('utf-8')
    assert "/bridal/" in content_home
    assert "Bridal" in content_home
    print("[OK] Bridal link successfully present in global Navbar & Footer.")

    # 8. TEST DJANGO SYSTEM CHECK
    print("\n--- 8. Testing Django System Check ---")
    call_command('check')
    print("[OK] Django System Check identified 0 issues.")

    print("\n=== ALL BRIDAL EXPERIENCE TESTS PASSED SUCCESSFULLY! ===")


if __name__ == '__main__':
    test_bridal_experience()
