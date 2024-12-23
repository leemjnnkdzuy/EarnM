import os
import asyncio
from src.download_video_form_youtube import download_youtube_video
from src.get_sound import extract_audio
from src.utils import create_folders
from src.get_original_sub import create_sub_from_mp3 
from src.translate_sub import translate_subtitle_file
from src.generate_audio import generate_audio

voice_map = {
    'en': 'David',
    'vi': 'David',
    'ja': 'David'
}

video_url = "https://www.youtube.com/watch?v=OuaW_IefFPg"
NameFolder = "test1"
TargetLang = "en"


async def async_main():
    download_path = os.path.join(".", NameFolder, "Downloads")
    audio_path = os.path.join(".", NameFolder, "OriginalSound")
    subs_path = os.path.join(".", NameFolder, "OriginalSubs")
    translated_subs_path = os.path.join(".", NameFolder, "TranslateSubs")
    generated_audio_path = os.path.join(".", NameFolder, "GeneratedAudio")
    final_video_path = os.path.join(".", NameFolder, "FinalVideo")
    
    if not create_folders([
        download_path,
        audio_path, 
        subs_path,
        translated_subs_path, 
        generated_audio_path, 
        final_video_path
    ]):
        print("Không thể tạo folder!")
        return
        
    success = download_youtube_video(video_url, download_path)
    if not success:
        print("Tải video không thành công!")
        return
        
    video_file = os.path.join(download_path, os.listdir(download_path)[0])
    
    if extract_audio(video_file, audio_path):
        print("Tách audio thành công!")
    else:
        print("Tách audio thất bại!!")
        return

    if not os.listdir(audio_path):
        print("Khong có audio được tạo!")
        return

    audio_file = os.path.join(audio_path, os.listdir(audio_path)[0])
    sub_file = os.path.join(subs_path, "subtitle.json")
    if create_sub_from_mp3(audio_file, sub_file):
        print("Sub tạo thành công!")
    else:
        print("Tạo sub thất bại!")
        return

    if os.path.exists(sub_file):
        translated_file = os.path.join(translated_subs_path, f"translate_{TargetLang}_subtitle.json")
        
        # Translation process
        print(f"\nBắt đầu dịch sang {TargetLang}...")
        if translate_subtitle_file(sub_file, translated_file, TargetLang):
            print(f"✓ Hoàn thành dịch sang {TargetLang}")
            
            # Audio generation
            voice_name = voice_map.get(TargetLang)
            if generate_audio(translated_file, generated_audio_path, voice_name):
                print("✓ Tạo audio thành công!")
            else:
                print("✗ Tạo audio thất bại!")
        else:
            print("✗ Quá trình dịch không thành công")

if __name__ == "__main__":
    asyncio.run(async_main())
