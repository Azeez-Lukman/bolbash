import os
import sys
import django

# Setup Django environment
sys.path.insert(0, r'c:\Users\USER\Documents\bolbash-beautyspot')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.contrib.auth.models import User
from booking.models import ServiceCategory, Service, Booking
from academy.models import CourseCategory, Course, Enrollment
from shop.models import ProductCategory, Product, Order, OrderItem


def run_tests():
    print("==================================================")
    print("STARTING PHASE 11 — DATABASE INTEGRITY AUDIT")
    print("==================================================")

    # Clean up previous test records
    Booking.objects.filter(customer_email="dbtest_user@example.com").delete()
    User.objects.filter(username__startswith="dbtest_").delete()
    Course.objects.filter(slug="db-unique-course").delete()
    Service.objects.filter(slug="db-unique-service").delete()
    Product.objects.filter(slug="db-unique-product").delete()

    # Setup categories & users
    s_cat = ServiceCategory.objects.first() or ServiceCategory.objects.create(name="DB Test Service Cat")
    c_cat = CourseCategory.objects.first() or CourseCategory.objects.create(name="DB Test Course Cat")
    p_cat = ProductCategory.objects.first() or ProductCategory.objects.create(name="DB Test Product Cat")

    test_user = User.objects.create_user(
        username="dbtest_user@example.com",
        email="dbtest_user@example.com",
        password="Pass123!DBUser"
    )

    # ----------------------------------------------------
    # 1. Unique Constraint Enforcement
    # ----------------------------------------------------
    print("\n--- 1. Unique Constraint Enforcement ---")

    # Unique Course Slug
    c1 = Course.objects.create(category=c_cat, title="Unique Course 1", slug="db-unique-course", price=10000.00)
    try:
        with transaction.atomic():
            Course.objects.create(category=c_cat, title="Unique Course 2", slug="db-unique-course", price=20000.00)
        assert False, "Duplicate Course slug allowed!"
    except IntegrityError:
        print("  [OK] Duplicate Course slug correctly raises IntegrityError.")

    # Unique Service Slug
    s1 = Service.objects.create(name="Unique Service 1", slug="db-unique-service", category=s_cat, price=15000.00)
    try:
        with transaction.atomic():
            Service.objects.create(name="Unique Service 2", slug="db-unique-service", category=s_cat, price=25000.00)
        assert False, "Duplicate Service slug allowed!"
    except IntegrityError:
        print("  [OK] Duplicate Service slug correctly raises IntegrityError.")

    # Unique Product Slug
    p1 = Product.objects.create(name="Unique Product 1", slug="db-unique-product", category=p_cat, price=5000.00)
    try:
        with transaction.atomic():
            Product.objects.create(name="Unique Product 2", slug="db-unique-product", category=p_cat, price=8000.00)
        assert False, "Duplicate Product slug allowed!"
    except IntegrityError:
        print("  [OK] Duplicate Product slug correctly raises IntegrityError.")

    # Unique Enrollment (user, course)
    e1 = Enrollment.objects.create(user=test_user, course=c1)
    try:
        with transaction.atomic():
            Enrollment.objects.create(user=test_user, course=c1)
        assert False, "Duplicate Enrollment (user, course) allowed!"
    except IntegrityError:
        print("  [OK] Duplicate Enrollment (user, course) correctly raises IntegrityError.")

    # ----------------------------------------------------
    # 2. Referential Integrity & Deletion Protection
    # ----------------------------------------------------
    print("\n--- 2. Referential Integrity & Foreign Key Protection ---")

    booking = Booking.objects.create(
        user=test_user,
        customer_name="DB Test Customer",
        customer_email=test_user.email,
        customer_phone="08012345678",
        service=s1,
        service_name_snapshot=s1.name,
        service_price_snapshot=s1.price,
        service_duration_snapshot=60,
        appointment_date="2026-09-01",
        appointment_time="10:00:00",
        amount_due=s1.price
    )

    # Deleting a Service that has active Bookings -> ProtectedError
    try:
        s1.delete()
        assert False, "Deleting referenced Service was allowed without ProtectedError!"
    except ProtectedError:
        print("  [OK] Attempting to delete a Service referenced by active Bookings correctly raises ProtectedError.")

    # Assert Booking and snapshots remain completely intact
    booking.refresh_from_db()
    assert booking.service_id == s1.id
    assert booking.service_name_snapshot == "Unique Service 1"
    assert booking.service_price_snapshot == 15000.00
    print("  [OK] Referential integrity preserved; Service and Booking data intact.")

    # ----------------------------------------------------
    # 3. Database Transaction Atomic Rollback Guarantee
    # ----------------------------------------------------
    print("\n--- 3. Database Transaction Atomic Rollback Guarantee ---")

    atomic_test_slug = "db-atomic-rollback-test-course"
    try:
        with transaction.atomic():
            Course.objects.create(
                category=c_cat,
                title="Atomic Rollback Course",
                slug=atomic_test_slug,
                price=30000.00
            )
            # Intentionally raise exception to trigger rollback
            raise RuntimeError("Simulated transaction failure")
    except RuntimeError:
        pass

    # Verify atomic_test_slug was NOT saved in database
    assert not Course.objects.filter(slug=atomic_test_slug).exists(), \
        "Atomic transaction failed! Uncommitted record was persisted in database."
    print("  [OK] Failed atomic transaction cleanly rolled back all uncommitted writes.")

    # Cleanup test data
    booking.delete()
    s1.delete()
    c1.delete()
    p1.delete()
    User.objects.filter(username__startswith="dbtest_").delete()

    print("==================================================")
    print("DATABASE INTEGRITY AUDIT PASSED! (100% SUCCESS)")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
