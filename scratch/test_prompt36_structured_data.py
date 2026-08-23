import os
import sys
import re
import json
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
    print("STARTING TEST SUITE FOR PHASE 10 — STRUCTURED DATA (JSON-LD)")
    print("==================================================")

    client = Client()

    # Dynamic objects
    svc_cat = ServiceCategory.objects.first() or ServiceCategory.objects.create(name="LD Hair Category")
    svc = Service.objects.filter(active=True).first()
    if not svc:
        svc = Service.objects.create(
            name="LD Frontal Styling",
            slug="ld-frontal-styling",
            category=svc_cat,
            short_description="Short desc",
            description="Full desc",
            price=20000.00,
            active=True
        )

    crs_cat = CourseCategory.objects.first() or CourseCategory.objects.create(name="LD Academy Category")
    crs = Course.objects.filter(active=True).first()
    if not crs:
        crs = Course.objects.create(
            category=crs_cat,
            title="LD Wig Masterclass",
            slug="ld-wig-masterclass",
            short_description="Short desc",
            full_description="Full desc",
            price=50000.00,
            active=True
        )

    prd_cat = ProductCategory.objects.first() or ProductCategory.objects.create(name="LD Shop Category")
    prd = Product.objects.filter(is_active=True).first()
    if not prd:
        prd = Product.objects.create(
            category=prd_cat,
            name="LD Hair Oil",
            slug="ld-hair-oil",
            short_description="Short desc",
            full_description="Full desc",
            price=3500.00,
            stock_quantity=15,
            is_active=True
        )

    test_targets = [
        ('core:index', {}, 'Home Page', 'BeautySalon'),
        ('core:service_detail', {'slug': svc.slug}, f'Service Detail ({svc.name})', 'Service'),
        ('academy:course_detail', {'slug': crs.slug}, f'Course Detail ({crs.title})', 'Course'),
        ('shop:product_detail', {'slug': prd.slug}, f'Product Detail ({prd.name})', 'Product'),
    ]

    json_ld_regex = re.compile(r'<script\s+type=["\']application/ld\+json["\']\s*>(.*?)</script>', re.IGNORECASE | re.DOTALL)

    verified_count = 0

    for url_name, kwargs, label, expected_type in test_targets:
        url = reverse(url_name, kwargs=kwargs)
        response = client.get(url)
        assert response.status_code == 200, f"Failed to load {label} at {url}"

        html = response.content.decode('utf-8')
        ld_matches = json_ld_regex.findall(html)

        assert len(ld_matches) > 0, f"No JSON-LD script tag found on {label} ({url})"

        # Parse JSON-LD content
        parsed_data = None
        for raw_json in ld_matches:
            data = json.loads(raw_json.strip())
            if data.get('@type') == expected_type:
                parsed_data = data
                break

        assert parsed_data is not None, f"Expected JSON-LD @type '{expected_type}' missing on {label} ({url})"
        assert parsed_data.get('@context') == "https://schema.org", f"Invalid @context on {label}: {parsed_data.get('@context')}"

        if expected_type == 'BeautySalon':
            assert parsed_data.get('name') == 'Bolbash Beauty Spot'
            assert 'address' in parsed_data
        elif expected_type == 'Service':
            assert parsed_data.get('name') == svc.name
            assert 'provider' in parsed_data
        elif expected_type == 'Course':
            assert parsed_data.get('name') == crs.title
            assert 'provider' in parsed_data
        elif expected_type == 'Product':
            assert parsed_data.get('name') == prd.name
            assert 'offers' in parsed_data

        verified_count += 1
        print(f"  [OK] {label} -> Verified JSON-LD Schema @type='{expected_type}' cleanly parsed.")

    print("==================================================")
    print(f"ALL {verified_count} ENTITIES PASSED JSON-LD STRUCTURED DATA AUDIT! (100% SUCCESS)")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
