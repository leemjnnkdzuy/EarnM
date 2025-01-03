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

def optimize_torch_performance():
    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = True
        torch.backends.cudnn.enabled = True
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        torch.backends.cudnn.deterministic = False
        
        for device in range(torch.cuda.device_count()):
            torch.cuda.set_per_process_memory_fraction(0.95, device)
            torch.cuda.empty_cache()

def generate_audio_from_text(tts, text: str, output_path: str, speaker_wav: str, language: str = "en") -> bool:
    try:
        print(f"Đang tạo audio cho đoạn văn: {text[:50]}...")
        tts.tts_to_file(
            text=text,
            file_path=output_path,
            speaker_wav=[speaker_wav],
            language=language,
            split_sentences=True,
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
        optimize_torch_performance()

        if torch.cuda.is_available():            
            print(f"CUDA: Enabled")
            print(f"GPU: {torch.cuda.get_device_name()}")
            print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**2:.0f} MB")

        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")

        logging.disable(logging.WARNING)
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2",
                  progress_bar=False,
                  gpu=torch.cuda.is_available())
        logging.disable(logging.NOTSET)
        
        if device == "cuda":
            try:
                tts.to(device)
                tts.model.half()
                
                vram_mb = torch.cuda.get_device_properties(0).total_memory / 1024**2
                chunk_size = int(vram_mb / 100) * 50
                tts.synthesizer.max_text_length = chunk_size
                
            except Exception as e:
                print(f"GPU optimization failed: {str(e)}")
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
                torch.cuda.empty_cache()
            else:
                print(f"Cảnh báo: Không thể tạo chunk #{chunk['id']}")
        
        print(f"Đã tạo thành công {success_count} trên tổng số {len(chunks)} chunks")
        return success_count > 0
            
    except Exception as e:
        print(f"Lỗi nghiêm trọng trong generate_audio: {str(e)}")
        return False