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
    print("STARTING TEST SUITE FOR PHASE 10 — OPEN GRAPH METADATA")
    print("==================================================")

    client = Client()
    user_email = "og_tester@example.com"

    # Cleanup
    User.objects.filter(email=user_email).delete()

    user = User.objects.create_user(
        username=user_email,
        email=user_email,
        password="TesterPassword123!",
        first_name="OG",
        last_name="Tester"
    )

    # Dynamic objects
    svc_cat = ServiceCategory.objects.first() or ServiceCategory.objects.create(name="OG Hair Category")
    svc = Service.objects.filter(active=True).first()
    if not svc:
        svc = Service.objects.create(
            name="OG Frontal Installation",
            slug="og-frontal-installation",
            category=svc_cat,
            short_description="OG Frontal hair styling service.",
            description="Full desc",
            price=40000.00,
            active=True
        )

    booking = Booking.objects.create(
        user=user,
        service=svc,
        customer_name="OG Tester",
        customer_phone="08012345678",
        customer_email=user_email,
        appointment_date=timezone.now().date(),
        appointment_time=datetime.time(12, 0),
        service_name_snapshot=svc.name,
        service_price_snapshot=svc.price,
        status=Booking.STATUS_CONFIRMED
    )

    crs_cat = CourseCategory.objects.first() or CourseCategory.objects.create(name="OG Academy Category")
    crs = Course.objects.filter(active=True).first()
    if not crs:
        crs = Course.objects.create(
            category=crs_cat,
            title="OG Wig Making Masterclass",
            slug="og-wig-making-masterclass",
            short_description="OG Wig making course.",
            description="Full desc",
            price=100000.00,
            active=True
        )

    prd_cat = ProductCategory.objects.first() or ProductCategory.objects.create(name="OG Shop Category")
    prd = Product.objects.filter(is_active=True).first()
    if not prd:
        prd = Product.objects.create(
            category=prd_cat,
            name="OG Edge Control Gel",
            slug="og-edge-control-gel",
            short_description="OG Edge control holding gel.",
            description="Full desc",
            price=5000.00,
            stock_quantity=10,
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

    og_site_name_re = re.compile(r'<meta\s+property=["\']og:site_name["\']\s+content=["\'](.*?)["\']\s*/?>', re.I)
    og_type_re = re.compile(r'<meta\s+property=["\']og:type["\']\s+content=["\'](.*?)["\']\s*/?>', re.I)
    og_title_re = re.compile(r'<meta\s+property=["\']og:title["\']\s+content=["\'](.*?)["\']\s*/?>', re.I)
    og_desc_re = re.compile(r'<meta\s+property=["\']og:description["\']\s+content=["\'](.*?)["\']\s*/?>', re.I)
    og_image_re = re.compile(r'<meta\s+property=["\']og:image["\']\s+content=["\'](.*?)["\']\s*/?>', re.I)
    og_url_re = re.compile(r'<meta\s+property=["\']og:url["\']\s+content=["\'](.*?)["\']\s*/?>', re.I)

    tw_card_re = re.compile(r'<meta\s+name=["\']twitter:card["\']\s+content=["\'](.*?)["\']\s*/?>', re.I)
    tw_title_re = re.compile(r'<meta\s+name=["\']twitter:title["\']\s+content=["\'](.*?)["\']\s*/?>', re.I)
    tw_desc_re = re.compile(r'<meta\s+name=["\']twitter:description["\']\s+content=["\'](.*?)["\']\s*/?>', re.I)
    tw_image_re = re.compile(r'<meta\s+name=["\']twitter:image["\']\s+content=["\'](.*?)["\']\s*/?>', re.I)

    verified_count = 0

    for url_name, kwargs, label in public_routes:
        if url_name == 'shop:checkout':
            client.post(reverse('shop:cart_add', kwargs={'product_id': prd.pk}), {'quantity': 1})

        url = reverse(url_name, kwargs=kwargs)
        response = client.get(url)
        assert response.status_code == 200, f"Failed to load {label} at {url}"

        html = response.content.decode('utf-8')

        site_name_m = og_site_name_re.search(html)
        type_m = og_type_re.search(html)
        title_m = og_title_re.search(html)
        desc_m = og_desc_re.search(html)
        image_m = og_image_re.search(html)
        url_m = og_url_re.search(html)

        tw_card_m = tw_card_re.search(html)
        tw_title_m = tw_title_re.search(html)
        tw_desc_m = tw_desc_re.search(html)
        tw_image_m = tw_image_re.search(html)

        assert site_name_m is not None, f"og:site_name missing on {label}"
        assert type_m is not None, f"og:type missing on {label}"
        assert title_m is not None, f"og:title missing on {label}"
        assert desc_m is not None, f"og:description missing on {label}"
        assert image_m is not None, f"og:image missing on {label}"
        assert url_m is not None, f"og:url missing on {label}"

        assert tw_card_m is not None, f"twitter:card missing on {label}"
        assert tw_title_m is not None, f"twitter:title missing on {label}"
        assert tw_desc_m is not None, f"twitter:description missing on {label}"
        assert tw_image_m is not None, f"twitter:image missing on {label}"

        assert site_name_m.group(1).strip() == "Bolbash Beauty Spot", f"Invalid og:site_name on {label}"
        assert tw_card_m.group(1).strip() == "summary_large_image", f"Invalid twitter:card on {label}"

        # Specific og:type assertions
        if url_name == 'core:service_detail':
            assert type_m.group(1).strip() == "article", f"Expected og:type=article for service_detail, got {type_m.group(1)}"
        elif url_name == 'academy:course_detail':
            assert type_m.group(1).strip() == "article", f"Expected og:type=article for course_detail, got {type_m.group(1)}"
        elif url_name == 'shop:product_detail':
            assert type_m.group(1).strip() == "product", f"Expected og:type=product for product_detail, got {type_m.group(1)}"

        verified_count += 1
        print(f"  [OK] {label} -> og:type='{type_m.group(1)}', og:title='{title_m.group(1)[:40]}...'")

    print("==================================================")
    print(f"ALL {verified_count} OPEN GRAPH & TWITTER CARD META TAGS VERIFIED CLEANLY! (100% SUCCESS)")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
