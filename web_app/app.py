import os
import sys
import torch
import librosa
import numpy as np
from flask import Flask, render_template, request, jsonify
from transformers import (
    Wav2Vec2ForCTC,
    Wav2Vec2Processor,
    DistilBertTokenizer,
    DistilBertForSequenceClassification
)

# Fix for Flask reloader and path issues
# Ensure we are running from the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
if script_dir not in sys.path:
    sys.path.append(script_dir)

app = Flask(__name__)

# Configuration
# Go up one level from web_app to PROJET_ROPOTIQUE, then into robot_voice_dataset/models
MODEL_DIR = os.path.abspath(os.path.join(script_dir, '..', 'robot_voice_dataset', 'models'))
ASR_MODEL_PATH = os.path.join(MODEL_DIR, 'asr_model')
INTENT_MODEL_PATH = os.path.join(MODEL_DIR, 'intent_model')

print(f"Model Directory: {MODEL_DIR}")
print(f"ASR Model Path: {ASR_MODEL_PATH}")
print(f"Intent Model Path: {INTENT_MODEL_PATH}")

# Device configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Load Models
print("Loading models...")
try:
    if not os.path.exists(ASR_MODEL_PATH):
        raise FileNotFoundError(f"ASR Model not found at {ASR_MODEL_PATH}")
    if not os.path.exists(INTENT_MODEL_PATH):
        raise FileNotFoundError(f"Intent Model not found at {INTENT_MODEL_PATH}")

    # ASR Model
    asr_processor = Wav2Vec2Processor.from_pretrained(ASR_MODEL_PATH)
    asr_model = Wav2Vec2ForCTC.from_pretrained(ASR_MODEL_PATH)
    asr_model.to(device)
    asr_model.eval()

    # Intent Model
    intent_tokenizer = DistilBertTokenizer.from_pretrained(INTENT_MODEL_PATH)
    intent_model = DistilBertForSequenceClassification.from_pretrained(INTENT_MODEL_PATH)
    intent_model.to(device)
    intent_model.eval()
    
    print("Models loaded successfully.")
except Exception as e:
    print(f"CRITICAL ERROR loading models: {e}")
    # Fallback for development if models are missing/corrupt
    asr_model = None
    intent_model = None

# Intent Mapping (based on training data order: AVANCER, DROITE, GAUCHE, STOP)
ID2INTENT = {
    0: "AVANCER",
    1: "DROITE",
    2: "GAUCHE",
    3: "STOP"
}

def process_audio(file_path):
    """Load and preprocess audio file."""
    # Load audio at 16kHz
    audio, sr = librosa.load(file_path, sr=16000, mono=True)
    
    # Normalize
    if np.max(np.abs(audio)) > 0:
        audio = audio / np.max(np.abs(audio))
        
    return audio

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save temporary file
    temp_path = os.path.join(script_dir, 'temp_audio.wav')
    file.save(temp_path)

    try:
        if asr_model is None or intent_model is None:
            return jsonify({'error': 'Models not loaded correctly. Check server logs.'}), 500

        # 1. Preprocess Audio
        audio_input = process_audio(temp_path)
        
        # 2. ASR Inference (Speech -> Text)
        inputs = asr_processor(audio_input, sampling_rate=16000, return_tensors="pt", padding=True)
        input_values = inputs.input_values.to(device)
        
        with torch.no_grad():
            logits = asr_model(input_values).logits
        
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = asr_processor.batch_decode(predicted_ids)[0]
        
        # 3. Intent Inference (Text -> Intent)
        # Tokenize transcription
        text_inputs = intent_tokenizer(
            transcription, 
            return_tensors="pt", 
            padding=True, 
            truncation=True, 
            max_length=64
        )
        
        input_ids = text_inputs['input_ids'].to(device)
        attention_mask = text_inputs['attention_mask'].to(device)
        
        with torch.no_grad():
            outputs = intent_model(input_ids, attention_mask=attention_mask)
        
        predicted_class_id = torch.argmax(outputs.logits, dim=1).item()
        predicted_intent = ID2INTENT.get(predicted_class_id, "UNKNOWN")
        confidence = torch.nn.functional.softmax(outputs.logits, dim=1)[0][predicted_class_id].item()

        return jsonify({
            'transcription': transcription,
            'intent': predicted_intent,
            'confidence': f"{confidence:.2f}"
        })

    except Exception as e:
        print(f"Prediction Error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    # use_reloader=False prevents the "No module named app" error in some Windows environments
    # when running from a parent directory or debugger.
    app.run(debug=True, port=5000, use_reloader=False)
