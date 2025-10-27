#!/usr/bin/env python3
"""
Voice Model Server for InsightHire
=================================

Dedicated server for voice confidence detection using the trained voice model.
Runs on port 5003 in dedicated VoiceTracking conda environment.

Usage:
    conda activate VoiceTracking
    python voice_model_server.py
"""

import os
import sys
import numpy as np
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
from datetime import datetime
import traceback
import json
import pickle

# Add the voice model directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
voice_model_dir = os.path.join(project_root, 'Models', 'Voice')

print(f"🔍 Looking for voice model files in: {voice_model_dir}")
print(f"📁 Project root: {project_root}")

# Import required libraries
try:
    import tensorflow as tf
    import librosa
    print("✅ TensorFlow and Librosa imported successfully!")
except ImportError as e:
    print(f"❌ Failed to import required libraries: {e}")
    print("Please ensure you're in the VoiceTracking environment with all dependencies installed")
    sys.exit(1)

# Verify model files exist
model_file = os.path.join(voice_model_dir, 'best_model1_weights.keras')
scaler_file = os.path.join(voice_model_dir, 'scaler2.pickle')
encoder_file = os.path.join(voice_model_dir, 'encoder2.pickle')

print(f"🔍 Checking model files:")
print(f"   Model: {'✅' if os.path.exists(model_file) else '❌'} {model_file}")
print(f"   Scaler: {'✅' if os.path.exists(scaler_file) else '❌'} {scaler_file}")
print(f"   Encoder: {'✅' if os.path.exists(encoder_file) else '❌'} {encoder_file}")

if not all(os.path.exists(f) for f in [model_file, scaler_file, encoder_file]):
    print("❌ Missing required model files!")
    sys.exit(1)

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('VoiceModelServer')

