"""
Enhanced Eye Confidence Detection - Fallback Implementation
Uses OpenCV-based detection when neural network models fail
"""
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class EyeConfidenceFallback:
    def __init__(self):
        """Initialize fallback eye confidence detection"""
        self.setup_cascades()
        
    def setup_cascades(self):
        """Setup OpenCV cascade classifiers"""
        try:
            # Use OpenCV built-in cascades
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            logger.info("✅ Eye fallback cascades loaded successfully")
        except Exception as e:
            logger.error(f"❌ Error loading cascades: {e}")
            
    def analyze_eye_confidence(self, frame):
        """Analyze eye confidence using OpenCV detection"""
        try:
            if frame is None:
                return {
                    'confidence': 0,
                    'confidence_level': 'no_frame'
                }
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) == 0:
                return {
                    'confidence': 0,
                    'confidence_level': 'no_face_detected'
                }
            
            total_confidence = 0
            eye_count = 0
            
            for (x, y, w, h) in faces:
                # Extract face region
                roi_gray = gray[y:y+h, x:x+w]
                
                # Detect eyes in face region
                eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 10)
                
                if len(eyes) >= 2:
                    # Calculate confidence based on eye pair detection
                    eye_confidence = min(0.9, 0.6 + (len(eyes) * 0.1))
                    total_confidence += eye_confidence
                    eye_count += 1
                elif len(eyes) == 1:
                    # Single eye detected - moderate confidence
                    total_confidence += 0.5
                    eye_count += 1
                    
            if eye_count > 0:
                avg_confidence = total_confidence / eye_count
                if avg_confidence >= 0.8:
                    confidence_level = 'high_confidence'
                elif avg_confidence >= 0.6:
                    confidence_level = 'moderate_confidence'
                elif avg_confidence >= 0.4:
                    confidence_level = 'low_confidence'
                else:
                    confidence_level = 'very_low_confidence'
                    
                return {
                    'confidence': round(avg_confidence, 2),
                    'confidence_level': confidence_level
                }
            else:
                return {
                    'confidence': 0,
                    'confidence_level': 'no_eyes_detected'
                }
                
        except Exception as e:
            logger.error(f"❌ Error in eye confidence analysis: {e}")
            return {
                'confidence': 0,
                'confidence_level': 'analysis_error'
            }
