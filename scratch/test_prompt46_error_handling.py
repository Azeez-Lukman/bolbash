import os
import sys
import django

# Setup Django environment
sys.path.insert(0, r'c:\Users\USER\Documents\bolbash-beautyspot')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client, RequestFactory
from core.views import custom_404, custom_403, custom_500


def run_tests():
    print("==================================================")
    print("STARTING PHASE 11 — ERROR HANDLING AUDIT")
    print("==================================================")

    client = Client()
    rf = RequestFactory()

    # 1. Testing 404 Not Found Page & Invalid Model Slugs
    print("\n--- 1. Testing 404 Not Found Handling ---")
    
    # Invalid URL path
    res_404_url = client.get('/non-existent-page-12345/')
    assert res_404_url.status_code == 404, f"Non-existent route returned status {res_404_url.status_code}, expected 404"
    print("  [OK] GET /non-existent-page-12345/ -> HTTP 404 Not Found")

    # Invalid Service detail slug
    res_svc_404 = client.get('/services/non-existent-service-slug/')
    assert res_svc_404.status_code == 404, f"Non-existent service slug returned {res_svc_404.status_code}, expected 404"
    print("  [OK] GET /services/non-existent-service-slug/ -> HTTP 404 Not Found")

    # Invalid Course detail slug
    res_crs_404 = client.get('/academy/courses/non-existent-course-slug/')
    assert res_crs_404.status_code == 404, f"Non-existent course slug returned {res_crs_404.status_code}, expected 404"
    print("  [OK] GET /academy/courses/non-existent-course-slug/ -> HTTP 404 Not Found")

    # Invalid Product detail slug
    res_prd_404 = client.get('/shop/products/non-existent-product-slug/')
    assert res_prd_404.status_code == 404, f"Non-existent product slug returned {res_prd_404.status_code}, expected 404"
    print("  [OK] GET /shop/products/non-existent-product-slug/ -> HTTP 404 Not Found")

    # 2. Testing Custom 403 Forbidden View Handler
    print("\n--- 2. Testing Custom 403 Forbidden View Handler ---")
    req_403 = rf.get('/some-forbidden-path/')
    res_403 = custom_403(req_403)
    assert res_403.status_code == 403, f"custom_403 returned status {res_403.status_code}, expected 403"
    print("  [OK] custom_403 view handler returns HTTP status 403 Forbidden.")

    # 3. Testing Custom 500 Server Error View Handler
    print("\n--- 3. Testing Custom 500 Server Error View Handler ---")
    req_500 = rf.get('/some-error-path/')
    res_500 = custom_500(req_500)
    assert res_500.status_code == 500, f"custom_500 returned status {res_500.status_code}, expected 500"
    print("  [OK] custom_500 view handler returns HTTP status 500 Internal Server Error.")

    print("==================================================")
    print("ERROR HANDLING AUDIT PASSED! (100% SUCCESS)")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
