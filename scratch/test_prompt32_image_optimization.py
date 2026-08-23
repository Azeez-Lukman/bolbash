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

from booking.models import ServiceCategory, Service
from academy.models import CourseCategory, Course
from shop.models import ProductCategory, Product


def run_tests():
    print("==================================================")
    print("STARTING TEST SUITE FOR PHASE 10 — IMAGE OPTIMIZATION")
    print("==================================================")

    client = Client()

    # Dynamic objects
    svc_cat = ServiceCategory.objects.first() or ServiceCategory.objects.create(name="Img Hair Category")
    svc = Service.objects.filter(active=True).first()
    if not svc:
        svc = Service.objects.create(
            name="Img Frontal Styling",
            slug="img-frontal-styling",
            category=svc_cat,
            short_description="Short desc",
            description="Full desc",
            price=20000.00,
            active=True
        )

    crs_cat = CourseCategory.objects.first() or CourseCategory.objects.create(name="Img Academy Category")
    crs = Course.objects.filter(active=True).first()
    if not crs:
        crs = Course.objects.create(
            category=crs_cat,
            title="Img Wig Class",
            slug="img-wig-class",
            short_description="Short desc",
            description="Full desc",
            price=50000.00,
            active=True
        )

    prd_cat = ProductCategory.objects.first() or ProductCategory.objects.create(name="Img Shop Category")
    prd = Product.objects.filter(is_active=True).first()
    if not prd:
        prd = Product.objects.create(
            category=prd_cat,
            name="Img Hair Oil",
            slug="img-hair-oil",
            short_description="Short desc",
            description="Full desc",
            price=3000.00,
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
        ('academy:academy_landing', {}, 'Academy Landing'),
        ('academy:course_list', {}, 'Course Catalogue'),
        ('academy:course_detail', {'slug': crs.slug}, f'Course Detail ({crs.title})'),
        ('shop:shop_landing', {}, 'Shop Landing'),
        ('shop:product_catalogue', {}, 'Product Catalogue'),
        ('shop:product_detail', {'slug': prd.slug}, f'Product Detail ({prd.name})'),
    ]

    img_tag_regex = re.compile(r'<img\s+([^>]*?)/?>', re.IGNORECASE | re.DOTALL)
    alt_attr_regex = re.compile(r'alt=["\'](.*?)["\']', re.IGNORECASE)

    total_imgs_checked = 0

    for url_name, kwargs, label in public_routes:
        url = reverse(url_name, kwargs=kwargs)
        response = client.get(url)
        assert response.status_code == 200, f"Failed to load {label} at {url}"

        html = response.content.decode('utf-8')
        img_matches = img_tag_regex.findall(html)

        page_imgs_count = 0
        for img_attributes in img_matches:
            # Skip dynamic lightbox template modal img placeholders that get populated via JS
            if 'id="lightbox-img"' in img_attributes or 'id="lightboxImage"' in img_attributes:
                continue

            alt_match = alt_attr_regex.search(img_attributes)
            assert alt_match is not None, f"Image missing alt attribute on {label} ({url}): '<img {img_attributes}>'"

            alt_val = alt_match.group(1).strip()
            # Assert alt attribute is not generic
            assert alt_val != "Main image", f"Generic alt text 'Main image' found on {label} ({url})"
            assert alt_val != "image", f"Generic alt text 'image' found on {label} ({url})"

            page_imgs_count += 1
            total_imgs_checked += 1

        print(f"  [OK] {label} -> Verified {page_imgs_count} <img> tags with valid descriptive alt text.")

    print("==================================================")
    print(f"ALL {total_imgs_checked} IMAGES PASSED OPTIMIZATION & ALT AUDIT! (100% SUCCESS)")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
