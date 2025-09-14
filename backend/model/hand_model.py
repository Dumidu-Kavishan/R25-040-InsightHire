"""
Hand Confidence Detection Model for InsightHire
Based on EDUGuard pattern with enhanced error handling
"""
import cv2
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
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    mp = None

# Import fallback models
try:
    from .fallback_models import FallbackHandDetector
except ImportError:
    from fallback_models import FallbackHandDetector

logger = logging.getLogger(__name__)

class HandConfidenceDetector:
    def __init__(self):
        self.fallback_detector = FallbackHandDetector()
        self.model = None
        self.mediapipe_available = False
        self.base_path = "/Users/dumidu/Downloads/Projects/InsightHire/Models"
        
        # Try to initialize MediaPipe if available
        if MEDIAPIPE_AVAILABLE:
            try:
                self.mp_hands = mp.solutions.hands
                self.hands = self.mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=2,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                self.mp_drawing = mp.solutions.drawing_utils
                self.mediapipe_available = True
                logger.info("✅ MediaPipe hand detection initialized")
            except Exception as e:
                logger.warning(f"MediaPipe initialization failed: {e}")
                self.mediapipe_available = False
        else:
            logger.info("🔄 MediaPipe not available, using fallback hand detection")
        
        # Try to load ML model
        self.load_model()
    
    def load_model(self):
        """Load the hand confidence model"""
        try:
            # Try to load the H5 file first (simpler)
            model_h5_path = os.path.join(self.base_path, "Hand", "als_hand_moments.h5")
            model_json_path = os.path.join(self.base_path, "Hand", "als_hand_moments.json")
            
            logger.info(f"Loading hand model from: {model_h5_path}")
            
            if not TENSORFLOW_AVAILABLE:
                logger.error("TensorFlow not available for hand model")
                return False
            
            # Try H5 file first
            if os.path.exists(model_h5_path):
                try:
                    self.model = tf.keras.models.load_model(model_h5_path)
                    logger.info("✅ Hand confidence model loaded from H5 file")
                    return True
                except Exception as h5_error:
                    logger.warning(f"H5 loading failed, trying JSON approach: {h5_error}")
            
            # Try JSON + weights approach for compatibility
            if os.path.exists(model_json_path):
                try:
                    with open(model_json_path, 'r') as json_file:
                        model_json = json_file.read()
                    
                    # Fix TensorFlow compatibility issues with the JSON
                    model_json_fixed = model_json.replace('"batch_shape"', '"input_shape"')
                    
                    # Create model from JSON
                    self.model = tf.keras.models.model_from_json(model_json_fixed)
                    logger.info("✅ Hand confidence model loaded from JSON")
                    return True
                    
                except Exception as json_error:
                    logger.error(f"JSON loading failed: {json_error}")
            
            logger.error(f"Model files not found: {model_h5_path} or {model_json_path}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error loading hand model: {e}")
            return False
    
    def detect_confidence(self, frame):
        """Detect hand confidence from frame"""
        try:
            # Use MediaPipe detection if available
            if self.mediapipe_available:
                return self._mediapipe_detection(frame)
            else:
                return self.fallback_detector.detect_confidence(frame)
                
        except Exception as e:
            logger.error(f"Error in hand confidence detection: {e}")
            return self.fallback_detector.detect_confidence(frame)
    
    def _mediapipe_detection(self, frame):
        """MediaPipe-based hand detection"""
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            if not results.multi_hand_landmarks:
                return {'confidence_level': 'no_hands_detected', 'confidence': 0.0}
            
            # Calculate confidence based on hand landmarks
            confidence_scores = []
            hand_count = len(results.multi_hand_landmarks)
            
            for hand_landmarks in results.multi_hand_landmarks:
                # Simple confidence based on landmark visibility and stability
                landmark_confidences = []
                for landmark in hand_landmarks.landmark:
                    # Higher visibility and more stable landmarks = higher confidence
                    landmark_conf = min(1.0, landmark.visibility if hasattr(landmark, 'visibility') else 0.8)
                    landmark_confidences.append(landmark_conf)
                
                hand_confidence = np.mean(landmark_confidences)
                confidence_scores.append(hand_confidence)
            
            # Overall confidence
            overall_confidence = np.mean(confidence_scores)
            
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
                'hands_detected': hand_count,
                'method': 'mediapipe_detection',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"MediaPipe detection error: {e}")
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
            'mediapipe_available': self.mediapipe_available,
            'tensorflow_available': TENSORFLOW_AVAILABLE,
            'model_loaded': self.model is not None,
            'fallback_available': True
        }
