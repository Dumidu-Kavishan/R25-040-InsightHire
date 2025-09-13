"""
Voice Confidence Detection Script for InsightHire
Based on EDUGuard model integration pattern
"""
import numpy as np
import tensorflow as tf
import os
import sys
import logging
import json
import pickle
from datetime import datetime
import librosa
import io

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import DatabaseManager
from voice_confidence_fallback import VoiceConfidenceFallback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('VoiceConfidenceDetection')

class VoiceConfidenceDetector:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.encoder = None
        self.fallback_detector = VoiceConfidenceFallback()
        self.load_model()
        self.load_preprocessing_tools()
    
    def load_model(self):
        """Load the voice confidence detection model"""
        try:
            # Use absolute path
            model_path = "/Users/dumidu/Downloads/Projects/InsightHire/Models/Voice/best_model1_weights.keras"
            if os.path.exists(model_path):
                logger.info(f"Loading voice confidence model from: {model_path}")
                # Load the model architecture first if available
                json_path = model_path.replace('best_model1_weights.keras', 'Confident_model.json')
                if os.path.exists(json_path):
                    with open(json_path, 'r') as json_file:
                        model_json = json_file.read()
                    self.model = tf.keras.models.model_from_json(model_json)
                    self.model.load_weights(model_path)
                else:
                    # Try to load weights directly
                    self.model = tf.keras.models.load_model(model_path)
                
                logger.info("✅ Voice confidence model loaded successfully")
                return
            else:
                raise FileNotFoundError(f"Voice confidence model not found at: {model_path}")
                
        except Exception as e:
            logger.error(f"❌ Error loading voice confidence model: {e}")
    
    def load_preprocessing_tools(self):
        """Load preprocessing tools (scaler and encoder)"""
        try:
            # Load scaler with absolute path
            scaler_path = "/Users/dumidu/Downloads/Projects/InsightHire/Models/Voice/scaler2.pickle"
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                logger.info("✅ Voice scaler loaded successfully")
            else:
                raise FileNotFoundError(f"Voice scaler not found at: {scaler_path}")
            
            # Load encoder with absolute path
            encoder_path = "/Users/dumidu/Downloads/Projects/InsightHire/Models/Voice/encoder2.pickle"
            if os.path.exists(encoder_path):
                with open(encoder_path, 'rb') as f:
                    self.encoder = pickle.load(f)
                logger.info("✅ Voice encoder loaded successfully")
            else:
                raise FileNotFoundError(f"Voice encoder not found at: {encoder_path}")
                    
        except Exception as e:
            logger.error(f"❌ Error loading preprocessing tools: {e}")
    
    def extract_features(self, audio_data, sample_rate=22050):
        """Extract audio features for voice confidence detection"""
        try:
            # Ensure audio is the right format
            if isinstance(audio_data, list):
                audio_data = np.array(audio_data, dtype=np.float32)
            
            # Make sure audio is 1D
            if len(audio_data.shape) > 1:
                audio_data = audio_data.flatten()
            
            # Normalize audio
            if np.max(np.abs(audio_data)) > 0:
                audio_data = audio_data / np.max(np.abs(audio_data))
            
            # Extract MFCC features
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            mfccs_mean = np.mean(mfccs, axis=1)
            
            # Extract spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
            spectral_centroids_mean = np.mean(spectral_centroids)
            
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)
            spectral_rolloff_mean = np.mean(spectral_rolloff)
            
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)
            spectral_bandwidth_mean = np.mean(spectral_bandwidth)
            
            # Extract zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(audio_data)
            zcr_mean = np.mean(zcr)
            
            # Extract chroma features
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
            chroma_mean = np.mean(chroma, axis=1)
            
            # Extract tempo
            tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            
            # Combine all features
            features = np.concatenate([
                mfccs_mean,
                [spectral_centroids_mean, spectral_rolloff_mean, 
                 spectral_bandwidth_mean, zcr_mean, tempo],
                chroma_mean
            ])
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting audio features: {e}")
            return None
    
    def preprocess_features(self, features):
        """Preprocess extracted features for model prediction"""
        try:
            # Reshape features for scaling
            features_reshaped = features.reshape(1, -1)
            
            # Scale features if scaler is available
            if self.scaler is not None:
                features_scaled = self.scaler.transform(features_reshaped)
            else:
                # Manual normalization if scaler not available
                features_scaled = (features_reshaped - np.mean(features_reshaped)) / (np.std(features_reshaped) + 1e-8)
            
            return features_scaled
            
        except Exception as e:
            logger.error(f"Error preprocessing features: {e}")
            return None
    
    def detect_confidence_from_audio_data(self, audio_data, sample_rate=22050):
        """Detect voice confidence from audio data"""
        try:
            # Use fallback detection if model failed to load
            if self.model is None:
                logger.info("Using fallback voice confidence detection")
                return self.fallback_detector.analyze_voice_confidence(audio_data, sample_rate)
            
            # Extract features
            features = self.extract_features(audio_data, sample_rate)
            if features is None:
                return {
                    'confidence_level': 'feature_extraction_error',
                    'confidence': 0.0,
                    'error': 'Failed to extract audio features'
                }
            
            # Preprocess features
            features_processed = self.preprocess_features(features)
            if features_processed is None:
                return {
                    'confidence_level': 'preprocessing_error',
                    'confidence': 0.0,
                    'error': 'Failed to preprocess features'
                }
            
            # Make prediction
            prediction = self.model.predict(features_processed, verbose=0)
            
            # Get confidence probability
            if len(prediction[0]) == 1:
                # Single output (sigmoid)
                confidence_probability = float(prediction[0][0])
            else:
                # Multiple outputs (softmax) - take confident class
                confidence_probability = float(prediction[0][1])  # Assuming index 1 is confident
            
            # Calculate audio quality metrics
            audio_quality = self._calculate_audio_quality(audio_data, sample_rate)
            
            # Adjust confidence based on audio quality
            adjusted_confidence = confidence_probability * audio_quality['quality_score']
            
            # Determine confidence level
            if adjusted_confidence > 0.7:
                confidence_level = 'very_confident'
                confidence = adjusted_confidence
            elif adjusted_confidence > 0.5:
                confidence_level = 'confident'
                confidence = adjusted_confidence
            elif adjusted_confidence > 0.3:
                confidence_level = 'somewhat_confident'
                confidence = adjusted_confidence
            else:
                confidence_level = 'not_confident'
                confidence = 1.0 - adjusted_confidence
            
            return {
                'confidence_level': confidence_level,
                'confidence': float(confidence),
                'raw_confidence': float(confidence_probability),
                'audio_quality': audio_quality,
                'feature_count': len(features),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error detecting voice confidence: {e}")
            return {
                'confidence_level': 'error',
                'confidence': 0.0,
                'error': str(e)
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
                'duration_seconds': len(audio_data) / sample_rate
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
    
    def detect_confidence_from_frequency_data(self, frequency_data):
        """Detect confidence from frequency domain audio data"""
        try:
            # Convert frequency data back to time domain
            if isinstance(frequency_data, list):
                frequency_data = np.array(frequency_data, dtype=np.float32)
            
            # Normalize frequency data
            if np.max(frequency_data) > 0:
                frequency_data = frequency_data / np.max(frequency_data)
            
            # Analyze frequency characteristics for confidence
            # Higher frequencies and energy distribution can indicate confidence
            
            # Energy in different frequency bands
            low_freq_energy = np.sum(frequency_data[:len(frequency_data)//4])
            mid_freq_energy = np.sum(frequency_data[len(frequency_data)//4:3*len(frequency_data)//4])
            high_freq_energy = np.sum(frequency_data[3*len(frequency_data)//4:])
            
            total_energy = low_freq_energy + mid_freq_energy + high_freq_energy
            
            if total_energy == 0:
                return {
                    'confidence_level': 'no_audio',
                    'confidence': 0.0
                }
            
            # Confidence indicators:
            # - Balanced frequency distribution
            # - Sufficient energy in mid frequencies (speech range)
            # - Not too much low frequency noise
            
            mid_freq_ratio = mid_freq_energy / total_energy
            high_freq_ratio = high_freq_energy / total_energy
            low_freq_ratio = low_freq_energy / total_energy
            
            # Confidence score based on frequency distribution
            confidence_score = 0.0
            
            # Mid frequencies are important for speech clarity
            confidence_score += mid_freq_ratio * 0.6
            
            # Some high frequencies indicate clarity
            confidence_score += min(high_freq_ratio * 2, 0.3)
            
            # Too much low frequency is often noise
            confidence_score += max(0, 0.1 - low_freq_ratio * 0.5)
            
            # Normalize to 0-1 range
            confidence_score = min(1.0, max(0.0, confidence_score))
            
            # Determine confidence level
            if confidence_score > 0.7:
                confidence_level = 'confident'
            elif confidence_score > 0.4:
                confidence_level = 'somewhat_confident'
            else:
                confidence_level = 'not_confident'
            
            return {
                'confidence_level': confidence_level,
                'confidence': float(confidence_score),
                'frequency_analysis': {
                    'low_freq_ratio': float(low_freq_ratio),
                    'mid_freq_ratio': float(mid_freq_ratio),
                    'high_freq_ratio': float(high_freq_ratio),
                    'total_energy': float(total_energy)
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error detecting confidence from frequency data: {e}")
            return {
                'confidence_level': 'error',
                'confidence': 0.0,
                'error': str(e)
            }

def save_voice_data(user_id, session_id, voice_data):
    """Save voice confidence data to database"""
    try:
        if not user_id or not session_id:
            logger.error("Missing user_id or session_id")
            return False
        
        db_manager = DatabaseManager(user_id)
        
        analysis_data = {
            'session_id': session_id,
            'type': 'voice_confidence',
            'timestamp': voice_data.get('timestamp', datetime.now().isoformat()),
            'prediction': voice_data,
            'model_version': '1.0'
        }
        
        result = db_manager.save_analysis_result(session_id, analysis_data)
        
        if result:
            logger.info(f"✅ Saved voice confidence data: {voice_data['confidence_level']}")
            return True
        else:
            logger.error("❌ Failed to save voice confidence data")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error saving voice data: {e}")
        return False

# Test function
def test_voice_confidence_detection():
    """Test voice confidence detection with microphone"""
    detector = VoiceConfidenceDetector()
    
    try:
        import pyaudio
        
        # Audio recording parameters
        CHUNK = 1024
        FORMAT = pyaudio.paFloat32
        CHANNELS = 1
        RATE = 22050
        RECORD_SECONDS = 3
        
        p = pyaudio.PyAudio()
        
        logger.info("Testing voice confidence detection. Recording for 3 seconds...")
        
        # Record audio
        stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       frames_per_buffer=CHUNK)
        
        frames = []
        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(np.frombuffer(data, dtype=np.float32))
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Combine audio data
        audio_data = np.concatenate(frames)
        
        # Detect confidence
        result = detector.detect_confidence_from_audio_data(audio_data, RATE)
        
        print(f"Voice Confidence Result: {result}")
        
    except ImportError:
        logger.error("PyAudio not available. Install with: pip install pyaudio")
    except Exception as e:
        logger.error(f"Error in voice confidence test: {e}")

if __name__ == "__main__":
    # Test the voice confidence detection
    test_voice_confidence_detection()
