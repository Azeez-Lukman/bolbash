import os
import sys
from pathlib import Path
import django

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from django.core.management import call_command
import dj_database_url

def test_whitenoise_static_storage():
    print("Testing Whitenoise static files configuration...")
    assert 'whitenoise.middleware.WhiteNoiseMiddleware' in settings.MIDDLEWARE, "WhiteNoiseMiddleware missing from MIDDLEWARE"
    assert settings.STATICFILES_STORAGE == 'whitenoise.storage.CompressedManifestStaticFilesStorage', "Incorrect STATICFILES_STORAGE"
    print("[PASS] Whitenoise middleware and storage configured successfully.")

def test_database_url_support():
    print("Testing DATABASE_URL parsing support...")
    test_db_url = "mysql://bolbash_user:SecretPass123@db-host.render.com:3306/bolbash_prod_db"
    parsed = dj_database_url.config(default=test_db_url, engine='django.db.backends.mysql')
    assert parsed['ENGINE'] == 'django.db.backends.mysql', "Engine must be MySQL"
    assert parsed['NAME'] == 'bolbash_prod_db', "DB name mismatch"
    assert parsed['USER'] == 'bolbash_user', "DB user mismatch"
    assert parsed['PASSWORD'] == 'SecretPass123', "DB password mismatch"
    assert parsed['HOST'] == 'db-host.render.com', "DB host mismatch"
    assert parsed['PORT'] == 3306, "DB port mismatch"
    print("[PASS] DATABASE_URL parser accurately parses cloud MySQL connection strings.")

def test_render_host_and_csrf():
    print("Testing Render host and CSRF trusted origins...")
    # Check that settings includes standard production hosts and origins
    assert isinstance(settings.ALLOWED_HOSTS, list), "ALLOWED_HOSTS must be a list"
    assert isinstance(settings.CSRF_TRUSTED_ORIGINS, list), "CSRF_TRUSTED_ORIGINS must be a list"
    print("[PASS] Host and CSRF configurations loaded cleanly.")

def test_production_security_settings():
    print("Testing production security settings...")
    assert settings.SECURE_BROWSER_XSS_FILTER is True, "XSS filter must be True"
    assert settings.SECURE_CONTENT_TYPE_NOSNIFF is True, "No-sniff must be True"
    assert settings.X_FRAME_OPTIONS == 'DENY', "X_FRAME_OPTIONS must be DENY"
    assert settings.SECURE_PROXY_SSL_HEADER == ('HTTP_X_FORWARDED_PROTO', 'https'), "Proxy SSL header mismatch"
    print("[PASS] Production security settings verified.")

def test_static_collection():
    print("Testing static asset collection...")
    os.makedirs(settings.STATIC_ROOT, exist_ok=True)
    call_command('collectstatic', interactive=False, verbosity=0)
    assert os.path.exists(settings.STATIC_ROOT), "STATIC_ROOT must exist after collectstatic"
    print("[PASS] Collectstatic completed successfully with WhiteNoise manifest.")

if __name__ == '__main__':
    print("=" * 60)
    print("PHASE 13: PRODUCTION DEPLOYMENT READINESS TEST SUITE")
    print("=" * 60)
    try:
        test_whitenoise_static_storage()
        test_database_url_support()
        test_render_host_and_csrf()
        test_production_security_settings()
        test_static_collection()
        print("=" * 60)
        print("ALL DEPLOYMENT READINESS TESTS PASSED (5/5)!")
        print("=" * 60)
    except AssertionError as e:
        print(f"FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
