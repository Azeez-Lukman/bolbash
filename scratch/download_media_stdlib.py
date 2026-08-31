import os
import re
import base64
import urllib.parse
import urllib.request

HTML_PATH = os.path.join(os.path.dirname(__file__), "..", ".system_generated", "steps", "21", "content.md")
# If html file doesn't exist, we will fetch directly
TARGET_URL = "https://hairbybolbash.netlify.app/"

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "images", "hairbybolbash"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_url(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode('utf-8', errors='ignore')

print("Fetching website HTML...")
try:
    html_content = fetch_url(TARGET_URL)
except Exception as e:
    print(f"Error fetching from URL: {e}")
    if os.path.exists(HTML_PATH):
        print(f"Reading from fallback file {HTML_PATH}...")
        with open(HTML_PATH, "r", encoding="utf-8") as f:
            html_content = f.read()
    else:
        html_content = ""

print(f"Loaded HTML content ({len(html_content)} bytes)")

# 1. Find all base64 data URIs
base64_matches = re.findall(r'data:image/([a-zA-Z0-9+]+);base64,([A-Za-z0-9+/=]+)', html_content)
print(f"Found {len(base64_matches)} base64 inline images.")

for idx, (img_type, b64_data) in enumerate(base64_matches, 1):
    ext = 'jpg' if img_type.lower() in ['jpeg', 'jpg'] else img_type.lower()
    filename = f"inline_logo_{idx}.{ext}" if idx == 1 else f"inline_image_{idx}.{ext}"
    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        data = base64.b64decode(b64_data)
        with open(filepath, "wb") as f:
            f.write(data)
        print(f" Saved base64 image {filename} ({len(data)} bytes)")
    except Exception as e:
        print(f" Failed base64 decode: {e}")

# 2. Find all src / srcset / href / url() attributes
urls_found = set()

# Regex patterns for img src, source src, video src, poster, url()
patterns = [
    r'src=[\'"]([^\'"]+)[\'"]',
    r'data-src=[\'"]([^\'"]+)[\'"]',
    r'srcset=[\'"]([^\'"]+)[\'"]',
    r'poster=[\'"]([^\'"]+)[\'"]',
    r'url\s*\(\s*[\'"]?([^\'")\s]+)[\'"]?\s*\)',
    r'https?://[^\s\'"<>\)]+?\.(?:jpg|jpeg|png|webp|gif|svg|mp4|webm|mov|ogg)'
]

for pat in patterns:
    for match in re.findall(pat, html_content, re.IGNORECASE):
        if match.startswith("data:"):
            continue
        # If srcset
        if "," in match and (" " in match or "w" in match or "x" in match):
            for part in match.split(","):
                u = part.strip().split()[0]
                urls_found.add(u)
        else:
            urls_found.add(match)

print(f"\nFound {len(urls_found)} raw URL references.")

valid_media_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg', '.mp4', '.webm', '.ogg', '.mov')

download_count = 0
for raw_url in sorted(urls_found):
    abs_url = urllib.parse.urljoin(TARGET_URL, raw_url)
    parsed = urllib.parse.urlparse(abs_url)
    path = parsed.path.lower()
    
    if any(path.endswith(ext) for ext in valid_media_extensions) or 'image' in path or 'video' in path:
        filename = os.path.basename(parsed.path)
        if not filename or "." not in filename:
            ext = ".jpg"
            filename = f"media_asset_{download_count+1}{ext}"
            
        filepath = os.path.join(OUTPUT_DIR, filename)
        print(f"Downloading {abs_url}...")
        try:
            req = urllib.request.Request(abs_url, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as resp, open(filepath, "wb") as f:
                data = resp.read()
                f.write(data)
            print(f" ✓ Saved {filename} ({len(data)} bytes)")
            download_count += 1
        except Exception as e:
            print(f" ✗ Error downloading {abs_url}: {e}")

print(f"\nCompleted download! Total assets saved to: {OUTPUT_DIR}")
