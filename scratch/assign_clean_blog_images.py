import os
import sys
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.conf import settings
from blog.models import BlogPost

media_blog_dir = os.path.join(settings.MEDIA_ROOT, 'blog')
os.makedirs(media_blog_dir, exist_ok=True)

# Copy premium clean images to media/blog/
static_img_dir = os.path.join(settings.BASE_DIR, 'static', 'images')

mappings = {
    'how-to-maintain-raw-virgin-hair-frontal-melt': 'bolbash_editorial_model.jpg',
    'hd-lace-vs-swiss-lace-guide': 'salon_hero_showcase.jpg',
    'ultimate-bridal-hair-preparation-guide': 'bridal_hero.jpg',
    '5-signs-your-wig-needs-professional-revamp': 'bolbash_hero_glam_model.jpg',
}

for slug, filename in mappings.items():
    src = os.path.join(static_img_dir, filename)
    if os.path.exists(src):
        dst = os.path.join(media_blog_dir, filename)
        shutil.copy2(src, dst)
        try:
            post = BlogPost.objects.get(slug=slug)
            post.featured_image = f'blog/{filename}'
            post.save(update_fields=['featured_image'])
            print(f"Updated {slug} -> blog/{filename}")
        except BlogPost.DoesNotExist:
            print(f"Post with slug {slug} not found")

print("All blog images updated successfully with clean premium assets.")
