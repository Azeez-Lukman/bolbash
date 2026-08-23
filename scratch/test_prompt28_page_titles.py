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

from booking.models import ServiceCategory, Service, Booking
from academy.models import CourseCategory, Course
from shop.models import ProductCategory, Product, Order
from django.utils import timezone
import datetime


def run_tests():
    print("==================================================")
    print("STARTING TEST SUITE FOR PHASE 10 — PAGE TITLES")
    print("==================================================")

    client = Client()
    user_email = "title_tester@example.com"

    # Cleanup test user & database records
    User.objects.filter(email=user_email).delete()

    user = User.objects.create_user(
        username=user_email,
        email=user_email,
        password="TesterPassword123!",
        first_name="Title",
        last_name="Tester"
    )

    # Ensure dynamic objects exist
    svc_cat = ServiceCategory.objects.first() or ServiceCategory.objects.create(name="Title Hair Category")
    svc = Service.objects.filter(active=True).first()
    if not svc:
        svc = Service.objects.create(
            name="Title Luxury Lace Melt",
            slug="title-luxury-lace-melt",
            category=svc_cat,
            short_description="Short desc",
            description="Full desc",
            price=30000.00,
            active=True
        )

    booking = Booking.objects.create(
        user=user,
        service=svc,
        customer_name="Title Tester",
        customer_phone="08012345678",
        customer_email=user_email,
        appointment_date=timezone.now().date(),
        appointment_time=datetime.time(10, 0),
        service_name_snapshot=svc.name,
        service_price_snapshot=svc.price,
        status=Booking.STATUS_CONFIRMED
    )

    crs_cat = CourseCategory.objects.first() or CourseCategory.objects.create(name="Title Academy Category")
    crs = Course.objects.filter(active=True).first()
    if not crs:
        crs = Course.objects.create(
            category=crs_cat,
            title="Masterclass in Wig Construction",
            slug="masterclass-wig-construction",
            short_description="Learn wig making from scratch",
            description="Comprehensive training program",
            price=150000.00,
            active=True
        )

    prd_cat = ProductCategory.objects.first() or ProductCategory.objects.create(name="Title Shop Category")
    prd = Product.objects.filter(is_active=True).first()
    if not prd:
        prd = Product.objects.create(
            category=prd_cat,
            name="Organic Lace Melt Spray",
            slug="organic-lace-melt-spray",
            short_description="Premium lace adhesive holding spray",
            description="Full description",
            price=12000.00,
            stock_quantity=20,
            is_active=True
        )

    # Routes checklist to verify
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
    ]

    title_regex = re.compile(r'<title>(.*?)</title>', re.IGNORECASE | re.DOTALL)

    verified_count = 0

    # 1. Verify Public & Dynamic Route Titles
    for url_name, kwargs, label in public_routes:
        url = reverse(url_name, kwargs=kwargs)

        if url_name == 'shop:checkout':
            # Add item to cart first so checkout loads HTTP 200
            client.post(reverse('shop:cart_add', kwargs={'product_id': prd.pk}), {'quantity': 1})

        response = client.get(url)
        assert response.status_code == 200, f"Failed to load {label} at {url}"

        html = response.content.decode('utf-8')
        match = title_regex.search(html)
        assert match is not None, f"Page title tag <title> missing on {label} ({url})"

        title_text = match.group(1).strip()
        assert len(title_text) > 0, f"Page title is empty on {label} ({url})"
        assert "Bolbash" in title_text, f"Brand name 'Bolbash' missing in title '{title_text}' for {label}"
        assert "None" not in title_text, f"Title contains 'None' on {label}: '{title_text}'"
        assert "null" not in title_text, f"Title contains 'null' on {label}: '{title_text}'"

        # Dynamic variable assertions
        if url_name == 'core:service_detail':
            assert svc.name in title_text, f"Dynamic service name '{svc.name}' missing in title '{title_text}'"
        elif url_name == 'academy:course_detail':
            assert crs.title in title_text, f"Dynamic course title '{crs.title}' missing in title '{title_text}'"
        elif url_name == 'shop:product_detail':
            assert prd.name in title_text, f"Dynamic product name '{prd.name}' missing in title '{title_text}'"
        elif url_name == 'booking:booking_confirmation':
            assert booking.reference in title_text, f"Dynamic booking reference '{booking.reference}' missing in title '{title_text}'"

        verified_count += 1
        print(f"  [OK] {label} -> Title: '{title_text}'")

    print(f"\nPhase 1: Verified {verified_count} public & dynamic page titles successfully.")

    # 2. Verify Authenticated Customer Account Page Titles
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
        match = title_regex.search(html)
        assert match is not None, f"Page title tag <title> missing on {label} ({url})"

        title_text = match.group(1).strip()
        assert len(title_text) > 0, f"Page title is empty on {label} ({url})"
        assert "Bolbash" in title_text, f"Brand name 'Bolbash' missing in title '{title_text}' for {label}"

        verified_count += 1
        print(f"  [OK] {label} -> Title: '{title_text}'")

    print(f"\nPhase 2: Verified {len(account_routes)} authenticated customer account page titles.")

    print("==================================================")
    print(f"ALL {verified_count} PAGE TITLES VERIFIED CLEANLY! (100% SUCCESS)")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
