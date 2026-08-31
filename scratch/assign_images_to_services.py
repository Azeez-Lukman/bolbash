import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from booking.models import Service

def assign_images():
    # 1. Hair Cut
    hair_cut_service = Service.objects.filter(name__icontains='hair cut').first()
    if hair_cut_service:
        # Assign hair styling / cut image
        hair_cut_service.image = 'hairbybolbash/ponytail_updo_1.jpg'
        hair_cut_service.save()
        print(f"Assigned image to Hair Cut: {hair_cut_service.image}")

    # 2. Hair Maintenance Products
    maintenance_service = Service.objects.filter(name__icontains='maintenance').first()
    if maintenance_service:
        maintenance_service.image = 'hairbybolbash/hair_product_oil_1.jpg'
        maintenance_service.save()
        print(f"Assigned image to Hair Maintenance Products: {maintenance_service.image}")

if __name__ == '__main__':
    assign_images()
