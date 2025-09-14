"""
Hand Confidence Detection Model for InsightHire
Now using YOLO11n-pose pre-trained model for better accuracy
"""
import cv2
import numpy as np
import os
import logging
import json
import math
from datetime import datetime
from collections import deque

# Try to import dependencies
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    YOLO = None

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

# ===== COMMENTED OUT OLD TENSORFLOW MODEL CODE =====
# try:
#     import tensorflow as tf
#     TENSORFLOW_AVAILABLE = True
# except ImportError:
#     TENSORFLOW_AVAILABLE = False
#     tf = None

logger = logging.getLogger(__name__)

class HandConfidenceDetector:
    def __init__(self):
        self.fallback_detector = FallbackHandDetector()
        self.yolo_model = None
        self.mediapipe_available = False
        self.base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Models')
        
        # Confidence tracking for stability analysis
        self.confidence_history = deque(maxlen=10)
        self.keypoint_history = deque(maxlen=5)
        
        # Hand keypoint indices (21 keypoints total)
        self.keypoints = {
            'wrist': 0,
            'thumb': [1, 2, 3, 4],
            'index': [5, 6, 7, 8],
            'middle': [9, 10, 11, 12],
            'ring': [13, 14, 15, 16],
            'pinky': [17, 18, 19, 20]
        }
        
        # Try to initialize MediaPipe as fallback
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
                logger.info("✅ MediaPipe hand detection initialized as fallback")
            except Exception as e:
                logger.warning(f"MediaPipe initialization failed: {e}")
                self.mediapipe_available = False
        else:
            logger.info("🔄 MediaPipe not available, using fallback hand detection")
        
        # Try to load YOLO model
        self.load_yolo_model()
    
    def load_yolo_model(self):
        """Load the YOLO11n-pose pre-trained hand model"""
        try:
            if not YOLO_AVAILABLE:
                logger.error("Ultralytics YOLO not available for hand model")
                return False
            
            # Try multiple possible paths for the YOLO model
            possible_paths = [
                os.path.join(self.base_path, "Hand", "pose-hands", "runs", "pose", "train", "weights", "best.pt"),
                os.path.join(self.base_path, "Hand", "pose-hands", "runs", "pose", "train", "weights", "last.pt"),
                "./Models/Hand/pose-hands/runs/pose/train/weights/best.pt",
                "../Models/Hand/pose-hands/runs/pose/train/weights/best.pt",
                "../../Models/Hand/pose-hands/runs/pose/train/weights/best.pt"
            ]
            
            for model_path in possible_paths:
                if os.path.exists(model_path):
                    logger.info(f"Loading YOLO hand model from: {model_path}")
                    self.yolo_model = YOLO(model_path)
                    logger.info("✅ YOLO11n-pose hand model loaded successfully")
                    return True
            
            logger.error("❌ YOLO hand model file not found in any expected location")
            logger.info("Searched paths:")
            for path in possible_paths:
                logger.info(f"  - {path}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error loading YOLO hand model: {e}")
            return False
    
    # ===== COMMENTED OUT OLD TENSORFLOW MODEL LOADING CODE =====
    # def load_model(self):
    #     """Load the hand confidence model"""
    #     try:
    #         # Try to load the H5 file first (simpler)
    #         model_h5_path = os.path.join(self.base_path, "Hand", "als_hand_moments.h5")
    #         model_json_path = os.path.join(self.base_path, "Hand", "als_hand_moments.json")
    #         
    #         logger.info(f"Loading hand model from: {model_h5_path}")
    #         
    #         if not TENSORFLOW_AVAILABLE:
    #             logger.error("TensorFlow not available for hand model")
    #             return False
    #         
    #         # Try H5 file first
    #         if os.path.exists(model_h5_path):
    #             try:
    #                 self.model = tf.keras.models.load_model(model_h5_path)
    #                 logger.info("✅ Hand confidence model loaded from H5 file")
    #                 return True
    #             except Exception as h5_error:
    #                 logger.warning(f"H5 loading failed, trying JSON approach: {h5_error}")
    #         
    #         # Try JSON + weights approach for compatibility
    #         if os.path.exists(model_json_path):
    #             try:
    #                 with open(model_json_path, 'r') as json_file:
    #                     model_json = json_file.read()
    #                 
    #                 # Fix TensorFlow compatibility issues with the JSON
    #                 model_json_fixed = model_json.replace('"batch_shape"', '"input_shape"')
    #                 
    #                 # Create model from JSON
    #                 self.model = tf.keras.models.model_from_json(model_json_fixed)
    #                 logger.info("✅ Hand confidence model loaded from JSON")
    #                 return True
    #                 
    #             except Exception as json_error:
    #                 logger.error(f"JSON loading failed: {json_error}")
    #         
    #         logger.error(f"Model files not found: {model_h5_path} or {model_json_path}")
    #         return False
    #         
    #     except Exception as e:
    #         logger.error(f"❌ Error loading hand model: {e}")
    #         return False
    
    def detect_confidence(self, frame):
        """Detect hand confidence from frame using YOLO11n-pose model"""
        try:
            # Use YOLO model if available
            if self.yolo_model is not None:
                return self._yolo_detection(frame)
            # Fallback to MediaPipe if YOLO not available
            elif self.mediapipe_available:
                return self._mediapipe_detection(frame)
            else:
                return self.fallback_detector.detect_confidence(frame)
                
        except Exception as e:
            logger.error(f"Error in hand confidence detection: {e}")
            return self.fallback_detector.detect_confidence(frame)
    
    def _yolo_detection(self, frame):
        """YOLO11n-pose based hand detection and confidence analysis"""
        try:
            # Run YOLO inference
            results = self.yolo_model(frame, verbose=False)
            
            # Process results
            for result in results:
                if result.keypoints is not None and len(result.keypoints.data) > 0:
                    # Get keypoints for the first detected hand
                    keypoints = result.keypoints.data[0].cpu().numpy()
                    
                    # Detect gesture
                    gesture = self._detect_gesture(keypoints)
                    orientation = self._detect_hand_orientation(keypoints)
                    stability = self._calculate_stability(keypoints)
                    
                    # Calculate confidence based on gesture and stability
                    confidence_score = self._calculate_confidence_score(gesture, stability, orientation)
                    
                    # Update confidence history for smoothing
                    self.confidence_history.append(confidence_score)
                    self.keypoint_history.append(keypoints)
                    
                    # Get smoothed confidence
                    smoothed_confidence = np.mean(list(self.confidence_history)) if self.confidence_history else confidence_score
                    
                    return {
                        'confidence_level': self._classify_confidence_level(smoothed_confidence),
                        'confidence': float(smoothed_confidence),
                        'gesture_detected': gesture,
                        'stability_score': float(stability),
                        'orientation': orientation,
                        'fingers_extended': self._count_extended_fingers(keypoints),
                        'hands_detected': len(result.keypoints.data),
                        'method': 'yolo11n_pose_detection',
                        'timestamp': datetime.now().isoformat()
                    }
            
            # No hand detected
            return {
                'confidence_level': 'no_hands_detected',
                'confidence': 0.0,
                'gesture_detected': 'no_hand',
                'hands_detected': 0,
                'method': 'yolo11n_pose_detection',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"YOLO detection error: {e}")
            return self.fallback_detector.detect_confidence(frame)
    
    def _detect_gesture(self, keypoints):
        """Detect hand gesture based on keypoint positions"""
        if len(keypoints) < 21:
            return "No Hand Detected"
        
        extended_fingers = self._count_extended_fingers(keypoints)
        wrist = keypoints[self.keypoints['wrist']]
        
        # Get individual finger states
        thumb_extended = self._is_finger_extended(keypoints, self.keypoints['thumb'])
        index_extended = self._is_finger_extended(keypoints, self.keypoints['index'])
        middle_extended = self._is_finger_extended(keypoints, self.keypoints['middle'])
        ring_extended = self._is_finger_extended(keypoints, self.keypoints['ring'])
        
        # Gesture recognition logic
        if extended_fingers == 0:
            return "Closed Fist"
        elif extended_fingers == 5:
            return "Open Palm"
        elif extended_fingers == 1:
            if index_extended:
                return "Pointing Gesture"
            elif thumb_extended:
                return "Thumbs Up"
            else:
                return "Single Finger"
        elif extended_fingers == 2:
            if index_extended and middle_extended:
                return "Peace Sign"
            else:
                return "Two Fingers"
        elif extended_fingers == 3:
            return "Three Fingers"
        elif extended_fingers == 4:
            return "Four Fingers"
        else:
            return f"{extended_fingers} Fingers Extended"
    
    def _is_finger_extended(self, keypoints, finger_keypoints):
        """Check if a finger is extended based on keypoint positions"""
        if len(finger_keypoints) < 4:
            return False
            
        # Get finger tip and base points
        finger_tip = keypoints[finger_keypoints[3]]  # Tip
        finger_base = keypoints[finger_keypoints[0]]  # Base
        
        # Check if finger tip is above finger base (extended)
        return finger_tip[1] < finger_base[1]
    
    def _count_extended_fingers(self, keypoints):
        """Count how many fingers are extended"""
        if len(keypoints) < 21:
            return 0
            
        wrist = keypoints[self.keypoints['wrist']]
        extended_count = 0
        
        # Check each finger
        for finger_name, finger_indices in self.keypoints.items():
            if finger_name == 'wrist':
                continue
                
            if self._is_finger_extended(keypoints, finger_indices):
                extended_count += 1
                
        return extended_count
    
    def _detect_hand_orientation(self, keypoints):
        """Detect hand orientation (front/back facing)"""
        if len(keypoints) < 21:
            return "Unknown"
        
        # Use wrist and middle finger base to determine orientation
        wrist = keypoints[self.keypoints['wrist']]
        middle_base = keypoints[self.keypoints['middle'][0]]
        
        # Simple heuristic based on relative positions
        if middle_base[0] > wrist[0]:
            return "Back Facing"
        else:
            return "Front Facing"
    
    def _calculate_stability(self, keypoints):
        """Calculate hand stability based on keypoint movement"""
        try:
            if len(self.keypoint_history) < 2:
                return 0.5  # Neutral stability if no history
            
            # Calculate movement between current and previous keypoints
            current_keypoints = keypoints
            previous_keypoints = self.keypoint_history[-1]
            
            # Calculate average movement
            total_movement = 0
            for i in range(min(len(current_keypoints), len(previous_keypoints))):
                movement = math.sqrt(
                    (current_keypoints[i][0] - previous_keypoints[i][0])**2 +
                    (current_keypoints[i][1] - previous_keypoints[i][1])**2
                )
                total_movement += movement
            
            avg_movement = total_movement / len(current_keypoints)
            
            # Convert movement to stability (less movement = more stable)
            stability = max(0.0, 1.0 - (avg_movement * 10))  # Scale factor
            return min(1.0, stability)
            
        except Exception as e:
            logger.warning(f"Error calculating stability: {e}")
            return 0.5
    
    def _calculate_confidence_score(self, gesture, stability, orientation):
        """Calculate confidence score based on gesture, stability, and orientation"""
        # Base confidence from gesture type
        gesture_confidences = {
            "Open Palm": 0.9,
            "Pointing Gesture": 0.85,
            "Thumbs Up": 0.8,
            "Peace Sign": 0.7,
            "Three Fingers": 0.6,
            "Two Fingers": 0.5,
            "Four Fingers": 0.6,
            "Single Finger": 0.4,
            "Closed Fist": 0.2,
            "No Hand Detected": 0.0
        }
        
        gesture_confidence = gesture_confidences.get(gesture, 0.5)
        
        # Orientation factor
        orientation_factor = 0.8 if orientation == "Front Facing" else 0.6
        
        # Weighted combination
        final_confidence = (
            gesture_confidence * 0.5 +      # 50% weight on gesture
            stability * 0.3 +               # 30% weight on stability
            orientation_factor * 0.2        # 20% weight on orientation
        )
        
        return min(1.0, max(0.0, final_confidence))
    
    def _classify_confidence_level(self, confidence_score):
        """Classify confidence score into levels"""
        if confidence_score >= 0.8:
            return "very_confident"
        elif confidence_score >= 0.6:
            return "confident"
        elif confidence_score >= 0.4:
            return "somewhat_confident"
        elif confidence_score >= 0.2:
            return "not_confident"
        else:
            return "very_unconfident"
    
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
            'yolo_available': YOLO_AVAILABLE,
            'yolo_model_loaded': self.yolo_model is not None,
            'mediapipe_available': self.mediapipe_available,
            'fallback_available': True,
            'model_type': 'YOLO11n-pose' if self.yolo_model is not None else 'MediaPipe Fallback'
        }
