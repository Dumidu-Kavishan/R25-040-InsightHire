"""
Eye Confidence Detection Model for InsightHire
Based on EDUGuard pattern with enhanced error handling
"""
import cv2
import numpy as np
import os
import logging
from datetime import datetime

# Try to import dependencies
try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    tf = None

# Import fallback models
try:
    from .fallback_models import FallbackEyeDetector
except ImportError:
    from fallback_models import FallbackEyeDetector

logger = logging.getLogger(__name__)

class EyeConfidenceDetector:
    def __init__(self):
        self.fallback_detector = FallbackEyeDetector()
        self.model = None
        self.face_cascade = None
        self.eye_cascade = None
        self.model_loaded = False
        self.base_path = "/Users/dumidu/Downloads/Projects/InsightHire/Models"
        
        self.load_model()
        self.load_cascades()
        
        if not self.model_loaded:
            logger.info("🔄 Using fallback eye confidence detector")
    
    def load_model(self):
        """Load the eye confidence model"""
        try:
            # Try multiple model files
            model_files = ["eyemodel.h5", "model.keras"]
            
            for model_file in model_files:
                model_path = os.path.join(self.base_path, "Eye", model_file)
                
                logger.info(f"Trying to load eye model from: {model_path}")
                
                if os.path.exists(model_path):
                    if not TENSORFLOW_AVAILABLE:
                        logger.error("TensorFlow not available for eye model")
                        return False
                    
                    # Load the model
                    self.model = tf.keras.models.load_model(model_path)
                    self.model_loaded = True
                    logger.info(f"✅ Eye confidence model loaded from: {model_path}")
                    return True
            
            logger.error(f"Model files not found in: {os.path.join(self.base_path, 'Eye')}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error loading eye model: {e}")
            self.model_loaded = False
            return False
    
    def load_cascades(self):
        """Load face and eye detection cascades"""
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            
            if self.face_cascade.empty() or self.eye_cascade.empty():
                raise Exception("Empty cascade classifiers")
            logger.info("✅ Eye detection cascades loaded successfully")
        except Exception as e:
            logger.error(f"❌ Error loading eye cascades: {e}")
            self.face_cascade = None
            self.eye_cascade = None
    
    def detect_confidence(self, frame):
        """Detect eye confidence from frame"""
        try:
            # Use advanced model if available
            if self.model_loaded and self.face_cascade is not None and self.eye_cascade is not None:
                return self._advanced_detection(frame)
            else:
                return self.fallback_detector.detect_confidence(frame)
                
        except Exception as e:
            logger.error(f"Error in eye confidence detection: {e}")
            return self.fallback_detector.detect_confidence(frame)
    
    def _advanced_detection(self, frame):
        """Advanced eye detection using ML model"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
            
            if len(faces) == 0:
                return {'confidence_level': 'no_face_detected', 'confidence': 0.0}
            
            # Process the largest face
            face = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = face
            
            # Extract face region
            face_roi = gray[y:y+h, x:x+w]
            face_roi_color = frame[y:y+h, x:x+w]
            
            # Detect eyes within face
            eyes = self.eye_cascade.detectMultiScale(face_roi, 1.1, 5)
            
            if len(eyes) == 0:
                return {'confidence_level': 'no_eyes_detected', 'confidence': 0.0}
            
            # Analyze each eye
            eye_confidences = []
            for (ex, ey, ew, eh) in eyes:
                # Extract eye region
                eye_roi = face_roi[ey:ey+eh, ex:ex+ew]
                
                # Resize for model input (assuming model expects specific size)
                try:
                    eye_resized = cv2.resize(eye_roi, (64, 64))
                    eye_normalized = eye_resized.astype(np.float32) / 255.0
                    eye_input = np.expand_dims(np.expand_dims(eye_normalized, axis=0), axis=-1)
                    
                    # Predict confidence
                    prediction = self.model.predict(eye_input, verbose=0)
                    confidence_score = float(prediction[0][0])
                    eye_confidences.append(confidence_score)
                    
                except Exception as e:
                    logger.warning(f"Error processing eye region: {e}")
                    continue
            
            if not eye_confidences:
                return self.fallback_detector.detect_confidence(frame)
            
            # Calculate overall confidence
            overall_confidence = np.mean(eye_confidences)
            
            # Map to confidence levels
            if overall_confidence > 0.7:
                confidence_level = 'confident'
            elif overall_confidence > 0.4:
                confidence_level = 'somewhat_confident'
            else:
                confidence_level = 'not_confident'
            
            return {
                'confidence_level': confidence_level,
                'confidence': float(overall_confidence),
                'eyes_detected': len(eyes),
                'method': 'tensorflow_cv2_model',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Advanced eye detection error: {e}")
            return self.fallback_detector.detect_confidence(frame)
    
    def detect_confidence_from_base64(self, frame_data):
        """Detect confidence from base64 encoded frame"""
        try:
            import base64
            
            # Decode base64 to frame
            img_data = base64.b64decode(frame_data.split(',')[1] if ',' in frame_data else frame_data)
            np_arr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return {'confidence_level': 'invalid_frame', 'confidence': 0.0}
            
            return self.detect_confidence(frame)
            
        except Exception as e:
            logger.error(f"Error processing base64 frame: {e}")
            return {'confidence_level': 'error', 'confidence': 0.0, 'error': str(e)}
    
    def is_available(self):
        """Check if the model is available"""
        return True  # Always available due to fallback
    
    def get_model_info(self):
        """Get information about the loaded model"""
        return {
            'tensorflow_available': TENSORFLOW_AVAILABLE,
            'model_loaded': self.model_loaded,
            'cascades_loaded': self.face_cascade is not None and self.eye_cascade is not None,
            'fallback_available': True
        }
