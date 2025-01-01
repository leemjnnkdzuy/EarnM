import subprocess
import re
import torch
import os
import time
import whisper
from dotenv import load_dotenv

voice_map = {
    'en': "assets/voice/en/Kendra_voice.wav",
}

default_url = "https://www.youtube.com/watch?v="

def create_folders(paths):
    try:
        for path in paths:
            os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        print(f"\nKhông thể tạo folder: {e}")
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
        nvidia_check = subprocess.run(['nvidia-smi'], capture_output=True)
        if nvidia_check.returncode != 0:
            return False
            
        result = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'], capture_output=True, text=True)
        return 'h264_nvenc' in result.stdout
    except:
        return False

def setup_gpu():
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.backends.cudnn.benchmark = True
        torch.backends.cudnn.enabled = True
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        return True
    return False

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

def set_grpc_env():
    os.environ["GRPC_VERBOSITY"] = "NONE"
    os.environ["GRPC_LOG_SEVERITY_LEVEL"] = "ERROR"

def load_whisper_model():
    try:
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = whisper.load_model("base", device=device)
        return model
    except Exception as e:
        print(f"Lỗi load model: {e}")
        return None

last_update = 0
def progress_hook(d):
    
    global last_update
    if d['status'] == 'downloading':
        current_time = time.time()
        if current_time - last_update >= 0.5:
            percent = d.get('_percent_str', '0.0%')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            print(f"\rDownloading... {percent} Speed: {speed} ETA: {eta}", end='', flush=True)
            last_update = current_time
    elif d['status'] == 'finished':
        print("\n\nTải video thành công, đang tách audio...")
