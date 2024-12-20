import os
from src.download_video_form_youtube import download_youtube_video
from src.get_sound import extract_audio_and_silent_video

video_url = "https://www.youtube.com/watch?v=stvWuowo1dU"
NameFolder = "123"

def create_folders(paths):
    try:
        for path in paths:
            os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating folders: {e}")
        return False

def main():
    download_path = os.path.join(".", NameFolder, "downloads")
    video_path = os.path.join(".", NameFolder, "VideoNoSound")
    audio_path = os.path.join(".", NameFolder, "OriginalSound")
    
    if not create_folders([download_path, video_path, audio_path]):
        print("Khong the tao folders!")
        return
        
    success = download_youtube_video(video_url, download_path)
    if not success:
        print("Video tai that bai!!")
        return
        
    video_file = os.path.join(download_path, os.listdir(download_path)[0])
    
    if extract_audio_and_silent_video(video_file, audio_path, video_path):
        print("Tach video thanh cong!!")
    else:
        print("Tach video that bai!!")

if __name__ == "__main__":
    main()
