import google.generativeai as genai
import json
import os
import time
from dotenv import load_dotenv
from src.utils import get_google_api_key

load_dotenv()
api_key = get_google_api_key()
genai.configure(api_key=api_key)

def split_text_into_sentences(text):
    sentences = []
    current = ""
    for char in text:
        current += char
        if char in ['.', '!', '?']:
            if current.strip():
                sentences.append(current.strip())
            current = ""
    if current.strip():
        sentences.append(current.strip())
    return sentences

def create_chunks(sentences, chunk_size=70):
    chunks = []
    current_chunk = []
    for sentence in sentences:
        current_chunk.append(sentence)
        if len(current_chunk) >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

def translate_text(text: str, target_lang: str) -> str:
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""You are a professional translator.
        Translate this text to {target_lang}. Keep the translation natural and accurate.
        Only return the translated text, nothing else.
        Text to translate: {text}"""
        
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            }
        ]
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                candidate_count=1,
                max_output_tokens=2048,
            ),
            safety_settings=safety_settings
        )
        
        if hasattr(response, 'text') and response.text:
            return response.text.strip()
        else:
            print("No translation received")
            return text
            
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return text

def translate_subtitle_file(input_file: str, output_file: str, target_lang: str) -> bool:
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            original_subs = json.load(f)

        full_text = " ".join(sub['text'] for sub in original_subs)
        
        sentences = split_text_into_sentences(full_text)
        
        chunks = create_chunks(sentences)
        temp_file = os.path.join(os.path.dirname(output_file), 'temp_translate_subs.json')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump([{'chunk': chunk} for chunk in chunks], f, ensure_ascii=False, indent=2)
        
        translated_chunks = []
        success_count = 0
        
        for i, chunk in enumerate(chunks, 1):
            print(f"\nXử lý chuck {i}/{len(chunks)}")
            translated = translate_text(chunk, target_lang)
            
            if translated and translated != chunk:
                translated_chunks.append(translated)
                success_count += 1
                print(f"Chunk {i} đã được dịch.")
            else:
                print(f"Chunk {i} không thể dịch.")
                translated_chunks.append(chunk)
            
            time.sleep(1)
        
        if success_count == 0:
            print("Không có chuck nào được tạo ra!")
            return False
        
        final_translation = " ".join(translated_chunks)
        
        video_duration = max(sub['end'] for sub in original_subs)
        final_subtitle = [{
            'start': 0,
            'end': video_duration,
            'text': final_translation
        }]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_subtitle, f, ensure_ascii=False, indent=2)
        
        print(f"Hoàn thành dịch {success_count}/{len(chunks)} chunks")
        return success_count > 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False
