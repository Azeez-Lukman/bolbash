import os
import sys
import django

# Setup Django environment
sys.path.insert(0, r'c:\Users\USER\Documents\bolbash-beautyspot')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from accounts.models import CustomerProfile
from academy.models import StudentProfile


def run_tests():
    print("==================================================")
    print("STARTING PHASE 11 — ACCESS CONTROL TESTING AUDIT")
    print("==================================================")

    client = Client()

    # Clean up previous test users
    User.objects.filter(username__startswith="acctest_").delete()

    # Create Test Users
    customer_user = User.objects.create_user(
        username="acctest_customer@example.com",
        email="acctest_customer@example.com",
        password="Pass123!Customer",
        first_name="Customer",
        last_name="User"
    )
    CustomerProfile.objects.create(user=customer_user, phone_number="08011111111")

    student_user = User.objects.create_user(
        username="acctest_student@example.com",
        email="acctest_student@example.com",
        password="Pass123!Student",
        first_name="Student",
        last_name="User"
    )
    StudentProfile.objects.create(user=student_user, phone_number="08022222222")

    staff_user = User.objects.create_user(
        username="acctest_staff@example.com",
        email="acctest_staff@example.com",
        password="Pass123!Staff",
        first_name="Staff",
        last_name="Admin",
        is_staff=True
    )

    # ----------------------------------------------------
    # 1. Unauthenticated Protected Route Matrix
    # ----------------------------------------------------
    print("\n--- 1. Unauthenticated Protected Route Matrix ---")
    client.logout()

    protected_unauth_routes = [
        ('/accounts/dashboard/', 'Customer Dashboard'),
        ('/accounts/appointments/', 'Customer Appointments'),
        ('/accounts/payments/', 'Customer Payments'),
        ('/accounts/profile/', 'Customer Profile'),
        ('/accounts/security/', 'Customer Security'),
        ('/academy/my-learning/', 'Academy LMS Dashboard'),
        ('/shop/my-orders/', 'Customer Shop Orders'),
        ('/admin-portal/', 'Admin Portal Root'),
        ('/admin-portal/appointments/', 'Admin Appointment List'),
        ('/admin-portal/shop/products/', 'Admin Product Inventory'),
    ]

    for route, label in protected_unauth_routes:
        res = client.get(route)
        assert res.status_code == 302, f"Unauthenticated access to {label} ({route}) returned {res.status_code}, expected 302"
        print(f"  [OK] Unauthenticated GET {route} -> HTTP 302 Redirect to Login")

    # ----------------------------------------------------
    # 2. Authenticated Customer Access & Role Boundary
    # ----------------------------------------------------
    print("\n--- 2. Authenticated Customer Access & Role Boundary ---")
    client.login(username=customer_user.username, password="Pass123!Customer")

    # Granted customer routes
    assert client.get('/accounts/dashboard/').status_code == 200
    assert client.get('/accounts/appointments/').status_code == 200
    print("  [OK] Customer granted HTTP 200 on Customer Dashboard & Appointments.")

    # Blocked admin routes -> 403 Forbidden
    admin_routes_for_customer = [
        '/admin-portal/',
        '/admin-portal/appointments/',
        '/admin-portal/shop/products/',
        '/admin-portal/academy/courses/',
    ]
    for route in admin_routes_for_customer:
        res_cust_admin = client.get(route)
        assert res_cust_admin.status_code == 403, f"Customer accessing {route} returned {res_cust_admin.status_code}, expected 403"
        print(f"  [OK] Customer blocked from {route} -> HTTP 403 Forbidden")

    # ----------------------------------------------------
    # 3. Authenticated Student Access & Role Boundary
    # ----------------------------------------------------
    print("\n--- 3. Authenticated Student Access & Role Boundary ---")
    client.login(username=student_user.username, password="Pass123!Student")

    # Granted student route
    assert client.get('/academy/my-learning/').status_code == 200
    print("  [OK] Student granted HTTP 200 on LMS My Learning Dashboard.")

    # Blocked admin routes -> 403 Forbidden
    for route in admin_routes_for_customer:
        res_stud_admin = client.get(route)
        assert res_stud_admin.status_code == 403, f"Student accessing {route} returned {res_stud_admin.status_code}, expected 403"
        print(f"  [OK] Student blocked from {route} -> HTTP 403 Forbidden")

    # ----------------------------------------------------
    # 4. Authenticated Staff Admin Access
    # ----------------------------------------------------
    print("\n--- 4. Authenticated Staff Admin Access ---")
    client.login(username=staff_user.username, password="Pass123!Staff")

    admin_staff_routes = [
        ('/admin-portal/', 'Admin Dashboard'),
        ('/admin-portal/appointments/', 'Admin Appointments'),
        ('/admin-portal/shop/products/', 'Admin Products'),
        ('/admin-portal/academy/courses/', 'Admin Courses'),
    ]

    for route, label in admin_staff_routes:
        res_staff = client.get(route)
        assert res_staff.status_code == 200, f"Staff accessing {route} returned {res_staff.status_code}, expected 200"
        print(f"  [OK] Staff User granted HTTP 200 on {label} ({route})")

    # Cleanup test users
    User.objects.filter(username__startswith="acctest_").delete()

    print("==================================================")
    print("ACCESS CONTROL & ROLE MATRIX AUDIT PASSED! (100% SUCCESS)")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
