import os
import sys
import io
import django
from PIL import Image

# Setup Django environment
sys.path.insert(0, r'c:\Users\USER\Documents\bolbash-beautyspot')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from admin_panel.forms import ProductForm, CourseForm, ServiceForm
from shop.models import ProductCategory
from academy.models import CourseCategory
from booking.models import ServiceCategory


def create_valid_image_bytes():
    buf = io.BytesIO()
    img = Image.new('RGB', (10, 10), color='pink')
    img.save(buf, format='PNG')
    return buf.getvalue()


def run_tests():
    print("==================================================")
    print("STARTING PHASE 11 — FILE UPLOAD VALIDATION AUDIT")
    print("==================================================")

    # Categories for form instantiation
    p_cat = ProductCategory.objects.first() or ProductCategory.objects.create(name="File Test Cat")

    # 1. Testing Script & Executable Extensions Rejection
    print("\n--- 1. Script & Executable Extension Rejection ---")
    bad_files = [
        ("malicious.php", b"<?php echo 'hack'; ?>", "application/x-php"),
        ("script.py", b"import os; os.system('ls')", "text/x-python"),
        ("payload.exe", b"MZ1234567890", "application/octet-stream"),
        ("shell.sh", b"#!/bin/bash\necho hack", "application/x-sh"),
        ("page.html", b"<script>alert('xss')</script>", "text/html"),
        ("vector.svg", b"<svg onload=alert(1)></svg>", "image/svg+xml"),
    ]

    for fname, content, ctype in bad_files:
        upload = SimpleUploadedFile(fname, content, content_type=ctype)
        form = ProductForm(data={
            'name': 'Test Product Bad Ext',
            'category': p_cat.id,
            'short_description': 'Short desc',
            'full_description': 'Full desc',
            'price': 5000,
            'stock_quantity': 10,
            'is_active': True,
        }, files={'image': upload})

        assert not form.is_valid(), f"DANGEROUS FILE ACCEPTED! File {fname} passed validation!"
        assert 'image' in form.errors
        print(f"  [OK] Dangerous file '{fname}' correctly rejected: {form.errors['image'][0]}")

    # 2. Testing Non-Image Content Header Rejection
    print("\n--- 2. Non-Image Content Header Rejection ---")
    fake_jpg = SimpleUploadedFile("fake_photo.jpg", b"This is plain text pretending to be a JPG file", content_type="image/jpeg")
    form_fake = ProductForm(data={
        'name': 'Test Product Fake JPG',
        'category': p_cat.id,
        'short_description': 'Short desc',
        'full_description': 'Full desc',
        'price': 5000,
        'stock_quantity': 10,
        'is_active': True,
    }, files={'image': fake_jpg})

    assert not form_fake.is_valid(), "Fake image header passed validation!"
    assert 'image' in form_fake.errors
    print(f"  [OK] Fake JPG file header correctly rejected by Pillow validation.")

    # 3. Testing Oversized File Rejection (>5MB)
    print("\n--- 3. Oversized File Rejection (>5MB) ---")
    valid_png = create_valid_image_bytes()
    huge_data = valid_png + (b"0" * (6 * 1024 * 1024))  # >6MB valid png header + trailing padding
    huge_file = SimpleUploadedFile("huge_photo.png", huge_data, content_type="image/png")
    form_huge = ProductForm(data={
        'name': 'Test Product Huge File',
        'category': p_cat.id,
        'short_description': 'Short desc',
        'full_description': 'Full desc',
        'price': 5000,
        'stock_quantity': 10,
        'is_active': True,
    }, files={'image': huge_file})

    assert not form_huge.is_valid(), "Oversized file (>5MB) passed validation!"
    assert 'image' in form_huge.errors
    print(f"  [OK] Oversized 6MB file correctly rejected: {form_huge.errors['image'][0]}")

    # 4. Testing Valid Image Acceptance
    print("\n--- 4. Valid Image File Acceptance ---")
    valid_png_bytes = create_valid_image_bytes()
    valid_file = SimpleUploadedFile("valid_product.png", valid_png_bytes, content_type="image/png")
    
    form_valid = ProductForm(data={
        'name': 'Valid Product Image',
        'category': p_cat.id,
        'short_description': 'Short desc',
        'full_description': 'Full desc',
        'price': 5000,
        'stock_quantity': 10,
        'is_active': True,
    }, files={'image': valid_file})

    assert form_valid.is_valid(), f"Valid image file rejected! Form errors: {form_valid.errors}"
    print("  [OK] Valid PNG image file (10x10 px) accepted cleanly.")

    print("==================================================")
    print("FILE UPLOAD VALIDATION AUDIT PASSED! (100% SUCCESS)")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
