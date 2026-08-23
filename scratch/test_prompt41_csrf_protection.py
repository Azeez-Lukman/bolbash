import os
import sys
import django

# Setup Django environment
sys.path.insert(0, r'c:\Users\USER\Documents\bolbash-beautyspot')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client


def run_tests():
    print("==================================================")
    print("STARTING PHASE 11 — CSRF PROTECTION AUDIT")
    print("==================================================")

    # Initialize client with STRICT CSRF enforcement enabled
    csrf_client = Client(enforce_csrf_checks=True)

    post_endpoints = [
        ('/accounts/login/', 'Customer Login'),
        ('/accounts/register/', 'Customer Registration'),
        ('/academy/login/', 'Student Login'),
        ('/academy/register/', 'Student Registration'),
        ('/booking/submit/', 'Booking Submission'),
        ('/contact/', 'Contact Form'),
        ('/feedback/', 'Customer Feedback Form'),
    ]

    print("\n--- 1. Testing Un-tokened POST Rejection (HTTP 403 Forbidden) ---")
    for endpoint, label in post_endpoints:
        response = csrf_client.post(endpoint, {'test_key': 'test_val'})
        assert response.status_code == 403, \
            f"CSRF PROTECTION FAILURE! Un-tokened POST to {label} ({endpoint}) returned status {response.status_code}, expected 403"
        print(f"  [OK] {label} ({endpoint}) -> HTTP 403 Forbidden (CSRF token missing rejected)")

    print("\n--- 2. Testing Valid CSRF Token Acceptance ---")
    # Retrieve page to obtain CSRF cookie and token
    get_res = csrf_client.get('/accounts/login/')
    assert get_res.status_code == 200
    csrf_token = get_res.cookies.get('csrftoken').value if get_res.cookies.get('csrftoken') else None
    
    # POST with valid CSRF token
    valid_post_res = csrf_client.post(
        '/accounts/login/',
        {'username': 'nonexistent@example.com', 'password': 'wrongpassword', 'csrfmiddlewaretoken': csrf_token}
    )
    assert valid_post_res.status_code != 403, \
        f"Valid CSRF token was rejected with 403! Status: {valid_post_res.status_code}"
    print("  [OK] Valid CSRF token accepted cleanly by CsrfViewMiddleware.")

    print("==================================================")
    print("CSRF PROTECTION AUDIT PASSED! (100% SUCCESS)")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
