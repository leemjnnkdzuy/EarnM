from TTS.api import TTS
import json
import os
import torch
import warnings
import logging
import transformers

warnings.filterwarnings('ignore')
logging.getLogger('transformers').setLevel(logging.ERROR)
transformers.logging.set_verbosity_error()
logging.getLogger('TTS').setLevel(logging.ERROR)

def generate_audio_from_text(tts, text: str, output_path: str, speaker_wav: str, language: str = "en") -> bool:
    try:
        print(f"Đang tạo audio cho đoạn văn: {text[:50]}...")
        tts.tts_to_file(
            text=text,
            file_path=output_path,
            speaker_wav=[speaker_wav],
            language=language,
            split_sentences=True
        )
        if os.path.exists(output_path):
            audio_size = os.path.getsize(output_path)
            print(f"Kích thước file audio đã tạo: {audio_size} bytes")
            if audio_size == 0:
                print("Cảnh báo: File audio được tạo ra rỗng")
                return False
            return True
        return False
    except Exception as e:
        print(f"Lỗi khi tạo audio: {str(e)}")
        return False

def generate_audio(translated_file: str, output_dir: str, speaker_wav: str, language: str = "en") -> bool:
    try:
        print(f"CUDA: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"GPU: {torch.cuda.get_device_name()}")
            print(f"Bộ nhớ: {torch.cuda.get_device_properties(0).total_memory / 1024**2} MB")

        logging.disable(logging.WARNING)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Đang sử dụng: {device}")
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        logging.disable(logging.NOTSET)
        
        try:
            tts.to(device)
        except Exception as e:
            device = "cpu"
            tts.to(device)
        
        os.makedirs(output_dir, exist_ok=True)

        temp_file = os.path.join(os.path.dirname(translated_file), 'temp_translate_subs.json')
        with open(temp_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)

        chunks.sort(key=lambda x: x['id'])

        success_count = 0
        for chunk in chunks:
            output_file = os.path.join(output_dir, f"audio_{chunk['id']:03d}.wav")
            
            print(f"\nĐang tạo chunk #{chunk['id']}/{len(chunks)}")
            if generate_audio_from_text(tts, chunk['text'], output_file, speaker_wav, language):
                success_count += 1
                print(f"Chunk #{chunk['id']} đã được tạo thành công.")
            else:
                print(f"Cảnh báo: Không thể tạo chunk #{chunk['id']}")
        
        print(f"Đã tạo thành công {success_count} trên tổng số {len(chunks)} chunks")
        return success_count > 0  # Return True if at least one chunk was generated
            
    except Exception as e:
        print(f"Lỗi nghiêm trọng trong generate_audio: {str(e)}")
        return False