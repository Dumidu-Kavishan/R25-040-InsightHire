#!/usr/bin/env python3
"""
Test the ONNX models directly using the original HaGRID methodology
"""

import cv2
import numpy as np
import os
import sys

# Import our classes
sys.path.append(os.path.dirname(__file__))
from model.hand_model import DynamicGesturesDetector

def test_with_hand_visible():
    """Test detection with a frame where user can put their hand in view"""
    print("🔍 Testing hand detection with live camera...")
    print("👋 Please put your hand in front of the camera and move it around")
    
    detector = DynamicGesturesDetector()
    
    # Open camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return
    
    print("📹 Camera opened. Press 'q' to quit, 's' to take snapshot test")
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Test every 30 frames (about once per second)
        if frame_count % 30 == 0:
            print(f"\n🎥 Testing frame {frame_count}...")
            result = detector.detect_confidence(frame)
            print(f"📊 Result: {result['confidence_level']} (conf: {result['confidence']:.2f})")
            if result['hands_detected'] > 0:
                print(f"👐 Hands detected: {result['hands_detected']}")
                print(f"🎯 Gestures: {result['gestures_detected']}")
        
        # Show the frame
        cv2.putText(frame, f"Frame: {frame_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "Put your hand in view! Press 'q' to quit", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow('Hand Detection Test', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            print(f"\n📸 Taking snapshot test...")
            result = detector.detect_confidence(frame)
            print(f"📊 Snapshot result:")
            for k, v in result.items():
                print(f"  {k}: {v}")
    
    cap.release()
    cv2.destroyAllWindows()

def test_synthetic_hands():
    """Test with synthetic hand-like shapes"""
    print("🔍 Testing with synthetic hand shapes...")
    
    detector = DynamicGesturesDetector()
    
    # Create a frame with hand-like shapes
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Add background noise to make it more realistic
    noise = np.random.randint(0, 50, (480, 640, 3), dtype=np.uint8)
    frame += noise
    
    # Draw hand-like shapes in skin color
    skin_color = (200, 180, 160)  # BGR format
    
    # Hand 1: Palm-like ellipse
    cv2.ellipse(frame, (200, 200), (60, 80), 0, 0, 360, skin_color, -1)
    # Fingers
    cv2.rectangle(frame, (170, 120), (190, 200), skin_color, -1)  # thumb
    cv2.rectangle(frame, (185, 100), (205, 180), skin_color, -1)  # index
    cv2.rectangle(frame, (200, 90), (220, 170), skin_color, -1)   # middle
    cv2.rectangle(frame, (215, 100), (235, 180), skin_color, -1)  # ring
    cv2.rectangle(frame, (225, 110), (245, 170), skin_color, -1)  # pinky
    
    # Hand 2: Different position
    cv2.ellipse(frame, (450, 300), (50, 70), 15, 0, 360, skin_color, -1)
    
    # Save for debugging
    cv2.imwrite("synthetic_hands_test.jpg", frame)
    
    print("📊 Testing synthetic hands...")
    result = detector.detect_confidence(frame)
    
    print(f"📊 Synthetic hands result:")
    for k, v in result.items():
        print(f"  {k}: {v}")
    
    # Show the frame
    cv2.imshow('Synthetic Hands Test', frame)
    cv2.waitKey(3000)  # Show for 3 seconds
    cv2.destroyAllWindows()

if __name__ == "__main__":
    print("🤖 ONNX Hand Detection Test Suite")
    print("=" * 50)
    
    # Test 1: Synthetic hands
    test_synthetic_hands()
    
    print("\n" + "=" * 50)
    
    # Test 2: Live camera
    test_with_hand_visible()