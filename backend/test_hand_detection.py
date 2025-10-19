#!/usr/bin/env python3
"""
Test hand detection to see detailed logs
"""

import cv2
import numpy as np
from model.hand_model import HandConfidenceDetector
import logging

# Set up logging to see all debug messages
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')

def test_hand_detection():
    """Test hand detection with a sample frame"""
    print("🔍 Testing hand detection...")
    
    # Initialize detector
    detector = HandConfidenceDetector()
    
    # Try to capture a real frame from camera
    cap = cv2.VideoCapture(0)
    ret, test_frame = cap.read()
    cap.release()
    
    if not ret:
        print("⚠️ Could not capture from camera, creating test frame...")
        # Create a more realistic test frame
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        # Add some hand-like shapes in flesh color
        cv2.ellipse(test_frame, (320, 240), (50, 80), 0, 0, 360, (200, 180, 160), -1)  # Hand-like ellipse
        cv2.ellipse(test_frame, (200, 200), (40, 60), 15, 0, 360, (200, 180, 160), -1)  # Another hand
    else:
        print("✅ Captured real frame from camera")
    
    print("📊 Running hand detection on test frame...")
    print(f"📏 Frame shape: {test_frame.shape}")
    
    # Run detection
    result = detector.detect_confidence(test_frame)
    
    print("🎯 Detection Result:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    # Save test frame for debugging
    cv2.imwrite("debug_test_frame.jpg", test_frame)
    print("💾 Saved test frame as 'debug_test_frame.jpg'")
    
    return result

if __name__ == "__main__":
    test_hand_detection()