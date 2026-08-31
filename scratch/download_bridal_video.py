import os
import sys

def download_tiktok(video_url, output_path):
    import yt_dlp
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    ydl_opts = {
        'outtmpl': output_path,
        'format': 'mp4/best',
        'quiet': False,
        'no_warnings': False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

if __name__ == '__main__':
    url1 = "https://www.tiktok.com/@officialbolbash/video/7676997677673975047"
    out1 = os.path.abspath("static/videos/bridal_hero_bg.mp4")
    print(f"Downloading {url1} to {out1}...")
    try:
        download_tiktok(url1, out1)
        print("Success for video 1!")
    except Exception as e:
        print(f"Error video 1: {e}")
        
    url2 = "https://www.tiktok.com/@officialbolbash/video/7677539491195768082"
    out2 = os.path.abspath("static/videos/bridal_lace_melt.mp4")
    print(f"Downloading {url2} to {out2}...")
    try:
        download_tiktok(url2, out2)
        print("Success for video 2!")
    except Exception as e:
        print(f"Error video 2: {e}")
