import os
import sys
from pathlib import Path
from decimal import Decimal

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
os.environ['DATABASE_URL'] = 'mysql://HnvyjHJhq2bDEnt.root:MZxzYbLrAv8ssDtJ@gateway01.eu-central-1.prod.aws.tidbcloud.com:4000/test'

import django
django.setup()

from booking.models import ServiceCategory, Service
from shop.models import ProductCategory, Product
from core.models import Review
from django.contrib.auth.models import User

# Categories
cat_hair, _ = ServiceCategory.objects.get_or_create(
    name="Hair Styling & Installations",
    defaults={'slug': 'hair-styling-installations', 'description': 'Frontal lace melts, custom wig units, luxury styling, and revamping.', 'display_order': 1}
)
cat_bridal, _ = ServiceCategory.objects.get_or_create(
    name="Bridal & Special Occasions",
    defaults={'slug': 'bridal-special-occasions', 'description': 'Full bespoke bridal glam, traditional wedding styling, and trials.', 'display_order': 2}
)
cat_nails, _ = ServiceCategory.objects.get_or_create(
    name="Nail Care & Beauty",
    defaults={'slug': 'nail-care-beauty', 'description': 'Manicure, pedicure, acrylic extensions, and gel artistry.', 'display_order': 3}
)

services = [
    (cat_bridal, "Bespoke Bridal Hair Styling & Glamour", "trending-bridal-hair-styling", "Complete wedding day hair styling, veil setting, and tiara placement.", Decimal("75000.00"), 180, "services/bridal_traditional.jpg", True),
    (cat_hair, "360 & Frontal Wig Installation (HD Melt)", "frontal-installation", "Precision hairline plucking, bleaching knots, skin melt, and luxury styling.", Decimal("25000.00"), 120, "services/salon_hero_showcase.jpg", True),
    (cat_hair, "360 Full Lace Wig Installation", "360-installation", "360 perimeter hairline custom installation with all-around hairline melt.", Decimal("28000.00"), 150, "services/wig_installation_1.jpg", True),
    (cat_hair, "Custom Wig Making & Machine Construction", "wig-making", "Custom fitted wig construction using your bundles and frontal/closure.", Decimal("20000.00"), 180, "services/wig_making_custom_2.jpg", False),
    (cat_hair, "Luxury Hair Revamping, Washing & Treatment", "revamping-of-weavon", "Deep conditioning treatment, lace renewal, detangling, and silky bone straight styling.", Decimal("15000.00"), 90, "services/wig_making_custom_1.jpg", True),
    (cat_nails, "Luxury Acrylic Nail Extensions & Gel Art", "nail-fixing", "Full acrylic nail set with custom gel art, charms, and cuticle care.", Decimal("12000.00"), 90, "services/acrylic_nails_art_1.jpg", True),
    (cat_nails, "Deluxe Spa Pedicure & Foot Treatment", "pedicure-treatment", "Exfoliating foot scrub, callus treatment, massage, and gel polish finish.", Decimal("10000.00"), 60, "services/pedicure_spa_clean_1.jpg", False),
]

for cat, name, slug, desc, price, dur, img, feat in services:
    s, created = Service.objects.update_or_create(
        slug=slug,
        defaults={
            'category': cat,
            'name': name,
            'short_description': desc,
            'description': desc,
            'price': price,
            'duration': dur,
            'image': img,
            'featured': feat,
            'active': True
        }
    )
    print(f"Service: {name} (Active: True)")

# Shop products
pcat, _ = ProductCategory.objects.get_or_create(name="Hair Care & Maintenance", defaults={'slug': 'hair-care-maintenance', 'description': 'Oils, sprays, serums, and protectants.'})

products = [
    (pcat, "Bolbash Ultra Shine Hair Serum", "bolbash-ultra-shine-serum", "Lightweight Argan oil serum for instant gloss and frizz control.", Decimal("6500.00"), 50, "shop/products/hair_spray_oil_1.jpg", True),
    (pcat, "Lace Melting & Extreme Hold Spray", "lace-melting-hold-spray", "Maximum hold invisible lace melting spray with weather-resistant bond.", Decimal("8500.00"), 40, "shop/products/hair_oil_serum_2.jpg", True),
]

for pcat, name, slug, desc, price, stock, img, feat in products:
    p, created = Product.objects.update_or_create(
        slug=slug,
        defaults={
            'category': pcat,
            'name': name,
            'short_description': desc,
            'full_description': desc,
            'price': price,
            'stock_quantity': stock,
            'image': img,
            'is_featured': feat,
            'is_active': True
        }
    )
    print(f"Product: {name} (Stock: {stock})")

print("\n--- Seeding Authentic Reviews ---")
u1, _ = User.objects.get_or_create(username="folake_adebisi", defaults={'first_name': 'Adebisi', 'last_name': 'Folake', 'email': 'folake@gmail.com'})
u2, _ = User.objects.get_or_create(username="seun_alabi", defaults={'first_name': 'Oluwaseun', 'last_name': 'Alabi', 'email': 'seun@yahoo.com'})
u3, _ = User.objects.get_or_create(username="amaka_okonkwo", defaults={'first_name': 'Amaka', 'last_name': 'Okonkwo', 'email': 'amaka@gmail.com'})

s_bridal = Service.objects.filter(slug='trending-bridal-hair-styling').first()
s_frontal = Service.objects.filter(slug='frontal-installation').first()
s_revamp = Service.objects.filter(slug='revamping-of-weavon').first()

Review.objects.update_or_create(
    user=u1, service=s_frontal,
    defaults={'rating': 5, 'comment': "My frontal installation for my wedding was completely seamless! The lace melt was invisible and lasted perfectly throughout the entire event. Bolbash is the absolute best!", 'status': Review.STATUS_APPROVED}
)
Review.objects.update_or_create(
    user=u2, service=s_bridal,
    defaults={'rating': 5, 'comment': "Bolbash styled my entire bridal party and me. Timely, courteous, and extraordinarily talented. My hair held gracefully all day.", 'status': Review.STATUS_APPROVED}
)
Review.objects.update_or_create(
    user=u3, service=s_revamp,
    defaults={'rating': 5, 'comment': "Brought in an old tangled wig and they revived it to bone straight silky perfection. Absolutely worth every naira!", 'status': Review.STATUS_APPROVED}
)

print(f"\nSeeding summary:")
print(f"Services: {Service.objects.count()}")
print(f"Products: {Product.objects.count()}")
print(f"Reviews: {Review.objects.count()}")
