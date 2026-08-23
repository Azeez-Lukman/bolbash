import os
import sys
import django
from decimal import Decimal
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from django.urls import reverse

from booking.models import ServiceCategory, Service, BusinessHours, BlockedDate, Booking
from academy.models import CourseCategory, Course, Module, Lesson, Enrollment, Certificate, StudentProfile
from shop.models import ProductCategory, Product, Order, OrderItem
from payments.models import Payment


def test_admin_panel():
    print("=== STARTING PHASE 7 ADMINISTRATION SYSTEM TEST SUITE ===")
    client = Client()

    # 1. SETUP USERS
    admin_user, _ = User.objects.get_or_create(
        username='admin_test',
        defaults={'email': 'admin@bolbash.com', 'is_staff': True, 'is_superuser': True}
    )
    admin_user.set_password('AdminPass123!')
    admin_user.save()

    regular_user, _ = User.objects.get_or_create(
        username='customer_test',
        defaults={'email': 'customer@example.com', 'is_staff': False, 'is_superuser': False}
    )
    regular_user.set_password('CustomerPass123!')
    regular_user.save()

    print("[OK] Test User Accounts Ready.")

    # 2. TEST SECURITY & ACCESS CONTROL
    print("\n--- Testing Access Control & Security ---")
    # Unauthenticated access
    client.logout()
    res = client.get('/admin-portal/')
    assert res.status_code == 302, f"Expected 302 redirect for anonymous user, got {res.status_code}"
    print("[OK] Unauthenticated request redirected to login.")

    # Regular Customer access
    client.login(username='customer_test', password='CustomerPass123!')
    res = client.get('/admin-portal/')
    assert res.status_code == 403, f"Expected 403 Forbidden for non-staff user, got {res.status_code}"
    assert "Administrative Access Restricted" in res.content.decode('utf-8')
    print("[OK] Non-staff user blocked with professional 403 Access Denied page.")

    # Admin access
    client.login(username='admin_test', password='AdminPass123!')
    res = client.get('/admin-portal/')
    assert res.status_code == 200, f"Expected 200 OK for admin staff user, got {res.status_code}"
    assert "Business Overview Dashboard" in res.content.decode('utf-8')
    print("[OK] Staff admin authenticated successfully to Central Dashboard.")

    # 3. TEST APPOINTMENT MANAGEMENT
    print("\n--- Testing Appointment Management ---")
    cat, _ = ServiceCategory.objects.get_or_create(name="Admin Test Category", slug="admin-test-cat")
    svc, _ = Service.objects.get_or_create(
        name="Admin Test Service",
        slug="admin-test-service",
        category=cat,
        defaults={'short_description': 'Test', 'description': 'Test', 'price': Decimal('15000.00'), 'duration': 60}
    )

    Booking.objects.filter(customer_email="alice@test.com").delete()

    booking = Booking.objects.create(
        customer_name="Alice AdminTest",
        customer_email="alice@test.com",
        customer_phone="08012345678",
        service=svc,
        service_name_snapshot=svc.name,
        service_price_snapshot=Decimal('15000.00'),
        amount_due=Decimal('5000.00'),
        appointment_date=date.today() + timedelta(days=2),
        appointment_time="10:00:00",
        status=Booking.STATUS_PENDING_PAYMENT
    )
    print(f"[OK] Created test booking #{booking.reference}")

    # List view
    res = client.get(reverse('admin_panel:appointment_list'))
    assert res.status_code == 200
    assert booking.reference in res.content.decode('utf-8')
    print("[OK] Booking appears in appointment list view.")

    # Detail & status update
    res = client.post(reverse('admin_panel:appointment_detail', kwargs={'reference': booking.reference}), {
        'status': Booking.STATUS_CONFIRMED,
        'payment_status': Booking.PAYMENT_PAID,
        'customer_note': 'Verified manually by admin'
    })
    assert res.status_code == 302
    booking.refresh_from_db()
    assert booking.status == Booking.STATUS_CONFIRMED
    assert booking.payment_status == Booking.PAYMENT_PAID
    print("[OK] Updated booking status to CONFIRMED & PAID.")

    # Reschedule appointment
    new_date = date.today() + timedelta(days=5)
    res = client.post(reverse('admin_panel:appointment_reschedule', kwargs={'reference': booking.reference}), {
        'appointment_date': new_date.isoformat(),
        'appointment_time': '14:00:00'
    })
    assert res.status_code == 302
    booking.refresh_from_db()
    assert booking.appointment_date == new_date
    assert str(booking.appointment_time) == '14:00:00'
    print("[OK] Booking rescheduled successfully.")

    # Blocked dates management
    target_blocked_date = date.today() + timedelta(days=10)
    BlockedDate.objects.filter(date=target_blocked_date).delete()

    res = client.post(reverse('admin_panel:blocked_dates'), {
        'action': 'add',
        'date': target_blocked_date.isoformat(),
        'reason': 'Salon Private Event',
        'is_active': 'on'
    })
    assert res.status_code == 302
    assert BlockedDate.objects.filter(date=date.today() + timedelta(days=10)).exists()
    print("[OK] Calendar date blocked successfully.")

    # 4. TEST CUSTOMER MANAGEMENT
    print("\n--- Testing Customer Management ---")
    res = client.get(reverse('admin_panel:customer_list'))
    assert res.status_code == 200
    assert regular_user.username in res.content.decode('utf-8')
    print("[OK] Customer directory loaded successfully.")

    # Customer details
    res = client.get(reverse('admin_panel:customer_detail', kwargs={'user_id': regular_user.id}))
    assert res.status_code == 200
    assert regular_user.email in res.content.decode('utf-8')
    print("[OK] Customer profile details loaded.")

    # Toggle active/suspended
    res = client.post(reverse('admin_panel:customer_detail', kwargs={'user_id': regular_user.id}), {
        'toggle_active': '1'
    })
    assert res.status_code == 302
    regular_user.refresh_from_db()
    assert regular_user.is_active is False
    print("[OK] Customer account suspended successfully.")

    # Reactivate
    res = client.post(reverse('admin_panel:customer_detail', kwargs={'user_id': regular_user.id}), {
        'toggle_active': '1'
    })
    regular_user.refresh_from_db()
    assert regular_user.is_active is True
    print("[OK] Customer account reactivated successfully.")

    # 5. TEST ACADEMY MANAGEMENT
    print("\n--- Testing Academy Management ---")
    ac_cat, _ = CourseCategory.objects.get_or_create(name="Admin Category", slug="admin-cat")
    Course.objects.filter(title='Admin Masterclass').delete()

    res = client.post(reverse('admin_panel:academy_course_create'), {
        'title': 'Admin Masterclass',
        'category': ac_cat.id,
        'short_description': 'Short intro',
        'full_description': 'Full syllabus',
        'duration': '2 Weeks',
        'price': '45000.00',
        'format_type': Course.FORMAT_PHYSICAL,
        'learning_outcomes': 'Skill 1\nSkill 2',
        'target_audience': 'Beginners',
        'prerequisites': 'None',
        'active': 'on',
        'featured': 'on'
    })
    assert res.status_code == 302
    course = Course.objects.get(title='Admin Masterclass')
    assert course.price == Decimal('45000.00')
    print("[OK] Academy course created successfully via admin form.")

    # Module & Lesson
    mod = Module.objects.create(course=course, title="Module 1: Foundations", order=1)
    les = Lesson.objects.create(module=mod, title="Lesson 1: Intro", content="Lesson text", order=1, is_preview=True)
    print("[OK] Module & Lesson created.")

    # Student & Certificate verification
    enr, _ = Enrollment.objects.get_or_create(user=regular_user, course=course)
    cert, _ = Certificate.get_or_create_for_enrollment(enr)
    res = client.get(reverse('admin_panel:academy_certificates'))
    assert res.status_code == 200
    assert cert.certificate_id in res.content.decode('utf-8')
    print("[OK] Graduation Certificate displayed & verified.")

    # 6. TEST SHOP & INVENTORY MANAGEMENT
    print("\n--- Testing Shop & Inventory Management ---")
    sh_cat, _ = ProductCategory.objects.get_or_create(name="Admin Shop Cat", slug="admin-shop-cat")
    Product.objects.filter(name='Luxury Hair Serum').delete()

    # Create product
    res = client.post(reverse('admin_panel:shop_product_create'), {
        'name': 'Luxury Hair Serum',
        'category': sh_cat.id,
        'short_description': 'Nourishing oil',
        'full_description': 'Full details',
        'price': '8500.00',
        'stock_quantity': 20,
        'is_active': 'on',
        'is_featured': 'on'
    })
    assert res.status_code == 302
    prod = Product.objects.get(name='Luxury Hair Serum')
    assert prod.stock_quantity == 20
    print("[OK] Shop product created via admin form.")

    # Update stock via inventory view
    res = client.post(reverse('admin_panel:shop_inventory'), {
        'product_id': prod.id,
        'stock_quantity': 35
    })
    assert res.status_code == 302
    prod.refresh_from_db()
    assert prod.stock_quantity == 35
    print("[OK] Product inventory updated to 35 units.")

    # Prevent negative stock
    res = client.post(reverse('admin_panel:shop_inventory'), {
        'product_id': prod.id,
        'stock_quantity': -5
    })
    assert res.status_code == 302
    prod.refresh_from_db()
    assert prod.stock_quantity == 35, "Stock should remain 35 on negative input"
    print("[OK] Negative inventory quantity rejected server-side.")

    # Shop Order Fulfilment
    ord_obj = Order.objects.create(
        user=regular_user,
        customer_name="Regular Customer",
        customer_email="customer@example.com",
        customer_phone="08099998888",
        shipping_address="123 Admin St",
        subtotal=Decimal('8500.00'),
        delivery_fee=Decimal('1500.00'),
        total_amount=Decimal('10000.00'),
        order_status=Order.STATUS_PENDING,
        payment_status=Order.PAYMENT_PAID
    )
    OrderItem.objects.create(
        order=ord_obj,
        product=prod,
        product_name_snapshot=prod.name,
        product_price_snapshot=prod.price,
        quantity=1,
        subtotal=prod.price
    )

    res = client.post(reverse('admin_panel:shop_order_detail', kwargs={'order_number': ord_obj.order_number}), {
        'order_status': Order.STATUS_PROCESSING,
        'payment_status': Order.PAYMENT_PAID
    })
    assert res.status_code == 302
    ord_obj.refresh_from_db()
    assert ord_obj.order_status == Order.STATUS_PROCESSING
    print("[OK] Order status updated to PROCESSING.")

    # 7. TEST SYSTEM CHECK
    print("\n--- Testing Django System Check ---")
    from django.core.management import call_command
    call_command('check')
    print("[OK] Django System Check identified 0 issues.")

    print("\n=== ALL PHASE 7 ADMINISTRATION TESTS PASSED SUCCESSFULLY! ===")


if __name__ == '__main__':
    test_admin_panel()
