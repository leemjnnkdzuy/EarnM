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
            speed=1.2
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

def generate_audio_direct(text: str, output_dir: str, speaker_wav: str, language: str = "en") -> bool:
    try:
        optimize_torch_performance()
        
        if torch.cuda.is_available():            
            print(f"CUDA: Enabled")
            print(f"GPU: {torch.cuda.get_device_name()}")
            print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**2:.0f} MB")
            print(f"Compute capability: {torch.cuda.get_device_capability()}")
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")

        model_path = "tts_models/multilingual/multi-dataset/xtts_v2"
        tts = TTS(model_path,
                  progress_bar=False, 
                  gpu=torch.cuda.is_available())
        
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
        output_file = os.path.join(output_dir, "output_audio.wav")
            
        print("\nGenerating audio...")
        if generate_audio_from_text(tts, text, output_file, speaker_wav, language):
            print("Audio generated successfully!")
            return True
        else:
            print("Failed to generate audio")
            return False
            
    except Exception as e:
        print(f"Critical error in generate_audio: {str(e)}")
        return False

if __name__ == "__main__":
    text = "However, the girl couldn't save the prospect of getting 10 delicious slime cores. And so Ai gently apologized to the slime before cutting off a part of its body. As the two were about to leave, an unusual sound rang out, followed by the appearance of Zen and his party. They were in a panic because they had discovered a monster Ozeze that rarely appeared in this area. Zen's face turned pale, blaming his bad luck and even blaming Ai for their previous unfortunate encounter. The Ozeze began to charge, and just the sight of it made Zen's party tremble in fear. Their party was no match for it. Just then, Ai and Lai ran over. As soon as he saw Ai, Zen smiled sinisterly and ordered his party to run towards Ai. Ai and Lai, those two will be our scapegoats. When Lai saw the Ozeze, he thought to himself that if he could defeat it, it would be the perfect start to his adventurer life. Lai charged forward despite Ai's warning that his swordsmanship skill did not enhance his physical defense. If he were to get hit, he would likely die instantly. However, Lai did not falter, eager to prove himself and make a mark in the adventurer world. With a surge of determination, Lai drew his sword and faced the monster. Having grasped the power of his swordsmanship skill, Lai was determined to test his mettle in a life-or-death battle with the Ozeze. Power surged through him, and he realized that he could win if he used his full potential with both his legs and sword. His mind focused on a single goal: to win, to prove himself, and to catch up to Lena, the one he admired. With all his concentration, Lai activated his ultimate skill, Raging Sword Slash. Light from the skill erupted, engulfing the Ozeze. The charging monster was instantly cut in half, its momentum halted. Lai let out a cry of joy, \"I won!\" Ai ran over to check on him, both relieved and unconvinced. \"Are you okay?\" From above, Zen's party had witnessed the battle. And all three of them were speechless when they realized that Lai had not only defeated the slime but also an Ozeze. Back at the adventurer's guild, Lai presented the Ozeze's core as proof and asked if he could exchange it for a reward. The other adventurers in the guild were shocked. Confirming the story, one of them even called over their receptionist. Just when Lai felt like he could finally step into the adventurer world with a proud start, everyone's attention was suddenly drawn to the return of an S-Rank party, the strongest among adventurers. Lai's eyes lit up when he recognized Lena, the party's saintly ace, but his joy of reunion was quickly extinguished by her cold reaction. Lena denied knowing him, leaving Lai confused and disappointed. Elsewhere, the silver-haired girl tried to ask the saint what had happened when she suddenly talked about a message she had received. She declared to the stunned crowd that a threat would soon befall the world. However, the girl couldn't save the prospect of getting 10 delicious slime cores. And so Ai gently apologized to the slime before cutting off a part of its body. As the two were about to leave, an unusual sound rang out, followed by the appearance of Zen and his party. They were in a panic because they had discovered a monster Ozeze that rarely appeared in this area. Zen's face turned pale, blaming his bad luck and even blaming Ai for their previous unfortunate encounter. The Ozeze began to charge, and just the sight of it made Zen's party tremble in fear. Their party was no match for it. Just then, Ai and Lai ran over. As soon as he saw Ai, Zen smiled sinisterly and ordered his party to run towards Ai. Ai and Lai, those two will be our scapegoats. When Lai saw the Ozeze, he thought to himself that if he could defeat it, it would be the perfect start to his adventurer life. Lai charged forward despite Ai's warning that his swordsmanship skill did not enhance his physical defense. If he were to get hit, he would likely die instantly. However, Lai did not falter, eager to prove himself and make a mark in the adventurer world. With a surge of determination, Lai drew his sword and faced the monster. Having grasped the power of his swordsmanship skill, Lai was determined to test his mettle in a life-or-death battle with the Ozeze. Power surged through him, and he realized that he could win if he used his full potential with both his legs and sword. His mind focused on a single goal: to win, to prove himself, and to catch up to Lena, the one he admired. With all his concentration, Lai activated his ultimate skill, Raging Sword Slash. Light from the skill erupted, engulfing the Ozeze. The charging monster was instantly cut in half, its momentum halted. Lai let out a cry of joy, \"I won!\" Ai ran over to check on him, both relieved and unconvinced."
    output_dir = "output"
    speaker_wav = "assets/voice/en/Kendra_voice.wav"
    language = "en"
    
    success = generate_audio_direct(text, output_dir, speaker_wav, language)
    if not success:
        print("Audio generation completed successfully")