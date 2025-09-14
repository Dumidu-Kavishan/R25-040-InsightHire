"""
Hand Confidence Detection Script for InsightHire
Now using YOLO11n-pose pre-trained model for better accuracy
"""
import cv2
import numpy as np
import os
import sys
import logging
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.hand_model import HandConfidenceDetector
from utils.database import DatabaseManager

# ===== COMMENTED OUT OLD TENSORFLOW MODEL CODE =====
# import tensorflow as tf
# from compatible_model_loader import load_model_compatible
# from hand_confidence_fallback import HandConfidenceFallback
# import mediapipe as mp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('HandConfidenceDetection')

class HandConfidenceDetectorWrapper:
    """Wrapper class that uses the new YOLO11n-pose hand model"""
    def __init__(self):
        # Use the new YOLO-based hand model
        self.detector = HandConfidenceDetector()
        logger.info("✅ Hand confidence detector initialized with YOLO11n-pose model")
    
    def detect_confidence(self, frame):
        """Detect hand confidence from video frame"""
        return self.detector.detect_confidence(frame)
    
    def detect_confidence_from_base64(self, frame_data):
        """Detect confidence from base64 encoded frame"""
        return self.detector.detect_confidence_from_base64(frame_data)
    
    def is_available(self):
        """Check if the model is available"""
        return self.detector.is_available()
    
    def get_model_info(self):
        """Get information about the loaded model"""
        return self.detector.get_model_info()
    
# ===== COMMENTED OUT OLD TENSORFLOW MODEL METHODS =====
# All the old MediaPipe and TensorFlow model methods have been replaced
# with the new YOLO11n-pose model implementation in the main HandConfidenceDetector class

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
    """Test hand confidence detection with webcam using new YOLO model"""
    detector = HandConfidenceDetectorWrapper()
    
    # Test with webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        logger.error("Cannot open webcam")
        return
    
    logger.info("Testing YOLO11n-pose hand confidence detection. Press 'q' to quit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect hand confidence using new YOLO model
        result = detector.detect_confidence(frame)
        
        # Display result on frame
        cv2.putText(frame, f"Confidence: {result['confidence_level']}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Score: {result['confidence']:.2f}", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Display additional YOLO model information
        if 'gesture_detected' in result:
            cv2.putText(frame, f"Gesture: {result['gesture_detected']}", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        if 'stability_score' in result:
            cv2.putText(frame, f"Stability: {result['stability_score']:.2f}", (10, 140), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        if 'orientation' in result:
            cv2.putText(frame, f"Orientation: {result['orientation']}", (10, 170), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        cv2.imshow('YOLO11n-pose Hand Confidence Detection Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Test the hand confidence detection
    test_hand_confidence_detection()