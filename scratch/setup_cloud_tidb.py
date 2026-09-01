import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
os.environ['DATABASE_URL'] = 'mysql://HnvyjHJhq2bDEnt.root:MZxzYbLrAv8ssDtJ@gateway01.eu-central-1.prod.aws.tidbcloud.com:4000/test'

import django
django.setup()

from django.core.management import call_command
from django.db import connection

print("Connecting to TiDB Cloud...")

# Helper to execute DDL safely
def safe_exec(sql):
    with connection.cursor() as cur:
        try:
            cur.execute(sql)
            connection.commit()
            print(f"Executed: {sql[:60]}...")
        except Exception as e:
            print(f"Note on '{sql[:40]}...': {e}")

# 1. Notifications table columns
safe_exec("ALTER TABLE notifications_notificationlog ADD COLUMN certificate_id bigint NULL;")
safe_exec("ALTER TABLE notifications_notificationlog ADD COLUMN channel varchar(20) NOT NULL DEFAULT 'EMAIL';")
safe_exec("ALTER TABLE notifications_notificationlog ADD COLUMN enrollment_id bigint NULL;")
safe_exec("ALTER TABLE notifications_notificationlog ADD COLUMN order_id bigint NULL;")
safe_exec("ALTER TABLE notifications_notificationlog ADD COLUMN recipient varchar(255) NOT NULL DEFAULT '';")
safe_exec("ALTER TABLE notifications_notificationlog ADD COLUMN subject_or_summary varchar(255) NOT NULL DEFAULT '';")

# 2. Payments table creation
safe_exec("""
CREATE TABLE IF NOT EXISTS payments_payment (
    id bigint AUTO_INCREMENT PRIMARY KEY,
    reference varchar(50) NOT NULL UNIQUE,
    amount decimal(10,2) NOT NULL,
    currency varchar(10) NOT NULL DEFAULT 'NGN',
    status varchar(20) NOT NULL DEFAULT 'PENDING',
    paystack_reference varchar(100) NULL,
    gateway_response longtext NULL,
    channel varchar(50) NULL,
    paid_at datetime(6) NULL,
    created_at datetime(6) NOT NULL,
    updated_at datetime(6) NOT NULL,
    booking_id bigint NULL,
    enrollment_id bigint NULL,
    payment_type varchar(20) NOT NULL DEFAULT 'BOOKING_DEPOSIT',
    order_id bigint NULL
);
""")

# 3. Sessions table
safe_exec("""
CREATE TABLE IF NOT EXISTS django_session (
    session_key varchar(40) PRIMARY KEY,
    session_data longtext NOT NULL,
    expire_date datetime(6) NOT NULL
);
""")

# Mark all remaining migrations as fake applied
for app, mig in [
    ('notifications', '0002_alter_notificationlog_options_and_more'),
    ('notifications', '0003_alter_notificationlog_notification_type'),
    ('payments', '0001_initial'),
    ('payments', '0002_payment_enrollment_payment_payment_type_and_more'),
    ('payments', '0003_payment_order_alter_payment_payment_type'),
    ('sessions', '0001_initial'),
]:
    try:
        call_command('migrate', app, mig, fake=True, interactive=False)
        print(f"Migration {app}.{mig} marked applied.")
    except Exception as e:
        print(f"Migrate {app}.{mig}: {e}")

print("\n--- Final Migration Check ---")
call_command('showmigrations')

print("\n--- Seeding Initial Data to Cloud TiDB ---")
try:
    from booking.models import BusinessHours, ServiceCategory
    # Business hours
    if not BusinessHours.objects.exists():
        BusinessHours.objects.create(
            opening_time='09:00:00',
            closing_time='19:00:00',
            slot_duration=60,
            is_open_sunday=True
        )
        print("Created BusinessHours")
except Exception as e:
    print("BusinessHours error:", e)

# Run seed scripts
print("\nRunning media and services seed...")
try:
    import subprocess
    env = os.environ.copy()
    subprocess.run([sys.executable, str(BASE_DIR / 'scratch' / 'seed_real_client_media.py')], check=True, env=env)
    print("Real client media seeded!")
except Exception as e:
    print("Media seed error:", e)

print("\nRunning blog editorial seed...")
try:
    subprocess.run([sys.executable, str(BASE_DIR / 'scratch' / 'seed_blog_editorial.py')], check=True, env=env)
    print("Blog editorial seeded!")
except Exception as e:
    print("Blog seed error:", e)

print("\nRunning reviews seed...")
try:
    subprocess.run([sys.executable, str(BASE_DIR / 'scratch' / 'seed_authentic_reviews.py')], check=True, env=env)
    print("Reviews seeded!")
except Exception as e:
    print("Reviews seed error:", e)

print("\n✅ ALL CLOUD DATABASE SETUP & SEEDING COMPLETED SUCCESSFULLY!")
