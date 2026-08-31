import os
import sys
import shutil
import django

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from booking.models import Service
from shop.models import Product
from academy.models import Course
from core.models import GalleryImage

SOURCE_DIR = os.path.join(settings.BASE_DIR, 'static', 'images', 'hairbybolbash')
MEDIA_ROOT = settings.MEDIA_ROOT

def copy_media_file(src_name, target_subpath):
    src = os.path.join(SOURCE_DIR, src_name)
    dst = os.path.join(MEDIA_ROOT, target_subpath)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"  Copied {src_name} -> {target_subpath}")
        return target_subpath
    else:
        print(f"  Source image not found: {src_name}")
        return None

print("=== 1. UPDATING SERVICES WITH REAL CLIENT IMAGES ===")
service_image_map = {
    1: 'bridal_hair_1.jpg',
    2: 'ponytail_updo_1.jpg',
    3: 'wig_installation_1.jpg',
    4: 'frontal_melt_1.jpg',
    5: 'wig_installation_2.jpg',
    6: 'wig_making_custom_1.jpg',
    7: 'frontal_melt_2.jpg',
    8: 'hair_revamping_1.jpg',
    9: 'nail_extensions_1.jpg',
    10: 'pedicure_manicure_1.jpg',
    11: 'pedicure_manicure_2.jpg',
    12: 'hair_revamping_2.jpg',
    13: 'hair_product_oil_1.jpg',
    14: 'body_piercing_1.jpg',
}

for svc_id, img_file in service_image_map.items():
    try:
        svc = Service.objects.get(id=svc_id)
        rel_path = copy_media_file(img_file, f"services/{img_file}")
        if rel_path:
            svc.image = rel_path
            svc.save()
            print(f" Updated Service [{svc.name}] with image {rel_path}")
    except Service.DoesNotExist:
        print(f" Service ID {svc_id} not found.")

print("\n=== 2. UPDATING SHOP PRODUCTS WITH REAL CLIENT IMAGES ===")
product_image_map = {
    1: 'hair_product_spray_1.jpg',
    2: 'hair_product_oil_1.jpg',
    3: 'hair_product_oil_1.jpg',
    5: 'hair_product_wax_1.jpg',
}

for prod_id, img_file in product_image_map.items():
    try:
        prod = Product.objects.get(id=prod_id)
        rel_path = copy_media_file(img_file, f"shop/products/{img_file}")
        if rel_path:
            prod.image = rel_path
            prod.save()
            print(f" Updated Product [{prod.name}] with image {rel_path}")
    except Product.DoesNotExist:
        print(f" Product ID {prod_id} not found.")

print("\n=== 3. UPDATING ACADEMY COURSES WITH REAL CLIENT IMAGES ===")
course_image_map = {
    1: 'wig_making_custom_2.jpg',
    2: 'wig_installation_1.jpg',
    3: 'bridal_hair_2.jpg',
    4: 'hair_revamping_1.jpg',
}

for course_id, img_file in course_image_map.items():
    try:
        c = Course.objects.get(id=course_id)
        rel_path = copy_media_file(img_file, f"academy/courses/{img_file}")
        if rel_path:
            c.thumbnail = rel_path
            c.save()
            print(f" Updated Course [{c.title}] with thumbnail {rel_path}")
    except Course.DoesNotExist:
        print(f" Course ID {course_id} not found.")

print("\n=== 4. POPULATING PORTFOLIO GALLERY IMAGES ===")
# Clear old placeholders if any
GalleryImage.objects.all().delete()

