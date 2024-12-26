import os
import json
import whisper
from glob import glob
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import torch
import logging
import warnings

def load_whisper_model():
    try:
        logging.getLogger("whisper").setLevel(logging.ERROR)
        warnings.filterwarnings("ignore")
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        model = whisper.load_model(
            "base",
            device=device,
            download_root=os.path.join(os.path.expanduser("~"), ".cache", "whisper")
        )
        return model
    except Exception as e:
        print(f"Error: {e}")
        return None

def transcribe_with_whisper(audio_file, model):
    try:
        if model is None:
            return ""
            
        with torch.no_grad():
            result = model.transcribe(
                audio_file,
                task="transcribe",
                fp16=False,
                temperature=0.0,
                best_of=1,
                word_timestamps=True,
                condition_on_previous_text=True,
                no_speech_threshold=0.6,
                compression_ratio_threshold=2.4
            )
        return result

    except Exception as e:
        print(f"Error: {e}")
        return None

def get_audio_duration(audio_file):
    audio = AudioSegment.from_wav(audio_file)
    return len(audio) / 1000.0

def detect_sentences(audio_file):
    audio = AudioSegment.from_wav(audio_file)
    
    min_silence_len = 150
    silence_thresh = audio.dBFS - 10
    keep_silence = 80
    
    nonsilent_ranges = detect_nonsilent(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        seek_step=3,
        keep_silence=keep_silence
    )
    
    return nonsilent_ranges

def create_sub_from_generated_audio(audio_dir, output_file):
    try:
        whisper_model = load_whisper_model()
        sub_data = []
        current_id = 1
        
        audio_files = sorted(glob(os.path.join(audio_dir, "audio_*.wav")))
        
        accumulated_time = 0
        for i, audio_file in enumerate(audio_files):
            print(f"\nXử lý audio file {i+1}/{len(audio_files)}: {audio_file}")
            
            result = transcribe_with_whisper(audio_file, whisper_model)
            base_duration = get_audio_duration(audio_file)
            
            if result and 'segments' in result:
                for segment in result['segments']:
                    if 'text' not in segment or not segment['text'].strip():
                        continue
                        
                    text = segment['text'].strip()
                    if len(text) > 0:
                        start_time = accumulated_time + segment['start']
                        end_time = accumulated_time + segment['end']
                        
                        if end_time - start_time < 0.3:
                            end_time = start_time + 0.3
                            
                        sub_data.append({
                            'id': current_id,
                            'start': round(start_time, 3),
                            'end': round(end_time, 3),
                            'text': text
                        })
                        current_id += 1
            
            accumulated_time += base_duration

        final_data = []
        i = 0
        while i < len(sub_data):
            current = sub_data[i]
            duration = current['end'] - current['start']
            
            if duration < 0.5 and i < len(sub_data) - 1:
                next_sub = sub_data[i + 1]
                merged_text = f"{current['text']} {next_sub['text']}"
                final_data.append({
                    'id': len(final_data) + 1,
                    'start': round(current['start'], 3),
                    'end': round(next_sub['end'], 3),
                    'text': merged_text
                })
                i += 2
            else:
                final_data.append({
                    'id': len(final_data) + 1,
                    'start': round(current['start'], 3),
                    'end': round(current['end'], 3),
                    'text': current['text']
                })
                i += 1

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
            
        return True
        
    except Exception as e:
        print(f"\nError: {e}")
        return False