class VoiceModelServer:
    """Voice model server using trained voice confidence model"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.encoder = None
        self.load_model()
        self.load_preprocessing_tools()
    
    def load_model(self):
        """Load the voice confidence detection model"""
        try:
            logger.info(f"Loading voice model from: {model_file}")
            
            # Try loading the model architecture first if available
            json_path = os.path.join(voice_model_dir, 'Confident_model.json')
            if os.path.exists(json_path):
                with open(json_path, 'r') as json_file:
                    model_json = json_file.read()
                self.model = tf.keras.models.model_from_json(model_json)
                self.model.load_weights(model_file)
                logger.info("✅ Model loaded from JSON architecture + weights")
            else:
                # Try to load weights directly
                self.model = tf.keras.models.load_model(model_file)
                logger.info("✅ Model loaded directly from weights file")
            
            logger.info("✅ Voice confidence model loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Error loading voice model: {e}")
            logger.error(traceback.format_exc())
            raise e
    
    def load_preprocessing_tools(self):
        """Load preprocessing tools (scaler and encoder)"""
        try:
            # Load scaler
            with open(scaler_file, 'rb') as f:
                self.scaler = pickle.load(f)
            logger.info("✅ Voice scaler loaded successfully")
            
            # Load encoder
            with open(encoder_file, 'rb') as f:
                self.encoder = pickle.load(f)
            logger.info("✅ Voice encoder loaded successfully")
                    
        except Exception as e:
            logger.error(f"❌ Error loading preprocessing tools: {e}")
            raise e
    
    def extract_features(self, audio_data, sample_rate=22050):
        """Extract audio features for voice confidence detection"""
        try:
            logger.info(f"🔍 Feature extraction started: input type={type(audio_data)}, length={len(audio_data) if hasattr(audio_data, '__len__') else 'unknown'}")
            
            # Ensure audio is the right format
            if isinstance(audio_data, list):
                audio_data = np.array(audio_data, dtype=np.float32)
                logger.info(f"📝 Converted list to numpy array: {audio_data.shape}")
            
            # Make sure audio is 1D
            if len(audio_data.shape) > 1:
                audio_data = audio_data.flatten()
                logger.info(f"📝 Flattened audio to 1D: {audio_data.shape}")
            
            # Check if audio has valid data
            if len(audio_data) == 0:
                logger.error("❌ Audio data is empty")
                return None
                
            logger.info(f"📊 Audio stats: min={audio_data.min():.3f}, max={audio_data.max():.3f}, mean={audio_data.mean():.3f}")
            
            # Normalize audio
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                audio_data = audio_data / max_val
                logger.info(f"📊 Audio normalized by {max_val:.3f}")
            else:
                logger.warning("⚠️ Audio max value is 0, adding small noise")
                audio_data = audio_data + 1e-8 * np.random.normal(0, 1, len(audio_data))
            
            # Extract MFCC features
            logger.info("🔄 Extracting MFCC features...")
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            mfccs_mean = np.mean(mfccs, axis=1)
            logger.info(f"✅ MFCC extracted: shape={mfccs.shape}, mean_shape={mfccs_mean.shape}")
            
            # Extract spectral features
            logger.info("🔄 Extracting spectral features...")
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
            spectral_centroids_mean = np.mean(spectral_centroids)
            
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)
            spectral_rolloff_mean = np.mean(spectral_rolloff)
            
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)
            spectral_bandwidth_mean = np.mean(spectral_bandwidth)
            logger.info("✅ Spectral features extracted")
            
            # Extract zero crossing rate
            logger.info("🔄 Extracting ZCR...")
            zcr = librosa.feature.zero_crossing_rate(audio_data)
            zcr_mean = np.mean(zcr)
            logger.info("✅ ZCR extracted")
            
            # Extract chroma features
            logger.info("🔄 Extracting chroma features...")
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
            chroma_mean = np.mean(chroma, axis=1)
            logger.info(f"✅ Chroma extracted: shape={chroma.shape}, mean_shape={chroma_mean.shape}")
            
            # Extract tempo
            logger.info("🔄 Extracting tempo...")
            try:
                tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
                # Ensure tempo is a scalar value
                if isinstance(tempo, np.ndarray):
                    tempo = float(tempo[0]) if len(tempo) > 0 else 120.0
                else:
                    tempo = float(tempo)
                logger.info(f"✅ Tempo extracted: {tempo}")
            except Exception as e:
                logger.warning(f"⚠️ Tempo extraction failed: {e}, using default 120")
                tempo = 120.0
            
            # Combine all features
            logger.info("🔄 Combining features...")
            features = np.concatenate([
                mfccs_mean,
                [spectral_centroids_mean, spectral_rolloff_mean, 
                 spectral_bandwidth_mean, zcr_mean, tempo],
                chroma_mean
            ])
            
            logger.info(f"✅ Feature extraction completed: {len(features)} features")
            logger.info(f"📊 Feature stats: min={features.min():.3f}, max={features.max():.3f}")
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Error extracting audio features: {e}")
            logger.error(f"📊 Audio data info: type={type(audio_data)}, shape={getattr(audio_data, 'shape', 'no shape')}")
            import traceback
            logger.error(f"📋 Full traceback: {traceback.format_exc()}")
            return None
    
    def preprocess_features(self, features):
        """Preprocess extracted features for model prediction"""
        try:
            # Reshape features for scaling
            features_reshaped = features.reshape(1, -1)
            
            # Scale features
            if self.scaler is not None:
                features_scaled = self.scaler.transform(features_reshaped)
            else:
                # Manual normalization if scaler not available
                features_scaled = (features_reshaped - np.mean(features_reshaped)) / (np.std(features_reshaped) + 1e-8)
            
            return features_scaled
            
        except Exception as e:
            logger.error(f"Error preprocessing features: {e}")
            return None
    
    def detect_silence(self, audio_data, sample_rate=22050):
        """Detect if audio is silent or contains meaningful content"""
        try:
            # Calculate RMS energy
            rms = np.sqrt(np.mean(audio_data ** 2))
            
            # Calculate zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
            zcr_mean = np.mean(zcr)
            
            # Thresholds for silence detection
            rms_threshold = 0.01  # Minimum energy level
            zcr_threshold = 0.1   # Minimum variation
            
            is_silent = rms < rms_threshold and zcr_mean < zcr_threshold
            
            return {
                'is_silent': bool(is_silent),
                'rms': float(rms),
                'zcr_mean': float(zcr_mean),
                'quality_indicators': {
                    'has_energy': bool(rms >= rms_threshold),
                    'has_variation': bool(zcr_mean >= zcr_threshold)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in silence detection: {e}")
            return {'is_silent': True, 'rms': 0.0, 'zcr_mean': 0.0}
    
    def analyze_voice_clip(self, audio_data, sample_rate=22050):
        """Analyze voice clip for confidence detection"""
        try:
            logger.info(f"🎤 Starting voice analysis: audio_type={type(audio_data)}, sample_rate={sample_rate}")
            
            # First check for silence
            silence_analysis = self.detect_silence(audio_data, sample_rate)
            logger.info(f"🔇 Silence analysis: {silence_analysis}")
            
            if silence_analysis['is_silent']:
                logger.info("🔇 Audio detected as silent, returning no_audio_detected")
                return {
                    'confidence_level': 'no_audio_detected',
                    'confidence': 0.0,
                    'emotion': 'no_audio_detected',
                    'method': 'silence_detection',
                    'silence_analysis': silence_analysis,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Prepare audio for CNN model (expects raw audio, not spectral features)
            logger.info("🔄 Preparing audio for CNN model...")
            
            # Ensure audio is the right format
            if isinstance(audio_data, list):
                audio_data = np.array(audio_data, dtype=np.float32)
            
            # Normalize audio
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                audio_data = audio_data / max_val
            
            # The model expects input shape (batch_size, sequence_length, 1)
            # Based on model architecture: input expects raw audio with 2376 samples
            target_length = 2376
            
            # Resample or pad/truncate audio to match expected length
            if len(audio_data) > target_length:
                # Truncate
                audio_data = audio_data[:target_length]
                logger.info(f"📏 Audio truncated to {target_length} samples")
            elif len(audio_data) < target_length:
                # Pad with zeros
                padding = target_length - len(audio_data)
                audio_data = np.pad(audio_data, (0, padding), mode='constant')
                logger.info(f"📏 Audio padded with {padding} zeros to {target_length} samples")
            
            # Reshape to (batch_size, sequence_length, 1) for Conv1D
            audio_reshaped = audio_data.reshape(1, target_length, 1)
            
            logger.info(f"📊 Prepared audio shape: {audio_reshaped.shape}")
            
            # Make prediction directly with raw audio
            logger.info("🔄 Making model prediction...")
            prediction = self.model.predict(audio_reshaped, verbose=0)
            logger.info(f"✅ Model prediction completed: shape={prediction.shape}")
            
            # Get confidence probability
            if len(prediction[0]) == 1:
                # Single output (sigmoid)
                confidence_probability = float(prediction[0][0])
                logger.info(f"📊 Single output prediction: {confidence_probability}")
            else:
                # Multiple outputs (softmax) - get the max confidence class
                confidence_probability = float(np.max(prediction[0]))
                predicted_class = int(np.argmax(prediction[0]))
                logger.info(f"📊 Multi-output prediction: {prediction[0]}, max confidence: {confidence_probability}, class: {predicted_class}")
            
            # Calculate audio quality metrics
            logger.info("🔄 Calculating audio quality...")
            audio_quality = self._calculate_audio_quality(audio_data, sample_rate)
            logger.info(f"📊 Audio quality: {audio_quality['quality_score']:.2f}")
            
            # Adjust confidence based on audio quality
            adjusted_confidence = confidence_probability * audio_quality['quality_score']
            logger.info(f"📊 Adjusted confidence: {confidence_probability:.3f} × {audio_quality['quality_score']:.3f} = {adjusted_confidence:.3f}")
            
            # Determine confidence level and emotion
            if adjusted_confidence > 0.7:
                confidence_level = 'very_confident'
                emotion = 'confident'
                confidence = adjusted_confidence
            elif adjusted_confidence > 0.5:
                confidence_level = 'confident'
                emotion = 'calm'
                confidence = adjusted_confidence
            elif adjusted_confidence > 0.3:
                confidence_level = 'somewhat_confident'
                emotion = 'neutral'
                confidence = adjusted_confidence
            else:
                confidence_level = 'not_confident'
                emotion = 'nervous'
                confidence = 1.0 - adjusted_confidence
            
            logger.info(f"🎯 Final result: {confidence_level} - {emotion} ({confidence:.3f})")
            
            return {
                'confidence_level': confidence_level,
                'confidence': float(confidence),
                'emotion': emotion,
                'method': 'cnn_model',
                'raw_confidence': float(confidence_probability),
                'audio_quality': audio_quality,
                'silence_analysis': silence_analysis,
                'input_shape': list(audio_reshaped.shape),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing voice clip: {e}")
            logger.error(traceback.format_exc())
            return {
                'confidence_level': 'error',
                'confidence': 0.0,
                'emotion': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _calculate_audio_quality(self, audio_data, sample_rate):
        """Calculate audio quality metrics"""
        try:
            # Signal-to-noise ratio estimation
            signal_power = np.mean(audio_data ** 2)
            noise_estimate = np.var(audio_data)
            snr = 10 * np.log10(signal_power / (noise_estimate + 1e-10))
            
            # Volume level
            rms = np.sqrt(np.mean(audio_data ** 2))
            
            # Frequency range coverage
            fft = np.fft.fft(audio_data)
            freqs = np.fft.fftfreq(len(fft), 1/sample_rate)
            magnitude = np.abs(fft)
            
            # Check frequency coverage (speech typically 80Hz - 8kHz)
            speech_band = (freqs >= 80) & (freqs <= 8000)
            speech_energy = np.sum(magnitude[speech_band])
            total_energy = np.sum(magnitude)
            frequency_coverage = speech_energy / (total_energy + 1e-10)
            
            # Calculate overall quality score
            snr_score = min(1.0, max(0.0, (snr + 10) / 40))  # Normalize SNR to 0-1
            volume_score = min(1.0, max(0.0, rms * 10))       # Normalize volume
            freq_score = min(1.0, frequency_coverage * 2)      # Normalize frequency coverage
            
            quality_score = (snr_score + volume_score + freq_score) / 3
            
            return {
                'quality_score': float(quality_score),
                'snr': float(snr),
                'rms': float(rms),
                'frequency_coverage': float(frequency_coverage),
                'duration_seconds': float(len(audio_data) / sample_rate)
            }
            
        except Exception as e:
            logger.warning(f"Error calculating audio quality: {e}")
            return {
                'quality_score': 0.5,
                'snr': 0.0,
                'rms': 0.0,
                'frequency_coverage': 0.0,
                'duration_seconds': 0.0
            }

# Initialize the voice model server
print("🔄 Initializing voice confidence model from trained models...")
try:
    voice_server = VoiceModelServer()
    print("✅ Voice confidence model initialized successfully!")
    print(f"🎤 Model loaded from: {voice_model_dir}")
except Exception as e:
    print(f"❌ Failed to initialize voice model: {e}")
    print(f"📁 Check if model files exist in: {voice_model_dir}")
    sys.exit(1)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'voice_confidence_detection',
        'model_path': voice_model_dir,
        'message': 'Voice confidence model from trained models',
        'port': 5003
    })

@app.route('/analyze_voice', methods=['POST'])
def analyze_voice():
    """Voice confidence detection using trained model"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Handle different input formats
        audio_data = None
        sample_rate = data.get('sample_rate', 22050)
        
        if 'audio_data' in data:
            # Direct audio array
            audio_data = np.array(data['audio_data'], dtype=np.float32)
        elif 'audio_base64' in data:
            # Base64 encoded audio
            import base64
            audio_bytes = base64.b64decode(data['audio_base64'])
            audio_data = np.frombuffer(audio_bytes, dtype=np.float32)
        else:
            return jsonify({'error': 'No audio data provided (audio_data or audio_base64)'}), 400
        
        if audio_data is None or len(audio_data) == 0:
            return jsonify({'error': 'Invalid or empty audio data'}), 400
        
        # Analyze the audio
        result = voice_server.analyze_voice_clip(audio_data, sample_rate)
        
        logger.info(f"🎤 Voice analysis result: {result.get('confidence_level')} - {result.get('emotion')} (confidence: {result.get('confidence', 0.0):.2f})")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Error in voice analysis: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': str(e),
            'confidence_level': 'error',
            'confidence': 0.0,
            'emotion': 'error',
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    print("🎤 Starting Voice Model Server on port 5003...")
    print("💡 Make sure you're running this in the VoiceTracking conda environment")
    print("🔗 Access health check at: http://localhost:5003/health")
    
    app.run(host='0.0.0.0', port=5003, debug=False)