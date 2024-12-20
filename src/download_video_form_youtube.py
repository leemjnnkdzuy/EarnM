import yt_dlp
import os
import shutil

def download_youtube_video(url: str, output_path: str = "./") -> bool:
    try:
        if not shutil.which('ffmpeg'):
            format_spec = 'best[ext=mp4]/best'
        else:
            format_spec = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

        os.makedirs(output_path, exist_ok=True)
        
        ydl_opts = {
            'format': format_spec,
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'progress_hooks': [progress_hook],
            'quiet': False,
            'merge_output_format': 'mp4'
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
    if d['status'] == 'downloading':
        print(f"Tai xuong: {d['_percent_str']} at {d['_speed_str']} ETA: {d['_eta_str']}")

