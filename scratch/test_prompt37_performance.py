import os
import sys
import django

# Setup Django environment
sys.path.insert(0, r'c:\Users\USER\Documents\bolbash-beautyspot')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.urls import reverse


def run_tests():
    print("==================================================")
    print("STARTING TEST SUITE FOR PHASE 10 — PERFORMANCE OPTIMIZATION")
    print("==================================================")

    client = Client()

    # 1. GZip Compression Test
    response = client.get('/', HTTP_ACCEPT_ENCODING='gzip')
    assert response.status_code == 200, f"Home page request failed with status {response.status_code}"
    assert response.has_header('Content-Encoding') and 'gzip' in response['Content-Encoding'], \
        f"GZip compression header missing! Header: {response.get('Content-Encoding')}"

    print("  [OK] GZip response compression verified (Content-Encoding: gzip).")

    # 2. Key Pages Load Speed & Response Header Audit
    perf_targets = [
        ('core:index', 'Home Page'),
        ('core:service_list', 'Services Catalogue'),
        ('academy:academy_landing', 'Academy Landing'),
        ('shop:shop_landing', 'Shop Landing'),
        ('core:contact', 'Contact Us'),
    ]

    for url_name, label in perf_targets:
        url = reverse(url_name)
        res = client.get(url, HTTP_ACCEPT_ENCODING='gzip')
        assert res.status_code == 200, f"Failed to load {label} at {url}"
        assert res.has_header('Content-Encoding') and 'gzip' in res['Content-Encoding']
        print(f"  [OK] {label} loaded cleanly with GZip compression.")

    print("==================================================")
    print("ALL PERFORMANCE OPTIMIZATION & COMPRESSION TESTS PASSED! (100% SUCCESS)")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
