# fix_fonts.py
import pygame
import requests
import os
from pathlib import Path

def download_fonts():
    """Tự động tải font Noto Sans (hỗ trợ Unicode)"""
    fonts_dir = Path("assets/fonts")
    fonts_dir.mkdir(parents=True, exist_ok=True)
    
    font_urls = {
        "NotoSans-Regular.ttf": "https://github.com/notofonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf",
        "NotoSans-Bold.ttf": "https://github.com/notofonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Bold.ttf",
    }
    
    downloaded = False
    
    for font_name, url in font_urls.items():
        font_path = fonts_dir / font_name
        if not font_path.exists():
            print(f"📥 Đang tải font {font_name}...")
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    with open(font_path, "wb") as f:
                        f.write(response.content)
                    print(f"✅ Đã tải {font_name}")
                    downloaded = True
                else:
                    print(f"⚠️ Không thể tải {font_name}")
            except Exception as e:
                print(f"⚠️ Lỗi tải font: {e}")
        else:
            print(f"✅ Font {font_name} đã có")
    
    return downloaded

if __name__ == "__main__":
    download_fonts()