gallery_data = [
    # BRIDAL
    {'title': 'Luxury Royal Bridal Styling', 'category': 'BRIDAL', 'file': 'bridal_hair_1.jpg', 'caption': 'Custom bridal hair sculpting with veil fitting for classic luxury.'},
    {'title': 'Glamorous Nigerian Bridal Hair', 'category': 'BRIDAL', 'file': 'bridal_hair_2.jpg', 'caption': 'Radiant wedding day hair design tailored for the modern bride.'},
    {'title': 'Traditional Engagement Hair & Makeup', 'category': 'BRIDAL', 'file': 'image_29.jpg', 'caption': 'Complete traditional wedding glam and crown placement.'},
    {'title': 'Elegance Bridal Updo Transformation', 'category': 'BRIDAL', 'file': 'image_30.jpg', 'caption': 'High glamour bridal updo with hand-styled waves.'},

    # HAIRSTYLES
    {'title': 'Sleek High Ponytail & Edges', 'category': 'HAIRSTYLES', 'file': 'ponytail_updo_1.jpg', 'caption': 'Ultra-sleek high ponytail with custom edge design.'},
    {'title': 'Luxury Hollywood Waves', 'category': 'HAIRSTYLES', 'file': 'ponytail_updo_2.jpg', 'caption': 'Glamorous Hollywood wave styling for special occasions.'},
    {'title': 'Knotless Braids & Patterned Cornrows', 'category': 'HAIRSTYLES', 'file': 'braids_cornrows_1.jpg', 'caption': 'Precision knotless braids crafted for clean scalp lines.'},
    {'title': 'Full Protective Braided Style', 'category': 'HAIRSTYLES', 'file': 'braids_cornrows_2.jpg', 'caption': 'Long-lasting protective cornrows and stitch braids.'},
    {'title': 'Glossy Silk Press Finish', 'category': 'HAIRSTYLES', 'file': 'image_31.jpg', 'caption': 'Featherweight silk press with intense shine treatment.'},
    {'title': 'Designer Braid Sculpting', 'category': 'HAIRSTYLES', 'file': 'image_32.jpg', 'caption': 'Intricate braided updo design for events.'},

    # WIG_MELT
    {'title': '360 HD Frontal Invisible Lace Melt', 'category': 'WIG_MELT', 'file': 'wig_installation_1.jpg', 'caption': 'Seamless 360 frontal melt giving natural scalp illusion.'},
    {'title': 'Flawless HD Frontal Custom Melt', 'category': 'WIG_MELT', 'file': 'wig_installation_2.jpg', 'caption': 'HD lace melt with customized hairline and baby hair.'},
    {'title': 'Seamless Skin-Fusion Lace Frontal', 'category': 'WIG_MELT', 'file': 'frontal_melt_1.jpg', 'caption': 'Melting technique tailored for effortless natural parting.'},
    {'title': 'Precision Plucked Lace Installation', 'category': 'WIG_MELT', 'file': 'frontal_melt_2.jpg', 'caption': 'Hand-plucked frontal installation with glueless finish.'},
    {'title': 'HD Closure Melt Transformation', 'category': 'WIG_MELT', 'file': 'image_33.jpg', 'caption': 'Flawless 5x5 HD closure installation.'},
    {'title': 'Custom Glueless Frontal Fitting', 'category': 'WIG_MELT', 'file': 'image_34.jpg', 'caption': 'Custom fitted glueless wig unit installation.'},

    # TRANSFORMATION
    {'title': 'Deep Conditioning & Hair Revamping', 'category': 'TRANSFORMATION', 'file': 'hair_revamping_1.jpg', 'caption': 'Full wig detox, steam treatment, and silk restoration.'},
    {'title': 'Color Bleaching & Weavon Restoration', 'category': 'TRANSFORMATION', 'file': 'hair_revamping_2.jpg', 'caption': 'Custom color tinting and lace bleach customization.'},
    {'title': 'Custom Hand-Crafted Wig Unit', 'category': 'TRANSFORMATION', 'file': 'wig_making_custom_1.jpg', 'caption': 'Custom machine-made wig constructed to client cap size.'},
    {'title': 'Custom Tailored Luxury Unit', 'category': 'TRANSFORMATION', 'file': 'wig_making_custom_2.jpg', 'caption': 'Virgin hair wig construction with custom highlights.'},
    {'title': 'Complete Weave Revitalizing', 'category': 'TRANSFORMATION', 'file': 'image_35.jpg', 'caption': 'Full hair bundle restoration and re-styling.'},
    {'title': 'Natural Hair Extension Weaving', 'category': 'TRANSFORMATION', 'file': 'image_36.jpg', 'caption': 'Volumizing weave installation and layer blending.'},

    # NATURAL_HAIR
    {'title': 'Nourishing Scalp & Natural Hair Care', 'category': 'NATURAL_HAIR', 'file': 'image_37.jpg', 'caption': 'Organic oil scalp treatment and deep moisture lock.'},
    {'title': 'Hydrating Moisture Lock Treatment', 'category': 'NATURAL_HAIR', 'file': 'image_38.jpg', 'caption': 'Deep conditioning treatment restoring natural bounce.'},
    {'title': 'Natural Texture Curl Definition', 'category': 'NATURAL_HAIR', 'file': 'image_39.jpg', 'caption': 'Curl pop definition and hydration treatment.'},
    {'title': 'Healthy Growth Protective Style', 'category': 'NATURAL_HAIR', 'file': 'image_40.jpg', 'caption': 'Scalp-friendly protective style for length retention.'},

    # EVENTS
    {'title': 'Soft Glam Makeup & Styling', 'category': 'EVENTS', 'file': 'makeup_glam_1.jpg', 'caption': 'Soft radiant glam makeup paired with sleek hair.'},
    {'title': 'Full Evening Glamour Transformation', 'category': 'EVENTS', 'file': 'makeup_glam_2.jpg', 'caption': 'High contrast evening makeup for special galas.'},
    {'title': 'Luxury Event Glamour', 'category': 'EVENTS', 'file': 'image_41.jpg', 'caption': 'Red carpet ready beauty look.'},
    {'title': 'Special Occasion Beauty Styling', 'category': 'EVENTS', 'file': 'image_42.jpg', 'caption': 'Elegant event makeup and hair finish.'},
    {'title': 'Red Carpet Beauty Transformation', 'category': 'EVENTS', 'file': 'image_43.jpg', 'caption': 'Sophisticated beauty look for VIP events.'},
    {'title': 'Gala Dinner Glam Finish', 'category': 'EVENTS', 'file': 'image_44.jpg', 'caption': 'Glossy glam finish for evening celebrations.'},
    {'title': 'Celebration Beauty Look', 'category': 'EVENTS', 'file': 'image_45.jpg', 'caption': 'Party glam with defined brows and flawless skin.'},
    {'title': 'Birthday Glam Transformation', 'category': 'EVENTS', 'file': 'image_46.jpg', 'caption': 'Birthday celebration full glam styling.'},
    {'title': 'High Fashion Editorial Styling', 'category': 'EVENTS', 'file': 'image_47.jpg', 'caption': 'High fashion editorial look created at Bolbash.'},
]

