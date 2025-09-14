"""
Test script for the Enhanced Eye Model (no dlib dependency)
"""
import cv2
import numpy as np
import logging
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(__file__))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_enhanced_eye_model():
    """Test the enhanced eye model"""
    try:
        logger.info("=== Testing Enhanced Eye Model (No dlib) ===")
        
        # Import the enhanced eye model
        from model.enhanced_eye_model import EnhancedEyeConfidenceDetector
        
        # Initialize the detector
        logger.info("Initializing enhanced eye detector...")
        detector = EnhancedEyeConfidenceDetector()
        
        # Get model info
        model_info = detector.get_model_info()
        logger.info("Model Info:")
        for key, value in model_info.items():
            logger.info(f"  {key}: {value}")
        
        # Create a test frame (dummy image)
        logger.info("Creating test frame...")
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        test_frame[:] = (128, 128, 128)  # Gray background
        
        # Add some simple shapes to simulate a face
        cv2.rectangle(test_frame, (200, 150), (440, 350), (255, 255, 255), -1)  # Face
        cv2.circle(test_frame, (280, 220), 20, (0, 0, 0), -1)  # Left eye
        cv2.circle(test_frame, (360, 220), 20, (0, 0, 0), -1)  # Right eye
        cv2.ellipse(test_frame, (320, 280), (30, 15), 0, 0, 180, (0, 0, 0), 2)  # Mouth
        
        # Test detection
        logger.info("Testing eye confidence detection...")
        result = detector.detect_confidence(test_frame)
        
        logger.info("Detection Result:")
        for key, value in result.items():
            if key == 'eye_analysis' and isinstance(value, list):
                logger.info(f"  {key}:")
                for i, eye_data in enumerate(value):
                    logger.info(f"    Eye {i+1}:")
                    for eye_key, eye_value in eye_data.items():
                        logger.info(f"      {eye_key}: {eye_value}")
            else:
                logger.info(f"  {key}: {value}")
        
        # Test base64 detection
        logger.info("Testing base64 detection...")
        _, buffer = cv2.imencode('.jpg', test_frame)
        import base64
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        result_base64 = detector.detect_confidence_from_base64(frame_base64)
        logger.info("Base64 Detection Result:")
        for key, value in result_base64.items():
            if key == 'eye_analysis' and isinstance(value, list):
                logger.info(f"  {key}:")
                for i, eye_data in enumerate(value):
                    logger.info(f"    Eye {i+1}:")
                    for eye_key, eye_value in eye_data.items():
                        logger.info(f"      {eye_key}: {eye_value}")
            else:
                logger.info(f"  {key}: {value}")
        
        logger.info("✅ Enhanced eye model test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing enhanced eye model: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_eye_model_integration():
    """Test the main eye model integration"""
    try:
        logger.info("=== Testing Main Eye Model Integration ===")
        
        # Import the main eye model
        from model.eye_model import EyeConfidenceDetector
        
        # Initialize the detector
        logger.info("Initializing main eye detector...")
        detector = EyeConfidenceDetector()
        
        # Get model info
        model_info = detector.get_model_info()
        logger.info("Main Model Info:")
        for key, value in model_info.items():
            logger.info(f"  {key}: {value}")
        
        # Create a test frame
        logger.info("Creating test frame...")
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        test_frame[:] = (128, 128, 128)  # Gray background
        
        # Add some simple shapes to simulate a face
        cv2.rectangle(test_frame, (200, 150), (440, 350), (255, 255, 255), -1)  # Face
        cv2.circle(test_frame, (280, 220), 20, (0, 0, 0), -1)  # Left eye
        cv2.circle(test_frame, (360, 220), 20, (0, 0, 0), -1)  # Right eye
        cv2.ellipse(test_frame, (320, 280), (30, 15), 0, 0, 180, (0, 0, 0), 2)  # Mouth
        
        # Test detection
        logger.info("Testing main eye confidence detection...")
        result = detector.detect_confidence(test_frame)
        
        logger.info("Main Detection Result:")
        for key, value in result.items():
            if key == 'eye_analysis' and isinstance(value, list):
                logger.info(f"  {key}:")
                for i, eye_data in enumerate(value):
                    logger.info(f"    Eye {i+1}:")
                    for eye_key, eye_value in eye_data.items():
                        logger.info(f"      {eye_key}: {eye_value}")
            else:
                logger.info(f"  {key}: {value}")
        
        logger.info("✅ Main eye model integration test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing main eye model integration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("Starting Enhanced Eye Model Tests (No dlib required)...")
    
    # Test enhanced model directly
    enhanced_success = test_enhanced_eye_model()
    
    # Test main model integration
    main_success = test_main_eye_model_integration()
    
    if enhanced_success and main_success:
        logger.info("🎉 All tests passed successfully!")
        logger.info("✅ Enhanced eye model is working without dlib dependency!")
    else:
        logger.error("❌ Some tests failed!")
        sys.exit(1)
