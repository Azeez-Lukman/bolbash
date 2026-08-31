import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from booking.models import Service

def deactivate_test_services():
    test_keywords = ['admin test', 'notif']
    
    services = Service.objects.all()
    deactivated = []
    
    for s in services:
        s_name_lower = s.name.lower()
        if any(kw in s_name_lower for kw in test_keywords):
            s.active = False
            s.featured = False
            s.save()
            deactivated.append(s.name)

    print(f"Successfully deactivated test services (active=False): {deactivated}")

if __name__ == '__main__':
    deactivate_test_services()
