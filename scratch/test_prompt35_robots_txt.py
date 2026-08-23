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
    print("STARTING TEST SUITE FOR PHASE 10 — ROBOTS.TXT")
    print("==================================================")

    client = Client()
    response = client.get('/robots.txt')

    assert response.status_code == 200, f"Failed to load /robots.txt, status code {response.status_code}"
    assert 'text/plain' in response['Content-Type'].lower(), f"Expected text/plain Content-Type, got '{response['Content-Type']}'"

    content = response.content.decode('utf-8')

    # Assert crawler directives
    assert "User-agent: *" in content, "Missing 'User-agent: *' directive"
    assert "Allow: /" in content, "Missing 'Allow: /' directive"
    assert "Disallow: /admin/" in content, "Missing 'Disallow: /admin/' directive"
    assert "Disallow: /admin-portal/" in content, "Missing 'Disallow: /admin-portal/' directive"
    assert "Disallow: /accounts/" in content, "Missing 'Disallow: /accounts/' directive"
    assert "Disallow: /booking/lookup/" in content, "Missing 'Disallow: /booking/lookup/' directive"
    assert "Disallow: /payments/" in content, "Missing 'Disallow: /payments/' directive"
    assert "Sitemap:" in content and "/sitemap.xml" in content, "Missing 'Sitemap:' directive pointing to /sitemap.xml"

    print("  [OK] /robots.txt endpoint responded with HTTP 200, text/plain header, and correct crawler directives.")
    print("==================================================")
    print("ROBOTS.TXT DIRECTIVE AUDIT PASSED! (100% SUCCESS)")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