for order, item in enumerate(gallery_data, start=1):
    rel_path = copy_media_file(item['file'], f"gallery/{item['file']}")
    if rel_path:
        g = GalleryImage.objects.create(
            title=item['title'],
            category=item['category'],
            image=rel_path,
            caption=item['caption'],
            display_order=order,
            is_active=True
        )
        print(f" Created GalleryImage [{g.title}] ({g.category}) -> {rel_path}")

print("\n=== 5. UPDATING STATIC HIGH-RES SHOWCASE ASSETS ===")
static_dest = os.path.join(settings.BASE_DIR, 'static', 'images')

static_updates = [
    ('bridal_hair_1.jpg', 'bridal_hero.jpg'),
    ('frontal_melt_1.jpg', 'frontal_melt_showcase.jpg'),
    ('bridal_hair_2.jpg', 'bridal_traditional.jpg'),
    ('makeup_glam_1.jpg', 'bolbash_hero_glam_model.jpg'),
    ('wig_installation_1.jpg', 'salon_hero_showcase.jpg'),
]

for src_name, dst_name in static_updates:
    src = os.path.join(SOURCE_DIR, src_name)
    dst = os.path.join(static_dest, dst_name)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f" Updated static image {dst_name} from {src_name}")

print("\n=== MEDIA SEEDING & INTEGRATION COMPLETE! ===")
