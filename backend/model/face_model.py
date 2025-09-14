"""
Face Stress Detection Model for InsightHire
Based on EDUGuard pattern with enhanced error handling
"""
import cv2
import numpy as np
import os
import logging
from datetime import datetime

# Try to import tensorflow and other dependencies
try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    tf = None

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False
    joblib = None

# Import fallback models
try:
    from .fallback_models import FallbackFaceDetector
except ImportError:
    from fallback_models import FallbackFaceDetector

logger = logging.getLogger(__name__)

# Import the improved face detection script
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'model_scripts'))

try:
    from face_stress_detection import FaceStressDetector as ImprovedFaceStressDetector
    IMPROVED_MODEL_AVAILABLE = True
except ImportError:
    IMPROVED_MODEL_AVAILABLE = False
    ImprovedFaceStressDetector = None

logger = logging.getLogger(__name__)

class FaceStressDetector:
    def __init__(self):
        self.fallback_detector = FallbackFaceDetector()
        self.detector = None
        
        # Try to use improved detector, fallback to basic
        if IMPROVED_MODEL_AVAILABLE:
            try:
                self.detector = ImprovedFaceStressDetector()
                logger.info("✅ Face stress detector initialized with improved model")
            except Exception as e:
                logger.warning(f"Failed to load improved model: {e}, using fallback")
                self.detector = None
        else:
            logger.info("🔄 Using fallback face stress detector")
    
    def detect_stress(self, frame):
        """Detect stress level from frame - main interface"""
        if self.detector:
            try:
                return self.detector.detect_stress(frame)
            except Exception as e:
                logger.warning(f"Improved detector failed: {e}, using fallback")
                return self.fallback_detector.detect_stress(frame)
        else:
            return self.fallback_detector.detect_stress(frame)
    
    def detect_stress_from_base64(self, frame_data):
        """Detect stress from base64 encoded frame"""
        if self.detector and hasattr(self.detector, 'detect_stress_from_base64'):
            try:
                return self.detector.detect_stress_from_base64(frame_data)
            except Exception as e:
                logger.warning(f"Base64 detection failed: {e}")
                return {'stress_level': 'error', 'confidence': 0.0, 'error': str(e)}
        else:
            return {'stress_level': 'base64_not_supported', 'confidence': 0.0}
    
    def is_available(self):
        """Check if the model is available"""
        return True  # Always available due to fallback
    
    def get_model_info(self):
        """Get information about the loaded model"""
        return {
            'improved_model_available': IMPROVED_MODEL_AVAILABLE,
            'tensorflow_available': TENSORFLOW_AVAILABLE,
            'fallback_available': True
        }
