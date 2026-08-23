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
from academy.models import StudentProfile, CourseCategory, Course, Module, Lesson, Enrollment
from booking.models import ServiceCategory, Service, Booking


def run_tests():
    print("==================================================")
    print("STARTING PHASE 11 — AUTHORIZATION TESTING AUDIT")
    print("==================================================")

    client = Client()

    # Clean up previous test objects if any
    User.objects.filter(username__startswith="authtest_").delete()
    Course.objects.filter(slug="auth-styling-masterclass").delete()

    # Create Users
    customer_a = User.objects.create_user(
        username="authtest_customer_a@example.com",
        email="authtest_customer_a@example.com",
        password="Pass123!CustomerA",
        first_name="Customer",
        last_name="A"
    )
    CustomerProfile.objects.create(user=customer_a, phone_number="08011111111")

    customer_b = User.objects.create_user(
        username="authtest_customer_b@example.com",
        email="authtest_customer_b@example.com",
        password="Pass123!CustomerB",
        first_name="Customer",
        last_name="B"
    )
    CustomerProfile.objects.create(user=customer_b, phone_number="08022222222")

    student_a = User.objects.create_user(
        username="authtest_student_a@example.com",
        email="authtest_student_a@example.com",
        password="Pass123!StudentA",
        first_name="Student",
        last_name="A"
    )
    StudentProfile.objects.create(user=student_a, phone_number="08033333333")

    staff_user = User.objects.create_user(
        username="authtest_staff@example.com",
        email="authtest_staff@example.com",
        password="Pass123!StaffUser",
        first_name="Staff",
        last_name="Admin",
        is_staff=True
    )

    # ----------------------------------------------------
    # 1. Vertical Authorization: Admin Portal Protection
    # ----------------------------------------------------
    print("\n--- 1. Vertical Authorization: Admin Portal Protection ---")
    
    # Unauthenticated -> Redirect 302
    client.logout()
    unauth_admin_resp = client.get('/admin-portal/')
    assert unauth_admin_resp.status_code == 302, f"Unauthenticated admin-portal GET returned {unauth_admin_resp.status_code}, expected 302"

    # Customer -> 403 Forbidden
    client.login(username=customer_a.username, password="Pass123!CustomerA")
    cust_admin_resp = client.get('/admin-portal/')
    assert cust_admin_resp.status_code == 403, f"Customer accessing admin-portal returned {cust_admin_resp.status_code}, expected 403"
    print("  [OK] Non-staff Customer blocked with HTTP 403 Forbidden on /admin-portal/")

    # Student -> 403 Forbidden
    client.login(username=student_a.username, password="Pass123!StudentA")
    stud_admin_resp = client.get('/admin-portal/')
    assert stud_admin_resp.status_code == 403, f"Student accessing admin-portal returned {stud_admin_resp.status_code}, expected 403"
    print("  [OK] Non-staff Student blocked with HTTP 403 Forbidden on /admin-portal/")

    # Staff User -> 200 Granted
    client.login(username=staff_user.username, password="Pass123!StaffUser")
    staff_admin_resp = client.get('/admin-portal/')
    assert staff_admin_resp.status_code == 200, f"Staff accessing admin-portal returned {staff_admin_resp.status_code}, expected 200"
    print("  [OK] Staff User granted access HTTP 200 on /admin-portal/")

    # ----------------------------------------------------
    # 2. Horizontal Authorization: Customer Appointment Review Ownership (IDOR Protection)
    # ----------------------------------------------------
    print("\n--- 2. Horizontal Authorization: Customer Appointment Review IDOR Protection ---")
    svc_cat = ServiceCategory.objects.first() or ServiceCategory.objects.create(name="Auth Category")
    svc = Service.objects.filter(active=True).first() or Service.objects.create(
        name="Auth Service", slug="auth-service", category=svc_cat, price=10000.00, active=True
    )

    # Booking for Customer B
    booking_b = Booking.objects.create(
        user=customer_b,
        customer_name="Customer B",
        customer_email=customer_b.email,
        customer_phone="08022222222",
        service=svc,
        service_name_snapshot=svc.name,
        service_price_snapshot=svc.price,
        service_duration_snapshot=svc.duration or 60,
        appointment_date="2026-08-01",
        appointment_time="10:00:00",
        amount_due=5000.00,
        status=Booking.STATUS_COMPLETED
    )

    # Customer A attempts to review Customer B's appointment
    client.login(username=customer_a.username, password="Pass123!CustomerA")
    idor_review_resp = client.get(f'/accounts/appointments/{booking_b.id}/review/', follow=True)
    assert 'not authorized' in idor_review_resp.content.decode('utf-8').lower(), \
        "Horizontal privilege escalation: Customer A was not blocked from reviewing Customer B's booking!"
    print("  [OK] Customer A blocked from accessing/reviewing Customer B's private appointment.")

    # ----------------------------------------------------
    # 3. Horizontal Authorization: Student Course Content & Payment Boundaries
    # ----------------------------------------------------
    print("\n--- 3. Horizontal Authorization: Student Course Enrollment & Payment Boundaries ---")
    crs_cat = CourseCategory.objects.first() or CourseCategory.objects.create(name="Auth Academy Cat")
    course = Course.objects.create(
        category=crs_cat,
        title="Auth Styling Masterclass",
        slug="auth-styling-masterclass",
        short_description="Short desc",
        full_description="Full desc",
        price=50000.00,
        active=True
    )

    module = Module.objects.create(course=course, title="Module 1", order=1)
    lesson = Lesson.objects.create(module=module, title="Lesson 1", slug="lesson-1", order=1)

    client.login(username=student_a.username, password="Pass123!StudentA")

    # Unenrolled student -> HTTP 404
    unenrolled_resp = client.get(f'/academy/courses/{course.slug}/lessons/{lesson.slug}/')
    assert unenrolled_resp.status_code == 404, f"Unenrolled student accessing lesson returned {unenrolled_resp.status_code}, expected 404"
    print("  [OK] Unenrolled Student blocked with HTTP 404 on course lesson player.")

    # Enroll student (Unpaid status)
    enrollment = Enrollment.objects.create(
        user=student_a,
        course=course,
        enrollment_status=Enrollment.STATUS_PENDING,
        payment_status=Enrollment.PAYMENT_UNPAID
    )

    # Enrolled but unpaid student -> Redirected with payment notice
    unpaid_resp = client.get(f'/academy/courses/{course.slug}/lessons/{lesson.slug}/', follow=True)
    assert 'tuition payment' in unpaid_resp.content.decode('utf-8').lower(), \
        "Unpaid student was able to access paid course lesson content!"
    print("  [OK] Enrolled Unpaid Student blocked with tuition payment boundary notice.")

    # Mark Enrollment PAID & ACTIVE
    enrollment.payment_status = Enrollment.PAYMENT_PAID
    enrollment.enrollment_status = Enrollment.STATUS_ACTIVE
    enrollment.save()

    # Enrolled & paid student -> Granted HTTP 200
    paid_resp = client.get(f'/academy/courses/{course.slug}/lessons/{lesson.slug}/')
    assert paid_resp.status_code == 200, f"Paid student accessing lesson returned {paid_resp.status_code}, expected 200"
    print("  [OK] Enrolled & Paid Student granted HTTP 200 access on course lesson player.")

    # ----------------------------------------------------
    # 4. Public Route Access Verification
    # ----------------------------------------------------
    print("\n--- 4. Public Route Access Matrix ---")
    public_urls = ['/', '/about/', '/services/', '/bridal/', '/gallery/', '/reviews/', '/contact/', '/academy/', '/shop/']
    client.logout()

    for url in public_urls:
        pub_resp = client.get(url)
        assert pub_resp.status_code == 200, f"Public route {url} returned status {pub_resp.status_code}"
        print(f"  [OK] Public GET {url} -> 200 OK")

    # Cleanup test users & objects
    booking_b.delete()
    enrollment.delete()
    lesson.delete()
    module.delete()
    course.delete()
    User.objects.filter(username__startswith="authtest_").delete()

    print("==================================================")
    print("AUTHORIZATION & ACCESS CONTROL AUDIT PASSED! (100% SUCCESS)")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
