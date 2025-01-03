import os
from pydub import AudioSegment
import json
import re
from concurrent.futures import ThreadPoolExecutor

def make_final_audio(subs_path: str, generated_audio_path: str, final_audio_path: str) -> bool:
    try:
        def get_audio_id(filename):
            match = re.search(r'audio_(\d+)\.wav', filename)
            return int(match.group(1)) if match else 0
            
        audio_files = [f for f in os.listdir(generated_audio_path)
                      if f.startswith("audio_") and f.endswith(".wav")]
        
        if not audio_files:
            print("Không tìm thấy file audio nào trong thư mục")
            return False
            
        audio_files.sort(key=get_audio_id)
        print(f"Đã tìm thấy {len(audio_files)} file audio để ghép")
        
        with ThreadPoolExecutor() as executor:
            segments = list(executor.map(lambda fp: AudioSegment.from_wav(fp),
                           [os.path.join(generated_audio_path, f) for f in audio_files if os.path.getsize(os.path.join(generated_audio_path, f)) != 0]))
        combined = AudioSegment.empty()
        for segment in segments:
            combined += segment

        if len(combined) == 0:
            print("Lỗi: Không có nội dung audio hợp lệ để ghép")
            return False

        actual_duration = len(combined)
        print(f"Thời lượng audio sau khi ghép: {actual_duration/1000:.2f} giây")
            
        subtitle_file = os.path.join(subs_path, 'subtitle.json')
        if not os.path.exists(subtitle_file):
            print("Không tìm thấy file subtitle.json")
            return False
            
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
            
        desired_start = min(chunk['start'] for chunk in chunks)
        desired_end = max(chunk['end'] for chunk in chunks)
        desired_duration = int((desired_end - desired_start) * 1000)
        
        print(f"Thời lượng subtitle cần đạt: {desired_duration/1000:.2f} giây")
        
        speed_factor = actual_duration / desired_duration
        print(f"Hệ số điều chỉnh tốc độ: {speed_factor:.2f}")
        
        try:
            if speed_factor > 1:
                combined = combined.speedup(playback_speed=speed_factor)
            else:
                combined = combined.speedup(playback_speed=speed_factor)
                
            final_duration = len(combined)
            print(f"Thời lượng sau điều chỉnh: {final_duration/1000:.2f} giây")
            
            if final_duration != desired_duration:
                if final_duration > desired_duration:
                    combined = combined[:desired_duration]
                else:
                    combined += AudioSegment.silent(duration=desired_duration - final_duration)
        except Exception as e:
            print(f"Lỗi khi điều chỉnh tốc độ: {str(e)}")
            return False

        output_path = os.path.join(final_audio_path, "final_audio.wav")
        combined.export(output_path, format="wav")
        print(f"Đã xuất file audio cuối cùng: {output_path}")
        return True
        
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        return False