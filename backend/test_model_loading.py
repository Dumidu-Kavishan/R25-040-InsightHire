#!/usr/bin/env python3
"""
Test AI model loading with fixed paths
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def test_model_loading():
    """Test loading all AI models"""
    logger.info("🧪 TESTING AI MODEL LOADING...")
    logger.info("=" * 50)
    
    try:
        # Test Face Stress Detection
        logger.info("📊 Testing Face Stress Detection...")
        from model_scripts.face_stress_detection import FaceStressDetector
        face_detector = FaceStressDetector()
        logger.info("✅ Face Stress Detection: LOADED")
        
    except Exception as e:
        logger.error(f"❌ Face Stress Detection: FAILED - {e}")
        
    try:
        # Test Eye Confidence Detection
        logger.info("👁️ Testing Eye Confidence Detection...")
        from model_scripts.eye_confidence_detection import EyeConfidenceDetector
        eye_detector = EyeConfidenceDetector()
        logger.info("✅ Eye Confidence Detection: LOADED")
        
    except Exception as e:
        logger.error(f"❌ Eye Confidence Detection: FAILED - {e}")
        
    try:
        # Test Hand Confidence Detection
        logger.info("✋ Testing Hand Confidence Detection...")
        from model_scripts.hand_confidence_detection import HandConfidenceDetector
        hand_detector = HandConfidenceDetector()
        logger.info("✅ Hand Confidence Detection: LOADED")
        
    except Exception as e:
        logger.error(f"❌ Hand Confidence Detection: FAILED - {e}")
        
    try:
        # Test Voice Confidence Detection
        logger.info("🎤 Testing Voice Confidence Detection...")
        from model_scripts.voice_confidence_detection import VoiceConfidenceDetector
        voice_detector = VoiceConfidenceDetector()
        logger.info("✅ Voice Confidence Detection: LOADED")
        
    except Exception as e:
        logger.error(f"❌ Voice Confidence Detection: FAILED - {e}")
        
    logger.info("=" * 50)
    logger.info("🎯 MODEL LOADING TEST COMPLETE!")
    logger.info("✅ If all models loaded successfully, your AI detection should work!")
    
if __name__ == '__main__':
    test_model_loading()
