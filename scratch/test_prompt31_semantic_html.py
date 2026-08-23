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
    print("STARTING TEST SUITE FOR PHASE 10 — SEMANTIC HTML")
    print("==================================================")

    client = Client()
    user_email = "semantic_tester@example.com"

    # Cleanup
    User.objects.filter(email=user_email).delete()

    user = User.objects.create_user(
        username=user_email,
        email=user_email,
        password="TesterPassword123!",
        first_name="Semantic",
        last_name="Tester"
    )

    # Dynamic objects
    svc_cat = ServiceCategory.objects.first() or ServiceCategory.objects.create(name="Semantic Hair Category")
    svc = Service.objects.filter(active=True).first()
    if not svc:
        svc = Service.objects.create(
            name="Semantic Wig Revamp",
            slug="semantic-wig-revamp",
            category=svc_cat,
            short_description="Full wig wash, deep conditioning, and restyling.",
            description="Full desc",
            price=25000.00,
            active=True
        )

    booking = Booking.objects.create(
        user=user,
        service=svc,
        customer_name="Semantic Tester",
        customer_phone="08012345678",
        customer_email=user_email,
        appointment_date=timezone.now().date(),
        appointment_time=datetime.time(14, 0),
        service_name_snapshot=svc.name,
        service_price_snapshot=svc.price,
        status=Booking.STATUS_CONFIRMED
    )

    crs_cat = CourseCategory.objects.first() or CourseCategory.objects.create(name="Semantic Academy Category")
    crs = Course.objects.filter(active=True).first()
    if not crs:
        crs = Course.objects.create(
            category=crs_cat,
            title="Professional Nail Artistry Diploma",
            slug="professional-nail-artistry-diploma",
            short_description="Comprehensive nail extension & manicure training.",
            description="Full desc",
            price=80000.00,
            active=True
        )

    prd_cat = ProductCategory.objects.first() or ProductCategory.objects.create(name="Semantic Shop Category")
    prd = Product.objects.filter(is_active=True).first()
    if not prd:
        prd = Product.objects.create(
            category=prd_cat,
            name="HD Lace Wig Cap Package",
            slug="hd-lace-wig-cap-package",
            short_description="Ultra-thin breathable HD lace wig caps.",
            description="Full desc",
            price=4500.00,
            stock_quantity=30,
            is_active=True
        )

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
    ]

    h1_regex = re.compile(r'<h1[\s>]', re.IGNORECASE)
    skip_link_regex = re.compile(r'href=["\']#main-content["\']', re.IGNORECASE)
    main_landmark_regex = re.compile(r'<main\s+id=["\']main-content["\']', re.IGNORECASE)

    verified_count = 0

    for url_name, kwargs, label in public_routes:
        if url_name == 'shop:checkout':
            client.post(reverse('shop:cart_add', kwargs={'product_id': prd.pk}), {'quantity': 1})

        url = reverse(url_name, kwargs=kwargs)
        response = client.get(url)
        assert response.status_code == 200, f"Failed to load {label} at {url}"

        html = response.content.decode('utf-8')

        # 1. Main landmark assertion
        assert main_landmark_regex.search(html) is not None, f"Landmark <main id=\"main-content\"> missing on {label} ({url})"
        assert 'role="main"' in html, f"Main role attribute role=\"main\" missing on {label} ({url})"

        # 2. Skip to content link assertion
        assert skip_link_regex.search(html) is not None, f"Skip to main content link missing on {label} ({url})"

        # 3. Header & Footer landmark assertions
        assert '<header' in html and 'role="banner"' in html, f"Header landmark <header role=\"banner\"> missing on {label}"
        assert '<footer' in html and 'role="contentinfo"' in html, f"Footer landmark <footer role=\"contentinfo\"> missing on {label}"

        # 4. Heading hierarchy assertion: Exactly 1 <h1> tag per page
        h1_matches = len(h1_regex.findall(html))
        assert h1_matches == 1, f"Expected exactly 1 <h1> tag on {label} ({url}), found {h1_matches}"

        verified_count += 1
        print(f"  [OK] {label} -> Landmark <main>, Skip Link, <h1> Count: {h1_matches}")

    print("==================================================")
    print(f"ALL {verified_count} PAGES PASSED SEMANTIC HTML & ACCESSIBILITY AUDIT! (100% SUCCESS)")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
