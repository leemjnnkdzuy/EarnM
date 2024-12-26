import os
import subprocess
import sys
import platform
import ctypes
import urllib.request

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() if os.name == 'nt' else os.getuid() == 0
    except:
        return False

def get_python311_path():
    if platform.system() == "Windows":
        potential_paths = [
            r"C:\Python311\python.exe",
            r"C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe",
            r"C:\Program Files\Python311\python.exe",
            r"C:\Program Files (x86)\Python311\python.exe"
        ]
        for path in potential_paths:
            expanded_path = os.path.expandvars(path)
            if os.path.exists(expanded_path):
                return expanded_path
    else:
        try:
            result = subprocess.run(['which', 'python3.11'], 
                                 capture_output=True, 
                                 text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
    return None

def download_get_pip():
    try:
        print("Downloading get-pip.py...")
        urllib.request.urlretrieve(
            "https://bootstrap.pypa.io/get-pip.py",
            "get-pip.py"
        )
        return True
    except Exception as e:
        print(f"Error downloading get-pip.py: {e}")
        return False

def setup_virtual_env():
    try:
        if not is_admin():
            print("Warning: Chạy không có quyền admin, một số thao tác có thể thất bại")

        python311_path = get_python311_path()
        if not python311_path:
            print("Không tìm thấy Python 3.11. Hãy cài đặt Python 3.11 trước!")
            return False

        subprocess.run([python311_path, "-m", "venv", "venv"], check=True)
        print("Đã tạo môi trường ảo với Python 3.11")

        if os.name == 'nt': 
            python_path = os.path.join("venv", "Scripts", "python")
            pip_path = os.path.join("venv", "Scripts", "pip")
        else: 
            python_path = os.path.join("venv", "bin", "python")
            pip_path = os.path.join("venv", "bin", "pip")

        result = subprocess.run([python_path, "--version"], 
                              capture_output=True, 
                              text=True)
        print(f"Phiên bản Python trong môi trường ảo: {result.stdout.strip()}")

        if not os.path.exists(pip_path):
            print("Pip không tồn tại, đang cài đặt...")
            if download_get_pip():
                try:
                    subprocess.run([python_path, "get-pip.py"], check=True)
                    print("Đã cài đặt pip")
                except subprocess.CalledProcessError as e:
                    print(f"Lỗi khi cài đặt pip: {e}")
                finally:
                    if os.path.exists("get-pip.py"):
                        os.remove("get-pip.py")
            else:
                print("Không thể tải get-pip.py")
                return False

        print("\nĐang cài đặt các thư viện...")
        packages = [
            "numpy",
            "scipy",
            "decorator",  
            "imageio",   
            "imageio-ffmpeg",  
            "Pillow",    
            "moviepy",    
            "python-dotenv",
            "pytube",
            "pydub",
            "ffmpeg-python",
            "openai-whisper",
            "TTS",
            "yt_dlp",
        ]
        
        for package in packages:
            print(f"\nĐang cài đặt {package}...")
            try:
                if package in ["Pillow", "moviepy", "imageio", "imageio-ffmpeg"]:
                    subprocess.run([python_path, "-m", "pip", "install", "--force-reinstall", package], check=True)
                else:
                    subprocess.run([python_path, "-m", "pip", "install", package], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Lỗi khi cài đặt {package}: {e}")
                return False

        print("Đã cài đặt thành công các thư viện")

        print("\nĐã thiết lập môi trường thành công!")
        print("\nĐể kích hoạt môi trường ảo:")
        if os.name == 'nt':
            print("    venv\\Scripts\\activate")
        else:
            print("    source venv/bin/activate")

        return True

    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi thiết lập môi trường: {e}")
    except Exception as e:
        print(f"Lỗi không xác định: {e}")
    return False

if __name__ == "__main__":
    setup_virtual_env()
