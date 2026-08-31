import os
import sys
import django
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from booking.models import ServiceCategory, Service
from shop.models import ProductCategory, Product
from academy.models import CourseCategory, Course
from core.models import GalleryImage

print("=== SERVICE CATEGORIES ===")
for cat in ServiceCategory.objects.all():
    print(f"- [{cat.id}] {cat.name} (slug: {cat.slug})")

print("\n=== SERVICES ===")
for svc in Service.objects.all():
    print(f"- [{svc.id}] {svc.name} (cat: {svc.category.name}, slug: {svc.slug}, img: {svc.image})")

print("\n=== PRODUCTS ===")
for prod in Product.objects.all():
    print(f"- [{prod.id}] {prod.name} (slug: {prod.slug}, img: {prod.image})")

print("\n=== COURSES ===")
for c in Course.objects.all():
    print(f"- [{c.id}] {c.title} (slug: {c.slug}, img: {c.thumbnail})")

print("\n=== EXISTING GALLERY IMAGES ===")
print(f"Total count: {GalleryImage.objects.count()}")
for img in GalleryImage.objects.all()[:10]:
    print(f"- [{img.id}] {img.title} ({img.category}) -> {img.image}")
