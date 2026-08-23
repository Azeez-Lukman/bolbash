import os
import sys
import django

# Setup Django Environment
sys.path.insert(0, r"c:\Users\USER\Documents\bolbash-beautyspot")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User
from academy.models import CourseCategory, Course, StudentProfile, Enrollment, Module, Lesson, LessonProgress, Certificate
from django.test import RequestFactory
from academy.views import my_learning, course_learn, lesson_detail, lesson_toggle_complete, view_certificate, verify_certificate

def run_tests():
    print("==================================================")
    print("STARTING TEST SUITE: PROMPT 15 — ACADEMY LMS, PROGRESS & CERTIFICATES")
    print("==================================================")

    # 1. Setup / Seed Data
    category, _ = CourseCategory.objects.get_or_create(
        name="Hair Styling Masterclass",
        defaults={"description": "Professional hair styling and wig installation."}
    )

    course, _ = Course.objects.get_or_create(
        slug="wig-installation-mastery",
        defaults={
            "title": "Wig Installation Mastery Masterclass",
            "category": category,
            "short_description": "Learn professional 360 frontal installation and melting techniques.",
            "full_description": "Comprehensive practical guide on wig customization and installation.",
            "duration": "2 Weeks",
            "price": 0.00, # Free / complimentary for test
            "format_type": Course.FORMAT_ONLINE,
            "active": True,
        }
    )

    # Modules & Lessons setup
    mod1, _ = Module.objects.get_or_create(
        course=course,
        order=1,
        defaults={"title": "Introduction & Cap Preparation", "description": "Preparing the client's hair and bald cap method."}
    )

    lsn1, _ = Lesson.objects.get_or_create(
        module=mod1,
        order=1,
        defaults={
            "title": "Bald Cap Method Step-by-Step",
            "summary": "Mastering the lace melting bald cap foundation.",
            "content": "Step 1: Clean hairline with alcohol.\nStep 2: Apply stocking cap and Got2b glue.\nStep 3: Blow dry and melt.",
            "duration_minutes": 20,
        }
    )

    lsn2, _ = Lesson.objects.get_or_create(
        module=mod1,
        order=2,
        defaults={
            "title": "Frontal Customization & Plucking",
            "summary": "Natural hairline plucking techniques.",
            "content": "Step 1: Bleach knots with 30vol developer.\nStep 2: Pluck hairline in small sections.",
            "duration_minutes": 30,
        }
    )

    print("[OK] [1/8] Seed Course, Modules, and Lessons verified.")

    # 2. Student User & Profile
    student_email = "lms_test_student@example.com"
    user = User.objects.filter(email=student_email).first()
    if user:
        user.delete()

    user = User.objects.create_user(
        username=student_email,
        email=student_email,
        password="TestPassword123!",
        first_name="Jane",
        last_name="Doe"
    )
    profile, _ = StudentProfile.objects.get_or_create(user=user, phone_number="08012345678")
    print("[OK] [2/8] Student User created successfully.")

    # 3. Course Enrollment
    enrollment, _ = Enrollment.objects.get_or_create(
        user=user,
        course=course,
        defaults={
            'enrollment_status': Enrollment.STATUS_ACTIVE,
            'payment_status': Enrollment.PAYMENT_PAID,
        }
    )
    # Reset any previous progress
    LessonProgress.objects.filter(user=user).delete()
    Certificate.objects.filter(user=user).delete()

    # Verify initial progress is 0%
    assert enrollment.get_progress_percentage() == 0, f"Expected 0%, got {enrollment.get_progress_percentage()}%"
    assert enrollment.get_progress_status_badge() == "Not Started"
    print("[OK] [3/8] Enrollment & 0% initial progress verified.")

    # 4. Student Dashboard View (my_learning)
    rf = RequestFactory()
    req = rf.get('/academy/my-learning/')
    req.user = user
    resp = my_learning(req)
    assert resp.status_code == 200
    print("[OK] [4/8] Student Dashboard rendering verified.")

    # 5. Lesson Detail & Progress Tracking
    # Complete Lesson 1
    progress1 = LessonProgress.objects.create(user=user, lesson=lsn1, completed=True)
    assert enrollment.get_completed_lessons_count() == 1
    assert enrollment.get_progress_percentage() == 50, f"Expected 50%, got {enrollment.get_progress_percentage()}%"
    assert enrollment.get_progress_status_badge() == "In Progress"
    print("[OK] [5/8] Real-time 50% Progress calculation verified.")

    # 6. Continue Learning resolution
    next_lsn = enrollment.get_next_unfinished_lesson()
    assert next_lsn.id == lsn2.id, f"Expected next lesson ID {lsn2.id}, got {next_lsn.id}"
    print("[OK] [6/8] Continue Learning smart navigation to Lesson 2 verified.")

    # 7. Complete All Lessons & Auto Certificate Generation
    progress2 = LessonProgress.objects.create(user=user, lesson=lsn2, completed=True)
    assert enrollment.get_completed_lessons_count() == 2
    assert enrollment.get_progress_percentage() == 100

    course_completed = enrollment.check_and_update_completion()
    assert course_completed is True
    assert enrollment.enrollment_status == Enrollment.STATUS_COMPLETED

    cert = Certificate.objects.filter(user=user, course=course).first()
    assert cert is not None
    assert cert.certificate_id.startswith("BBA-CERT-")
    print(f"[OK] [7/8] Course 100% completion & Graduation Certificate '{cert.certificate_id}' generated successfully.")

    # 8. Public Certificate Verification
    req_verify = rf.get(f'/academy/verify-certificate/?id={cert.certificate_id}')
    resp_verify = verify_certificate(req_verify)
    assert resp_verify.status_code == 200
    assert cert.certificate_id in resp_verify.content.decode()

    # Invalid ID Check
    req_invalid = rf.get('/academy/verify-certificate/?id=INVALID-REF-999')
    resp_invalid = verify_certificate(req_invalid)
    assert resp_invalid.status_code == 200
    assert "Certificate Not Found" in resp_invalid.content.decode()
    print("[OK] [8/8] Public Certificate Verification (Valid & Invalid states) verified.")


    print("==================================================")
    print("ALL 8 LMS TEST SCENARIOS PASSED WITH 100% SUCCESS!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
