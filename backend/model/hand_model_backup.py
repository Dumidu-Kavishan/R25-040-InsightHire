"""
Hand Confidence Detection Model for InsightHire
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
        """Load the hand confidence model from multiple possible paths"""
        if not TENSORFLOW_AVAILABLE:
            logger.info("TensorFlow not available for hand model")
            return
            
        model_paths = [
            '/Users/dumidu/Downloads/Projects/InsightHire/Models/Hand/als_hand_moments.h5',
            os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Models', 'Hand', 'als_hand_moments.h5'),
            os.path.join(os.path.dirname(__file__), '..', '..', 'Models', 'Hand', 'als_hand_moments.h5'),
            'Models/Hand/als_hand_moments.h5',
            '../Models/Hand/als_hand_moments.h5',
            '../../Models/Hand/als_hand_moments.h5'
        ]
        
        for model_path in model_paths:
            try:
                if os.path.exists(model_path):
                    # Try different keras imports
                    try:
                        self.model = tf.keras.models.load_model(model_path)
                    except Exception as keras_error:
                        logger.warning(f"TensorFlow keras failed: {keras_error}")
                        continue
                    
                    logger.info(f"✅ Hand confidence model loaded from: {model_path}")
                    return
            except Exception as e:
                logger.warning(f"⚠️ Could not load model from {model_path}: {e}")
                continue
        
        logger.warning("❌ Could not load hand confidence model from any path")
    
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
    
    def load_model(self):
        """Load the hand confidence detection model"""
        try:
            # Try multiple possible paths
            possible_paths = [
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Models', 'Hand', 'als_hand_moments.h5'),
                os.path.join(os.path.dirname(__file__), '..', '..', 'Models', 'Hand', 'als_hand_moments.h5'),
                './Models/Hand/als_hand_moments.h5',
                '../Models/Hand/als_hand_moments.h5',
                '../../Models/Hand/als_hand_moments.h5'
            ]
            
            for model_path in possible_paths:
                if os.path.exists(model_path):
                    logger.info(f"Loading hand confidence model from: {model_path}")
                    self.model = tf.keras.models.load_model(model_path)
                    logger.info("✅ Hand confidence model loaded successfully")
                    return
            
            logger.error("❌ Hand confidence model file not found")
                
        except Exception as e:
            logger.error(f"❌ Error loading hand confidence model: {e}")
    
    def detect_confidence(self, frame):
        """Detect hand confidence from video frame"""
        try:
            if not self.mediapipe_available:
                return self._fallback_hand_detection(frame)
            
            if self.model is None:
                return {
                    'confidence_level': 'model_not_loaded',
                    'confidence': 0.0,
                    'error': 'Model not loaded'
                }
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the frame
            results = self.hands.process(rgb_frame)
            
            if not results.multi_hand_landmarks:
                return {
                    'confidence_level': 'no_hands_detected',
                    'confidence': 0.0,
                    'hands_detected': 0
                }
            
            # Use the first detected hand
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Extract landmark coordinates
            landmarks = []
            for landmark in hand_landmarks.landmark:
                landmarks.extend([landmark.x, landmark.y, landmark.z])
            
            # Preprocess landmarks for model
            landmarks_array = np.array(landmarks, dtype=np.float32)
            landmarks_batch = np.expand_dims(landmarks_array, axis=0)
            
            # Ensure correct shape (63 features: 21 landmarks * 3 coordinates)
            if landmarks_batch.shape[1] != 63:
                if landmarks_batch.shape[1] < 63:
                    padding = np.zeros((1, 63 - landmarks_batch.shape[1]))
                    landmarks_batch = np.concatenate([landmarks_batch, padding], axis=1)
                else:
                    landmarks_batch = landmarks_batch[:, :63]
            
            # Make prediction
            prediction = self.model.predict(landmarks_batch, verbose=0)
            
            # Get confidence probability
            if len(prediction[0]) == 1:
                confidence_probability = float(prediction[0][0])
            else:
                confidence_probability = float(prediction[0][1])  # Assuming index 1 is confident
            
            # Determine confidence level
            if confidence_probability > 0.7:
                confidence_level = 'very_confident'
                confidence = confidence_probability
            elif confidence_probability > 0.5:
                confidence_level = 'confident'
                confidence = confidence_probability
            elif confidence_probability > 0.3:
                confidence_level = 'somewhat_confident'
                confidence = confidence_probability
            else:
                confidence_level = 'not_confident'
                confidence = 1.0 - confidence_probability
            
            return {
                'confidence_level': confidence_level,
                'confidence': float(confidence),
                'confidence_probability': float(confidence_probability),
                'hands_detected': len(results.multi_hand_landmarks),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error detecting hand confidence: {e}")
            return {
                'confidence_level': 'error',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _fallback_hand_detection(self, frame):
        """Fallback hand detection when MediaPipe is not available"""
        try:
            # Simple hand detection using skin color detection
            # Convert to HSV for better skin detection
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Define skin color range in HSV
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)
            
            # Create mask for skin color
            mask = cv2.inRange(hsv, lower_skin, upper_skin)
            
            # Apply morphological operations to clean up the mask
            kernel = np.ones((3,3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return {
                    'confidence_level': 'no_hands_detected',
                    'confidence': 0.0,
                    'hands_detected': 0,
                    'method': 'fallback_skin_detection'
                }
            
            # Find largest contours (potential hands)
            large_contours = [c for c in contours if cv2.contourArea(c) > 1000]
            
            if not large_contours:
                return {
                    'confidence_level': 'no_hands_detected',
                    'confidence': 0.0,
                    'hands_detected': 0,
                    'method': 'fallback_skin_detection'
                }
            
            # Simple confidence estimation based on contour properties
            largest_contour = max(large_contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            
            # Estimate confidence based on hand area and shape
            confidence_score = min(1.0, area / 10000)  # Normalize area
            
            if confidence_score > 0.6:
                confidence_level = 'confident'
            elif confidence_score > 0.3:
                confidence_level = 'somewhat_confident'
            else:
                confidence_level = 'not_confident'
            
            return {
                'confidence_level': confidence_level,
                'confidence': float(confidence_score),
                'hands_detected': len(large_contours),
                'method': 'fallback_skin_detection',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in fallback hand detection: {e}")
            return {
                'confidence_level': 'error',
                'confidence': 0.0,
                'error': str(e),
                'method': 'fallback_skin_detection'
            }
    
    def load_model(self):
        """Load the hand confidence detection model"""
        try:
            model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Models', 'Hand', 'als_hand_moments.h5')
            if os.path.exists(model_path):
                self.model = tf.keras.models.load_model(model_path)
                logger.info("Hand confidence model loaded successfully")
            else:
                logger.error(f"Model file not found: {model_path}")
        except Exception as e:
            logger.error(f"Error loading hand confidence model: {e}")
    
    def extract_hand_landmarks(self, frame):
        """Extract hand landmarks from frame"""
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            if results.multi_hand_landmarks:
                landmarks_list = []
                for hand_landmarks in results.multi_hand_landmarks:
                    landmarks = []
                    for landmark in hand_landmarks.landmark:
                        landmarks.extend([landmark.x, landmark.y, landmark.z])
                    landmarks_list.append(landmarks)
                return landmarks_list, results.multi_hand_landmarks
            
            return [], None
        except Exception as e:
            logger.error(f"Error extracting hand landmarks: {e}")
            return [], None
    
    def calculate_hand_features(self, landmarks):
        """Calculate hand gesture features"""
        try:
            if len(landmarks) < 63:  # 21 landmarks * 3 coordinates
                return None
            
            # Convert to numpy array and reshape
            landmarks_array = np.array(landmarks[:63]).reshape(21, 3)
            
            # Calculate distances between key points
            features = []
            
            # Thumb tip to index tip distance
            thumb_tip = landmarks_array[4]
            index_tip = landmarks_array[8]
            features.append(np.linalg.norm(thumb_tip - index_tip))
            
            # Index tip to middle tip distance
            middle_tip = landmarks_array[12]
            features.append(np.linalg.norm(index_tip - middle_tip))
            
            # Middle tip to ring tip distance
            ring_tip = landmarks_array[16]
            features.append(np.linalg.norm(middle_tip - ring_tip))
            
            # Ring tip to pinky tip distance
            pinky_tip = landmarks_array[20]
            features.append(np.linalg.norm(ring_tip - pinky_tip))
            
            # Palm center to each fingertip
            palm_center = landmarks_array[0]  # Wrist as palm center approximation
            for tip_idx in [4, 8, 12, 16, 20]:
                features.append(np.linalg.norm(landmarks_array[tip_idx] - palm_center))
            
            # Hand openness (average distance from palm to fingertips)
            fingertip_distances = [np.linalg.norm(landmarks_array[tip_idx] - palm_center) 
                                 for tip_idx in [4, 8, 12, 16, 20]]
            features.append(np.mean(fingertip_distances))
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Error calculating hand features: {e}")
            return None
    
    def detect_confidence(self, frame):
        """Detect confidence level from hand gestures"""
        try:
            if self.model is None:
                return {'confidence_level': 'unknown', 'confidence': 0.0}
            
            landmarks_list, hand_landmarks = self.extract_hand_landmarks(frame)
            
            if not landmarks_list:
                return {'confidence_level': 'no_hands_detected', 'confidence': 0.0}
            
            confidence_scores = []
            
            for landmarks in landmarks_list:
                features = self.calculate_hand_features(landmarks)
                if features is not None:
                    # Reshape for model input
                    features_input = features.reshape(1, -1)
                    
                    # Pad or truncate to match model input size if needed
                    if features_input.shape[1] < 10:  # Assuming model expects 10 features
                        padding = np.zeros((1, 10 - features_input.shape[1]))
                        features_input = np.concatenate([features_input, padding], axis=1)
                    elif features_input.shape[1] > 10:
                        features_input = features_input[:, :10]
                    
                    # Make prediction
                    prediction = self.model.predict(features_input, verbose=0)
                    confidence_scores.append(float(prediction[0][0]))
            
            if confidence_scores:
                # Use the average confidence from all detected hands
                avg_confidence = np.mean(confidence_scores)
                
                if avg_confidence > 0.5:
                    confidence_level = 'confident'
                    confidence = avg_confidence
                else:
                    confidence_level = 'not_confident'
                    confidence = 1.0 - avg_confidence
                
                return {
                    'confidence_level': confidence_level,
                    'confidence': confidence,
                    'hands_detected': len(landmarks_list),
                    'hand_landmarks': hand_landmarks is not None
                }
            
            return {'confidence_level': 'processing_error', 'confidence': 0.0}
            
        except Exception as e:
            logger.error(f"Error detecting hand confidence: {e}")
            return {'confidence_level': 'error', 'confidence': 0.0}
