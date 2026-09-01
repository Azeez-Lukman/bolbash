import os
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
os.environ['DATABASE_URL'] = 'mysql://HnvyjHJhq2bDEnt.root:MZxzYbLrAv8ssDtJ@gateway01.eu-central-1.prod.aws.tidbcloud.com:4000/test'

import django
django.setup()

from django.db import connection

print("1. Syncing django_migrations table...")
remaining_migrations = [
    ('notifications', '0002_alter_notificationlog_options_and_more'),
    ('notifications', '0003_alter_notificationlog_notification_type'),
    ('payments', '0001_initial'),
    ('payments', '0002_payment_enrollment_payment_payment_type_and_more'),
    ('payments', '0003_payment_order_alter_payment_payment_type'),
    ('sessions', '0001_initial'),
    ('shop', '0001_initial'),
]

now = datetime.now()
with connection.cursor() as cur:
    for app, name in remaining_migrations:
        cur.execute("SELECT id FROM django_migrations WHERE app=%s AND name=%s", [app, name])
        if not cur.fetchone():
            cur.execute("INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)", [app, name, now])
            print(f"Recorded migration: {app}.{name}")
    connection.commit()

print("All migrations synced in TiDB!")

# Now check models
from booking.models import Service, ServiceCategory, BusinessHours
from blog.models import BlogPost, BlogCategory
from core.models import Review

print("\n2. Checking existing counts:")
print(f"Categories: {ServiceCategory.objects.count()}, Services: {Service.objects.count()}")
print(f"Blog categories: {BlogCategory.objects.count()}, Blog posts: {BlogPost.objects.count()}")
print(f"Reviews: {Review.objects.count()}")
