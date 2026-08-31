import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import ServiceCategory, Service

def remove_test_categories():
    test_keywords = ['admin test', 'notif']
    
    # Get a fallback valid category like 'Hair Styling'
    fallback_cat = ServiceCategory.objects.exclude(name__icontains='test').exclude(name__icontains='notif').first()
    
    categories = ServiceCategory.objects.all()
    deleted_names = []
    
    for cat in categories:
        cat_name_lower = cat.name.lower()
        if any(kw in cat_name_lower for kw in test_keywords):
            # Reassign services to fallback category & deactivate them
            services = Service.objects.filter(category=cat)
            for s in services:
                if fallback_cat:
                    s.category = fallback_cat
                s.is_active = False
                s.save()
            
            name = cat.name
            cat.delete()
            deleted_names.append(name)

    print(f"Successfully deleted test categories: {deleted_names}")

if __name__ == '__main__':
    remove_test_categories()
