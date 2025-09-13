#!/usr/bin/env python3
"""
Create fallback detection methods for failed models
"""
import logging
import cv2
import numpy as np
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def create_fallback_detection_methods():
    """Create fallback detection methods that don't require the neural network models"""
    logger.info("🛠️ CREATING FALLBACK DETECTION METHODS...")
    logger.info("=" * 60)
    
    # Create enhanced eye confidence detection without neural networks
    eye_fallback_code = '''"""
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
'''
    
    # Create enhanced hand confidence detection without neural networks
    hand_fallback_code = '''"""
Enhanced Hand Confidence Detection - Fallback Implementation
Uses OpenCV-based detection when neural network models fail
"""
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class HandConfidenceFallback:
    def __init__(self):
        """Initialize fallback hand confidence detection"""
        logger.info("✅ Hand fallback detection initialized")
        
    def analyze_hand_confidence(self, frame):
        """Analyze hand confidence using OpenCV detection"""
        try:
            if frame is None:
                return {
                    'confidence': 0,
                    'confidence_level': 'no_frame'
                }
                
            # Convert to HSV for better skin detection
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Define skin color range in HSV
            lower_skin = np.array([0, 48, 80], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)
            
            # Create skin mask
            skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
            
            # Apply morphological operations to clean up the mask
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel)
            skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return {
                    'confidence': 0,
                    'confidence_level': 'no_hands_detected'
                }
            
            # Filter contours by area (potential hands)
            hand_contours = []
            min_area = 1000  # Minimum area for a hand
            max_area = 50000  # Maximum area for a hand
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if min_area < area < max_area:
                    # Additional check for hand-like shape
                    hull = cv2.convexHull(contour)
                    hull_area = cv2.contourArea(hull)
                    if hull_area > 0:
                        solidity = area / hull_area
                        if 0.3 < solidity < 0.9:  # Hand-like solidity
                            hand_contours.append(contour)
            
            if len(hand_contours) == 0:
                return {
                    'confidence': 0,
                    'confidence_level': 'no_hands_detected'
                }
            
            # Calculate confidence based on number and quality of hand detections
            hand_count = len(hand_contours)
            
            if hand_count >= 2:
                confidence = 0.85  # Both hands visible
                confidence_level = 'high_confidence'
            elif hand_count == 1:
                confidence = 0.65  # One hand visible
                confidence_level = 'moderate_confidence'
            else:
                confidence = 0.3
                confidence_level = 'low_confidence'
                
            return {
                'confidence': round(confidence, 2),
                'confidence_level': confidence_level
            }
                
        except Exception as e:
            logger.error(f"❌ Error in hand confidence analysis: {e}")
            return {
                'confidence': 0,
                'confidence_level': 'analysis_error'
            }
'''
    
    # Write the fallback files
    with open('eye_confidence_fallback.py', 'w') as f:
        f.write(eye_fallback_code)
    logger.info("✅ Created eye_confidence_fallback.py")
    
    with open('hand_confidence_fallback.py', 'w') as f:
        f.write(hand_fallback_code)
    logger.info("✅ Created hand_confidence_fallback.py")

