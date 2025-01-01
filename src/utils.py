import subprocess
import re
import torch
import os
import whisper
from dotenv import load_dotenv

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
        # Check NVIDIA GPU
        nvidia_check = subprocess.run(['nvidia-smi'], capture_output=True)
        if nvidia_check.returncode != 0:
            return False
            
        # Check NVENC support
        result = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'], capture_output=True, text=True)
        return 'h264_nvenc' in result.stdout
    except:
        return False

def setup_gpu():
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.backends.cudnn.benchmark = True
        torch.backends.cudnn.enabled = True
        torch.backends.cuda.matmul.allow_tf32 = True  # Enable TF32
        torch.backends.cudnn.allow_tf32 = True        # Enable TF32
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
