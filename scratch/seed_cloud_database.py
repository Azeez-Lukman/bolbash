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

from django.contrib.auth.models import User
from booking.models import BusinessHours, ServiceCategory, Service
from blog.models import BlogCategory, BlogPost
from core.models import Review, GalleryImage
from shop.models import ProductCategory, Product
from academy.models import CourseCategory, Course

print("--- 1. Seeding Business Hours ---")
if not BusinessHours.objects.exists():
    BusinessHours.objects.create(
        opening_time='09:00:00',
        closing_time='19:00:00',
        slot_duration=60,
        is_open_sunday=True
    )
    print("BusinessHours created!")

print("--- 2. Seeding Service Categories & Services ---")
cat_hair, _ = ServiceCategory.objects.get_or_create(
    name="Hair Styling & Installations",
    defaults={'slug': 'hair-styling-installations', 'description': 'Frontal lace melts, custom wig units, luxury styling, and revamping.', 'icon': '✂️', 'order': 1}
)
cat_bridal, _ = ServiceCategory.objects.get_or_create(
    name="Bridal & Special Occasions",
    defaults={'slug': 'bridal-special-occasions', 'description': 'Full bespoke bridal glam, traditional wedding styling, and trials.', 'icon': '👰', 'order': 2}
)
cat_nails, _ = ServiceCategory.objects.get_or_create(
    name="Nail Care & Beauty",
    defaults={'slug': 'nail-care-beauty', 'description': 'Manicure, pedicure, acrylic extensions, and gel artistry.', 'icon': '💅', 'order': 3}
)

services_data = [
    (cat_bridal, "Bespoke Bridal Hair Styling & Glamour", "bridal-hairstyling-glam", "Complete wedding day hair styling, veil setting, and tiara placement.", Decimal("75000.00"), 180, "services/bridal_traditional.jpg", True),
    (cat_hair, "360 & Frontal Wig Installation (HD Melt)", "frontal-wig-installation", "Precision hairline plucking, bleaching knots, skin melt, and luxury styling.", Decimal("25000.00"), 120, "services/salon_hero_showcase.jpg", True),
    (cat_hair, "Custom Wig Making & Machine Construction", "custom-wig-making", "Custom fitted wig construction using your bundles and frontal/closure.", Decimal("20000.00"), 180, "services/wig_making_custom_2.jpg", False),
    (cat_hair, "Luxury Hair Revamping, Washing & Treatment", "luxury-hair-revamping", "Deep conditioning treatment, lace renewal, detangling, and silky bone straight styling.", Decimal("15000.00"), 90, "services/wig_making_custom_1.jpg", True),
    (cat_nails, "Luxury Acrylic Nail Extensions & Gel Art", "luxury-acrylic-nails", "Full acrylic nail set with custom gel art, charms, and cuticle care.", Decimal("12000.00"), 90, "services/acrylic_nails_art_1.jpg", True),
    (cat_nails, "Deluxe Spa Pedicure & Foot Treatment", "deluxe-spa-pedicure", "Exfoliating foot scrub, callus treatment, massage, and gel polish finish.", Decimal("10000.00"), 60, "services/pedicure_spa_clean_1.jpg", False),
]

for cat, name, slug, desc, price, dur, img_path, feat in services_data:
    svc, created = Service.objects.get_or_create(
        slug=slug,
        defaults={
            'category': cat,
            'name': name,
            'short_description': desc,
            'description': desc,
            'price': price,
            'duration_minutes': dur,
            'image': img_path,
            'featured': feat,
            'active': True
        }
    )
    if created:
        print(f"Created service: {name}")

print(f"Total Services: {Service.objects.count()}")

print("--- 3. Seeding Editorial Blog Posts ---")
bcat_hair, _ = BlogCategory.objects.get_or_create(name="Hair Care & Maintenance", defaults={'slug': 'hair-care-maintenance', 'description': 'Expert tips for raw virgin hair and lace wig longevity.'})
bcat_bridal, _ = BlogCategory.objects.get_or_create(name="Bridal & Glamour", defaults={'slug': 'bridal-glamour', 'description': 'Inspiration and styling guides for brides.'})

