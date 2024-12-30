from moviepy import *
import os
from src.utils import check_gpu_support, get_gpu_encoding_settings
from typing import Optional

def make_final_video(download_path: str, audio_path: str, final_video_path: str, mode: Optional[int] = 2) -> bool:
    try:
        video_file = os.path.join(download_path, os.listdir(download_path)[0])
        
        audio_file = os.path.join(audio_path, 'final_audio.mp3')
        
        video = VideoFileClip(video_file)
        audio = AudioFileClip(audio_file)
        
        video_no_audio = video.without_audio()
        
        final_clip = CompositeVideoClip([video_no_audio])
        final_clip.audio = audio
        
        if mode is not None:
            if mode == 1:
                final_clip = final_clip.resize((1280, 720))
            elif mode == 2:
                final_clip = final_clip.resize((1920, 1080))
            elif mode == 3:
                final_clip = final_clip.resize((2560, 1440))
            elif mode == 4:
                final_clip = final_clip.resize((3840, 2160))
        
        output_path = os.path.join(final_video_path, "final_video.mp4")
        
        if check_gpu_support():
            gpu_params = get_gpu_encoding_settings()
            final_clip.write_videofile(
                output_path,
                codec=gpu_params['codec'],
                audio_codec='aac',
                threads=16,
                ffmpeg_params=gpu_params['params']
            )
        else:
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                threads=16
            )
        
        video.close()
        audio.close()
        final_clip.close()
        
        return True
    except Exception as e:
        print(f"Error creating final video: {str(e)}")
        return False
