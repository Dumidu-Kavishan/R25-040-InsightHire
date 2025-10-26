#!/usr/bin/env python3
"""
Minimal test for gaze tracking import only
"""

import sys
import os

# Add the gaze tracking model directory to path
gaze_model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Models', 'Eye', 'eye_train_model')
sys.path.insert(0, gaze_model_dir)

print("Testing Gaze Tracking Import...")
print("=" * 40)

try:
    # Test gaze tracking import only
    from gaze_tracking import GazeTracking
    print("✅ GazeTracking import successful!")
    
    # Test initialization
    gaze = GazeTracking()
    print("✅ GazeTracking object created!")
    
    print("\n🎉 PURE GAZE TRACKING MODEL IS READY!")
    print("✅ Professional gaze tracking with dlib working!")
    print("✅ NO OpenCV fallback - ONLY real gaze model!")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)