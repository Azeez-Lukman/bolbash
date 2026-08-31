import os
import re
import base64
import urllib.request
import urllib.parse

HTML_PATH = r"C:\Users\USER\.gemini\antigravity-ide\brain\b843ab40-cc61-4535-90c7-ee2a8d3fc13b\.system_generated\steps\21\content.md"
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "images", "hairbybolbash"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(HTML_PATH, "r", encoding="utf-8") as f:
    html_content = f.read()

print(f"Reading HTML content from {HTML_PATH} ({len(html_content)} bytes)...", flush=True)

# 1. Extract base64 images
base64_matches = re.findall(r'data:image/([a-zA-Z0-9+]+);base64,([A-Za-z0-9+/=]+)', html_content)
print(f"Found {len(base64_matches)} base64 inline images.", flush=True)

# Map known service index to meaningful image names
image_names = [
    "logo_main.jpg",
    "bridal_hair_1.jpg",
    "bridal_hair_2.jpg",
    "wig_installation_1.jpg",
    "wig_installation_2.jpg",
    "frontal_melt_1.jpg",
    "frontal_melt_2.jpg",
    "hair_revamping_1.jpg",
    "hair_revamping_2.jpg",
    "wig_making_custom_1.jpg",
    "wig_making_custom_2.jpg",
    "ponytail_updo_1.jpg",
    "ponytail_updo_2.jpg",
    "braids_cornrows_1.jpg",
    "braids_cornrows_2.jpg",
    "pedicure_manicure_1.jpg",
    "pedicure_manicure_2.jpg",
    "nail_extensions_1.jpg",
    "nail_extensions_2.jpg",
    "body_piercing_1.jpg",
    "body_piercing_2.jpg",
    "lash_extensions_1.jpg",
    "lash_extensions_2.jpg",
    "makeup_glam_1.jpg",
    "makeup_glam_2.jpg",
    "hair_product_oil_1.jpg",
    "hair_product_spray_1.jpg",
    "hair_product_wax_1.jpg"
]

extracted_files = []

for idx, (img_type, b64_data) in enumerate(base64_matches):
    ext = 'jpg' if img_type.lower() in ['jpeg', 'jpg'] else img_type.lower()
    if idx < len(image_names):
        filename = image_names[idx]
        if not filename.endswith(f".{ext}"):
            filename = f"{os.path.splitext(filename)[0]}.{ext}"
    else:
        filename = f"image_{idx+1}.{ext}"

    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        b64_clean = b64_data.strip()
        b64_padded = b64_clean + '=' * (-len(b64_clean) % 4)
        data = base64.b64decode(b64_padded)
        with open(filepath, "wb") as f:
            f.write(data)
        file_size = len(data)
        extracted_files.append((filename, filepath, file_size))
        print(f" Saved [{idx+1}/{len(base64_matches)}] {filename} ({file_size} bytes)", flush=True)
    except Exception as e:
        print(f" Error decoding image {idx+1}: {e}", flush=True)

# 2. Search for external HTTP image and video links
http_links = set(re.findall(r'https?://[^\s\'"<>\)]+?\.(?:jpg|jpeg|png|webp|gif|svg|mp4|webm|mov|ogg)', html_content, re.IGNORECASE))
print(f"\nFound {len(http_links)} external media HTTP URLs.", flush=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

for url in http_links:
    parsed = urllib.parse.urlparse(url)
    filename = os.path.basename(parsed.path)
    filepath = os.path.join(OUTPUT_DIR, filename)
    print(f"Downloading external file {url}...", flush=True)
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp, open(filepath, "wb") as f:
            data = resp.read()
            f.write(data)
        print(f" Saved {filename} ({len(data)} bytes)", flush=True)
        extracted_files.append((filename, filepath, len(data)))
    except Exception as e:
        print(f" Failed to download {url}: {e}", flush=True)

print(f"\nExtraction complete! Saved {len(extracted_files)} media assets to:\n{OUTPUT_DIR}", flush=True)
