import os
import re
import urllib.parse
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://hairbybolbash.netlify.app/"
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "images", "downloaded"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})

visited_pages = set()
found_media_urls = set()

def get_absolute_url(base, link):
    if not link:
        return None
    return urllib.parse.urljoin(base, link.strip())

def extract_urls_from_text(text, base):
    urls = set()
    # find url(...) in css
    css_urls = re.findall(r'url\s*\(\s*[\'"]?([^\'")\s]+)[\'"]?\s*\)', text, re.IGNORECASE)
    for u in css_urls:
        if not u.startswith("data:"):
            urls.add(get_absolute_url(base, u))
    return urls

def crawl_page(url):
    if url in visited_pages or not url.startswith(BASE_URL):
        return
    visited_pages.add(url)
    print(f"Crawling: {url}")
    
    try:
        resp = session.get(url, timeout=15)
        if resp.status_code != 200:
            print(f"Failed to fetch {url}: {resp.status_code}")
            return
        
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # 1. img tags
        for img in soup.find_all("img"):
            for attr in ["src", "data-src", "srcset", "data-srcset"]:
                val = img.get(attr)
                if val:
                    if "," in val and (" " in val or "w" in val or "x" in val):
                        # handle srcset
                        parts = val.split(",")
                        for part in parts:
                            part_url = part.strip().split()[0]
                            found_media_urls.add(get_absolute_url(url, part_url))
                    else:
                        found_media_urls.add(get_absolute_url(url, val))
                        
        # 2. video & source tags
        for vid in soup.find_all(["video", "source"]):
            for attr in ["src", "data-src", "poster"]:
                val = vid.get(attr)
                if val:
                    found_media_urls.add(get_absolute_url(url, val))
                    
        # 3. meta & link tags
        for meta in soup.find_all("meta"):
            val = meta.get("content")
            if val and any(ext in val.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg', '.mp4', '.webm', '.ogv']):
                found_media_urls.add(get_absolute_url(url, val))
                
        for link in soup.find_all("link"):
            rel = link.get("rel", [])
            if isinstance(rel, list):
                rel = " ".join(rel)
            if "icon" in rel or "image" in link.get("type", ""):
                val = link.get("href")
                if val:
                    found_media_urls.add(get_absolute_url(url, val))
            elif "stylesheet" in rel:
                css_url = get_absolute_url(url, link.get("href"))
                if css_url:
                    try:
                        css_resp = session.get(css_url, timeout=10)
                        if css_resp.status_code == 200:
                            css_media = extract_urls_from_text(css_resp.text, css_url)
                            found_media_urls.update(css_media)
                    except Exception as e:
                        print(f"Error fetching CSS {css_url}: {e}")
                        
        # 4. Inline CSS styles
        for tag in soup.find_all(style=True):
            style_text = tag.get("style", "")
            inline_media = extract_urls_from_text(style_text, url)
            found_media_urls.update(inline_media)
            
        # 5. Internal page links to crawl whole site
        for a in soup.find_all("a", href=True):
            href = a.get("href")
            abs_a = get_absolute_url(url, href)
            if abs_a and abs_a.startswith(BASE_URL) and "#" not in abs_a:
                crawl_page(abs_a)

    except Exception as e:
        print(f"Error crawling {url}: {e}")

print("Starting scraper...")
crawl_page(BASE_URL)

print(f"\nFound {len(found_media_urls)} potential media URLs:")
for media_url in sorted(found_media_urls):
    if media_url:
        print(" -", media_url)

# Now download all media files
print("\nDownloading media files...")
downloaded_count = 0
for media_url in sorted(found_media_urls):
    if not media_url or media_url.startswith("data:"):
        continue
        
    parsed = urllib.parse.urlparse(media_url)
    filename = os.path.basename(parsed.path)
    if not filename or "." not in filename:
        continue
        
    # Check extension
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg', '.mp4', '.webm', '.ogg', '.mov', '.avi', '.mp3']:
        continue

    dest_path = os.path.join(OUTPUT_DIR, filename)
    print(f"Downloading {filename} from {media_url}...")
    try:
        r = session.get(media_url, stream=True, timeout=30)
        if r.status_code == 200:
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"  ✓ Saved to {dest_path} ({os.path.getsize(dest_path)} bytes)")
            downloaded_count += 1
        else:
            print(f"  ✗ Failed HTTP {r.status_code}")
    except Exception as e:
        print(f"  ✗ Exception: {e}")

print(f"\nDone! Downloaded {downloaded_count} files to {OUTPUT_DIR}")
