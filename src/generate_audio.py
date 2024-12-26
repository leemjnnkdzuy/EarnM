from TTS.api import TTS
import json
import os
from pydub import AudioSegment

def generate_audio_from_text(tts, text: str, output_path: str, speaker_wav: str, language: str = "en") -> bool:
    try:
        tts.tts_to_file(
            text=text,
            file_path=output_path,
            speaker_wav=[speaker_wav],
            language=language,
            split_sentences=True
        )
        return os.path.exists(output_path)
    except Exception as e:
        print(f"Error: {e}")
        return False

def adjust_audio_duration(audio_file: str, start_time: float, end_time: float) -> bool:
    try:
        audio = AudioSegment.from_wav(audio_file)
        
        start_ms = int(start_time * 1000)
        end_ms = int(end_time * 1000)
        
        audio_segment = audio[start_ms:end_ms]
        
        audio_segment.export(audio_file, format="wav")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def generate_audio(translated_file: str, output_dir: str, speaker_wav: str, language: str = "en") -> bool:
    try:
        try:
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)
        except:
            print("CUDA not available, falling back to CPU.")
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
        os.makedirs(output_dir, exist_ok=True)
        
        with open(translated_file, 'r', encoding='utf-8') as f:
            subtitles = json.load(f)

        for i, sub in enumerate(subtitles):
            output_file = os.path.join(output_dir, f"audio_{i:03d}.wav")
            
            print(f"\nGenerating audio {i+1}/{len(subtitles)}")
            if not generate_audio_from_text(tts, sub['text'], output_file, speaker_wav, language):
                return False
                
            if 'start' in sub and 'end' in sub:
                if not adjust_audio_duration(output_file, sub['start'], sub['end']):
                    return False

        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False