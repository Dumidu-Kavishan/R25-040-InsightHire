"""
Eye Confidence Detection Script for InsightHire
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
logger = logging.getLogger('EyeConfidenceDetection')

class EyeConfidenceDetector:
    def __init__(self):
        self.model = None
        self.face_cascade = None
        self.eye_cascade = None
        self.load_model()
        self.load_cascades()
    
    def load_model(self):
        """Load the eye confidence detection model"""
        try:
            # Try multiple possible paths
            possible_paths = [
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Models', 'Eye', 'eyemodel.h5'),
                os.path.join(os.path.dirname(__file__), '..', '..', 'Models', 'Eye', 'eyemodel.h5'),
                './Models/Eye/eyemodel.h5',
                '../Models/Eye/eyemodel.h5',
                '../../Models/Eye/eyemodel.h5'
            ]
            
            for model_path in possible_paths:
                if os.path.exists(model_path):
                    logger.info(f"Loading eye confidence model from: {model_path}")
                    self.model = tf.keras.models.load_model(model_path, compile=False)
                    logger.info("✅ Eye confidence model loaded successfully")
                    return
            
            logger.error("❌ Eye confidence model file not found in any expected location")
            logger.info("Searched paths:")
            for path in possible_paths:
                logger.info(f"  - {path}")
                
        except Exception as e:
            logger.error(f"❌ Error loading eye confidence model: {e}")
    
    def load_cascades(self):
        """Load OpenCV cascade classifiers"""
        try:
            # Load face cascade
            face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
            
            # Load eye cascade
            eye_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
            self.eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
            
            if self.face_cascade.empty() or self.eye_cascade.empty():
                logger.error("❌ Failed to load cascade classifiers")
            else:
                logger.info("✅ Face and eye cascades loaded successfully")
                
        except Exception as e:
            logger.error(f"❌ Error loading cascades: {e}")
    
    def preprocess_eye(self, eye_img):
        """Preprocess eye image for model prediction"""
        try:
            # Resize to model input size (assuming 24x24 for eye detection)
            eye_resized = cv2.resize(eye_img, (24, 24))
            
            # Convert to grayscale if needed
            if len(eye_resized.shape) == 3:
                eye_gray = cv2.cvtColor(eye_resized, cv2.COLOR_BGR2GRAY)
            else:
                eye_gray = eye_resized
            
            # Normalize pixel values to [0, 1]
            eye_normalized = eye_gray.astype(np.float32) / 255.0
            
            # Add batch and channel dimensions
            eye_batch = np.expand_dims(eye_normalized, axis=0)
            eye_batch = np.expand_dims(eye_batch, axis=-1)
            
            return eye_batch
            
        except Exception as e:
            logger.error(f"Error preprocessing eye: {e}")
            return None
    
    def detect_eyes_in_face(self, face_roi):
        """Detect eyes within a face region"""
        try:
            eyes = self.eye_cascade.detectMultiScale(
                face_roi,
                scaleFactor=1.1,
                minNeighbors=3,
                minSize=(15, 15)
            )
            return eyes
            
        except Exception as e:
            logger.error(f"Error detecting eyes: {e}")
            return []
    
    def analyze_eye_contact(self, eyes, face_w, face_h):
        """Analyze eye contact based on eye positions"""
        try:
            if len(eyes) < 2:
                return 0.5  # Neutral if can't detect both eyes
            
            # Get eye centers
            eye_centers = []
            for (ex, ey, ew, eh) in eyes:
                center_x = ex + ew // 2
                center_y = ey + eh // 2
                eye_centers.append((center_x, center_y))
            
            # Calculate eye symmetry and position
            if len(eye_centers) >= 2:
                left_eye = eye_centers[0]
                right_eye = eye_centers[1]
                
                # Eye level (should be roughly horizontal)
                eye_level_diff = abs(left_eye[1] - right_eye[1])
                eye_level_score = max(0, 1 - (eye_level_diff / (face_h * 0.1)))
                
                # Eye spacing (should be proportional to face width)
                eye_distance = abs(left_eye[0] - right_eye[0])
                expected_distance = face_w * 0.3
                spacing_score = max(0, 1 - abs(eye_distance - expected_distance) / expected_distance)
                
                # Eye position (should be in upper half of face)
                avg_eye_y = (left_eye[1] + right_eye[1]) / 2
                position_score = max(0, 1 - (avg_eye_y / (face_h * 0.6)))
                
                # Combined score
                confidence_score = (eye_level_score + spacing_score + position_score) / 3
                return min(1.0, max(0.0, confidence_score))
            
            return 0.5
            
        except Exception as e:
            logger.error(f"Error analyzing eye contact: {e}")
            return 0.5
    
    def detect_confidence(self, frame):
        """Detect eye confidence from video frame"""
        try:
            if self.model is None:
                return {
                    'confidence_level': 'model_not_loaded',
                    'confidence': 0.0,
                    'error': 'Model not loaded'
                }
            
            if self.face_cascade is None or self.eye_cascade is None:
                return {
                    'confidence_level': 'cascades_not_loaded',
                    'confidence': 0.0,
                    'error': 'Cascades not loaded'
                }
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(50, 50)
            )
            
            if len(faces) == 0:
                return {
                    'confidence_level': 'no_face_detected',
                    'confidence': 0.0,
                    'faces_detected': 0
                }
            
            # Use the largest face
            largest_face = max(faces, key=lambda x: x[2] * x[3])
            x, y, w, h = largest_face
            
            # Extract face region
            face_roi = gray[y:y+h, x:x+w]
            
            # Detect eyes in face
            eyes = self.detect_eyes_in_face(face_roi)
            
            if len(eyes) == 0:
                return {
                    'confidence_level': 'no_eyes_detected',
                    'confidence': 0.0,
                    'eyes_detected': 0,
                    'face_coordinates': [int(x), int(y), int(w), int(h)]
                }
            
            # Analyze eye contact using geometric analysis
            eye_contact_score = self.analyze_eye_contact(eyes, w, h)
            
            # Use the first detected eye for model prediction
            ex, ey, ew, eh = eyes[0]
            eye_roi = face_roi[ey:ey+eh, ex:ex+ew]
            
            # Preprocess eye for model
            eye_input = self.preprocess_eye(eye_roi)
            if eye_input is not None and self.model is not None:
                try:
                    # Make prediction
                    prediction = self.model.predict(eye_input, verbose=0)
                    
                    # Get confidence probability
                    if len(prediction[0]) == 1:
                        # Single output (sigmoid)
                        model_confidence = float(prediction[0][0])
                    else:
                        # Multiple outputs (softmax) - take confident class
                        model_confidence = float(prediction[0][1])  # Assuming index 1 is confident
                    
                    # Combine model prediction with geometric analysis
                    combined_confidence = (model_confidence + eye_contact_score) / 2
                    
                except Exception as model_error:
                    logger.warning(f"Model prediction failed, using geometric analysis: {model_error}")
                    combined_confidence = eye_contact_score
            else:
                # Use only geometric analysis if model fails
                combined_confidence = eye_contact_score
            
            # Determine confidence level
            if combined_confidence > 0.7:
                confidence_level = 'very_confident'
                confidence = combined_confidence
            elif combined_confidence > 0.5:
                confidence_level = 'confident'
                confidence = combined_confidence
            elif combined_confidence > 0.3:
                confidence_level = 'somewhat_confident'
                confidence = combined_confidence
            else:
                confidence_level = 'not_confident'
                confidence = 1.0 - combined_confidence
            
            return {
                'confidence_level': confidence_level,
                'confidence': float(confidence),
                'eye_contact_score': float(eye_contact_score),
                'model_confidence': float(model_confidence) if 'model_confidence' in locals() else None,
                'eyes_detected': len(eyes),
                'faces_detected': len(faces),
                'face_coordinates': [int(x), int(y), int(w), int(h)],
                'eye_coordinates': [[int(ex+x), int(ey+y), int(ew), int(eh)] for ex, ey, ew, eh in eyes],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error detecting eye confidence: {e}")
            return {
                'confidence_level': 'error',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def detect_confidence_from_base64(self, frame_data):
        """Detect eye confidence from base64 encoded frame"""
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
            logger.error(f"Error detecting eye confidence from base64: {e}")
            return {
                'confidence_level': 'error',
                'confidence': 0.0,
                'error': str(e)
            }

def save_eye_data(user_id, session_id, eye_data):
    """Save eye confidence data to database"""
    try:
        if not user_id or not session_id:
            logger.error("Missing user_id or session_id")
            return False
        
        db_manager = DatabaseManager(user_id)
        
        analysis_data = {
            'session_id': session_id,
            'type': 'eye_confidence',
            'timestamp': eye_data.get('timestamp', datetime.now().isoformat()),
            'prediction': eye_data,
            'model_version': '1.0'
        }
        
        result = db_manager.save_analysis_result(session_id, analysis_data)
        
        if result:
            logger.info(f"✅ Saved eye confidence data: {eye_data['confidence_level']}")
            return True
        else:
            logger.error("❌ Failed to save eye confidence data")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error saving eye data: {e}")
        return False

# Test function
def test_eye_confidence_detection():
    """Test eye confidence detection with webcam"""
    detector = EyeConfidenceDetector()
    
    # Test with webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        logger.error("Cannot open webcam")
        return
    
    logger.info("Testing eye confidence detection. Press 'q' to quit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect eye confidence
        result = detector.detect_confidence(frame)
        
        # Display result on frame
        cv2.putText(frame, f"Eye Confidence: {result['confidence_level']}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Score: {result['confidence']:.2f}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Draw face rectangle
        if 'face_coordinates' in result:
            x, y, w, h = result['face_coordinates']
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        # Draw eye rectangles
        if 'eye_coordinates' in result:
            for eye_coords in result['eye_coordinates']:
                ex, ey, ew, eh = eye_coords
                cv2.rectangle(frame, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
        
        cv2.imshow('Eye Confidence Detection Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Test the eye confidence detection
    test_eye_confidence_detection()