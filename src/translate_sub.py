import google.generativeai as genai
import json
import os
import time
from dotenv import load_dotenv
from src.utils import get_google_api_key

load_dotenv()
api_key = get_google_api_key()
genai.configure(api_key=api_key)

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
            print("\nKhông thể dịch văn bản.")
            return text
            
    except Exception as e:
        print(f"\nError: {str(e)}")
        return text

def translate_subtitle_file(input_file: str, output_file: str, target_lang: str) -> bool:
    try:
        chunks_file = os.path.join(os.path.dirname(input_file), 'subtitle_chunks.json')
        with open(chunks_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)

        temp_file = os.path.join(os.path.dirname(output_file), 'temp_translate_subs.json')
        
        translated_chunks = []
        success_count = 0
        
        for i, chunk in enumerate(chunks, 1):
            print(f"\nXử lý chunk #{chunk['id']}/{len(chunks)}")
            translated = translate_text(chunk['text'], target_lang)
            
            if translated and translated != chunk['text']:
                translated_chunks.append({
                    'id': chunk['id'],
                    'sentences': chunk['sentences'],
                    'text': translated
                })
                success_count += 1
                print(f"Chunk #{chunk['id']} đã được dịch thành công.")
            else:
                print(f"Chunk #{chunk['id']} không thể dịch.")
                translated_chunks.append(chunk)
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(translated_chunks, f, ensure_ascii=False, indent=2)
            
            time.sleep(1)
        
        if success_count == 0:
            print("\nKhông có chunk nào được dịch!")
            return False

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(translated_chunks, f, ensure_ascii=False, indent=2)
        
        print(f"Hoàn thành dịch {success_count}/{len(chunks)} chunks")
        return success_count > 0
        
    except Exception as e:
        print(f"\nError: {e}")
        return False
