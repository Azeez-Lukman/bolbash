import os
import sys
import django

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from shop.models import ProductCategory, Product

def update_test_categories():
    print("--- Current Product Categories ---")
    for cat in ProductCategory.objects.all():
        print(f"ID: {cat.id} | Name: '{cat.name}' | Slug: '{cat.slug}'")

    # 1. Rename 'Admin Shop Cat' -> 'Wigs & Frontals'
    admin_cat = ProductCategory.objects.filter(name__icontains='Admin Shop Cat').first()
    if admin_cat:
        admin_cat.name = 'Wigs & Frontals'
        admin_cat.slug = 'wigs-frontals'
        admin_cat.description = 'Luxury 360 & frontal wigs, closures, and custom hair extensions.'
        admin_cat.icon = '💇‍♀️'
        admin_cat.save()
        print(f" Updated 'Admin Shop Cat' -> 'Wigs & Frontals' [OK]")

    # 2. Rename 'Notif Shop' -> 'Skin & Beauty Essentials'
    notif_cat = ProductCategory.objects.filter(name__icontains='Notif Shop').first()
    if notif_cat:
        notif_cat.name = 'Skin & Beauty Essentials'
        notif_cat.slug = 'skin-beauty-essentials'
        notif_cat.description = 'Nourishing skincare oils, glow serums, and beauty accessories.'
        notif_cat.icon = '✨'
        notif_cat.save()
        print(f" Updated 'Notif Shop' -> 'Skin & Beauty Essentials' [OK]")

    print("\n--- Updated Product Categories ---")
    for cat in ProductCategory.objects.all():
        print(f"ID: {cat.id} | Name: '{cat.name}' | Slug: '{cat.slug}' | Icon: '{cat.icon}'")

if __name__ == '__main__':
    update_test_categories()
