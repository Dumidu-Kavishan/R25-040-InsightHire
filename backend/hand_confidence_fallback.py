"""
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
