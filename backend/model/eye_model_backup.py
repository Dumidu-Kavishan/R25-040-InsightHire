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
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) == 0:
                return {'confidence_level': 'no_face_detected', 'confidence': 0.0}
            
            # Use largest face
            x, y, w, h = max(faces, key=lambda x: x[2] * x[3])
            face_roi = gray[y:y+h, x:x+w]
            
            # Detect eyes in face
            eyes = self.eye_cascade.detectMultiScale(face_roi, 1.1, 3)
            
            if len(eyes) < 1:
                return {'confidence_level': 'no_eyes_detected', 'confidence': 0.0}
            
            confidence_scores = []
            
            for (ex, ey, ew, eh) in eyes:
                # Extract eye region
                eye_roi = face_roi[ey:ey+eh, ex:ex+ew]
                
                # Preprocess for model
                try:
                    eye_resized = cv2.resize(eye_roi, (64, 64))  # Common eye model size
                    eye_normalized = eye_resized / 255.0
                    eye_input = np.expand_dims(eye_normalized, axis=0)
                    eye_input = np.expand_dims(eye_input, axis=-1)
                    
                    # Predict confidence
                    prediction = self.model.predict(eye_input, verbose=0)
                    
                    if prediction.shape[-1] == 1:
                        confidence_score = float(prediction[0][0])
                    else:
                        confidence_score = float(np.max(prediction[0]))
                    
                    confidence_scores.append(confidence_score)
                    
                except Exception as model_error:
                    logger.warning(f"Model prediction failed for eye: {model_error}")
                    # Fallback calculation
                    confidence_scores.append(0.5)
            
            # Average confidence across eyes
            overall_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
            
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
                'method': 'tensorflow_model',
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
            'model_loaded': self.model_loaded,
            'tensorflow_available': TENSORFLOW_AVAILABLE,
            'cascades_loaded': self.face_cascade is not None and self.eye_cascade is not None,
            'fallback_available': True
        }
    
    def load_model(self):
        """Load the eye confidence detection model"""
        try:
            model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Models', 'Eye', 'eyemodel.h5')
            if os.path.exists(model_path):
                self.model = tf.keras.models.load_model(model_path)
                logger.info("Eye confidence model loaded successfully")
            else:
                # Try alternative model file
                alt_model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Models', 'Eye', 'model.keras')
                if os.path.exists(alt_model_path):
                    self.model = tf.keras.models.load_model(alt_model_path)
                    logger.info("Eye confidence model (keras format) loaded successfully")
                else:
                    logger.error(f"Model file not found: {model_path}")
        except Exception as e:
            logger.error(f"Error loading eye confidence model: {e}")
    
    def load_cascades(self):
        """Load OpenCV cascade classifiers"""
        try:
            # Face cascade
            face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
            
            # Eye cascade
            eye_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
            self.eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
            
            logger.info("Eye and face cascades loaded successfully")
        except Exception as e:
            logger.error(f"Error loading cascades: {e}")
    
    def detect_eyes(self, frame):
        """Detect eyes in frame"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces first
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) == 0:
                return []
            
            eyes_data = []
            
            for (x, y, w, h) in faces:
                # Region of interest (face area)
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]
                
                # Detect eyes within the face
                eyes = self.eye_cascade.detectMultiScale(roi_gray)
                
                for (ex, ey, ew, eh) in eyes:
                    # Adjust coordinates to full frame
                    eye_x = x + ex
                    eye_y = y + ey
                    
                    # Extract eye region
                    eye_region = gray[eye_y:eye_y+eh, eye_x:eye_x+ew]
                    
                    eyes_data.append({
                        'region': eye_region,
                        'coordinates': (eye_x, eye_y, ew, eh),
                        'face_region': (x, y, w, h)
                    })
            
            return eyes_data
            
        except Exception as e:
            logger.error(f"Error detecting eyes: {e}")
            return []
    
    def preprocess_eye(self, eye_region):
        """Preprocess eye region for model prediction"""
        try:
            # Resize to model input size (assuming 64x64 based on common eye models)
            eye_resized = cv2.resize(eye_region, (64, 64))
            
            # Normalize
            eye_normalized = eye_resized / 255.0
            
            # Add batch and channel dimensions
            eye_batch = np.expand_dims(eye_normalized, axis=0)
            eye_batch = np.expand_dims(eye_batch, axis=-1)
            
            return eye_batch
            
        except Exception as e:
            logger.error(f"Error preprocessing eye: {e}")
            return None
    
    def analyze_gaze_direction(self, eye_region):
        """Analyze gaze direction from eye region"""
        try:
            # Simple gaze analysis based on pupil position
            # This is a simplified approach - more sophisticated methods exist
            
            # Apply threshold to find dark regions (pupil)
            _, thresh = cv2.threshold(eye_region, 50, 255, cv2.THRESH_BINARY_INV)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Find largest contour (likely pupil)
                largest_contour = max(contours, key=cv2.contourArea)
                
                # Get centroid
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    
                    # Determine gaze direction based on pupil position
                    eye_center_x = eye_region.shape[1] // 2
                    eye_center_y = eye_region.shape[0] // 2
                    
                    # Calculate relative position
                    rel_x = (cx - eye_center_x) / eye_center_x
                    rel_y = (cy - eye_center_y) / eye_center_y
                    
                    # Classify gaze direction
                    if abs(rel_x) < 0.3 and abs(rel_y) < 0.3:
                        return 'center'  # Confident gaze
                    elif rel_x < -0.3:
                        return 'left'
                    elif rel_x > 0.3:
                        return 'right'
                    else:
                        return 'vertical'  # Up or down
            
            return 'unknown'
            
        except Exception as e:
            logger.error(f"Error analyzing gaze: {e}")
            return 'unknown'
    
    def detect_confidence(self, frame):
        """Detect confidence level from eye behavior"""
        try:
            if self.model is None or self.eye_cascade is None:
                return {'confidence_level': 'unknown', 'confidence': 0.0}
            
            eyes_data = self.detect_eyes(frame)
            
            if not eyes_data:
                return {'confidence_level': 'no_eyes_detected', 'confidence': 0.0}
            
            confidence_scores = []
            gaze_directions = []
            
            for eye_data in eyes_data:
                eye_region = eye_data['region']
                
                # Preprocess for model
                eye_input = self.preprocess_eye(eye_region)
                if eye_input is not None:
                    # Make prediction
                    prediction = self.model.predict(eye_input, verbose=0)
                    confidence_scores.append(float(prediction[0][0]))
                
                # Analyze gaze direction
                gaze_direction = self.analyze_gaze_direction(eye_region)
                gaze_directions.append(gaze_direction)
            
            if confidence_scores:
                # Calculate overall confidence
                avg_model_confidence = np.mean(confidence_scores)
                
                # Factor in gaze direction
                center_gaze_count = gaze_directions.count('center')
                gaze_confidence = center_gaze_count / len(gaze_directions)
                
                # Combine model prediction and gaze analysis
                overall_confidence = (avg_model_confidence * 0.7) + (gaze_confidence * 0.3)
                
                if overall_confidence > 0.5:
                    confidence_level = 'confident'
                    confidence = overall_confidence
                else:
                    confidence_level = 'not_confident'
                    confidence = 1.0 - overall_confidence
                
                return {
                    'confidence_level': confidence_level,
                    'confidence': confidence,
                    'eyes_detected': len(eyes_data),
                    'gaze_directions': gaze_directions,
                    'dominant_gaze': max(set(gaze_directions), key=gaze_directions.count) if gaze_directions else 'unknown'
                }
            
            return {'confidence_level': 'processing_error', 'confidence': 0.0}
            
        except Exception as e:
            logger.error(f"Error detecting eye confidence: {e}")
            return {'confidence_level': 'error', 'confidence': 0.0}
