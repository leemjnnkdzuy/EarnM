import subprocess
import re
import os
from dotenv import load_dotenv

def create_folders(paths):
    try:
        for path in paths:
            os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Không thể tạo folder: {e}")
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
        print("\nKhông tìm thấy ffmpeg")
        return False

def check_gpu_support():
    try:
        result = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'], capture_output=True, text=True)
        if 'h264_nvenc' not in result.stdout:
            return False
            
        nvidia_check = subprocess.run(['nvidia-smi'], capture_output=True)
        return nvidia_check.returncode == 0
    except:
        return False

def get_gpu_encoding_settings():
    return {
        'codec': 'h264_nvenc',
        'preset': 'p6',
        'params': [
            '-preset', 'hq',
            '-rc:v', 'vbr',
            '-cq', '16',
            '-qmin', '16',
            '-qmax', '21',
            '-profile:v', 'high',
            '-pixel_format', 'yuv420p',
            '-b:v', '0',
            '-maxrate', '400M',
            '-bufsize', '400M'
        ]
    }

def sanitize_filename(filename):
    clean_name = re.sub(r'[<>:"/\\|?*]', '', filename)
    clean_name = clean_name.replace(' ', '_')
    return clean_name

def get_google_api_key():
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_API_KEY không được tìm thấy!\n")
    print("GOOGLE_API_KEY load thành công!\n")
    return api_key
