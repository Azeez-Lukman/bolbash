import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Ensure DATABASE_URL is set to TiDB
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
os.environ['DATABASE_URL'] = 'mysql://HnvyjHJhq2bDEnt.root:MZxzYbLrAv8ssDtJ@gateway01.eu-central-1.prod.aws.tidbcloud.com:4000/test'

import django
django.setup()

from booking.models import BusinessHours

# 1. Business hours
if not BusinessHours.objects.exists():
    for day in range(7):
        BusinessHours.objects.create(
            day_of_week=day,
            opening_time='09:00:00',
            closing_time='18:00:00',
            is_active=True
        )
    print("Created BusinessHours for all 7 days.")

# 2. Real client media & services
print("\n--- 1. Seeding Real Client Services & Media ---")
from scratch.seed_real_client_media import populate_media
populate_media()

# 3. Blog editorial
print("\n--- 2. Seeding Luxury Blog Editorial ---")
from scratch.seed_blog_editorial import seed_blog
seed_blog()

# 4. Authentic client reviews
print("\n--- 3. Seeding Authentic Client Reviews ---")
from scratch.seed_authentic_reviews import seed_authentic_reviews
seed_authentic_reviews()

print("\nALL TI DB SEEDING COMPLETED SUCCESSFULLY!")
