import speech_recognition as sr
import subprocess
import os
import json
from pydub import AudioSegment
from pydub.silence import split_on_silence
import whisper

def load_whisper_model():
    return whisper.load_model("base")

def transcribe_with_whisper(audio_file, model):
    try:
        result = model.transcribe(
            audio_file,
            language="vi",
            task="transcribe",
            fp16=False
        )
        return result["text"]
    except Exception as e:
        print(f"Lỗi whisper: {e}")
        return ""

def create_sub_from_mp3(mp3_file, output_file):
    temp_wav = mp3_file + ".wav"
    try:
        whisper_model = load_whisper_model()
        
        subprocess.run(
            ["ffmpeg", "-y", "-i", mp3_file, "-ar", "16000", "-ac", "1", temp_wav], 
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        audio_segment = AudioSegment.from_wav(temp_wav)
        chunks = split_on_silence(
            audio_segment,
            min_silence_len=1000,
            silence_thresh=audio_segment.dBFS - 20,
            keep_silence=800,
            seek_step=25
        )
        
        sub_data = []
        current_offset = 0.0
        
        for i, chunk in enumerate(chunks, 1):
            duration_ms = len(chunk)
            if duration_ms < 1000:
                current_offset += duration_ms
                continue
                
            chunk_wav_path = temp_wav + "_chunk.wav"
            chunk.export(chunk_wav_path, format="wav")
            
            try:
                text = transcribe_with_whisper(chunk_wav_path, whisper_model)
                if text:
                    sub_data.append({
                        "id": i,
                        "start": current_offset / 1000.0,
                        "end": (current_offset + duration_ms) / 1000.0,
                        "text": text.strip()
                    })
                current_offset += duration_ms
                
            except Exception as e:
                print(f"Lỗi nhận dạng đoạn: {e}")
                current_offset += duration_ms
            
            os.remove(chunk_wav_path)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(sub_data, f, ensure_ascii=False, indent=2)
            
        return True
        
    except Exception as e:
        print(f"Loi khi tao sub: {e}")
        return False
    finally:
        if os.path.exists(temp_wav):
            os.remove(temp_wav)