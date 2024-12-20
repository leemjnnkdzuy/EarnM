from moviepy import VideoFileClip
import os

def extract_audio_and_silent_video(video_path, output_dir_audio, output_dir_video):
    try:
        video = VideoFileClip(video_path)
        
        filename = os.path.splitext(os.path.basename(video_path))[0]
        
        audio = video.audio
        audio_path = os.path.join(output_dir_audio, f"{filename}.mp3")
        audio.write_audiofile(audio_path)
        
        silent_video = video.without_audio()
        video_path = os.path.join(output_dir_video, f"{filename}_nosound.mp4")
        silent_video.write_videofile(video_path)
        
        video.close()
        audio.close()
        silent_video.close()
        
        return True
    except Exception as e:
        print(f"Error processing video: {e}")
        return False
