import os
from src.download_video_form_youtube import download_youtube_video
from src.get_sound import extract_audio_and_silent_video
from src.folder_utils import create_folders
from src.get_sub import create_sub_from_mp3

video_url = "https://www.youtube.com/watch?v=5PvzGDU8WjM"
NameFolder = "test1"

def main():
    download_path = os.path.join(".", NameFolder, "Downloads")
    video_path = os.path.join(".", NameFolder, "VideoNoSound")
    audio_path = os.path.join(".", NameFolder, "OriginalSound")
    subs_path = os.path.join(".", NameFolder, "Subs")
    
    if not create_folders([download_path, video_path, audio_path, subs_path]):
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
        return

    if not os.listdir(audio_path):
        print("Khong co audio duoc tao!")
        return

    audio_file = os.path.join(audio_path, os.listdir(audio_path)[0])
    sub_file = os.path.join(subs_path, "subtitle.txt")
    if create_sub_from_mp3(audio_file, sub_file):
        print("Da tao sub thanh cong!!")
    else:
        print("Tao sub that bai!!")

if __name__ == "__main__":
    main()
