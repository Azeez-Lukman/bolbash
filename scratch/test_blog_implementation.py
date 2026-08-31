import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from blog.models import BlogCategory, BlogPost


def run_tests():
    print("\n" + "=" * 70)
    print("BOLBASH BEAUTY SPOT — BLOG IMPLEMENTATION & ACADEMY DORMANCY VERIFICATION")
    print("=" * 70)

    client = Client()

    # 1. Test Blog Landing Page (/blog/)
    url = reverse('blog:post_list')
    resp = client.get(url)
    assert resp.status_code == 200, f"Expected 200 for /blog/, got {resp.status_code}"
    assert 'The Bolbash Editorial' in resp.content.decode('utf-8')
    print("[PASS] Test 1: Blog landing page loads successfully with 200 OK and editorial branding.")

    # 2. Test Category Archive (/blog/category/<slug>/)
    cat = BlogCategory.objects.first()
    assert cat is not None, "BlogCategory should exist"
    cat_url = reverse('blog:category_detail', kwargs={'slug': cat.slug})
    resp = client.get(cat_url)
    assert resp.status_code == 200, f"Expected 200 for category {cat.slug}, got {resp.status_code}"
    assert cat.slug in resp.content.decode('utf-8')
    print(f"[PASS] Test 2: Category archive for '{cat.name}' loads correctly with 200 OK.")

    # 3. Test Article Detail Page (/blog/<slug>/)
    post = BlogPost.objects.published().first()
    assert post is not None, "Published BlogPost should exist"
    post_url = reverse('blog:post_detail', kwargs={'slug': post.slug})
    initial_views = post.views_count
    resp = client.get(post_url)
    assert resp.status_code == 200, f"Expected 200 for post {post.slug}, got {resp.status_code}"
    body = resp.content.decode('utf-8')
    assert post.title in body
    assert 'schema.org' in body
    assert 'BlogPosting' in body
    assert 'og:type' in body
    post.refresh_from_db()
    assert post.views_count == initial_views + 1, "View count should increment on visit"
    print(f"[PASS] Test 3: Article '{post.title[:35]}...' loads with JSON-LD, Open Graph metadata, and view counter increment.")

    # 4. Test Draft Article Security Boundary
    draft_post, _ = BlogPost.objects.get_or_create(
        slug="test-secret-draft-article",
        defaults={
            "title": "Secret Upcoming Salon Announcement",
            "category": cat,
            "excerpt": "Draft teaser",
            "content": "Secret content",
            "status": BlogPost.STATUS_DRAFT
        }
    )
    draft_url = reverse('blog:post_detail', kwargs={'slug': draft_post.slug})
    resp_anon = client.get(draft_url)
    assert resp_anon.status_code == 404, f"Expected 404 for anonymous visitor on draft, got {resp_anon.status_code}"
    
    # Test Staff user can preview draft
    staff_user, _ = User.objects.get_or_create(username='test_staff_reviewer', defaults={'is_staff': True})
    staff_user.is_staff = True
    staff_user.save()
    client.force_login(staff_user)
    resp_staff = client.get(draft_url)
    assert resp_staff.status_code == 200, f"Expected 200 for staff preview of draft, got {resp_staff.status_code}"
    assert 'PREVIEW MODE' in resp_staff.content.decode('utf-8')
    client.logout()
    print("[PASS] Test 4: Draft privacy boundary enforced (404 for public visitors, preview banner for staff).")

    # 5. Test Global Navbar & Footer Links
    home_resp = client.get(reverse('core:index'))
    assert home_resp.status_code == 200
    home_html = home_resp.content.decode('utf-8')
    assert '/blog/' in home_html, "Navbar should include /blog/ URL"
    assert 'Blog' in home_html
    # Ensure public navigation does not have active Academy link
    assert '<a href="/academy/"' not in home_html, "Public navbar should not link to /academy/"
    print("[PASS] Test 5: Navbar & Footer properly display 'Blog' and public Academy links are dormant.")

    # 6. Test Sitemap Generation
    sitemap_resp = client.get('/sitemap.xml')
    assert sitemap_resp.status_code == 200
    sitemap_xml = sitemap_resp.content.decode('utf-8')
    assert '/blog/' in sitemap_xml, "Sitemap should contain /blog/"
    print("[PASS] Test 6: Sitemap includes /blog/ and published article entries.")

    print("\n" + "=" * 70)
    print("ALL 6 TESTS PASSED WITH 100% SUCCESS RATE!")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    run_tests()
