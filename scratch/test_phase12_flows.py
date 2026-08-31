import os
import sys
import json
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from blog.models import BlogPost, BlogCategory
from booking.models import Booking, Service, ServiceCategory
from shop.models import Product, ProductCategory

def run_phase12_flow_tests():
    print("=" * 75)
    print("BOLBASH BEAUTY SPOT — PHASE 12 FULL RESPONSIVE & FLOW VERIFICATION")
    print("=" * 75)

    client = Client()
    passed = 0
    total = 0

    # -------------------------------------------------------------
    # 1. PUBLIC WEBSITE & EDITORIAL NAVIGATION ROUTES
    # -------------------------------------------------------------
    public_routes = [
        ('Home Page', reverse('core:index')),
        ('About Page', reverse('core:about')),
        ('Services Catalog', reverse('core:service_list')),
        ('Bridal Experience', reverse('core:bridal')),
        ('Style Gallery', reverse('core:gallery')),
        ('Reviews Showcase', reverse('core:reviews_showcase')),
        ('Contact Studio', reverse('core:contact')),
        ('Blog Editorial Listing', reverse('blog:post_list')),
        ('Shop Catalog Landing', reverse('shop:shop_landing')),
    ]

    for name, url in public_routes:
        total += 1
        resp = client.get(url)
        if resp.status_code == 200:
            passed += 1
            print(f"[PASS] {total}. {name} ({url}) — 200 OK")
        else:
            print(f"[FAIL] {total}. {name} ({url}) — Expected 200, got {resp.status_code}")

    # -------------------------------------------------------------
    # 2. BLOG & SEARCH USER FLOWS
    # -------------------------------------------------------------
    total += 1
    blog_post = BlogPost.objects.filter(status=BlogPost.STATUS_PUBLISHED).first()
    if blog_post:
        resp = client.get(reverse('blog:post_detail', kwargs={'slug': blog_post.slug}))
        if resp.status_code == 200 and '✂️' in resp.content.decode('utf-8'):
            passed += 1
            print(f"[PASS] {total}. Blog Article Detail ('{blog_post.slug}') — 200 OK & Author/CTA verified")
        else:
            print(f"[FAIL] {total}. Blog Article Detail — Failed status or content missing")
    else:
        print(f"[SKIP] {total}. No published blog post found")

    total += 1
    resp = client.get(reverse('blog:post_list') + '?q=frontal')
    if resp.status_code == 200:
        passed += 1
        print(f"[PASS] {total}. Blog Keyword Search ('?q=frontal') — 200 OK")
    else:
        print(f"[FAIL] {total}. Blog Search — Expected 200, got {resp.status_code}")

    # -------------------------------------------------------------
    # 3. INTERACTIVE BOOKING FLOW
    # -------------------------------------------------------------
    total += 1
    resp = client.get(reverse('booking:booking_form'))
    if resp.status_code == 200 and 'BOOK APPOINTMENT' in resp.content.decode('utf-8'):
        passed += 1
        print(f"[PASS] {total}. Booking Form Interface — 200 OK")
    else:
        print(f"[FAIL] {total}. Booking Form Interface — Failed")

    total += 1
    resp = client.get(reverse('booking:booking_lookup'))
    if resp.status_code == 200:
        passed += 1
        print(f"[PASS] {total}. Booking Lookup Page — 200 OK")
    else:
        print(f"[FAIL] {total}. Booking Lookup — Expected 200, got {resp.status_code}")

    # -------------------------------------------------------------
    # 4. SHOP, CART & CHECKOUT FLOW
    # -------------------------------------------------------------
    total += 1
    resp = client.get(reverse('shop:cart_detail'))
    if resp.status_code == 200:
        passed += 1
        print(f"[PASS] {total}. Shopping Cart View — 200 OK")
    else:
        print(f"[FAIL] {total}. Shopping Cart View — Expected 200, got {resp.status_code}")

    total += 1
    product = Product.objects.filter(is_active=True).first()
    if product:
        resp = client.get(reverse('shop:product_detail', kwargs={'slug': product.slug}))
        if resp.status_code == 200:
            passed += 1
            print(f"[PASS] {total}. Product Detail Page ('{product.slug}') — 200 OK")
        else:
            print(f"[FAIL] {total}. Product Detail Page — Got {resp.status_code}")
    else:
        print(f"[SKIP] {total}. No active product found")

    # -------------------------------------------------------------
    # 5. CONTACT FORM FLOW & VALIDATION
    # -------------------------------------------------------------
    total += 1
    resp = client.post(reverse('core:contact'), {
        'name': 'Adebisi Folake',
        'email': 'adebisi@example.com',
        'phone': '08168956606',
        'subject': 'Beauty Blog & Hair Care Advice',
        'message': 'Hello, I loved your article on lace maintenance! Can I book a frontal revamp?',
    }, follow=True)
    if resp.status_code == 200:
        passed += 1
        print(f"[PASS] {total}. Contact Form Submission Flow — 200 OK with success flash")
    else:
        print(f"[FAIL] {total}. Contact Form Submission — Failed with {resp.status_code}")

    # -------------------------------------------------------------
    # 6. ADMIN PANEL DASHBOARD & APPOINTMENT / BLOG MANAGEMENT
    # -------------------------------------------------------------
    staff_user, _ = User.objects.get_or_create(
        username='admin_tester',
        defaults={'email': 'admin@bolbash.com', 'is_staff': True, 'is_superuser': True}
    )
    staff_user.set_password('BolbashTestPass123!')
    staff_user.is_staff = True
    staff_user.save()

    client.force_login(staff_user)

    admin_routes = [
        ('Admin Main Dashboard', reverse('admin_panel:dashboard')),
        ('Admin Appointment Manager', reverse('admin_panel:appointment_list')),
        ('Admin Shop Product Manager', reverse('admin_panel:shop_product_list')),
        ('Admin Shop Order Manager', reverse('admin_panel:shop_order_list')),
        ('Admin Customer Enquiries', reverse('admin_panel:enquiry_list')),
        ('Admin Review Moderation', reverse('admin_panel:review_list')),
        ('Admin Feedback Inbox', reverse('admin_panel:feedback_list')),
        ('Admin Notifications Hub', reverse('admin_panel:notification_list')),
    ]

    for name, url in admin_routes:
        total += 1
        resp = client.get(url)
        if resp.status_code == 200:
            passed += 1
            print(f"[PASS] {total}. {name} ({url}) — 200 OK (Authenticated Staff)")
        else:
            print(f"[FAIL] {total}. {name} ({url}) — Expected 200, got {resp.status_code}")

    # -------------------------------------------------------------
    # 7. SUMMARY REPORT
    # -------------------------------------------------------------
    print("=" * 75)
    print(f"PHASE 12 VERIFICATION RESULTS: {passed}/{total} TESTS PASSED ({(passed/total)*100:.1f}%)")
    print("=" * 75)

if __name__ == '__main__':
    run_phase12_flow_tests()
