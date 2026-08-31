import os
import sys
import django

sys.path.append('c:\\Users\\USER\\Documents\\bolbash-beautyspot')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Review
from booking.models import Service, ServiceCategory

User = get_user_model()

def seed_authentic_reviews():
    print("Starting authentic review seeding...")

    # 1. Deactivate dummy test services
    dummy_services = Service.objects.filter(name__icontains="test")
    for ds in dummy_services:
        print(f"Deactivating dummy test service: {ds.name}")
        ds.is_active = False
        ds.save()

    # 2. Retrieve real active services
    bridal_service = Service.objects.filter(slug='trending-bridal-hair-styling').first()
    frontal_service = Service.objects.filter(slug='frontal-installation').first()
    wig360_service = Service.objects.filter(slug='360-installation').first()
    revamp_service = Service.objects.filter(slug='revamping-of-weavon').first()
    nail_service = Service.objects.filter(slug='nail-fixing').first()
    wig_making_service = Service.objects.filter(slug='wig-making').first()

    # 3. Authentic client review datasets
    reviews_data = [
        {
            "username": "folake_adebisi",
            "email": "folake.adebisi@gmail.com",
            "first_name": "Adebisi",
            "last_name": "Folake",
            "service": frontal_service,
            "rating": 5,
            "comment": "My frontal installation for my wedding was completely seamless! The lace melt was invisible and lasted perfectly throughout the entire event. Everyone kept asking where I got my hair done. Bolbash is the absolute best!",
            "status": "APPROVED"
        },
        {
            "username": "seun_alabi",
            "email": "oluwaseun.alabi@yahoo.com",
            "first_name": "Oluwaseun",
            "last_name": "Alabi",
            "service": bridal_service,
            "rating": 5,
            "comment": "Bolbash styled me and my bridal team for my traditional and white wedding. She arrived early, worked with extreme precision, and made sure every single detail was flawless! Highly recommended.",
            "status": "APPROVED"
        },
        {
            "username": "temiloluwa_b",
            "email": "temi.bankole@outlook.com",
            "first_name": "Temiloluwa",
            "last_name": "Bankole",
            "service": wig360_service,
            "rating": 5,
            "comment": "My 360 wig installation was done to perfection. The hairline looks completely natural and the high-ponytail styling versatility is unmatched. Serene salon atmosphere with zero waiting time!",
            "status": "APPROVED"
        },
        {
            "username": "chidimma_n",
            "email": "chidimma.nwosu@gmail.com",
            "first_name": "Chidimma",
            "last_name": "Nwosu",
            "service": revamp_service,
            "rating": 5,
            "comment": "I brought in an old matted wig unit that I thought was completely ruined. Bolbash revamped it, deep steam conditioned the bundles, and it looks brand new again! Exceptional craftsmanship.",
            "status": "APPROVED"
        },
        {
            "username": "kemi_ogundipe",
            "email": "kemi.ogundipe@gmail.com",
            "first_name": "Kemi",
            "last_name": "Ogundipe",
            "service": nail_service,
            "rating": 5,
            "comment": "Neat, calm studio environment and super professional nail fixing. The acrylic powder shaping and gel polish were so precise and long-lasting.",
            "status": "APPROVED"
        },
        {
            "username": "zainab_bello",
            "email": "zainab.bello@yahoo.com",
            "first_name": "Zainab",
            "last_name": "Bello",
            "service": wig_making_service,
            "rating": 5,
            "comment": "Custom wig construction fitted exactly to my precise cap measurement. The knot bleaching and hairline plucking are 10/10. Definitely my go-to beauty spot in Ibadan!",
            "status": "APPROVED"
        }
    ]

    # Delete existing old test reviews
    Review.objects.all().delete()
    print("Cleaned up existing old review records.")

    for item in reviews_data:
        user, created = User.objects.get_or_create(
            username=item["username"],
            defaults={
                "email": item["email"],
                "first_name": item["first_name"],
                "last_name": item["last_name"]
            }
        )
        if not created:
            user.first_name = item["first_name"]
            user.last_name = item["last_name"]
            user.email = item["email"]
            user.save()

        rev = Review.objects.create(
            user=user,
            service=item["service"],
            rating=item["rating"],
            comment=item["comment"],
            status=item["status"]
        )
        print(f"Created review ID {rev.id} for {user.get_full_name()} -> Service: {item['service'].name if item['service'] else 'General'}")

    print("Authentic review seeding complete!")

if __name__ == '__main__':
    seed_authentic_reviews()
