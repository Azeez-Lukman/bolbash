import os
import sys
import xml.etree.ElementTree as ET
import django

# Setup Django environment
sys.path.insert(0, r'c:\Users\USER\Documents\bolbash-beautyspot')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.urls import reverse

from booking.models import ServiceCategory, Service
from academy.models import CourseCategory, Course
from shop.models import ProductCategory, Product


def run_tests():
    print("==================================================")
    print("STARTING TEST SUITE FOR PHASE 10 — SITEMAP (XML)")
    print("==================================================")

    client = Client()

    # Dynamic objects
    svc_cat = ServiceCategory.objects.first() or ServiceCategory.objects.create(name="Sitemap Hair Category")
    svc = Service.objects.filter(active=True).first()
    if not svc:
        svc = Service.objects.create(
            name="Sitemap Frontal Styling",
            slug="sitemap-frontal-styling",
            category=svc_cat,
            short_description="Short desc",
            description="Full desc",
            price=20000.00,
            active=True
        )

    crs_cat = CourseCategory.objects.first() or CourseCategory.objects.create(name="Sitemap Academy Category")
    crs = Course.objects.filter(active=True).first()
    if not crs:
        crs = Course.objects.create(
            category=crs_cat,
            title="Sitemap Wig Class",
            slug="sitemap-wig-class",
            short_description="Short desc",
            full_description="Full desc",
            price=50000.00,
            active=True
        )

    prd_cat = ProductCategory.objects.first() or ProductCategory.objects.create(name="Sitemap Shop Category")
    prd = Product.objects.filter(is_active=True).first()
    if not prd:
        prd = Product.objects.create(
            category=prd_cat,
            name="Sitemap Hair Serum",
            slug="sitemap-hair-serum",
            short_description="Short desc",
            full_description="Full desc",
            price=3500.00,
            stock_quantity=15,
            is_active=True
        )

    response = client.get('/sitemap.xml')
    assert response.status_code == 200, f"Failed to load /sitemap.xml, status code {response.status_code}"
    assert 'xml' in response['Content-Type'].lower(), f"Expected XML Content-Type, got '{response['Content-Type']}'"

    xml_content = response.content.decode('utf-8')
    root = ET.fromstring(xml_content)

    # Namespace handling
    ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    urls_found = []
    for url_node in root.findall('sm:url', ns):
        loc = url_node.find('sm:loc', ns).text
        priority = url_node.find('sm:priority', ns).text if url_node.find('sm:priority', ns) is not None else None
        changefreq = url_node.find('sm:changefreq', ns).text if url_node.find('sm:changefreq', ns) is not None else None
        urls_found.append((loc, priority, changefreq))

    assert len(urls_found) > 0, "No URLs found inside sitemap XML root"

    # Static URL assertions
    expected_static_paths = [
        reverse('core:index'),
        reverse('core:about'),
        reverse('core:service_list'),
        reverse('core:bridal'),
        reverse('core:gallery'),
        reverse('core:reviews_showcase'),
        reverse('core:contact'),
        reverse('academy:academy_landing'),
        reverse('academy:course_list'),
        reverse('shop:shop_landing'),
        reverse('shop:product_catalogue'),
    ]

    all_locs = [u[0] for u in urls_found]

    for path in expected_static_paths:
        matched = any(path in loc for loc in all_locs)
        assert matched, f"Expected static path '{path}' missing from sitemap XML"

    # Dynamic model URL assertions
    assert any(svc.get_absolute_url() in loc for loc in all_locs), f"Service URL '{svc.get_absolute_url()}' missing from sitemap XML"
    assert any(crs.get_absolute_url() in loc for loc in all_locs), f"Course URL '{crs.get_absolute_url()}' missing from sitemap XML"
    assert any(prd.get_absolute_url() in loc for loc in all_locs), f"Product URL '{prd.get_absolute_url()}' missing from sitemap XML"

    print(f"  [OK] Successfully indexed {len(urls_found)} URLs in /sitemap.xml")
    print("==================================================")
    print("SITEMAP XML GENERATION & ROUTING AUDIT PASSED! (100% SUCCESS)")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
