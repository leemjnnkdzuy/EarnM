import yt_dlp
import os
import subprocess

def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        print("Warning: ffmpeg is not installed. Using fallback format...")
        return False

def download_youtube_video(url: str, output_path: str = "./") -> bool:
    try:
        has_ffmpeg = check_ffmpeg()
        
        if not has_ffmpeg:
            format_spec = 'best'
        else:
            format_spec = 'bestvideo*+bestaudio/best'  # Get absolute best quality

        os.makedirs(output_path, exist_ok=True)
        
        ydl_opts = {
            'format': format_spec,
            'outtmpl': f'{output_path}/video.%(ext)s',
            'progress_hooks': [progress_hook],
            'quiet': False,
            'merge_output_format': 'mp4',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            'format_sort': ['res:2160', 'res:1440', 'res:1080'],  # Prioritize high resolutions
            'ignoreerrors': True,
            'fragment_retries': 5
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        return True
        
    except Exception as e:
        print(f"ERR: {str(e)}")
        return False

def progress_hook(d):
    if d['status'] == 'finished':
        print('Tai thanh cong, bat dau noi doan khuc ...')