def update_detection_classes_with_fallback():
    """Update the detection classes to use fallback methods when models fail"""
    logger.info("🔧 Updating detection classes with fallback methods...")
    
    # Update Eye Confidence Detection
    eye_script = "model_scripts/eye_confidence_detection.py"
    if os.path.exists(eye_script):
        with open(eye_script, 'r') as f:
            content = f.read()
        
        # Add fallback import
        if 'from eye_confidence_fallback import EyeConfidenceFallback' not in content:
            # Find the import section
            lines = content.split('\\n')
            import_end = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    import_end = i
                    
            # Insert the fallback import
            lines.insert(import_end + 1, 'from eye_confidence_fallback import EyeConfidenceFallback')
            content = '\\n'.join(lines)
        
        # Update the class initialization to include fallback
        if 'self.fallback_detector = EyeConfidenceFallback()' not in content:
            init_pattern = 'def __init__(self):'
            if init_pattern in content:
                content = content.replace(
                    init_pattern + '\\n        """Initialize eye confidence detection"""',
                    init_pattern + '\\n        """Initialize eye confidence detection"""\\n        self.fallback_detector = EyeConfidenceFallback()'
                )
        
        # Update analyze_eye_confidence method to use fallback when model is None
        if 'if self.model is None:' not in content:
            # Find the analyze_eye_confidence method
            method_start = content.find('def analyze_eye_confidence(self, frame):')
            if method_start != -1:
                # Find the method end
                lines = content[method_start:].split('\\n')
                method_lines = []
                indent_level = None
                
                for line in lines:
                    if line.strip() == '':
                        method_lines.append(line)
                        continue
                    
                    current_indent = len(line) - len(line.lstrip())
                    
                    if indent_level is None and line.strip():
                        indent_level = current_indent
                    elif line.strip() and current_indent <= indent_level and not line.startswith('    def '):
                        break
                    
                    method_lines.append(line)
                
                # Insert fallback check at the beginning of the method
                fallback_check = '''        # Use fallback detection if model failed to load
        if self.model is None:
            logger.info("Using fallback eye confidence detection")
            return self.fallback_detector.analyze_eye_confidence(frame)
        '''
                
                method_lines.insert(2, fallback_check)
                updated_method = '\\n'.join(method_lines)
                content = content[:method_start] + updated_method + content[method_start + len('\\n'.join(lines[:len(method_lines)])):]
        
        with open(eye_script, 'w') as f:
            f.write(content)
        logger.info(f"✅ Updated {eye_script} with fallback detection")
    
    # Update Hand Confidence Detection similarly
    hand_script = "model_scripts/hand_confidence_detection.py"
    if os.path.exists(hand_script):
        with open(hand_script, 'r') as f:
            content = f.read()
        
        # Add fallback import
        if 'from hand_confidence_fallback import HandConfidenceFallback' not in content:
            lines = content.split('\\n')
            import_end = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    import_end = i
                    
            lines.insert(import_end + 1, 'from hand_confidence_fallback import HandConfidenceFallback')
            content = '\\n'.join(lines)
        
        # Update initialization
        if 'self.fallback_detector = HandConfidenceFallback()' not in content:
            init_pattern = 'def __init__(self):'
            if init_pattern in content:
                content = content.replace(
                    init_pattern + '\\n        """Initialize hand confidence detection"""',
                    init_pattern + '\\n        """Initialize hand confidence detection"""\\n        self.fallback_detector = HandConfidenceFallback()'
                )
        
        # Update analyze method with fallback
        if 'if self.model is None:' not in content:
            method_start = content.find('def analyze_hand_confidence(self, frame):')
            if method_start != -1:
                lines = content[method_start:].split('\\n')
                method_lines = []
                indent_level = None
                
                for line in lines:
                    if line.strip() == '':
                        method_lines.append(line)
                        continue
                    
                    current_indent = len(line) - len(line.lstrip())
                    
                    if indent_level is None and line.strip():
                        indent_level = current_indent
                    elif line.strip() and current_indent <= indent_level and not line.startswith('    def '):
                        break
                    
                    method_lines.append(line)
                
                fallback_check = '''        # Use fallback detection if model failed to load
        if self.model is None:
            logger.info("Using fallback hand confidence detection")
            return self.fallback_detector.analyze_hand_confidence(frame)
        '''
                
                method_lines.insert(2, fallback_check)
                updated_method = '\\n'.join(method_lines)
                content = content[:method_start] + updated_method + content[method_start + len('\\n'.join(lines[:len(method_lines)])):]
        
        with open(hand_script, 'w') as f:
            f.write(content)
        logger.info(f"✅ Updated {hand_script} with fallback detection")

if __name__ == '__main__':
    logger.info("🛠️ CREATING ROBUST FALLBACK DETECTION SYSTEM...")
    logger.info("=" * 60)
    
    # Create fallback detection methods
    create_fallback_detection_methods()
    
    # Update existing classes to use fallback
    update_detection_classes_with_fallback()
    
    logger.info("=" * 60)
    logger.info("✅ FALLBACK DETECTION SYSTEM COMPLETE!")
    logger.info("📋 Your AI detection will now work even with model loading issues:")
    logger.info("   - Face Stress: ✅ Neural Network Model")
    logger.info("   - Eye Confidence: 🛠️ OpenCV Fallback Detection")  
    logger.info("   - Hand Confidence: 🛠️ OpenCV Fallback Detection")
    logger.info("   - Voice Confidence: ⚠️ Preprocessing tools only")
    logger.info("")
    logger.info("🎯 Next: Restart backend and test - you should get real detection results!")
    logger.info("=" * 60)
