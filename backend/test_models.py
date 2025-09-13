#!/usr/bin/env python3
"""
Test script to verify all models are working with the RealTimeAnalyzer
"""
import cv2
import numpy as np
import time
import logging
from realtime_analyzer import RealTimeAnalyzer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_models():
    """Test all models with the RealTimeAnalyzer"""
    
    # Create analyzer instance
    analyzer = RealTimeAnalyzer("test-interview-123", "test-user-123")
    
    # Start analysis
    analyzer.start_analysis()
    logger.info("✅ Analyzer started")
    
    # Create a test frame (640x480 RGB)
    test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Add some basic shapes to make it more realistic
    cv2.rectangle(test_frame, (200, 150), (400, 350), (255, 255, 255), -1)  # Face area
    cv2.circle(test_frame, (250, 200), 20, (0, 0, 0), -1)  # Left eye
    cv2.circle(test_frame, (350, 200), 20, (0, 0, 0), -1)  # Right eye
    cv2.rectangle(test_frame, (280, 250), (320, 280), (0, 0, 0), -1)  # Mouth
    
    logger.info(f"📹 Created test frame: {test_frame.shape}")
    
    # Send multiple frames to trigger analysis
    for i in range(5):
        logger.info(f"📤 Sending frame {i+1}/5...")
        analyzer.add_video_frame(test_frame)
        time.sleep(1)  # Wait a bit between frames
    
    # Wait for analysis to complete
    time.sleep(5)
    
    # Get results
    results = analyzer.get_latest_results()
    logger.info("📊 Analysis Results:")
    logger.info(f"   Face Stress: {results.get('face_stress', {})}")
    logger.info(f"   Hand Confidence: {results.get('hand_confidence', {})}")
    logger.info(f"   Eye Confidence: {results.get('eye_confidence', {})}")
    logger.info(f"   Voice Confidence: {results.get('voice_confidence', {})}")
    
    # Stop analyzer
    analyzer.stop_analysis()
    logger.info("⏹️ Analyzer stopped")
    
    return results

if __name__ == "__main__":
    logger.info("🚀 Starting model testing...")
    try:
        results = test_models()
        logger.info("✅ Model testing completed successfully!")
        
        # Check if we got valid results
        valid_results = 0
        for key in ['face_stress', 'hand_confidence', 'eye_confidence', 'voice_confidence']:
            if key in results and isinstance(results[key], dict):
                confidence = results[key].get('confidence', 0)
                if confidence > 0:
                    valid_results += 1
                    logger.info(f"✅ {key}: Valid result with confidence {confidence}")
                else:
                    logger.warning(f"⚠️ {key}: Low or zero confidence")
            else:
                logger.error(f"❌ {key}: No valid result")
        
        logger.info(f"📈 Summary: {valid_results}/4 models returned valid results")
        
    except Exception as e:
        logger.error(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
