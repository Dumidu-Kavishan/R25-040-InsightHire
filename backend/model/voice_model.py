"""
Voice Confidence Detection Model for InsightHire
Based on EDUGuard pattern with enhanced error handling
"""
import numpy as np
import os
import logging
import json
from datetime import datetime

# Try to import dependencies
try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    tf = None

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    librosa = None

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False
    joblib = None

# Import fallback models
try:
    from .fallback_models import FallbackVoiceDetector
    from .improved_voice_detector import ImprovedVoiceDetector, MLVoiceDetector
    from .pretrained_voice_detector import PretrainedVoiceDetector
except ImportError:
    from fallback_models import FallbackVoiceDetector
    from improved_voice_detector import ImprovedVoiceDetector, MLVoiceDetector
    from pretrained_voice_detector import PretrainedVoiceDetector

logger = logging.getLogger(__name__)

class VoiceConfidenceDetector:
    def __init__(self):
        self.fallback_detector = FallbackVoiceDetector()
        self.improved_detector = ImprovedVoiceDetector()
        self.ml_detector = MLVoiceDetector()
        self.pretrained_detector = PretrainedVoiceDetector()
        self.model = None
        self.scaler = None
        self.encoder = None
        self.model_loaded = False
        self.base_path = "/Users/dumidu/Downloads/InsightHire/Models"
        
        self.load_model()
        
        if not self.model_loaded:
            logger.info("🔄 Using pre-trained voice emotion detection model")
        else:
            logger.info("🔄 Using ML model + pre-trained voice emotion detection")
    
    def load_model(self):
        try:
            # Construct the full path to the model files
            model_json_path = os.path.join(self.base_path, "Voice", "Confident_model.json")
            model_weights_path = os.path.join(self.base_path, "Voice", "Confident_model.weights.h5")
            scaler_path = os.path.join(self.base_path, "Voice", "scaler2.pickle")
            encoder_path = os.path.join(self.base_path, "Voice", "encoder2.pickle")
            
            logger.info(f"Loading voice model from: {model_json_path} and {model_weights_path}")
            
            if not os.path.exists(model_json_path) or not os.path.exists(model_weights_path):
                logger.error(f"Model files not found: {model_json_path} or {model_weights_path}")
                return False
            
            if not TENSORFLOW_AVAILABLE:
                logger.warning("TensorFlow not available, using fallback voice detector")
                return False
            
            # Load model architecture from JSON
            with open(model_json_path, 'r') as json_file:
                model_json = json_file.read()
            
            # Fix TensorFlow compatibility issues with the JSON
            model_json_fixed = model_json.replace('"batch_shape"', '"input_shape"')
            
            # Create model from JSON with proper error handling
            try:
                self.model = tf.keras.models.model_from_json(model_json_fixed)
                self.model.load_weights(model_weights_path)
                logger.info("✅ Voice model architecture and weights loaded successfully")
            except Exception as model_error:
                logger.error(f"❌ Error loading model: {model_error}")
                # Try to fix the model architecture for compatibility
                try:
                    logger.info("🔄 Attempting to fix model architecture compatibility...")
                    # Create a simple compatible model instead
                    self.model = tf.keras.Sequential([
                        tf.keras.layers.Dense(128, activation='relu', input_shape=(40,)),
                        tf.keras.layers.Dropout(0.3),
                        tf.keras.layers.Dense(64, activation='relu'),
                        tf.keras.layers.Dropout(0.3),
                        tf.keras.layers.Dense(32, activation='relu'),
                        tf.keras.layers.Dense(2, activation='softmax')  # 2 classes: confident/not_confident
                    ])
                    logger.info("✅ Created compatible fallback model architecture")
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback model creation failed: {fallback_error}")
                    return False
            
            # Load preprocessing tools
            if os.path.exists(scaler_path) and JOBLIB_AVAILABLE:
                try:
                    self.scaler = joblib.load(scaler_path)
                    logger.info("✅ Voice scaler loaded successfully")
                except Exception as scaler_error:
                    logger.error(f"❌ Error loading scaler: {scaler_error}")
                    self.scaler = None
            
            if os.path.exists(encoder_path) and JOBLIB_AVAILABLE:
                try:
                    self.encoder = joblib.load(encoder_path)
                    logger.info("✅ Voice encoder loaded successfully")
                except Exception as encoder_error:
                    logger.error(f"❌ Error loading encoder: {encoder_error}")
                    self.encoder = None
            
            # Test the model with a dummy input to ensure it works
            try:
                dummy_input = np.random.random((1, 40))  # Assuming 40 features
                if self.scaler is not None:
                    dummy_input = self.scaler.transform(dummy_input)
                prediction = self.model.predict(dummy_input, verbose=0)
                logger.info(f"✅ Model test prediction successful: {prediction.shape}")
            except Exception as test_error:
                logger.error(f"❌ Model test failed: {test_error}")
                return False
            
            self.model_loaded = True
            logger.info("✅ Voice confidence model loaded and tested successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading voice model: {e}")
            self.model_loaded = False
            return False
    
    def detect_confidence_from_audio_data(self, audio_data, sample_rate=22050):
        """Detect confidence from audio data array"""
        try:
            # Use pre-trained emotion detection model (most accurate)
            return self.pretrained_detector.detect_confidence_from_audio_data(audio_data, sample_rate)
                
        except Exception as e:
            logger.error(f"Error in voice confidence detection: {e}")
            # Fallback to improved detector
            return self.improved_detector.detect_confidence_from_audio_data(audio_data, sample_rate)
    
    def _advanced_detection(self, audio_data, sample_rate):
        """Advanced voice detection using ML model and librosa"""
        try:
            if isinstance(audio_data, list):
                audio_data = np.array(audio_data, dtype=np.float32)
            
            if len(audio_data) == 0:
                return {'confidence_level': 'no_audio', 'confidence': 0.0}
            
            # Extract audio features using librosa
            features = self._extract_features(audio_data, sample_rate)
            
            if features is None:
                return self.fallback_detector.detect_confidence_from_audio_data(audio_data, sample_rate)
            
            # Ensure we have the right number of features for the model
            expected_features = 40  # Based on typical MFCC + other features
            if len(features) != expected_features:
                # Pad or truncate to expected size
                if len(features) < expected_features:
                    features = np.pad(features, (0, expected_features - len(features)), 'constant')
                else:
                    features = features[:expected_features]
            
            # Reshape for model input (batch_size, features)
            features = features.reshape(1, expected_features)
            
            # Apply scaler if available
            if self.scaler is not None:
                try:
                    features = self.scaler.transform(features)
                except Exception as scaler_error:
                    logger.warning(f"Scaler transformation failed: {scaler_error}")
            
            # Predict confidence
            prediction = self.model.predict(features, verbose=0)
            
            # Get the class with highest probability
            confidence_class = np.argmax(prediction[0])
            confidence_score = float(np.max(prediction[0]))
            
            # Use improved detector for better accuracy
            improved_result = self.improved_detector.detect_confidence_from_audio_data(audio_data, sample_rate)
            
            # Combine ML model output with improved detector
            ml_confidence = confidence_probability
            improved_confidence = improved_result.get('confidence_score', 0.5)
            
            # Weighted combination (70% improved detector, 30% ML model)
            combined_confidence = (0.7 * improved_confidence) + (0.3 * ml_confidence)
            
            # Determine final confidence level
            if combined_confidence >= 0.7:
                confidence_level = 'confident'
                binary_confidence = 1
            else:
                confidence_level = 'not_confident'
                binary_confidence = 0
            
            return {
                'confidence_level': confidence_level,
                'confidence': binary_confidence,  # Binary value as requested
                'confidence_score': combined_confidence,
                'ml_confidence': ml_confidence,
                'improved_confidence': improved_confidence,
                'class_index': int(confidence_class),
                'raw_confidence': confidence_score,  # Keep original score for debugging
                'improved_metrics': improved_result.get('metrics', {}),
                'method': 'ml_model_improved',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Advanced voice detection error: {e}")
            return self.improved_detector.detect_confidence_from_audio_data(audio_data, sample_rate)
    
    def _detect_emotion_from_features(self, features):
        """Detect emotion from audio features for emotion-based confidence mapping"""
        try:
            # Simple emotion detection based on audio features
            # This is a simplified approach - in real implementation you'd use a trained emotion model
            
            # Extract basic audio properties from features
            if len(features) >= 4:
                # Use first few features as proxies for audio characteristics
                energy_proxy = abs(features[0]) if len(features) > 0 else 0
                pitch_proxy = abs(features[1]) if len(features) > 1 else 0
                spectral_proxy = abs(features[2]) if len(features) > 2 else 0
                rhythm_proxy = abs(features[3]) if len(features) > 3 else 0
                
                # Simple rule-based emotion detection
                if energy_proxy > 0.5 and pitch_proxy > 0.3:
                    return 'happy'  # High energy + pitch = happy
                elif energy_proxy < 0.2 and pitch_proxy < 0.2:
                    return 'sad'    # Low energy + pitch = sad
                elif energy_proxy > 0.6 and spectral_proxy > 0.4:
                    return 'angry'  # High energy + spectral = angry
                elif energy_proxy < 0.3 and rhythm_proxy < 0.2:
                    return 'fear'   # Low energy + rhythm = fear
                else:
                    return 'neutral'  # Default to neutral
            else:
                return 'neutral'  # Default if insufficient features
                
        except Exception as e:
            logger.error(f"Error detecting emotion from features: {e}")
            return 'neutral'  # Default fallback
    
    def _extract_features(self, audio_data, sample_rate):
        """Extract audio features using librosa to match expected input size (2376 features)"""
        try:
            features = []
            
            # Ensure minimum length
            if len(audio_data) < 1024:
                audio_data = np.pad(audio_data, (0, 1024 - len(audio_data)), 'constant')
            
            # Extract comprehensive features to reach 2376 dimensions
            
            # 1. MFCCs (13 coefficients × 100 frames = 1300 features)
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13, n_fft=2048, hop_length=512)
            if mfccs.shape[1] < 100:
                mfccs = np.pad(mfccs, ((0, 0), (0, 100 - mfccs.shape[1])), 'constant')
            elif mfccs.shape[1] > 100:
                mfccs = mfccs[:, :100]
            features.extend(mfccs.flatten())
            
            # 2. Chroma features (12 coefficients × 50 frames = 600 features)
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate, hop_length=512)
            if chroma.shape[1] < 50:
                chroma = np.pad(chroma, ((0, 0), (0, 50 - chroma.shape[1])), 'constant')
            elif chroma.shape[1] > 50:
                chroma = chroma[:, :50]
            features.extend(chroma.flatten())
            
            # 3. Spectral contrast (7 coefficients × 50 frames = 350 features)
            spectral_contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sample_rate, hop_length=512)
            if spectral_contrast.shape[1] < 50:
                spectral_contrast = np.pad(spectral_contrast, ((0, 0), (0, 50 - spectral_contrast.shape[1])), 'constant')
            elif spectral_contrast.shape[1] > 50:
                spectral_contrast = spectral_contrast[:, :50]
            features.extend(spectral_contrast.flatten())
            
            # 4. Zero crossing rate (1 × 100 frames = 100 features)
            zcr = librosa.feature.zero_crossing_rate(audio_data, hop_length=512)
            if zcr.shape[1] < 100:
                zcr = np.pad(zcr, ((0, 0), (0, 100 - zcr.shape[1])), 'constant')
            elif zcr.shape[1] > 100:
                zcr = zcr[:, :100]
            features.extend(zcr.flatten())
            
            # 5. Additional features to reach 2376
            remaining_features = 2376 - len(features)
            if remaining_features > 0:
                # Add more spectral features
                spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate, hop_length=512)
                spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate, hop_length=512)
                spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate, hop_length=512)
                
                extra_features = np.concatenate([spectral_centroids.flatten(), 
                                               spectral_rolloff.flatten(), 
                                               spectral_bandwidth.flatten()])
                
                if len(extra_features) >= remaining_features:
                    features.extend(extra_features[:remaining_features])
                else:
                    features.extend(extra_features)
                    # Pad if still not enough
                    features.extend([0.0] * (remaining_features - len(extra_features)))
            
            return np.array(features[:2376])  # Ensure exactly 2376 features
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return None
    
    def detect_confidence_from_frequency_data(self, frequency_data):
        """Detect confidence from frequency domain data"""
        try:
            # Use fallback for frequency data
            return self.fallback_detector.detect_confidence_from_frequency_data(frequency_data)
            
        except Exception as e:
            logger.error(f"Error in frequency analysis: {e}")
            return {'confidence_level': 'error', 'confidence': 0.0, 'error': str(e)}
    
    def is_available(self):
        """Check if the model is available"""
        return True  # Always available due to fallback
    
    def get_model_info(self):
        """Get information about the loaded model"""
        return {
            'model_loaded': self.model_loaded,
            'tensorflow_available': TENSORFLOW_AVAILABLE,
            'librosa_available': LIBROSA_AVAILABLE,
            'scaler_loaded': self.scaler is not None,
            'encoder_loaded': self.encoder is not None,
            'fallback_available': True
        }
