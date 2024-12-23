import torch
import soundfile as sf
from fairseq.checkpoint_utils import load_model_ensemble_and_task
import json
import os
import numpy as np

def setup_tts():
    try:
        models, cfg, task = load_model_ensemble_and_task(
            ['path/to/model.pt'],
            task='text_to_speech'
        )
        model = models[0].cuda() if torch.cuda.is_available() else models[0]
        model.eval()
        return model, task
    except Exception as e:
        print(f"Error initializing TTS: {e}")
        return None, None

def generate_audio_from_text(model, task, text: str, output_path: str) -> bool:
    try:
        # Prepare text input
        sample = task.build_dataset_for_inference([text], [len(text)])
        sample = [sample[0]]
        
        # Generate audio
        with torch.no_grad():
            net_output = model(sample)
            audio = net_output['wav_out'][0].cpu().numpy()
        
        # Normalize audio
        audio = audio / np.abs(audio).max()
        
        # Save as WAV file
        sf.write(output_path, audio, task.cfg.sample_rate)
        print(f"Generated: {os.path.basename(output_path)}")
        return True
        
    except Exception as e:
        print(f"Generation error: {str(e)}")
        return False

def generate_audio(translated_file: str, output_dir: str, voice_name: str = None) -> bool:
    """Main function to generate audio from translated subtitle"""
    try:
        model, task = setup_tts()
        if not model or not task:
            return False
            
        if not os.path.exists(translated_file):
            print(f"Translation file not found: {translated_file}")
            return False
            
        os.makedirs(output_dir, exist_ok=True)
        
        with open(translated_file, 'r', encoding='utf-8') as f:
            subtitles = json.load(f)
            
        for i, sub in enumerate(subtitles):
            output_file = os.path.join(
                output_dir,
                f"audio_{i:03d}.wav"
            )
            
            print(f"\nGenerating audio {i+1}/{len(subtitles)}")
            
            if not generate_audio_from_text(model, task, sub['text'], output_file):
                print(f"Failed to generate audio segment {i+1}")
                return False
                
        print("\n✓ Audio generation completed!")
        return True
        
    except Exception as e:
        print(f"Error in audio generation: {str(e)}")
        return False