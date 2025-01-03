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
            if i + 1 < len(chars) and chars[i+1].isdigit():
                i += 1
                current += chars[i]
            else:
                while i + 1 < len(chars) and chars[i+1] in ['.', '!', '?']:
                    current += chars[i+1]
                    i += 1
                if current.strip():
                    sentences.append(current.strip())
                current = ""
        i += 1
    
    if current.strip():
        sentences.append(current.strip())
    
    return sentences

def create_chunks_from_text(text: str):
    punctuation = {'.', '!', '?'}
    words = text.split()
    chunks = []
    start = 0
    MAX_WORDS = 2000

    while start < len(words):
        end = min(start + MAX_WORDS, len(words))
        chunk_words = words[start:end]

        cut_index = -1
        for i in range(len(chunk_words) - 1, -1, -1):
            if chunk_words[i] and chunk_words[i][-1] in punctuation:
                cut_index = i
                break

        if cut_index != -1 and end < len(words):
            end = start + cut_index + 1
            chunk_words = words[start:end]

        chunk_text = ' '.join(chunk_words)
        chunks.append({
            'id': len(chunks) + 1,
            'sentences': [],
            'text': chunk_text
        })
        start = end

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
