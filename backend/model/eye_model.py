"""
Eye Confidence Detection Model for InsightHire
Uses Hybrid approach: Gaze Tracking (Primary) -> TensorFlow (Secondary) -> Fallback (Tertiary)
"""
import cv2
import numpy as np
import os
import logging
from datetime import datetime

# Import the enhanced eye detector (no dlib dependency)
try:
    from .enhanced_eye_model import EnhancedEyeConfidenceDetector
except ImportError:
    from enhanced_eye_model import EnhancedEyeConfidenceDetector

logger = logging.getLogger(__name__)

class EyeConfidenceDetector:
    def __init__(self):
        # Use the enhanced eye detector (no dlib dependency)
        self.enhanced_detector = EnhancedEyeConfidenceDetector()
        logger.info("✅ Enhanced eye confidence detector initialized")
    
    def load_model(self):
        """Load the eye confidence model (delegated to enhanced detector)"""
        return self.enhanced_detector.load_tensorflow_model()
    
    def load_cascades(self):
        """Load face and eye detection cascades (delegated to enhanced detector)"""
        return self.enhanced_detector.load_cascades()
    
    def detect_confidence(self, frame):
        """Detect eye confidence from frame using enhanced approach"""
        return self.enhanced_detector.detect_confidence(frame)
    
    def _advanced_detection(self, frame):
        """Advanced eye detection using ML model (delegated to enhanced detector)"""
        return self.enhanced_detector._tensorflow_detection(frame)
    
    def detect_confidence_from_base64(self, frame_data):
        """Detect confidence from base64 encoded frame"""
        return self.enhanced_detector.detect_confidence_from_base64(frame_data)
    
    def is_available(self):
        """Check if the model is available"""
        return self.enhanced_detector.is_available()
    
    def get_model_info(self):
        """Get information about the loaded model"""
        return self.enhanced_detector.get_model_info()
