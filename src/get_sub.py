import speech_recognition as sr
import subprocess
import os

def create_sub_from_mp3(mp3_file, output_file):
    temp_wav = mp3_file + ".wav"
    try:
        subprocess.run(["ffmpeg", "-y", "-i", mp3_file, "-ar", "16000", "-ac", "1", temp_wav], check=True)
        r = sr.Recognizer()
        with sr.AudioFile(temp_wav) as source:
            audio = r.record(source)
        text = r.recognize_google(audio, language="vi-VN")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)
        return True
    except Exception as e:
        print(f"Loi khi tao sub: {e}")
        return False
    finally:
        if os.path.exists(temp_wav):
            os.remove(temp_wav)
