import os
import sys
import django

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory, Client
from django.template.loader import render_to_string
from django.core.management import call_command
from core.views import custom_404, custom_500


def test_loading_and_error_states():
    print("=== STARTING PHASE ROADMAP: GLOBAL COMPONENTS — LOADING & ERROR STATES TESTS ===")
    rf = RequestFactory()
    client = Client()

    # 1. TEST CUSTOM 404 VIEW & TEMPLATE
    print("\n--- 1. Testing Custom 404 Page Not Found View & Template ---")
    request_404 = rf.get('/non-existent-page-test-xyz-999/')
    response_404 = custom_404(request_404)
    assert response_404.status_code == 404, f"Expected 404 status code, got {response_404.status_code}"
    content_404 = response_404.content.decode('utf-8')
    assert "Page Not Found" in content_404 or "404" in content_404
    assert "Return Home" in content_404
    assert "Explore Services" in content_404
    assert "Visit Academy" in content_404
    assert "Visit Shop" in content_404
    print("[OK] Custom 404 handler & template verified successfully.")

    # 2. TEST CUSTOM 500 VIEW & TEMPLATE
    print("\n--- 2. Testing Custom 500 Server Error View & Template ---")
    request_500 = rf.get('/cause-server-error/')
    response_500 = custom_500(request_500)
    assert response_500.status_code == 500, f"Expected 500 status code, got {response_500.status_code}"
    content_500 = response_500.content.decode('utf-8')
    assert "Something Went Wrong" in content_500 or "500" in content_500
    assert "Reload Page" in content_500
    print("[OK] Custom 500 handler & template verified successfully.")

    # 3. TEST REUSABLE TEMPLATE COMPONENTS RENDERING
    print("\n--- 3. Testing Component Partials Rendering ---")
    
    # Spinner
    spinner_html = render_to_string('components/loading_spinner.html', {'size': 'md', 'color': 'pink'})
    assert 'role="status"' in spinner_html
    assert 'animate-spin' in spinner_html
    print("  [OK] loading_spinner.html rendered.")

    # Page Loader
    loader_html = render_to_string('components/page_loader.html')
    assert 'global-page-loader' in loader_html
    assert 'Processing...' in loader_html
    print("  [OK] page_loader.html rendered.")

    # Card Skeleton
    card_sk_html = render_to_string('components/skeletons/card_skeleton.html')
    assert 'animate-pulse' in card_sk_html
    print("  [OK] card_skeleton.html rendered.")

    # Table Skeleton
    table_sk_html = render_to_string('components/skeletons/table_skeleton.html')
    assert 'animate-pulse' in table_sk_html
    assert 'divide-y' in table_sk_html
    print("  [OK] table_skeleton.html rendered.")

    # Summary Skeleton
    summary_sk_html = render_to_string('components/skeletons/summary_skeleton.html')
    assert 'animate-pulse' in summary_sk_html
    print("  [OK] summary_skeleton.html rendered.")

    # Error State
    error_state_html = render_to_string('components/error_state.html', {
        'title': 'Connection Interrupted',
        'message': 'Failed to fetch items.',
        'retry_text': 'Try Again Now'
    })
    assert 'Connection Interrupted' in error_state_html
    assert 'Try Again Now' in error_state_html
    print("  [OK] error_state.html rendered.")

    # Empty State
    empty_state_html = render_to_string('components/empty_state.html', {
        'icon': '📦',
        'title': 'No Products Found',
        'message': 'Check back later for new arrivals.',
        'cta_url': '/shop/',
        'cta_text': 'Browse Shop'
    })
    assert 'No Products Found' in empty_state_html
    assert 'Browse Shop' in empty_state_html
    print("  [OK] empty_state.html rendered.")

    # Field Error
    field_err_html = render_to_string('components/field_error.html', {
        'errors': ['Please enter a valid email address.']
    })
    assert 'Please enter a valid email address.' in field_err_html
    assert 'role="alert"' in field_err_html
    print("  [OK] field_error.html rendered.")

    # 4. TEST STATIC JS UI STATES FILE
    print("\n--- 4. Testing ui_states.js Controller Static File ---")
    js_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'js', 'ui_states.js')
    assert os.path.exists(js_path), "ui_states.js does not exist in static/js/"
    with open(js_path, 'r', encoding='utf-8') as f:
        js_code = f.read()
    assert "BolbashUI" in js_code
    assert "showButtonLoading" in js_code
    assert "showToast" in js_code
    assert "showFormError" in js_code
    assert "clearFormErrors" in js_code
    print("[OK] ui_states.js structure and methods verified.")

    # 5. TEST DJANGO SYSTEM CHECK
    print("\n--- 5. Testing Django System Check ---")
    call_command('check')
    print("[OK] Django System Check identified 0 issues.")

    print("\n=== ALL GLOBAL COMPONENTS — LOADING & ERROR STATES TESTS PASSED SUCCESSFULLY! ===")


if __name__ == '__main__':
    test_loading_and_error_states()
