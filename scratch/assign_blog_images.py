import os
import sys
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.conf import settings
from blog.models import BlogPost


def assign_blog_media():
    print("Assigning real high-res images to blog posts...")
    
    media_blog_dir = os.path.join(settings.MEDIA_ROOT, 'blog')
    os.makedirs(media_blog_dir, exist_ok=True)

    static_images_dir = os.path.join(settings.BASE_DIR, 'static', 'images', 'hairbybolbash')

    mapping = {
        "how-to-maintain-raw-virgin-hair-frontal-melt": "frontal_melt_1.jpg",
        "ultimate-bridal-hair-preparation-guide": "bridal_hair_1.jpg",
        "5-signs-your-wig-needs-professional-revamp": "hair_revamping_1.jpg",
        "hd-lace-vs-swiss-lace-guide": "wig_installation_1.jpg",
        "test-secret-draft-article": "wig_making_custom_1.jpg"
    }

    for slug, img_filename in mapping.items():
        src_path = os.path.join(static_images_dir, img_filename)
        dest_path = os.path.join(media_blog_dir, img_filename)

        if os.path.exists(src_path):
            shutil.copy2(src_path, dest_path)
            post = BlogPost.objects.filter(slug=slug).first()
            if post:
                post.featured_image = f'blog/{img_filename}'
                post.save(update_fields=['featured_image'])
                print(f"  - Assigned {img_filename} to '{post.title}'")
        else:
            print(f"  - Source image not found: {src_path}")

    print("Blog media assignment complete!")


if __name__ == '__main__':
    assign_blog_media()
