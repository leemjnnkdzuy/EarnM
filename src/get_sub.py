import speech_recognition as sr
import subprocess
import os
import json
from pydub import AudioSegment
from pydub.silence import split_on_silence
import re
import whisper

def split_sentences(text, max_length=100):
    sentences = re.split(r'([.!?]+)', text)
    result = []
    current = ""
    
    for i in range(0, len(sentences)-1, 2):
        if sentences[i].strip():
            sentence = sentences[i].strip() + (sentences[i+1] if i+1 < len(sentences) else "")
            if len(current) + len(sentence) > max_length:
                if current:
                    result.append(current)
                current = sentence
            else:
                current = (current + " " + sentence).strip()
    
    if current:
        result.append(current)
    return result if result else [text]

def process_chunks(chunks, min_chunk_length=1500):
    processed_chunks = []
    current_chunk = None
    
    for chunk in chunks:
        if current_chunk is None:
            current_chunk = chunk
        elif len(current_chunk) < min_chunk_length:
            current_chunk = current_chunk + chunk
        else:
            processed_chunks.append(current_chunk)
            current_chunk = chunk
    
    if current_chunk is not None:
        processed_chunks.append(current_chunk)
    
    return processed_chunks

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
        
        sub_data = []
        audio_segment = AudioSegment.from_wav(temp_wav)
        chunks = split_on_silence(
            audio_segment,
            min_silence_len=1000,  # Tăng thời gian im lặng tối thiểu
            silence_thresh=audio_segment.dBFS - 20,  # Tăng độ nhạy
            keep_silence=800,  # Giữ nhiều silence hơn
            seek_step=25  # Tăng độ chính xác
        )
        
        chunks = process_chunks(chunks, min_chunk_length=2000)  # Tăng độ dài chunk tối thiểu
        
        current_offset = 0.0
        sub_id = 1
        sub_data = []

        for chunk in chunks:
            duration_ms = len(chunk)
            if duration_ms < 1000:  # Tăng ngưỡng lọc
                current_offset += duration_ms
                continue
                
            chunk_wav_path = temp_wav + "_chunk.wav"
            chunk.export(chunk_wav_path, format="wav")
            
            try:
                # Sử dụng Whisper thay vì Google Speech
                text = transcribe_with_whisper(chunk_wav_path, whisper_model)
                if text:
                    sentences = split_sentences(text, max_length=150)
                    
                    avg_time = duration_ms / len(sentences)
                    min_time_per_sentence = 1500
                    
                    for i, sentence in enumerate(sentences):
                        if len(sentence.strip()) > 0:
                            sentence_time = max(
                                min_time_per_sentence, 
                                avg_time * (len(sentence) / (len(text) / len(sentences)))
                            )
                            
                            start_time = current_offset
                            end_time = start_time + sentence_time
                            
                            sub_data.append({
                                "id": sub_id,
                                "start": start_time / 1000.0,
                                "end": end_time / 1000.0,
                                "text": sentence.strip()
                            })
                            current_offset += sentence_time
                            sub_id += 1
                
            except Exception as e:
                print(f"Lỗi nhận dạng đoạn: {e}")
                current_offset += duration_ms
            
            os.remove(chunk_wav_path)

        merged_subs = []
        temp_sub = None
        
        for sub in sub_data:
            if temp_sub is None:
                temp_sub = sub
            elif (sub["start"] - temp_sub["end"] < 0.2 and
                  len(temp_sub["text"] + sub["text"]) < 150):
                temp_sub["end"] = sub["end"]
                temp_sub["text"] += " " + sub["text"]
            else:
                merged_subs.append(temp_sub)
                temp_sub = sub
        
        if temp_sub:
            merged_subs.append(temp_sub)

        final_subs = []
        for i, sub in enumerate(merged_subs, 1):
            if i > 1:
                prev_end = final_subs[-1]["end"]
                if sub["start"] < prev_end + 0.1:
                    sub["start"] = prev_end + 0.1
            sub["id"] = i
            final_subs.append(sub)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(final_subs, f, ensure_ascii=False, indent=2)
            
        return True
        
    except Exception as e:
        print(f"Loi khi tao sub: {e}")
        return False
    finally:
        if os.path.exists(temp_wav):
            os.remove(temp_wav)
