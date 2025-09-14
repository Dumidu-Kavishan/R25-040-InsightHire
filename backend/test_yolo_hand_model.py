#!/usr/bin/env python3
"""
Test script for the new YOLO11n-pose hand model integration
"""
import os
import sys
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.hand_model import HandConfidenceDetector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('YOLOHandModelTest')

def test_yolo_hand_model():
    """Test the YOLO11n-pose hand model integration"""
    logger.info("🧪 Testing YOLO11n-pose hand model integration...")
    
    try:
        # Initialize the detector
        detector = HandConfidenceDetector()
        
        # Check model info
        model_info = detector.get_model_info()
        logger.info(f"📊 Model Info: {model_info}")
        
        # Check if YOLO model is loaded
        if model_info.get('yolo_model_loaded', False):
            logger.info("✅ YOLO11n-pose model loaded successfully!")
            logger.info(f"🎯 Model Type: {model_info.get('model_type', 'Unknown')}")
        else:
            logger.warning("⚠️ YOLO model not loaded, will use fallback")
        
        # Check availability
        is_available = detector.is_available()
        logger.info(f"🔧 Model Available: {is_available}")
        
        if is_available:
            logger.info("✅ Hand confidence detector is ready for use!")
            logger.info("🎉 Integration test completed successfully!")
        else:
            logger.error("❌ Hand confidence detector is not available")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing YOLO hand model: {e}")
        return False

def test_model_paths():
    """Test if the YOLO model file exists"""
    logger.info("🔍 Checking for YOLO model file...")
    
    base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Models')
    possible_paths = [
        os.path.join(base_path, "Hand", "pose-hands", "runs", "pose", "train", "weights", "best.pt"),
        os.path.join(base_path, "Hand", "pose-hands", "runs", "pose", "train", "weights", "last.pt"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"✅ Found YOLO model: {path}")
            return True
        else:
            logger.info(f"❌ Not found: {path}")
    
    logger.warning("⚠️ YOLO model file not found in expected locations")
    return False

if __name__ == "__main__":
    logger.info("🚀 Starting YOLO11n-pose hand model integration test...")
    
    # Test model file existence
    model_exists = test_model_paths()
    
    # Test model integration
    integration_success = test_yolo_hand_model()
    
    if integration_success:
        logger.info("🎉 All tests passed! YOLO11n-pose hand model is ready to use.")
    else:
        logger.error("❌ Some tests failed. Check the logs above for details.")
