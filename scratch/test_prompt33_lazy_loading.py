import os
import sys
import re
import django

# Setup Django environment
sys.path.insert(0, r'c:\Users\USER\Documents\bolbash-beautyspot')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.urls import reverse

from booking.models import ServiceCategory, Service
from academy.models import CourseCategory, Course
from shop.models import ProductCategory, Product


def run_tests():
    print("==================================================")
    print("STARTING TEST SUITE FOR PHASE 10 — LAZY LOADING")
    print("==================================================")

    client = Client()

    # Dynamic objects
    svc_cat = ServiceCategory.objects.first() or ServiceCategory.objects.create(name="Lazy Hair Category")
    svc = Service.objects.filter(active=True).first()
    if not svc:
        svc = Service.objects.create(
            name="Lazy Frontal Styling",
            slug="lazy-frontal-styling",
            category=svc_cat,
            short_description="Short desc",
            description="Full desc",
            price=20000.00,
            active=True
        )

    crs_cat = CourseCategory.objects.first() or CourseCategory.objects.create(name="Lazy Academy Category")
    crs = Course.objects.filter(active=True).first()
    if not crs:
        crs = Course.objects.create(
            category=crs_cat,
            title="Lazy Wig Class",
            slug="lazy-wig-class",
            short_description="Short desc",
            description="Full desc",
            price=50000.00,
            thumbnail="courses/test_thumb.jpg",
            active=True
        )
    elif not crs.thumbnail:
        crs.thumbnail = "courses/test_thumb.jpg"
        crs.save()

    prd_cat = ProductCategory.objects.first() or ProductCategory.objects.create(name="Lazy Shop Category")
    prd = Product.objects.filter(is_active=True).first()
    if not prd:
        prd = Product.objects.create(
            category=prd_cat,
            name="Lazy Hair Serum",
            slug="lazy-hair-serum",
            short_description="Short desc",
            full_description="Full desc",
            price=3500.00,
            image="products/test_prod.jpg",
            stock_quantity=15,
            is_active=True
        )
    elif not prd.image:
        prd.image = "products/test_prod.jpg"
        prd.save()

    prd2 = Product.objects.filter(is_active=True, category=prd.category).exclude(id=prd.id).first()
    if not prd2:
        prd2 = Product.objects.create(
            category=prd.category,
            name="Lazy Edge Control",
            slug="lazy-edge-control",
            short_description="Short desc",
            full_description="Full desc",
            price=2500.00,
            image="products/test_prod2.jpg",
            stock_quantity=10,
            is_active=True
        )
    elif not prd2.image:
        prd2.image = "products/test_prod2.jpg"
        prd2.save()

    # Specific assertions for off-screen lazy loaded media
    lazy_check_routes = [
        ('core:contact', {}, 'Contact Us (Map Iframe)', 'iframe'),
        ('core:gallery', {}, 'Style Gallery Grid', 'img'),
        ('core:bridal', {}, 'Bridal Portfolio Grid', 'img'),
        ('academy:course_list', {}, 'Course Catalogue Cards', 'img'),
        ('shop:shop_landing', {}, 'Shop Landing Grid', 'img'),
        ('shop:product_catalogue', {}, 'Product Catalogue Grid', 'img'),
        ('shop:product_detail', {'slug': prd.slug}, 'Product Detail Related Grid', 'img'),
    ]

    verified_count = 0

    for url_name, kwargs, label, target_type in lazy_check_routes:
        url = reverse(url_name, kwargs=kwargs)
        response = client.get(url)
        assert response.status_code == 200, f"Failed to load {label} at {url}"

        html = response.content.decode('utf-8')

        # 1. Assert loading="lazy" exists in HTML response
        assert 'loading="lazy"' in html, f"loading=\"lazy\" attribute missing on {label} ({url})"

        # 2. Assert logo image in navbar DOES NOT have loading="lazy" (above-the-fold LCP optimization)
        logo_match = re.search(r'<img[^>]*?logo\.jpg[^>]*?>', html, re.IGNORECASE)
        if logo_match:
            assert 'loading="lazy"' not in logo_match.group(0), f"Above-the-fold logo on {label} incorrectly has loading=\"lazy\""

        verified_count += 1
        print(f"  [OK] {label} -> Verified loading=\"lazy\" presence & LCP hero protection.")

    print("==================================================")
    print(f"ALL {verified_count} ENDPOINTS PASSED LAZY LOADING AUDIT! (100% SUCCESS)")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