blogs_data = [
    (bcat_hair, "The Art of Raw Virgin Hair Maintenance: 5 Salon Secrets", "art-of-raw-virgin-hair", "Raw virgin hair requires intentional hydration, heat protection, and gentle detangling to maintain its bounce.", "Raw virgin hair is an investment in pure luxury. Unlike processed hair, raw virgin hair requires intentional hydration, sulfate-free washing, and silk bonnet wrapping at night. In this comprehensive salon guide, Bolbash Beauty Spot breaks down the 5 golden rules our master stylists swear by.", "blog/blog_raw_hair_care.jpg", True),
    (bcat_bridal, "Bridal Hair Timeline: When to Book, Prep, and Test Your Style", "bridal-hair-timeline-guide", "Your wedding day is one of the most photographed moments of your life. Plan your hair prep with our timeline.", "Your wedding day is one of the most photographed moments of your life. Discover our month-by-month bridal timeline covering consultation dates, custom unit ordering, trial sessions, and veil integration.", "blog/blog_bridal_timeline.jpg", True),
    (bcat_hair, "Frontal Melt 101: How to Achieve an Invisible Scalp Finish", "frontal-melt-101-invisible-scalp", "The secret behind an undetectable frontal install is precision customization and HD lace matching.", "Achieving a true invisible scalp finish starts with thin HD lace, bleached knots, skin-tone matching lace tint, and residue-free holding adhesive. Learn how Bolbash creates melting artistry that lasts.", "blog/blog_frontal_melt.jpg", True),
]

for bcat, title, slug, excerpt, content, img_path, feat in blogs_data:
    post, created = BlogPost.objects.get_or_create(
        slug=slug,
        defaults={
            'category': bcat,
            'title': title,
            'excerpt': excerpt,
            'content': content,
            'featured_image': img_path,
            'is_featured': feat,
            'status': BlogPost.STATUS_PUBLISHED,
            'meta_title': title,
            'meta_description': excerpt
        }
    )
    if created:
        print(f"Created blog post: {title}")

print(f"Total Blog Posts: {BlogPost.objects.count()}")

print("--- 4. Seeding Products & Categories ---")
pcat_care, _ = ProductCategory.objects.get_or_create(name="Hair Care & Maintenance", defaults={'slug': 'hair-care-maintenance', 'description': 'Serums, sprays, and heat protectants.'})

products_data = [
    (pcat_care, "Bolbash Ultra Shine Serum", "bolbash-ultra-shine-serum", "Lightweight Argan oil serum for instant gloss and frizz control.", Decimal("6500.00"), 50, "shop/products/hair_spray_oil_1.jpg", True),
    (pcat_care, "Lace Melting & Hold Spray", "lace-melting-hold-spray", "Maximum hold invisible lace melting spray with weather-resistant bond.", Decimal("8500.00"), 40, "shop/products/hair_oil_serum_2.jpg", True),
]

for pcat, name, slug, desc, price, stock, img_path, feat in products_data:
    prod, created = Product.objects.get_or_create(
        slug=slug,
        defaults={
            'category': pcat,
            'name': name,
            'short_description': desc,
            'full_description': desc,
            'price': price,
            'stock_quantity': stock,
            'image': img_path,
            'is_featured': feat,
            'is_active': True
        }
    )
    if created:
        print(f"Created product: {name}")

print(f"Total Products: {Product.objects.count()}")

print("--- 5. Seeding Client Reviews ---")
# Create or get a dummy user for reviews
user_bolbash, _ = User.objects.get_or_create(username="client_tiwa", defaults={'first_name': 'Tiwatope', 'last_name': 'A.', 'email': 'tiwa@example.com'})
user_bolbash2, _ = User.objects.get_or_create(username="client_chidinma", defaults={'first_name': 'Chidinma', 'last_name': 'O.', 'email': 'chidinma@example.com'})
user_bolbash3, _ = User.objects.get_or_create(username="client_folake", defaults={'first_name': 'Folake', 'last_name': 'B.', 'email': 'folake@example.com'})

svc_bridal = Service.objects.filter(slug="bridal-hairstyling-glam").first()
svc_frontal = Service.objects.filter(slug="frontal-wig-installation").first()
svc_revamp = Service.objects.filter(slug="luxury-hair-revamping").first()

reviews_data = [
    (user_bolbash, svc_bridal, 5, "Bolbash Beauty Spot made my wedding day unforgettable! The frontal melt was completely invisible and my curls held all through the reception dance. Best salon in Ibadan!"),
    (user_bolbash2, svc_frontal, 5, "Flawless frontal installation! The hairline looks like it is growing directly from my scalp. Super professional staff and serene atmosphere."),
    (user_bolbash3, svc_revamp, 5, "Brought in an old tangled wig and they revived it to bone straight silky perfection. Absolutely worth every naira!"),
]

for usr, svc, rating, comment in reviews_data:
    rev, created = Review.objects.get_or_create(
        user=usr,
        service=svc,
        defaults={
            'customer_name': f"{usr.first_name} {usr.last_name}",
            'rating': rating,
            'comment': comment,
            'status': Review.STATUS_APPROVED
        }
    )
    if created:
        print(f"Created review by {usr.first_name}")

print(f"Total Reviews: {Review.objects.count()}")

print("\n🎉 ALL LIVE DATABASE SEEDING COMPLETED SUCCESSFULLY!")
