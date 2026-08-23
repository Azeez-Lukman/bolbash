import os
import sys
import re
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

from booking.models import ServiceCategory, Service, Booking
from academy.models import CourseCategory, Course
from shop.models import ProductCategory, Product


def run_tests():
    print("==================================================")
    print("STARTING TEST SUITE FOR PHASE 10 — META DESCRIPTIONS")
    print("==================================================")

    client = Client()
    user_email = "meta_tester@example.com"

    # Cleanup test user & data
    User.objects.filter(email=user_email).delete()

    user = User.objects.create_user(
        username=user_email,
        email=user_email,
        password="TesterPassword123!",
        first_name="Meta",
        last_name="Tester"
    )

    # Dynamic objects
    svc_cat = ServiceCategory.objects.first() or ServiceCategory.objects.create(name="Meta Hair Category")
    svc = Service.objects.filter(active=True).first()
    if not svc:
        svc = Service.objects.create(
            name="Meta Luxury Frontal Styling",
            slug="meta-luxury-frontal-styling",
            category=svc_cat,
            short_description="Bespoke frontal hair styling and lace melting service in Ibadan.",
            description="Full desc",
            price=35000.00,
            active=True
        )

    booking = Booking.objects.create(
        user=user,
        service=svc,
        customer_name="Meta Tester",
        customer_phone="08012345678",
        customer_email=user_email,
        appointment_date=timezone.now().date(),
        appointment_time=datetime.time(11, 0),
        service_name_snapshot=svc.name,
        service_price_snapshot=svc.price,
        status=Booking.STATUS_CONFIRMED
    )

    crs_cat = CourseCategory.objects.first() or CourseCategory.objects.create(name="Meta Academy Category")
    crs = Course.objects.filter(active=True).first()
    if not crs:
        crs = Course.objects.create(
            category=crs_cat,
            title="Lace Melt Artistry Masterclass",
            slug="lace-melt-artistry-masterclass",
            short_description="Master flawless frontal lace customization and melting techniques in Ibadan.",
            description="Comprehensive training",
            price=120000.00,
            active=True
        )

    prd_cat = ProductCategory.objects.first() or ProductCategory.objects.create(name="Meta Shop Category")
    prd = Product.objects.filter(is_active=True).first()
    if not prd:
        prd = Product.objects.create(
            category=prd_cat,
            name="Silk Infusion Hair Treatment",
            slug="silk-infusion-hair-treatment",
            short_description="Nourishing silk protein formula for natural and extension hair.",
            description="Full desc",
            price=8500.00,
            stock_quantity=15,
            is_active=True
        )

    # Routes to test
    public_routes = [
        ('core:index', {}, 'Home Page'),
        ('core:about', {}, 'About Us'),
        ('core:bridal', {}, 'Bridal Experience'),
        ('core:gallery', {}, 'Style Gallery'),
        ('core:contact', {}, 'Contact Us'),
        ('core:service_list', {}, 'Services Catalogue'),
        ('core:service_detail', {'slug': svc.slug}, f'Service Detail ({svc.name})'),
        ('core:reviews_showcase', {}, 'Reviews Showcase'),
        ('core:feedback', {}, 'Customer Feedback'),
        ('booking:booking_form', {}, 'Booking Form'),
        ('booking:booking_lookup', {}, 'Booking Lookup'),
        ('booking:booking_confirmation', {'reference': booking.reference}, f'Booking Confirmation ({booking.reference})'),
        ('academy:academy_landing', {}, 'Academy Landing'),
        ('academy:course_list', {}, 'Course Catalogue'),
        ('academy:course_detail', {'slug': crs.slug}, f'Course Detail ({crs.title})'),
        ('academy:verify_certificate', {}, 'Verify Certificate'),
        ('academy:login', {}, 'Student Login'),
        ('academy:register', {}, 'Student Register'),
        ('shop:shop_landing', {}, 'Shop Landing'),
        ('shop:product_catalogue', {}, 'Product Catalogue'),
        ('shop:product_detail', {'slug': prd.slug}, f'Product Detail ({prd.name})'),
        ('shop:cart_detail', {}, 'Cart Detail'),
        ('shop:checkout', {}, 'Shop Checkout'),
        ('accounts:login', {}, 'Customer Sign In'),
        ('accounts:register', {}, 'Customer Registration'),
        ('accounts:password_reset', {}, 'Password Reset'),
        ('accounts:password_reset_done', {}, 'Password Reset Done'),
    ]

    meta_desc_regex = re.compile(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']\s*/?>', re.IGNORECASE | re.DOTALL)

    verified_count = 0

    # 1. Verify Public & Dynamic Meta Descriptions
    for url_name, kwargs, label in public_routes:
        if url_name == 'shop:checkout':
            client.post(reverse('shop:cart_add', kwargs={'product_id': prd.pk}), {'quantity': 1})

        url = reverse(url_name, kwargs=kwargs)
        response = client.get(url)
        assert response.status_code == 200, f"Failed to load {label} at {url}"

        html = response.content.decode('utf-8')
        match = meta_desc_regex.search(html)
        assert match is not None, f"Meta description tag <meta name=\"description\"> missing on {label} ({url})"

        desc_text = match.group(1).strip()
        assert len(desc_text) >= 15, f"Meta description too short ({len(desc_text)} chars) on {label} ({url}): '{desc_text}'"
        assert len(desc_text) <= 350, f"Meta description too long ({len(desc_text)} chars) on {label} ({url})"

        # Dynamic meta description evaluation assertions
        if url_name == 'core:service_detail':
            assert svc.short_description in desc_text or svc.name in desc_text, f"Dynamic service info missing in meta description '{desc_text}'"
        elif url_name == 'academy:course_detail':
            assert crs.short_description in desc_text or crs.title in desc_text, f"Dynamic course info missing in meta description '{desc_text}'"
        elif url_name == 'shop:product_detail':
            assert prd.short_description in desc_text or prd.name in desc_text, f"Dynamic product info missing in meta description '{desc_text}'"

        verified_count += 1
        print(f"  [OK] {label} -> Meta Description ({len(desc_text)} chars): '{desc_text[:60]}...'")

    print(f"\nPhase 1: Verified {verified_count} public & dynamic meta descriptions successfully.")

    # 2. Verify Authenticated Customer Account Meta Descriptions
    client.login(username=user_email, password="TesterPassword123!")

    account_routes = [
        ('accounts:dashboard', {}, 'Customer Dashboard'),
        ('accounts:upcoming_appointments', {}, 'Upcoming Appointments'),
        ('accounts:appointment_history', {}, 'Appointment History'),
        ('accounts:payment_history', {}, 'Payment History Ledger'),
        ('accounts:profile', {}, 'Profile Management'),
        ('accounts:security', {}, 'Account Security'),
    ]

    for url_name, kwargs, label in account_routes:
        url = reverse(url_name, kwargs=kwargs)
        response = client.get(url)
        assert response.status_code == 200, f"Failed to load {label} at {url}"

        html = response.content.decode('utf-8')
        match = meta_desc_regex.search(html)
        assert match is not None, f"Meta description tag missing on {label} ({url})"

        desc_text = match.group(1).strip()
        assert len(desc_text) >= 15, f"Meta description too short on {label} ({url}): '{desc_text}'"

        verified_count += 1
        print(f"  [OK] {label} -> Meta Description ({len(desc_text)} chars): '{desc_text[:60]}...'")

    print(f"\nPhase 2: Verified {len(account_routes)} authenticated customer account meta descriptions.")

    print("==================================================")
    print(f"ALL {verified_count} META DESCRIPTIONS VERIFIED CLEANLY! (100% SUCCESS)")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
