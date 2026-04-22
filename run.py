# run.py
#!/usr/bin/env python3
"""
Galactic Guardian - Game Launcher
Run this file to start the game
"""

import sys
import subprocess
import os

def check_dependencies():
    """Kiểm tra và cài đặt dependencies nếu cần"""
    required = ['pygame', 'opencv-python', 'mediapipe', 'numpy']
    missing = []
    
    for package in required:
        try:
            if package == 'opencv-python':
                __import__('cv2')
            else:
                __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"⚠️ Thiếu các gói: {', '.join(missing)}")
        answer = input("Có muốn cài đặt tự động không? (y/n): ")
        if answer.lower() == 'y':
            for package in missing:
                print(f"📦 Đang cài {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print("✅ Đã cài xong!")
            return True
        else:
            print("❌ Vui lòng cài thủ công: pip install -r requirements.txt")
            return False
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🌌 GALACTIC GUARDIAN - Hành Trình Không Gian")
    print("=" * 60)
    
    if check_dependencies():
        # Chạy game
        try:
            import main
        except Exception as e:
            print(f"❌ Lỗi khi chạy game: {e}")
            input("Press Enter to exit...")
    else:
        input("Press Enter to exit...")