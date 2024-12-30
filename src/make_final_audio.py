import os
from pydub import AudioSegment
import json

def make_final_audio(subs_path: str, generated_audio_path: str, final_audio_path: str) -> bool:
    try:
        audio_files = [f for f in os.listdir(generated_audio_path)
                      if f.startswith("audio_") and f.endswith(".wav")]
        if not audio_files:
            print("Không tìm thấy file audio nào trong thư mục")
            return False
            
        print(f"Đã tìm thấy {len(audio_files)} file audio để ghép")
        audio_files.sort()
        combined = AudioSegment.empty()
        
        for f in audio_files:
            file_path = os.path.join(generated_audio_path, f)
            if os.path.getsize(file_path) == 0:
                print(f"Cảnh báo: Bỏ qua file audio rỗng {f}")
                continue
            segment = AudioSegment.from_wav(file_path)
            combined += segment

        if len(combined) == 0:
            print("Lỗi: Không có nội dung audio hợp lệ để ghép")
            return False

        try:
            with open(os.path.join(subs_path, 'subtitle.json'), 'r', encoding='utf-8') as f:
                chunks = json.load(f)
            desired_start = min(chunk['start'] for chunk in chunks)
            desired_end = max(chunk['end'] for chunk in chunks)
            desired_duration = int((desired_end - desired_start) * 1000)
            current_duration = len(combined)
            if current_duration > 0:
                speed_factor = desired_duration / current_duration
                combined = combined._spawn(
                    combined.raw_data,
                    overrides={"frame_rate": int(combined.frame_rate * speed_factor)}
                ).set_frame_rate(combined.frame_rate)
        except:
            pass

        output_path = os.path.join(final_audio_path, "final_audio.mp3")
        combined.export(output_path, format="mp3")
        return True
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        return False