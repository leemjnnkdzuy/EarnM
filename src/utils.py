import subprocess
import re
import os

def create_folders(paths):
    try:
        for path in paths:
            os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Khong the tao folder: {e}")
        return False

def check_ffmpeg():
    try:
        subprocess.run(
            ['ffmpeg', '-version'], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        return True
    except FileNotFoundError:
        print("Khong tim thay ffmpeg")
        return False

def check_gpu_support():
    try:
        result = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'], capture_output=True, text=True)
        return 'hevc_nvenc' in result.stdout
    except:
        return False

def sanitize_filename(filename):
    clean_name = re.sub(r'[<>:"/\\|?*]', '', filename)
    clean_name = clean_name.replace(' ', '_')
    return clean_name
