import os
import sys
import django

# Setup Django environment
sys.path.insert(0, r'c:\Users\USER\Documents\bolbash-beautyspot')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User


def run_tests():
    print("==================================================")
    print("STARTING NAVBAR NAVIGATION ROUTE AUDIT")
    print("==================================================")

    client = Client()

    nav_endpoints = [
        ('/', 'Home'),
        ('/about/', 'About'),
        ('/services/', 'Services'),
        ('/bridal/', 'Bridal'),
        ('/gallery/', 'Gallery'),
        ('/academy/', 'Academy'),
        ('/shop/', 'Shop'),
        ('/contact/', 'Contact'),
        ('/shop/cart/', 'Cart'),
        ('/booking/', 'BOOK APPOINTMENT'),
    ]

    for endpoint, label in nav_endpoints:
        res = client.get(endpoint)
        assert res.status_code == 200, f"Navbar link {label} ({endpoint}) returned status {res.status_code}, expected 200"
        print(f"  [OK] Navbar link '{label}' ({endpoint}) -> 200 OK")

    # Verify unauthenticated homepage does NOT render My Account
    res_unauth = client.get('/')
    assert b'My Account' not in res_unauth.content, "My Account is rendered for unauthenticated guest on homepage!"
    print("  [OK] Unauthenticated guest visitor does NOT see 'My Account' on navbar/homepage.")

    # Create & login test user to verify My Account renders for authenticated user
    User.objects.filter(username="navtest_user@example.com").delete()
    test_user = User.objects.create_user(username="navtest_user@example.com", password="Pass123!NavUser")
    client.force_login(test_user)
    
    res_auth = client.get('/')
    assert b'My Account' in res_auth.content, "My Account is missing for authenticated user on homepage!"
    print("  [OK] Authenticated logged-in user DOES see 'My Account' on navbar/homepage.")

    # Cleanup
    test_user.delete()

    print("==================================================")
    print("NAVBAR ROUTE AUDIT PASSED! (100% SUCCESS)")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
