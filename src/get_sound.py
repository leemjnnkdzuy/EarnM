from moviepy import *
from .utils import sanitize_filename
import os

def extract_audio(video_path, output_dir_audio):
    try:
        video = VideoFileClip(video_path)
        
        filename = os.path.splitext(os.path.basename(video_path))[0]
        filename = sanitize_filename(filename)
        
        if video.audio is not None:
            audio = video.audio
            audio_path = os.path.join(output_dir_audio, f"{filename}.mp3")
            audio.write_audiofile(
                audio_path, 
                codec='mp3', 
                bitrate='320k',
                ffmpeg_params=['-q:a', '0']
            )
            audio.close()
            
        video.close()
        return True
        
    except Exception as e:
        print(f"ERR: {e}")
        if 'video' in locals():
            video.close()
        return False
