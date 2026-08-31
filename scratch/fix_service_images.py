import os
import sys
import shutil
import django

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from booking.models import Service

src_dir = os.path.join(settings.BASE_DIR, 'static', 'images', 'hairbybolbash')
media_svc_dir = os.path.join(settings.MEDIA_ROOT, 'services')
os.makedirs(media_svc_dir, exist_ok=True)

# 1. Hair Cut (ID 2)
src_haircut = os.path.join(src_dir, 'ponytail_updo_1.jpg')
dst_haircut = os.path.join(media_svc_dir, 'hair_cut_1.jpg')
if os.path.exists(src_haircut):
    shutil.copy2(src_haircut, dst_haircut)
    svc = Service.objects.get(id=2)
    svc.image = 'services/hair_cut_1.jpg'
    svc.save()
    print("Updated Hair Cut service image to services/hair_cut_1.jpg")

# 2. Hair Maintenance Products (ID 13)
src_prod = os.path.join(src_dir, 'hair_product_oil_1.jpg')
dst_prod = os.path.join(media_svc_dir, 'hair_product_oil_1.jpg')
if os.path.exists(src_prod):
    shutil.copy2(src_prod, dst_prod)
    svc = Service.objects.get(id=13)
    svc.image = 'services/hair_product_oil_1.jpg'
    svc.save()
    print("Updated Hair Maintenance Products service image to services/hair_product_oil_1.jpg")

print("\n--- Service Image Verification ---")
for s in Service.objects.filter(active=True):
    exists = os.path.exists(s.image.path) if s.image else False
    print(f"ID {s.id}: {s.name} -> {s.image.name if s.image else 'NO IMAGE'} | Exists: {exists}")
