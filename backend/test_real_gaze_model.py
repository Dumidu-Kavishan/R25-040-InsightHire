#!/usr/bin/env python3
"""
Test script to verify the real gaze tracking model works
Run this in GazeTracking conda environment before starting the server
"""

import sys
import os

# Get the absolute path properly
script_dir = os.path.dirname(os.path.abspath(__file__))  # backend directory
project_root = os.path.dirname(script_dir)  # go up one level to project root
gaze_model_dir = os.path.join(project_root, 'Models', 'Eye', 'eye_train_model', 'gaze_tracking')
sys.path.insert(0, gaze_model_dir)

print("="*60)
print("🔬 TESTING REAL GAZE TRACKING MODEL")
print("="*60)
print(f"📁 Script directory: {script_dir}")
print(f"📁 Project root: {project_root}")
print(f"🎯 Model directory: {gaze_model_dir}")

# Check if directory exists
if not os.path.exists(gaze_model_dir):
    print(f"❌ Model directory does not exist: {gaze_model_dir}")
    sys.exit(1)

# Check if model file exists
model_file = os.path.join(gaze_model_dir, 'trained_models', 'shape_predictor_68_face_landmarks.dat')
print(f"🔍 Looking for model file: {model_file}")

if os.path.exists(model_file):
    print(f"✅ Model file found!")
    file_size = os.path.getsize(model_file) / (1024 * 1024)  # MB
    print(f"📦 Model file size: {file_size:.1f} MB")
else:
    print(f"❌ Model file NOT found!")
    print("🔧 Please ensure the trained model file exists")
    sys.exit(1)

# Test importing the module
print("\n🔄 Testing module import...")
try:
    # Add the parent directory to properly handle the package
    parent_dir = os.path.dirname(gaze_model_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    # Import the gaze_tracking package
    import gaze_tracking
    from gaze_tracking import GazeTracking
    print("✅ GazeTracking imported successfully!")
except ImportError as e:
    print(f"❌ Failed to import GazeTracking: {e}")
    print("🔧 Trying alternative import method...")
    
    try:
        # Try importing the module directly
        import importlib.util
        spec = importlib.util.spec_from_file_location("gaze_tracking_module", 
                                                      os.path.join(gaze_model_dir, "gaze_tracking.py"))
        gaze_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gaze_module)
        GazeTracking = gaze_module.GazeTracking
        print("✅ GazeTracking imported via direct file loading!")
    except Exception as e2:
        print(f"❌ All import methods failed: {e2}")
        sys.exit(1)

# Test initializing the model
print("\n🔄 Testing model initialization...")
try:
    gaze_tracker = GazeTracking()
    print("✅ GazeTracking model initialized successfully!")
except Exception as e:
    print(f"❌ Failed to initialize model: {e}")
    sys.exit(1)

# Test with a dummy frame (black image)
print("\n🔄 Testing with dummy frame...")
try:
    import cv2
    import numpy as np
    
    # Create a black test image
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Test the model with the frame
    gaze_tracker.refresh(test_frame)
    
    # Get results (should be None for black image)
    horizontal_ratio = gaze_tracker.horizontal_ratio()
    vertical_ratio = gaze_tracker.vertical_ratio()
    is_blinking = gaze_tracker.is_blinking()
    
    print(f"✅ Model processed frame successfully!")
    print(f"📊 Horizontal ratio: {horizontal_ratio}")
    print(f"📊 Vertical ratio: {vertical_ratio}")
    print(f"👁️ Is blinking: {is_blinking}")
    
    if horizontal_ratio is None and vertical_ratio is None:
        print("✅ Model correctly detected NO EYES in test image!")
    else:
        print("⚠️ Model detected eyes in black image (unexpected)")
        
except Exception as e:
    print(f"❌ Error testing with frame: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("🎉 ALL TESTS PASSED!")
print("✅ Real gaze tracking model is ready to use")
print("🚀 You can now start the real gaze tracking server")
print("="*60)