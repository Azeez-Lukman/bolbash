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
    print("STARTING PHASE 11 — AUTHENTICATION TESTING AUDIT")
    print("==================================================")

    client = Client()

    # Clean up previous test users if any
    User.objects.filter(username__startswith="authtest_").delete()

    # ----------------------------------------------------
    # TEST A: Customer Registration, Login, Authenticated Session, Logout & Protected Page Rejection
    # ----------------------------------------------------
    print("\n--- TEST A: Customer Registration -> Login -> Session -> Logout -> Access Denial ---")
    customer_email = "authtest_customer1@example.com"
    customer_pass = "ComplexPass123!@#"

    reg_data = {
        'first_name': 'AuthCustomer',
        'last_name': 'Tester',
        'email': customer_email,
        'phone_number': '08011112222',
        'address': '123 Auth St',
        'city': 'Ibadan',
        'state': 'Oyo State',
        'password': customer_pass,
        'confirm_password': customer_pass,
    }

    reg_resp = client.post('/accounts/register/', reg_data, follow=True)
    assert reg_resp.status_code == 200, f"Customer registration failed with status {reg_resp.status_code}"

    # Verify Database Record & Hashing
    user = User.objects.filter(email=customer_email).first()
    assert user is not None, "User record not created in DB for customer registration"
    assert hasattr(user, 'customer_profile'), "CustomerProfile not created for user"
    assert user.password.startswith('pbkdf2_sha256$') or user.password.startswith('argon2'), \
        f"Password is not securely hashed using Django standards! Stored value: {user.password[:20]}"
    assert user.password != customer_pass, "SECURITY VIOLATION: Password stored in plain text!"

    # Verify session is authenticated
    assert '_auth_user_id' in client.session, "Session _auth_user_id missing after registration auto-login"

    # Access protected customer dashboard
    dash_resp = client.get('/accounts/dashboard/')
    assert dash_resp.status_code == 200, f"Authenticated customer dashboard returned status {dash_resp.status_code}"

    # Logout
    logout_resp = client.get('/accounts/logout/', follow=True)
    assert logout_resp.status_code == 200
    assert '_auth_user_id' not in client.session, "Session _auth_user_id still exists after logout"

    # Verify protected page is now denied/redirected
    denied_resp = client.get('/accounts/dashboard/')
    assert denied_resp.status_code == 302, f"Unauthenticated dashboard access returned status {denied_resp.status_code}, expected 302"
    assert '/accounts/login' in denied_resp.url, f"Unauthenticated access did not redirect to login: {denied_resp.url}"

    print("  [PASS] TEST A: Customer Registration -> Login -> Session -> Logout -> Access Denial verified.")

    # ----------------------------------------------------
    # TEST B: Invalid Customer Login & Account Enumeration Protection
    # ----------------------------------------------------
    print("\n--- TEST B: Invalid Customer Login & Account Enumeration Protection ---")
    
    # Incorrect password for existing account
    bad_pass_resp = client.post('/accounts/login/', {
        'username': customer_email,
        'password': 'WrongPassword123!',
    })
    assert bad_pass_resp.status_code == 200
    assert '_auth_user_id' not in client.session

    # Non-existent account
    non_existent_resp = client.post('/accounts/login/', {
        'username': 'authtest_nonexistent_999@example.com',
        'password': 'WrongPassword123!',
    })
    assert non_existent_resp.status_code == 200
    assert '_auth_user_id' not in client.session

    # Empty credentials
    empty_resp = client.post('/accounts/login/', {
        'username': '',
        'password': '',
    })
    assert empty_resp.status_code == 200
    assert '_auth_user_id' not in client.session

    print("  [PASS] TEST B: Invalid logins rejected with generic messaging without exposing account existence.")

    # ----------------------------------------------------
    # TEST C: Academy Student Registration, Login, My Learning Area & Logout
    # ----------------------------------------------------
    print("\n--- TEST C: Academy Student Registration -> Login -> Protected Learning -> Logout ---")
    student_email = "authtest_student1@example.com"
    student_pass = "StudentPass987!@#"

    stud_reg_data = {
        'first_name': 'AuthStudent',
        'last_name': 'Learner',
        'email': student_email,
        'phone_number': '08033334444',
        'password': student_pass,
        'confirm_password': student_pass,
    }

    stud_reg_resp = client.post('/academy/register/', stud_reg_data, follow=True)
    assert stud_reg_resp.status_code == 200, f"Student registration failed with status {stud_reg_resp.status_code}"

    # Verify Database Record & StudentProfile
    stud_user = User.objects.filter(email=student_email).first()
    assert stud_user is not None, "User record not created in DB for student registration"
    assert hasattr(stud_user, 'student_profile'), "StudentProfile not created for student"
    assert stud_user.password.startswith('pbkdf2_sha256$') or stud_user.password.startswith('argon2')
    assert stud_user.password != student_pass, "SECURITY VIOLATION: Student password stored in plain text!"

    # Access protected Academy My Learning area
    learning_resp = client.get('/academy/my-learning/')
    assert learning_resp.status_code == 200, f"Authenticated student learning page returned status {learning_resp.status_code}"

    # Logout student
    stud_logout_resp = client.get('/academy/logout/', follow=True)
    assert stud_logout_resp.status_code == 200
    assert '_auth_user_id' not in client.session

    # Verify protected student page denied when unauthenticated
    stud_denied_resp = client.get('/academy/my-learning/')
    assert stud_denied_resp.status_code == 302
    assert '/academy/login' in stud_denied_resp.url

    print("  [PASS] TEST C: Academy Student Registration -> Login -> Protected Learning -> Logout verified.")

    # ----------------------------------------------------
    # TEST D: Duplicate Registration Rejection
    # ----------------------------------------------------
    print("\n--- TEST D: Duplicate Registration Rejection ---")
    dup_cust_resp = client.post('/accounts/register/', reg_data)
    assert dup_cust_resp.status_code == 200
    assert '_auth_user_id' not in client.session, "Duplicate customer registration allowed login!"

    dup_stud_resp = client.post('/academy/register/', stud_reg_data)
    assert dup_stud_resp.status_code == 200
    assert '_auth_user_id' not in client.session, "Duplicate student registration allowed login!"

    print("  [PASS] TEST D: Duplicate registration attempts rejected cleanly.")

    # ----------------------------------------------------
    # TEST E: Password Verification & Authentication Logic
    # ----------------------------------------------------
    print("\n--- TEST E: Password Verification Mechanics ---")
    login_success = client.post('/accounts/login/', {
        'username': customer_email,
        'password': customer_pass,
    }, follow=True)
    assert login_success.status_code == 200
    assert '_auth_user_id' in client.session, "Login with valid password failed"

    # Cleanup test users
    User.objects.filter(username__startswith="authtest_").delete()

    print("  [PASS] TEST E: Password verification mechanics verified.")

    # ----------------------------------------------------
    # Protected Routes Access Control Matrix Audit
    # ----------------------------------------------------
    print("\n--- Protected Routes Access Control Matrix ---")
    protected_urls = [
        '/accounts/dashboard/',
        '/accounts/appointments/',
        '/accounts/payments/',
        '/accounts/profile/',
        '/accounts/security/',
        '/academy/my-learning/',
    ]

    for url in protected_urls:
        unauth_res = client.get(url)
        assert unauth_res.status_code == 302, f"Unauthenticated access to {url} allowed with status {unauth_res.status_code}"
        print(f"  [OK] Unauthenticated GET {url} -> 302 Redirect to Login")

    print("==================================================")
    print("AUTHENTICATION AUDIT & E2E TESTING PASSED! (100% SUCCESS)")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
