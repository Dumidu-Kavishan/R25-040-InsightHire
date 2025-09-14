"""
Hybrid Eye Confidence Detection Model for InsightHire
Combines Gaze Tracking (dlib-based) with TensorFlow model and fallback system
"""
import cv2
import numpy as np
import os
import logging
from datetime import datetime
import sys

# Add gaze tracking to path
gaze_tracking_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Models', 'Eye', 'eye_train_model')
if gaze_tracking_path not in sys.path:
    sys.path.append(gaze_tracking_path)

# Try to import dependencies
try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    tf = None

# Try to import gaze tracking
try:
    from gaze_tracking import GazeTracking
    GAZE_TRACKING_AVAILABLE = True
except ImportError:
    GAZE_TRACKING_AVAILABLE = False
    GazeTracking = None

# Import fallback models
try:
    from .fallback_models import FallbackEyeDetector
except ImportError:
    from fallback_models import FallbackEyeDetector

logger = logging.getLogger(__name__)

class HybridEyeConfidenceDetector:
    def __init__(self):
        self.gaze_tracker = None
        self.tensorflow_model = None
        self.fallback_detector = FallbackEyeDetector()
        self.face_cascade = None
        self.eye_cascade = None
        self.model_loaded = False
        self.gaze_tracking_loaded = False
        self.cascades_loaded = False
        
        # Get current working directory for model paths
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.base_path = os.path.join(current_dir, 'Models')
        
        # Initialize components
        self.load_gaze_tracking()
        self.load_tensorflow_model()
        self.load_cascades()
        
        # Log initialization status
        self.log_initialization_status()
    
    def load_gaze_tracking(self):
        """Load the gaze tracking system (primary detection method)"""
        try:
            if not GAZE_TRACKING_AVAILABLE:
                logger.warning("Gaze tracking not available - dlib or dependencies missing")
                return False
            
            self.gaze_tracker = GazeTracking()
            self.gaze_tracking_loaded = True
            logger.info("✅ Gaze tracking system loaded successfully")
            return True
            
        except (ImportError, OSError, RuntimeError) as e:
            logger.error(f"❌ Error loading gaze tracking: {e}")
            self.gaze_tracking_loaded = False
            return False
    
    def load_tensorflow_model(self):
        """Load the TensorFlow model (secondary detection method)"""
        try:
            if not TENSORFLOW_AVAILABLE:
                logger.warning("TensorFlow not available for eye model")
                return False
            
            # Try multiple model files
            model_files = ["eyemodel.h5", "model.keras"]
            
            for model_file in model_files:
                model_path = os.path.join(self.base_path, "Eye", model_file)
                
                if os.path.exists(model_path):
                    logger.info(f"Loading TensorFlow eye model from: {model_path}")
                    self.tensorflow_model = tf.keras.models.load_model(model_path)
                    self.model_loaded = True
                    logger.info(f"✅ TensorFlow eye model loaded from: {model_path}")
                    return True
            
            logger.warning("TensorFlow model files not found")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error loading TensorFlow model: {e}")
            self.model_loaded = False
            return False
    
    def load_cascades(self):
        """Load face and eye detection cascades"""
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            
            if self.face_cascade.empty() or self.eye_cascade.empty():
                raise Exception("Empty cascade classifiers")
            
            self.cascades_loaded = True
            logger.info("✅ Eye detection cascades loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading eye cascades: {e}")
            self.face_cascade = None
            self.eye_cascade = None
            self.cascades_loaded = False
            return False
    
    def log_initialization_status(self):
        """Log the initialization status of all components"""
        logger.info("=== Hybrid Eye Model Initialization Status ===")
        logger.info("Gaze Tracking: %s", '✅' if self.gaze_tracking_loaded else '❌')
        logger.info("TensorFlow Model: %s", '✅' if self.model_loaded else '❌')
        logger.info("OpenCV Cascades: %s", '✅' if self.cascades_loaded else '❌')
        logger.info("Fallback Detector: ✅ (always available)")
        
        if not any([self.gaze_tracking_loaded, self.model_loaded, self.cascades_loaded]):
            logger.warning("⚠️ All primary detection methods failed - using fallback only")
    
    def detect_confidence(self, frame):
        """Detect eye confidence using hybrid approach"""
        try:
            # Method 1: Try Gaze Tracking (Primary)
            if self.gaze_tracking_loaded:
                result = self._gaze_tracking_detection(frame)
                if result is not None:
                    return result
            
            # Method 2: Try TensorFlow Model (Secondary)
            if self.model_loaded and self.cascades_loaded:
                result = self._tensorflow_detection(frame)
                if result is not None:
                    return result
            
            # Method 3: Use Fallback (Tertiary)
            logger.info("Using fallback eye detection")
            return self.fallback_detector.detect_confidence(frame)
            
        except Exception as e:
            logger.error(f"Error in hybrid eye confidence detection: {e}")
            return self.fallback_detector.detect_confidence(frame)
    
    def _gaze_tracking_detection(self, frame):
        """Primary detection using gaze tracking system"""
        try:
            # Refresh gaze tracking with new frame
            self.gaze_tracker.refresh(frame)
            
            # Check if pupils are located
            if not self.gaze_tracker.pupils_located:
                return None  # Fall back to next method
            
            # Get gaze tracking data
            is_blinking = self.gaze_tracker.is_blinking()
            is_center = self.gaze_tracker.is_center()
            is_left = self.gaze_tracker.is_left()
            is_right = self.gaze_tracker.is_right()
            horizontal_ratio = self.gaze_tracker.horizontal_ratio()
            vertical_ratio = self.gaze_tracker.vertical_ratio()
            
            # Calculate confidence based on gaze behavior
            confidence_score = self._calculate_gaze_confidence(
                is_blinking, is_center, is_left, is_right, 
                horizontal_ratio, vertical_ratio
            )
            
            # Determine confidence level
            if confidence_score > 0.7:
                confidence_level = 'confident'
            elif confidence_score > 0.4:
                confidence_level = 'somewhat_confident'
            else:
                confidence_level = 'not_confident'
            
            # Get pupil coordinates
            left_pupil = self.gaze_tracker.pupil_left_coords()
            right_pupil = self.gaze_tracker.pupil_right_coords()
            
            return {
                'confidence_level': confidence_level,
                'confidence': float(confidence_score),
                'eyes_detected': 2 if left_pupil and right_pupil else 0,
                'method': 'gaze_tracking_dlib',
                'gaze_data': {
                    'is_blinking': is_blinking,
                    'is_center': is_center,
                    'is_left': is_left,
                    'is_right': is_right,
                    'horizontal_ratio': horizontal_ratio,
                    'vertical_ratio': vertical_ratio,
                    'left_pupil': left_pupil,
                    'right_pupil': right_pupil
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Gaze tracking detection error: {e}")
            return None
    
    def _calculate_gaze_confidence(self, is_blinking, is_center, is_left, is_right, horizontal_ratio, vertical_ratio):
        """Calculate confidence score based on gaze tracking data"""
        try:
            # Base confidence
            base_confidence = 0.8
            
            # Blinking penalty
            if is_blinking:
                base_confidence = 0.2
                return base_confidence
            
            # Gaze direction analysis
            if is_center:
                # Looking at center (camera/screen) - high confidence
                base_confidence += 0.15
            elif is_left or is_right:
                # Looking away - moderate penalty
                base_confidence -= 0.2
            
            # Horizontal ratio analysis (more precise)
            if horizontal_ratio is not None:
                if 0.4 <= horizontal_ratio <= 0.6:
                    # Center gaze range
                    base_confidence += 0.1
                elif horizontal_ratio < 0.2 or horizontal_ratio > 0.8:
                    # Extreme gaze positions
                    base_confidence -= 0.3
            
            # Vertical ratio analysis
            if vertical_ratio is not None:
                if 0.3 <= vertical_ratio <= 0.7:
                    # Normal vertical range
                    base_confidence += 0.05
                elif vertical_ratio < 0.1 or vertical_ratio > 0.9:
                    # Extreme vertical positions
                    base_confidence -= 0.2
            
            # Ensure confidence is within bounds
            return max(0.0, min(1.0, base_confidence))
            
        except Exception as e:
            logger.error(f"Error calculating gaze confidence: {e}")
            return 0.5  # Default moderate confidence
    
    def _tensorflow_detection(self, frame):
        """Secondary detection using TensorFlow model"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
            
            if len(faces) == 0:
                return None  # Fall back to next method
            
            # Process the largest face
            face = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = face
            
            # Extract face region
            face_roi = gray[y:y+h, x:x+w]
            
            # Detect eyes within face
            eyes = self.eye_cascade.detectMultiScale(face_roi, 1.1, 5)
            
            if len(eyes) == 0:
                return None  # Fall back to next method
            
            # Analyze each eye with TensorFlow model
            eye_confidences = []
            for (ex, ey, ew, eh) in eyes:
                # Extract eye region
                eye_roi = face_roi[ey:ey+eh, ex:ex+ew]
                
                # Resize for model input
                try:
                    eye_resized = cv2.resize(eye_roi, (64, 64))
                    eye_normalized = eye_resized.astype(np.float32) / 255.0
                    eye_input = np.expand_dims(np.expand_dims(eye_normalized, axis=0), axis=-1)
                    
                    # Predict confidence
                    prediction = self.tensorflow_model.predict(eye_input, verbose=0)
                    confidence_score = float(prediction[0][0])
                    eye_confidences.append(confidence_score)
                    
                except Exception as e:
                    logger.warning(f"Error processing eye region with TensorFlow: {e}")
                    continue
            
            if not eye_confidences:
                return None  # Fall back to next method
            
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
            logger.error(f"TensorFlow detection error: {e}")
            return None
    
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
        """Check if any detection method is available"""
        return True  # Always available due to fallback
    
    def get_model_info(self):
        """Get information about the loaded models"""
        return {
            'gaze_tracking_available': GAZE_TRACKING_AVAILABLE,
            'gaze_tracking_loaded': self.gaze_tracking_loaded,
            'tensorflow_available': TENSORFLOW_AVAILABLE,
            'tensorflow_model_loaded': self.model_loaded,
            'cascades_loaded': self.cascades_loaded,
            'fallback_available': True,
            'base_path': self.base_path
        }
