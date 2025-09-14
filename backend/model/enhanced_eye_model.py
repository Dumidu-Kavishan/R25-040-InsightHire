"""
Enhanced Eye Confidence Detection Model for InsightHire
Alternative implementation without dlib dependency
Uses advanced OpenCV techniques for better eye detection
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

class EnhancedEyeConfidenceDetector:
    def __init__(self):
        self.tensorflow_model = None
        self.fallback_detector = FallbackEyeDetector()
        self.face_cascade = None
        self.eye_cascade = None
        self.model_loaded = False
        self.cascades_loaded = False
        
        # Get current working directory for model paths
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.base_path = os.path.join(current_dir, 'Models')
        
        # Initialize components
        self.load_tensorflow_model()
        self.load_cascades()
        
        # Log initialization status
        self.log_initialization_status()
    
    def load_tensorflow_model(self):
        """Load the TensorFlow model"""
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
        logger.info("=== Enhanced Eye Model Initialization Status ===")
        logger.info("TensorFlow Model: %s", '✅' if self.model_loaded else '❌')
        logger.info("OpenCV Cascades: %s", '✅' if self.cascades_loaded else '❌')
        logger.info("Fallback Detector: ✅ (always available)")
        
        if not any([self.model_loaded, self.cascades_loaded]):
            logger.warning("⚠️ All primary detection methods failed - using fallback only")
    
    def detect_confidence(self, frame):
        """Detect eye confidence using enhanced approach"""
        try:
            # Method 1: Try Enhanced OpenCV Detection (Primary)
            if self.cascades_loaded:
                result = self._enhanced_opencv_detection(frame)
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
            logger.error(f"Error in enhanced eye confidence detection: {e}")
            return self.fallback_detector.detect_confidence(frame)
    
    def _enhanced_opencv_detection(self, frame):
        """Enhanced eye detection using advanced OpenCV techniques"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Enhanced face detection with multiple scales
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            if len(faces) == 0:
                return None  # Fall back to next method
            
            # Process the largest face
            face = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = face
            
            # Extract face region
            face_roi = gray[y:y+h, x:x+w]
            
            # Enhanced eye detection with multiple parameters
            eyes = self.eye_cascade.detectMultiScale(
                face_roi,
                scaleFactor=1.1,
                minNeighbors=3,
                minSize=(15, 15),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            if len(eyes) == 0:
                return None  # Fall back to next method
            
            # Analyze eye regions for confidence
            eye_analysis = self._analyze_eye_regions(face_roi, eyes)
            
            if eye_analysis is None:
                return None  # Fall back to next method
            
            # Calculate confidence based on eye analysis
            confidence_score = self._calculate_enhanced_confidence(eye_analysis)
            
            # Determine confidence level
            if confidence_score > 0.7:
                confidence_level = 'confident'
            elif confidence_score > 0.4:
                confidence_level = 'somewhat_confident'
            else:
                confidence_level = 'not_confident'
            
            return {
                'confidence_level': confidence_level,
                'confidence': float(confidence_score),
                'eyes_detected': len(eyes),
                'method': 'enhanced_opencv_detection',
                'eye_analysis': eye_analysis,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Enhanced OpenCV detection error: {e}")
            return None
    
    def _analyze_eye_regions(self, face_roi, eyes):
        """Analyze eye regions for quality and characteristics"""
        try:
            eye_metrics = []
            
            for (ex, ey, ew, eh) in eyes:
                # Extract eye region
                eye_roi = face_roi[ey:ey+eh, ex:ex+ew]
                
                # Calculate eye metrics
                metrics = {}
                
                # 1. Eye size and aspect ratio
                metrics['area'] = ew * eh
                metrics['aspect_ratio'] = ew / eh if eh > 0 else 0
                
                # 2. Eye brightness and contrast
                metrics['brightness'] = np.mean(eye_roi)
                metrics['contrast'] = np.std(eye_roi)
                
                # 3. Eye symmetry (if we have both eyes)
                if len(eyes) >= 2:
                    # Calculate symmetry between eyes
                    other_eyes = [e for e in eyes if not np.array_equal(e, (ex, ey, ew, eh))]
                    if other_eyes:
                        other_eye = other_eyes[0]
                        other_roi = face_roi[other_eye[1]:other_eye[1]+other_eye[3], 
                                           other_eye[0]:other_eye[0]+other_eye[2]]
                        metrics['symmetry'] = self._calculate_symmetry(eye_roi, other_roi)
                    else:
                        metrics['symmetry'] = 0.5
                else:
                    metrics['symmetry'] = 0.5
                
                # 4. Eye sharpness (edge detection)
                edges = cv2.Canny(eye_roi, 50, 150)
                metrics['sharpness'] = np.sum(edges) / (ew * eh)
                
                # 5. Eye openness (pupil detection)
                metrics['openness'] = self._calculate_eye_openness(eye_roi)
                
                eye_metrics.append(metrics)
            
            return eye_metrics
            
        except Exception as e:
            logger.error(f"Error analyzing eye regions: {e}")
            return None
    
    def _calculate_symmetry(self, eye1, eye2):
        """Calculate symmetry between two eye regions"""
        try:
            # Resize both eyes to same size
            size = (min(eye1.shape[1], eye2.shape[1]), min(eye1.shape[0], eye2.shape[0]))
            eye1_resized = cv2.resize(eye1, size)
            eye2_resized = cv2.resize(eye2, size)
            
            # Calculate difference
            diff = cv2.absdiff(eye1_resized, eye2_resized)
            symmetry_score = 1.0 - (np.mean(diff) / 255.0)
            
            return max(0.0, min(1.0, symmetry_score))
            
        except Exception as e:
            logger.error(f"Error calculating symmetry: {e}")
            return 0.5
    
    def _calculate_eye_openness(self, eye_roi):
        """Calculate how open the eye is"""
        try:
            # Use threshold to detect pupil
            _, thresh = cv2.threshold(eye_roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return 0.5
            
            # Find largest contour (likely pupil)
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            total_area = eye_roi.shape[0] * eye_roi.shape[1]
            
            # Calculate openness ratio
            openness_ratio = area / total_area
            
            # Map to 0-1 scale (lower ratio = more open)
            openness_score = max(0.0, min(1.0, 1.0 - openness_ratio * 2))
            
            return openness_score
            
        except Exception as e:
            logger.error(f"Error calculating eye openness: {e}")
            return 0.5
    
    def _calculate_enhanced_confidence(self, eye_analysis):
        """Calculate confidence score based on enhanced eye analysis"""
        try:
            if not eye_analysis:
                return 0.0
            
            # Base confidence
            base_confidence = 0.6
            
            # Analyze each eye
            for eye_metrics in eye_analysis:
                # Eye size bonus (reasonable size)
                if 200 < eye_metrics['area'] < 2000:
                    base_confidence += 0.1
                
                # Aspect ratio bonus (eye-like proportions)
                if 0.8 < eye_metrics['aspect_ratio'] < 2.5:
                    base_confidence += 0.05
                
                # Brightness bonus (good lighting)
                if 50 < eye_metrics['brightness'] < 200:
                    base_confidence += 0.05
                
                # Contrast bonus (clear features)
                if eye_metrics['contrast'] > 20:
                    base_confidence += 0.05
                
                # Symmetry bonus
                if eye_metrics['symmetry'] > 0.7:
                    base_confidence += 0.1
                
                # Sharpness bonus
                if eye_metrics['sharpness'] > 0.1:
                    base_confidence += 0.05
                
                # Openness bonus
                if eye_metrics['openness'] > 0.6:
                    base_confidence += 0.1
            
            # Cap confidence
            return max(0.0, min(1.0, base_confidence))
            
        except Exception as e:
            logger.error(f"Error calculating enhanced confidence: {e}")
            return 0.5
    
    def _tensorflow_detection(self, frame):
        """TensorFlow model detection (same as hybrid model)"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
            
            if len(faces) == 0:
                return None
            
            face = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = face
            face_roi = gray[y:y+h, x:x+w]
            
            eyes = self.eye_cascade.detectMultiScale(face_roi, 1.1, 5)
            
            if len(eyes) == 0:
                return None
            
            eye_confidences = []
            for (ex, ey, ew, eh) in eyes:
                eye_roi = face_roi[ey:ey+eh, ex:ex+ew]
                
                try:
                    eye_resized = cv2.resize(eye_roi, (64, 64))
                    eye_normalized = eye_resized.astype(np.float32) / 255.0
                    eye_input = np.expand_dims(np.expand_dims(eye_normalized, axis=0), axis=-1)
                    
                    prediction = self.tensorflow_model.predict(eye_input, verbose=0)
                    confidence_score = float(prediction[0][0])
                    eye_confidences.append(confidence_score)
                    
                except Exception as e:
                    logger.warning(f"Error processing eye region with TensorFlow: {e}")
                    continue
            
            if not eye_confidences:
                return None
            
            overall_confidence = np.mean(eye_confidences)
            
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
            'tensorflow_available': TENSORFLOW_AVAILABLE,
            'tensorflow_model_loaded': self.model_loaded,
            'cascades_loaded': self.cascades_loaded,
            'fallback_available': True,
            'base_path': self.base_path,
            'enhanced_features': True
        }
