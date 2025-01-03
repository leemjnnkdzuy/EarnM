import os
import asyncio
import warnings
import signal
from dotenv import load_dotenv

from src.utils import set_grpc_env, create_folders, voice_map, default_url
from src.download_video_form_youtube import download_youtube_video
from src.get_sound import extract_audio
from src.get_original_sub import create_sub_from_mp3 
from src.translate_sub import translate_subtitle_file
from src.generate_audio import generate_audio
from src.get_translate_sub import create_sub_from_generated_audio
from src.make_final_video import make_final_video
from src.create_chunk import create_chunks_from_subtitles, save_chunks
from src.make_final_audio import make_final_audio

warnings.filterwarnings("ignore", category=FutureWarning)
load_dotenv()

video_ID = os.getenv('VIDEO_ID')
if not video_ID:
    print("VIDEO_ID không được tìm thấy!")
    exit()
else:
    print(f"VIDEO_ID: {video_ID}")

TargetLang = "en"

async def cleanup():
    await asyncio.sleep(0.5)

async def async_main():
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(handle_signal(s)))
    
    try:
        download_path = os.path.join(".", video_ID, "Downloads")
        audio_path = os.path.join(".", video_ID, "OriginalSound")
        subs_path = os.path.join(".", video_ID, "OriginalSubs")
        translated_subs_path = os.path.join(".", video_ID, "TranslateSubs")
        generated_audio_path = os.path.join(".", video_ID, "GeneratedAudio")
        final_video_path = os.path.join(".", video_ID, "FinalVideo")
        final_audio_path = os.path.join(".", video_ID, "FinalAudio")
        
        # 1: 720p, 2: 1080p, 3: 1440p, 4: 2160p, None: original
        render_mode = 3
        
        if not create_folders([
            download_path,
            audio_path, 
            subs_path,
            translated_subs_path, 
            generated_audio_path, 
            final_video_path,
            final_audio_path
        ]):
            print("\nKhông thể tạo folder!")
            return
            
        success = download_youtube_video(default_url + video_ID, download_path)
        if not success:
            print("\nTải video không thành công!")
            return
            
        video_file = os.path.join(download_path, os.listdir(download_path)[0])
        
        if extract_audio(video_file, audio_path):
            print("\nTách audio thành công!")
        else:
            print("\nTách audio thất bại!")
            return

        if not os.listdir(audio_path):
            print("\nKhông có audio được tạo!")
            return

        audio_file = os.path.join(audio_path, os.listdir(audio_path)[0])
        sub_file = os.path.join(subs_path, "subtitle.json")

        print("\nBắt đầu tạo sub...")
        if create_sub_from_mp3(audio_file, sub_file):
            print("\nSub tạo thành công!")
            
            chunks = create_chunks_from_subtitles(sub_file)
            chunks_file = os.path.join(subs_path, "subtitle_chunks.json")
            if save_chunks(chunks, chunks_file):
                print(f"\nĐã tạo {len(chunks)} chunks và lưu vào {chunks_file}")
            else:
                print("\nKhông thể tạo chunks!")
                return
        else:
            print("\nTạo sub thất bại!")
            return

        if os.path.exists(sub_file):
            translated_file = os.path.join(translated_subs_path, f"translate_{TargetLang}_subtitle.json")
            
            print(f"\nBắt đầu dịch sang {TargetLang}...")
            if translate_subtitle_file(sub_file, translated_file, TargetLang):
                print(f"\nHoàn thành dịch sang {TargetLang}")
                
                voice_sample = voice_map.get(TargetLang)
                if not voice_sample:
                    print(f"\nLỗi: Không tìm thấy mẫu giọng nói cho ngôn ngữ {TargetLang}")
                    return
                    
                print(f"\nSử dụng mẫu giọng nói: {voice_sample}")
                if not os.path.exists(voice_sample):
                    print(f"\nLỗi: Không tìm thấy file mẫu giọng nói: {voice_sample}")
                    return
                    
                if generate_audio(translated_file, generated_audio_path, voice_sample, TargetLang):
                    print("\nTạo audio thành công!")
                else:
                    print("\nTạo audio thất bại! Vui lòng kiểm tra logs để biết thêm chi tiết.")
                    return

                if make_final_audio(subs_path, generated_audio_path, final_audio_path):
                    print("\nGhép các đoạn audio thành công!")
                    
                    if create_sub_from_generated_audio(final_audio_path, translated_file):
                        print("\nCập nhật sub từ audio thành công!")
                        
                        if make_final_video(download_path, final_audio_path, final_video_path, mode=render_mode):
                            print("\nTạo video cuối cùng thành công!")
                        else:
                            print("\nTạo video cuối cùng thất bại!")
                    else:
                        print("\nCập nhật sub từ audio thất bại!")
                else:
                    print("\nGhép các đoạn audio thất bại!")
            else:
                print("Quá trình dịch không thành công")
    except asyncio.CancelledError:
        print("\nShutting down gracefully...")
        await cleanup()
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        await cleanup()

async def handle_signal(signal):
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)
    await cleanup()
    asyncio.get_event_loop().stop()

if __name__ == "__main__":
    set_grpc_env()
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\n")
    except Exception as e:
        print(f"\nError: {str(e)}")