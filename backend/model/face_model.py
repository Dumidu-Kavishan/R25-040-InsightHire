"""
Face Stress Detection Script for InsightHire
Based on EDUGuard model integration pattern
"""
import cv2
import numpy as np
import tensorflow as tf
import os
import sys
import logging
# Using standard TensorFlow model loading

import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('FaceStressDetection')

class FaceStressDetector:
    def __init__(self):
        self.model = None
        self.face_cascade = None
        self.emotion_model = None
        
        # Stress mapping based on emotions
        self.stress_mapping = {
            'angry': 'stress',
            'disgust': 'stress', 
            'fear': 'stress',
            'happy': 'non_stress',
            'neutral': 'non_stress',
            'sad': 'stress',
            'surprise': 'non_stress'
        }
        
        # Confidence mapping for stress levels
        self.stress_confidence = {
            'stress': 0.9,
            'non_stress': 0.8
        }
        
        self.load_model()
        self.load_face_cascade()
        self.load_emotion_model()
    
    def load_face_cascade(self):
        """Load OpenCV face cascade classifier"""
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            if self.face_cascade.empty():
                logger.error("❌ Failed to load face cascade classifier")
            else:
                logger.info("✅ Face cascade loaded successfully")
                
        except Exception as e:
            logger.error(f"❌ Error loading face cascade: {e}")

    def load_model(self):
        """Load the face stress detection model"""
        try:
            # Try multiple possible paths
            possible_paths = [
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Models', 'Face', 'stress_model.h5'),
                os.path.join(os.path.dirname(__file__), '..', '..', 'Models', 'Face', 'stress_model.h5'),
                './Models/Face/stress_model.h5',
                '../Models/Face/stress_model.h5',
                '../../Models/Face/stress_model.h5'
            ]
            
            for model_path in possible_paths:
                if os.path.exists(model_path):
                    logger.info(f"Loading face stress model from: {model_path}")
                    self.model = tf.keras.models.load_model(model_path, compile=False)
                    logger.info("✅ Face stress model loaded successfully")
                    return
            
            logger.error("❌ Face stress model file not found in any expected location")
            logger.info("Searched paths:")
            for path in possible_paths:
                logger.info(f"  - {path}")
                
        except Exception as e:
            logger.error(f"❌ Error loading face stress model: {e}")
    
    def load_emotion_model(self):
        """Load emotion recognition model for better stress detection"""
        try:
            # Try to load a pre-trained emotion model
            # For now, we'll use a simple rule-based approach
            logger.info("Using rule-based emotion detection for stress mapping")
            self.emotion_model = "rule_based"
            
        except Exception as e:
            logger.error(f"❌ Error loading emotion model: {e}")
            self.emotion_model = None
    
    def detect_emotion_from_face(self, face_img):
        """Detect emotion from face image using simple feature analysis"""
        try:
            # Convert to grayscale
            if len(face_img.shape) == 3:
                gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
            else:
                gray = face_img
            
            # Simple emotion detection based on facial features
            # This is a simplified approach - in real implementation you'd use a trained model
            
            # Calculate basic features
            mean_intensity = np.mean(gray)
            std_intensity = np.std(gray)
            
            # Use Haar cascades for eye and mouth detection
            eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            mouth_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
            
            eyes = eye_cascade.detectMultiScale(gray, 1.1, 5)
            smiles = mouth_cascade.detectMultiScale(gray, 1.8, 20)
            
            # Simple rule-based emotion detection
            if len(smiles) > 0:
                return 'happy', 0.8
            elif mean_intensity < 80:  # Dark/shadowed face might indicate stress
                return 'angry', 0.7
            elif std_intensity > 50:  # High variance might indicate tension
                return 'fear', 0.6
            elif len(eyes) >= 2:  # Normal face with visible eyes
                return 'neutral', 0.75
            else:
                return 'neutral', 0.5
                
        except Exception as e:
            logger.error(f"Error detecting emotion: {e}")
            return 'neutral', 0.5
    
    def preprocess_face(self, face_img):
        """Preprocess face image for model prediction"""
        try:
            # Resize to model input size (48x48 for stress detection)
            face_resized = cv2.resize(face_img, (48, 48))
            
            # Convert to grayscale if needed
            if len(face_resized.shape) == 3:
                face_gray = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
            else:
                face_gray = face_resized
            
            # Normalize pixel values to [0, 1]
            face_normalized = face_gray.astype(np.float32) / 255.0
            
            # Add batch and channel dimensions
            face_batch = np.expand_dims(face_normalized, axis=0)
            face_batch = np.expand_dims(face_batch, axis=-1)
            
            return face_batch
            
        except Exception as e:
            logger.error(f"Error preprocessing face: {e}")
            return None
    
    def detect_stress(self, frame):
        """
        Detect stress level using emotion-based mapping
        """
        try:
            # Check if face cascade is available
            if self.face_cascade is None:
                return {
                    'stress_level': 'cascade_not_loaded',
                    'confidence': 0.0,
                    'error': 'Face cascade not loaded',
                    'method': 'emotion_mapping'
                }
            
            # Detect faces
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                logger.warning("⚠️ No faces detected in frame")
                return {
                    'stress_level': 'unknown',
                    'confidence': 0.0,
                    'faces_detected': 0,
                    'method': 'emotion_mapping'
                }
            
            logger.info(f"✅ Found {len(faces)} face(s)")
            
            # Process the largest face
            largest_face = max(faces, key=lambda x: x[2] * x[3])
            x, y, w, h = largest_face
            
            # Extract face region
            face_img = frame[y:y+h, x:x+w]
            
            # Detect emotion from face
            emotion, emotion_confidence = self.detect_emotion_from_face(face_img)
            
            # Map emotion to stress level
            stress_level = self.stress_mapping.get(emotion, 'moderate_stress')
            stress_confidence = self.stress_confidence.get(stress_level, 0.5)
            
            # Combine emotion and stress confidence
            final_confidence = (emotion_confidence + stress_confidence) / 2
            
            logger.info(f"🧠 Detected emotion: {emotion} (confidence: {emotion_confidence:.2f})")
            logger.info(f"😰 Mapped to stress: {stress_level} (confidence: {final_confidence:.2f})")
            
            # Convert to binary stress value
            binary_stress = 1 if stress_level == 'stress' else 0
            
            return {
                'stress_level': stress_level,
                'stress': binary_stress,
                'confidence': final_confidence,
                'faces_detected': len(faces),
                'emotion': emotion,
                'emotion_confidence': emotion_confidence,
                'face_coordinates': [int(x), int(y), int(w), int(h)],
                'timestamp': datetime.now().isoformat(),
                'method': 'emotion_mapping'
            }
            
        except Exception as e:
            logger.error(f"❌ Error in stress detection: {e}")
            return {
                'stress_level': 'unknown',
                'confidence': 0.0,
                'faces_detected': 0,
                'error': str(e),
                'method': 'emotion_mapping'
            }
            
        except Exception as e:
            logger.error(f"Error detecting stress: {e}")
            return {
                'stress_level': 'error',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def detect_stress_from_base64(self, frame_data):
        """Detect stress from base64 encoded frame"""
        try:
            # Decode base64 frame
            import base64
            frame_bytes = base64.b64decode(frame_data.split(',')[1] if ',' in frame_data else frame_data)
            np_arr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return {
                    'stress_level': 'decode_error',
                    'confidence': 0.0,
                    'error': 'Failed to decode frame'
                }
            
            return self.detect_stress(frame)
            
        except Exception as e:
            logger.error(f"Error detecting stress from base64: {e}")
            return {
                'stress_level': 'error',
                'confidence': 0.0,
                'error': str(e)
            }

def save_stress_data(user_id, session_id, stress_data):
    """Save stress detection data to database"""
    try:
        if not user_id or not session_id:
            logger.error("Missing user_id or session_id")
            return False
        
        db_manager = DatabaseManager(user_id)
        
        analysis_data = {
            'session_id': session_id,
            'type': 'face_stress',
            'timestamp': stress_data.get('timestamp', datetime.now().isoformat()),
            'prediction': stress_data,
            'model_version': '1.0'
        }
        
        result = db_manager.save_analysis_result(session_id, analysis_data)
        
        if result:
            logger.info(f"✅ Saved face stress data: {stress_data['stress_level']}")
            return True
        else:
            logger.error("❌ Failed to save face stress data")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error saving stress data: {e}")
        return False

# Test function
def test_face_stress_detection():
    """Test face stress detection with webcam"""
    detector = FaceStressDetector()
    
    # Test with webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        logger.error("Cannot open webcam")
        return
    
    logger.info("Testing face stress detection. Press 'q' to quit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect stress
        result = detector.detect_stress(frame)
        
        # Display result on frame
        cv2.putText(frame, f"Stress: {result['stress_level']}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Confidence: {result['confidence']:.2f}", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Draw face rectangle if detected
        if 'face_coordinates' in result:
            x, y, w, h = result['face_coordinates']
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        cv2.imshow('Face Stress Detection Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Test the face stress detection
    test_face_stress_detection()
