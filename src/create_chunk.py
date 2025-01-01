import json
from typing import List, Dict

def split_text_into_sentences(text: str) -> List[str]:
    sentences = []
    current = ""
    chars = list(text)
    i = 0
    
    while i < len(chars):
        current += chars[i]
        
        if chars[i] in ['.', '!', '?']:
            while i + 1 < len(chars) and chars[i+1] in ['.', '!', '?']:
                current += chars[i+1]
                i += 1
            
            if current.strip() and len(current.strip()) <= 230:
                sentences.append(current.strip())
            elif current.strip():
                last_end = -1
                for j in range(min(230, len(current))):
                    if current[j] in ['.', '!', '?']:
                        last_end = j + 1
                
                if last_end != -1:
                    sentences.append(current[:last_end].strip())
                    current = current[last_end:].strip()
                    i -= len(current)
                    continue
            current = ""
        i += 1
    
    if current.strip() and len(current.strip()) <= 230:
        sentences.append(current.strip())
    
    return sentences

def create_chunks_from_text(text: str, sentences_per_chunk: int = 50) -> List[Dict]:
    sentences = split_text_into_sentences(text)
    chunks = []
    current_chunk = []
    chunk_id = 1
    
    for sentence in sentences:
        current_chunk.append(sentence)
        
        if len(current_chunk) >= sentences_per_chunk:
            chunks.append({
                'id': chunk_id,
                'sentences': current_chunk.copy(),
                'text': ' '.join(current_chunk)
            })
            chunk_id += 1
            current_chunk = []
    
    if current_chunk:
        chunks.append({
            'id': chunk_id,
            'sentences': current_chunk,
            'text': ' '.join(current_chunk)
        })
    
    return chunks

def create_chunks_from_subtitles(subtitle_file: str) -> List[Dict]:
    try:
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            subtitles = json.load(f)
            
        full_text = ' '.join(sub['text'] for sub in subtitles)
        return create_chunks_from_text(full_text)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

def save_chunks(chunks: List[Dict], output_file: str) -> bool:
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
