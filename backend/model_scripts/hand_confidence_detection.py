"""
Hand Confidence Detection Script for InsightHire
Based on EDUGuard model integration pattern
"""
import cv2
import numpy as np
import tensorflow as tf
import os
import sys
import logging
from compatible_model_loader import load_model_compatible
from hand_confidence_fallback import HandConfidenceFallback

import json
from datetime import datetime
import mediapipe as mp

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('HandConfidenceDetection')

class HandConfidenceDetector:
    def __init__(self):
        self.model = None
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.load_model()
    
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
                    self.model = load_model_compatible(model_path, compile_model=False)
                    logger.info("✅ Hand confidence model loaded successfully")
                    return
            
            logger.error("❌ Hand confidence model file not found in any expected location")
            logger.info("Searched paths:")
            for path in possible_paths:
                logger.info(f"  - {path}")
                
        except Exception as e:
            logger.error(f"❌ Error loading hand confidence model: {e}")
    
    def extract_hand_landmarks(self, frame):
        """Extract hand landmarks using MediaPipe"""
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the frame
            results = self.hands.process(rgb_frame)
            
            if results.multi_hand_landmarks:
                hand_landmarks_list = []
                
                for hand_landmarks in results.multi_hand_landmarks:
                    # Extract landmark coordinates
                    landmarks = []
                    for landmark in hand_landmarks.landmark:
                        landmarks.extend([landmark.x, landmark.y, landmark.z])
                    
                    hand_landmarks_list.append(landmarks)
                
                return hand_landmarks_list
            
            return []
            
        except Exception as e:
            logger.error(f"Error extracting hand landmarks: {e}")
            return []
    
    def preprocess_landmarks(self, landmarks):
        """Preprocess hand landmarks for model prediction"""
        try:
            # Convert to numpy array
            landmarks_array = np.array(landmarks, dtype=np.float32)
            
            # Normalize landmarks (they should already be normalized by MediaPipe)
            # Add batch dimension
            landmarks_batch = np.expand_dims(landmarks_array, axis=0)
            
            # Ensure the correct shape (assuming 63 features: 21 landmarks * 3 coordinates)
            if landmarks_batch.shape[1] != 63:
                logger.warning(f"Unexpected landmark shape: {landmarks_batch.shape}")
                # Pad or truncate to expected size
                if landmarks_batch.shape[1] < 63:
                    padding = np.zeros((1, 63 - landmarks_batch.shape[1]))
                    landmarks_batch = np.concatenate([landmarks_batch, padding], axis=1)
                else:
                    landmarks_batch = landmarks_batch[:, :63]
            
            return landmarks_batch
            
        except Exception as e:
            logger.error(f"Error preprocessing landmarks: {e}")
            return None
    
    def detect_confidence(self, frame):
        """Detect hand confidence from video frame"""
        try:
            if self.model is None:
                return {
                    'confidence_level': 'model_not_loaded',
                    'confidence': 0.0,
                    'error': 'Model not loaded'
                }
            
            # Extract hand landmarks
            hand_landmarks_list = self.extract_hand_landmarks(frame)
            
            if not hand_landmarks_list:
                return {
                    'confidence_level': 'no_hands_detected',
                    'confidence': 0.0,
                    'hands_detected': 0
                }
            
            # Use the first detected hand
            landmarks = hand_landmarks_list[0]
            
            # Preprocess landmarks
            landmarks_input = self.preprocess_landmarks(landmarks)
            if landmarks_input is None:
                return {
                    'confidence_level': 'preprocessing_error',
                    'confidence': 0.0,
                    'error': 'Landmark preprocessing failed'
                }
            
            # Make prediction
            prediction = self.model.predict(landmarks_input, verbose=0)
            
            # Get confidence probability
            if len(prediction[0]) == 1:
                # Single output (sigmoid)
                confidence_probability = float(prediction[0][0])
            else:
                # Multiple outputs (softmax) - take confident class
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
                'hands_detected': len(hand_landmarks_list),
                'gesture_stability': self._calculate_gesture_stability(landmarks),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error detecting hand confidence: {e}")
            return {
                'confidence_level': 'error',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _calculate_gesture_stability(self, landmarks):
        """Calculate gesture stability based on hand position"""
        try:
            # Simple stability measure based on hand center position
            # Get wrist and middle finger positions
            wrist_x, wrist_y = landmarks[0], landmarks[1]
            middle_tip_x, middle_tip_y = landmarks[36], landmarks[37]  # Middle finger tip
            
            # Calculate hand center
            center_x = (wrist_x + middle_tip_x) / 2
            center_y = (wrist_y + middle_tip_y) / 2
            
            # Return stability score (simplified)
            return min(1.0, abs(center_x - 0.5) + abs(center_y - 0.5))
            
        except Exception as e:
            logger.warning(f"Error calculating gesture stability: {e}")
            return 0.5
    
    def detect_confidence_from_base64(self, frame_data):
        """Detect hand confidence from base64 encoded frame"""
        try:
            # Decode base64 frame
            import base64
            frame_bytes = base64.b64decode(frame_data.split(',')[1] if ',' in frame_data else frame_data)
            np_arr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return {
                    'confidence_level': 'decode_error',
                    'confidence': 0.0,
                    'error': 'Failed to decode frame'
                }
            
            return self.detect_confidence(frame)
            
        except Exception as e:
            logger.error(f"Error detecting hand confidence from base64: {e}")
            return {
                'confidence_level': 'error',
                'confidence': 0.0,
                'error': str(e)
            }

def save_hand_data(user_id, session_id, hand_data):
    """Save hand confidence data to database"""
    try:
        if not user_id or not session_id:
            logger.error("Missing user_id or session_id")
            return False
        
        db_manager = DatabaseManager(user_id)
        
        analysis_data = {
            'session_id': session_id,
            'type': 'hand_confidence',
            'timestamp': hand_data.get('timestamp', datetime.now().isoformat()),
            'prediction': hand_data,
            'model_version': '1.0'
        }
        
        result = db_manager.save_analysis_result(session_id, analysis_data)
        
        if result:
            logger.info(f"✅ Saved hand confidence data: {hand_data['confidence_level']}")
            return True
        else:
            logger.error("❌ Failed to save hand confidence data")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error saving hand data: {e}")
        return False

# Test function
def test_hand_confidence_detection():
    """Test hand confidence detection with webcam"""
    detector = HandConfidenceDetector()
    
    # Test with webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        logger.error("Cannot open webcam")
        return
    
    logger.info("Testing hand confidence detection. Press 'q' to quit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect hand confidence
        result = detector.detect_confidence(frame)
        
        # Display result on frame
        cv2.putText(frame, f"Confidence: {result['confidence_level']}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Score: {result['confidence']:.2f}", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Draw hand landmarks if detected
        if result['confidence_level'] not in ['no_hands_detected', 'model_not_loaded', 'error']:
            # Extract and draw landmarks
            hand_landmarks_list = detector.extract_hand_landmarks(frame)
            if hand_landmarks_list:
                # Draw landmarks on frame (simplified)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                hands_results = detector.hands.process(rgb_frame)
                
                if hands_results.multi_hand_landmarks:
                    for hand_landmarks in hands_results.multi_hand_landmarks:
                        detector.mp_drawing.draw_landmarks(
                            frame, hand_landmarks, detector.mp_hands.HAND_CONNECTIONS)
        
        cv2.imshow('Hand Confidence Detection Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Test the hand confidence detection
    test_hand_confidence_detection()