#!/usr/bin/env python3
"""
Real Gaze Tracking Eye Model Server - PRODUCTION VERSION
Uses the actual trained eye model from Models/Eye/eye_train_model/gaze_tracking
Runs on port 5001 in GazeTracking conda environment
"""

import sys
import os
import json
import base64
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
from datetime import datetime

# Get the absolute path properly
script_dir = os.path.dirname(os.path.abspath(__file__))  # backend directory
project_root = os.path.dirname(script_dir)  # go up one level to project root
gaze_model_dir = os.path.join(project_root, 'Models', 'Eye', 'eye_train_model', 'gaze_tracking')
sys.path.insert(0, gaze_model_dir)

print(f"🔍 Looking for gaze tracking model in: {gaze_model_dir}")
print(f"📁 Project root: {project_root}")

# Verify the model file exists
model_file = os.path.join(gaze_model_dir, 'trained_models', 'shape_predictor_68_face_landmarks.dat')
if os.path.exists(model_file):
    print(f"✅ Model file found: {model_file}")
else:
    print(f"❌ Model file NOT found: {model_file}")
    print("🔧 Please ensure the trained model file exists")

try:
    # Add the parent directory to properly handle the package
    parent_dir = os.path.dirname(gaze_model_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    # Import the gaze_tracking package
    import gaze_tracking
    from gaze_tracking import GazeTracking
    print("✅ GazeTracking imported successfully from trained model!")
except ImportError as e:
    print(f"❌ Failed to import GazeTracking from trained model: {e}")
    print("� Trying alternative import method...")
    
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
        print(f"📁 Model directory: {gaze_model_dir}")
        print("🔧 Current Python path:")
        for p in sys.path[:5]:  # Show first 5 paths
            print(f"   - {p}")
        sys.exit(1)

# Initialize Flask
try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    print("✅ Flask imported successfully!")
except ImportError as e:
    print(f"❌ Failed to import Flask: {e}")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

# Initialize the REAL gaze tracking model
print("🔄 Initializing REAL gaze tracking model from trained models...")
try:
    gaze_tracker = GazeTracking()
    print("✅ REAL gaze tracking model initialized successfully!")
    print(f"👁️ Model loaded from: {gaze_model_dir}")
except Exception as e:
    print(f"❌ Failed to initialize gaze tracking model: {e}")
    print(f"📁 Check if model files exist in: {gaze_model_dir}")
    sys.exit(1)

def process_image_data(image_data):
    """Convert base64 image to OpenCV format"""
    try:
        # Remove data URL prefix if present
        if 'data:image' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decode base64
        image_bytes = base64.b64decode(image_data)
        
        # Convert to PIL Image
        pil_image = Image.open(BytesIO(image_bytes))
        
        # Convert to OpenCV format
        opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        return opencv_image
    except Exception as e:
        print(f"❌ Error processing image: {e}")
        return None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'real_gaze_tracking',
        'model_path': gaze_model_dir,
        'message': 'REAL gaze tracking model from trained models'
    })

@app.route('/detect_gaze', methods=['POST'])
def detect_gaze():
    """REAL gaze tracking detection using trained model"""
    try:
        data = request.json
        
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Process the image
        frame = process_image_data(data['image'])
        if frame is None:
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Use the REAL gaze tracking model
        gaze_tracker.refresh(frame)
        
        # Get actual gaze analysis results from the trained model
        is_blinking = gaze_tracker.is_blinking()
        is_right = gaze_tracker.is_right()
        is_left = gaze_tracker.is_left()
        is_center = gaze_tracker.is_center()
        horizontal_ratio = gaze_tracker.horizontal_ratio()
        vertical_ratio = gaze_tracker.vertical_ratio()
        
        # Check if eyes are actually detected
        # If ratios are None, no eyes were found
        eyes_detected = horizontal_ratio is not None and vertical_ratio is not None
        
        # Build gaze_movements_detected array based on actual detection
        gaze_movements_detected = []
        if eyes_detected:
            if is_blinking:
                gaze_movements_detected.append('is_blinking')
            if is_right:
                gaze_movements_detected.append('is_right')
            if is_left:
                gaze_movements_detected.append('is_left')
            if is_center:
                gaze_movements_detected.append('is_center')
            
            # Add ratio-based movements
            if horizontal_ratio is not None:
                if horizontal_ratio >= 0.65:
                    gaze_movements_detected.append('is_right_ratio')
                elif horizontal_ratio <= 0.35:
                    gaze_movements_detected.append('is_left_ratio')
                else:
                    gaze_movements_detected.append('is_center_ratio')
            
            if vertical_ratio is not None:
                if vertical_ratio >= 0.6:
                    gaze_movements_detected.append('is_down_ratio')
                elif vertical_ratio <= 0.4:
                    gaze_movements_detected.append('is_up_ratio')
        
        # Get pupil coordinates if available
        left_pupil = gaze_tracker.pupil_left_coords()
        right_pupil = gaze_tracker.pupil_right_coords()
        
        # Convert numpy types to native Python types for JSON serialization
        def convert_to_serializable(value):
            """Convert numpy types to native Python types"""
            if value is None:
                return None
            if hasattr(value, 'item'):  # numpy scalar
                return value.item()
            if hasattr(value, 'tolist'):  # numpy array
                return value.tolist()
            if isinstance(value, (tuple, list)):
                return [convert_to_serializable(v) for v in value]
            return value
        
        # Build result based on ACTUAL model detection
        result = {
            'model_type': 'REAL_GAZE_TRACKING',
            'model_path': gaze_model_dir,
            'fallback_used': False,
            'gaze_detected': bool(eyes_detected),
            'eyes_detected': bool(eyes_detected),  # Add this field explicitly
            'confidence': 0.95 if eyes_detected else 0.0,
            'confidence_level': 'confident' if eyes_detected else 'not_confident',
            'gaze_movements_detected': gaze_movements_detected,
            'gaze_analysis': {
                'is_blinking': convert_to_serializable(is_blinking),
                'is_right': convert_to_serializable(is_right),
                'is_left': convert_to_serializable(is_left),
                'is_center': convert_to_serializable(is_center),
                'horizontal_ratio': convert_to_serializable(horizontal_ratio),
                'vertical_ratio': convert_to_serializable(vertical_ratio),
                'left_pupil': convert_to_serializable(left_pupil),
                'right_pupil': convert_to_serializable(right_pupil)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"🎯 REAL gaze tracking result - Eyes detected: {eyes_detected}, Movements: {gaze_movements_detected}")
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Error in real gaze detection: {e}")
        return jsonify({
            'error': 'Real gaze detection failed',
            'details': str(e),
            'model_type': 'REAL_GAZE_TRACKING'
        }), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get model status"""
    return jsonify({
        'model_type': 'REAL_GAZE_TRACKING',
        'model_path': gaze_model_dir,
        'status': 'active',
        'description': 'Real gaze tracking using trained dlib model',
        'port': 5001,
        'endpoints': ['/health', '/detect_gaze', '/status']
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 REAL GAZE TRACKING EYE MODEL SERVER")
    print("="*60)
    print("✅ Model: REAL gaze tracking with trained dlib")
    print(f"✅ Model Path: {gaze_model_dir}")
    print("✅ Technology: Professional eye tracking")
    print("✅ Port: 5001")
    print("✅ Environment: GazeTracking conda")
    print("✅ Status: READY")
    print("="*60)
    
    try:
        app.run(host='0.0.0.0', port=5001, debug=True)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")