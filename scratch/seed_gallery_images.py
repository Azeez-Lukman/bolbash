import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.models import GalleryImage
from django.core.files import File

def seed_gallery():
    print("Checking Gallery Images...")
    if GalleryImage.objects.count() > 0:
        print(f"Gallery images already exist: {GalleryImage.objects.count()} items.")
        return

    images_data = [
        {
            'title': 'Luxury Royal Bridal Styling',
            'category': 'BRIDAL',
            'caption': 'Bespoke bridal crown styling and luxury veil placement for wedding ceremony.',
            'src_path': 'static/images/bridal_hero.jpg',
            'order': 1,
        },
        {
            'title': '360 HD Frontal Invisible Lace Melt',
            'category': 'WIG_MELT',
            'caption': 'Flawless skin-like frontal melt with natural hairline customization.',
            'src_path': 'static/images/frontal_melt_showcase.jpg',
            'order': 2,
        },
        {
            'title': 'Traditional Engagement Glam',
            'category': 'BRIDAL',
            'caption': 'Elegantly sculpted traditional engagement hair styling and headpiece glam.',
            'src_path': 'static/images/bridal_traditional.jpg',
            'order': 3,
        },
        {
            'title': 'Signature Glossy Silk Press',
            'category': 'HAIRSTYLES',
            'caption': 'Ultra-smooth, heat-protected silk press with healthy trim finish.',
            'src_path': 'static/images/salon_hero_showcase.jpg',
            'order': 4,
        },
    ]

    for data in images_data:
        if os.path.exists(data['src_path']):
            with open(data['src_path'], 'rb') as f:
                img_file = File(f, name=os.path.basename(data['src_path']))
                item = GalleryImage.objects.create(
                    title=data['title'],
                    category=data['category'],
                    caption=data['caption'],
                    display_order=data['order'],
                    is_active=True
                )
                item.image.save(os.path.basename(data['src_path']), img_file, save=True)
                print(f"Created GalleryImage: {item.title}")

if __name__ == '__main__':
    seed_gallery()
