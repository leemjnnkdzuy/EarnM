import speech_recognition as sr
import subprocess
import os
import json
from pydub import AudioSegment
from pydub.silence import split_on_silence

def create_sub_from_mp3(mp3_file, output_file):
    temp_wav = mp3_file + ".wav"
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", mp3_file, "-ar", "16000", "-ac", "1", temp_wav], 
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        r = sr.Recognizer()
        sub_data = []
        audio_segment = AudioSegment.from_wav(temp_wav)
        chunks = split_on_silence(
            audio_segment,
            min_silence_len=500,
            silence_thresh=audio_segment.dBFS - 14,
            keep_silence=250
        )
        current_offset = 0.0
        for chunk in chunks:
            duration_ms = len(chunk)
            chunk_wav_path = temp_wav + "_chunk.wav"
            chunk.export(chunk_wav_path, format="wav")
            with sr.AudioFile(chunk_wav_path) as source:
                audio = r.record(source)
            text = ""
            try:
                text = r.recognize_google(audio, language="vi-VN")
            except:
                pass
            sub_data.append({
                "start": current_offset / 1000.0,
                "end": (current_offset + duration_ms) / 1000.0,
                "text": text
            })
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
