import subprocess
import os
from typing import Optional

def get_video_info(video_path: str) -> dict:
    cmd = [
        'ffprobe', '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,r_frame_rate',
        '-of', 'json',
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        import json
        info = json.loads(result.stdout)
        return info['streams'][0]
    return {}

def make_final_video(download_path: str, audio_path: str, final_video_path: str, mode: Optional[int] = 2) -> bool:
    try:
        video_file = os.path.join(download_path, 'video.mp4')
        audio_file = os.path.join(audio_path, 'final_audio.mp3')
        output_path = os.path.join(final_video_path, "final_video.mp4")
        temp_video = os.path.join(final_video_path, "temp_video.mp4")

        # Get target resolution
        resolutions = {
            1: (1280, 720),
            2: (1920, 1080),
            3: (2560, 1440),
            4: (3840, 2160)
        }
        width, height = resolutions.get(mode, (1920, 1080))

        # Step 1: Scale video with GPU acceleration
        print("\nĐang scale video...")
        scale_cmd = [
            'ffmpeg', '-y',
            '-hwaccel', 'cuda',
            '-hwaccel_output_format', 'cuda',
            '-i', video_file,
            '-c:v', 'h264_nvenc',
            '-preset', 'p1',
            '-tune', 'hq',
            '-rc:v', 'vbr',
            '-cq', '18',
            '-qmin', '16',
            '-qmax', '21',
            '-b:v', '50000k',
            '-maxrate', '100M',
            '-bufsize', '50M',
            '-vf', f'scale={width}:{height}',
            '-an',
            temp_video
        ]
        
        result = subprocess.run(scale_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Lỗi khi scale video: {result.stderr}")
            return False

        # Step 2: Merge scaled video with audio
        print("Đang merge audio...")
        merge_cmd = [
            'ffmpeg', '-y',
            '-i', temp_video,
            '-i', audio_file,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-b:a', '192k',
            output_path
        ]
        
        result = subprocess.run(merge_cmd, capture_output=True, text=True)
        
        # Cleanup temp file
        if os.path.exists(temp_video):
            os.remove(temp_video)

        if result.returncode != 0:
            print(f"Lỗi khi merge audio: {result.stderr}")
            return False

        print("Render video thành công!")
        return True

    except Exception as e:
        print(f"Lỗi: {str(e)}")
        return False
