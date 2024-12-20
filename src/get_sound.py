from moviepy.editor import VideoFileClip
import os

from .utils import sanitize_filename, check_gpu_support

def extract_audio_and_silent_video(video_path, output_dir_audio, output_dir_video):
    try:
        video = VideoFileClip(video_path)
        
        filename = os.path.splitext(os.path.basename(video_path))[0]
        filename = sanitize_filename(filename)
        
        if video.audio is not None:
            audio = video.audio
            audio_path = os.path.join(output_dir_audio, f"{filename}.mp3")
            audio.write_audiofile(audio_path, codec='mp3', bitrate='320k')
            audio.close()
        else:
            print("Video doesn't have audio track")
        
        video_path = os.path.join(output_dir_video, f"{filename}_nosound.mp4")
        
        has_gpu = check_gpu_support()
        if has_gpu:
            print("Dang dung GPU de processing video")
            try:
                fps = video.fps
                size = video.size
                duration = video.duration
                
                video.write_videofile(
                    video_path,
                    fps=fps,
                    codec='h264_nvenc',
                    ffmpeg_params=[
                        '-preset', 'hq',
                        '-rc', 'vbr',
                        '-cq', '1',
                        '-profile:v', 'high',
                        '-pixel_format', 'yuv420p',
                        '-b:v', '0',
                        '-maxrate', '130M',
                        '-bufsize', '130M'
                    ],
                    write_logfile=False,
                    threads=16,
                    preset='slow',
                    audio=False
                )
            except Exception as ve:
                print(f"Khong the dung GPU de processing video: {ve}")
                return False
        else:
            print("GPU khong ho tro!")
            return False
        
        video.close()
        
        return True
    except Exception as e:
        print(f"ERR: {e}")
        if 'video' in locals():
            video.close()
        return False
