"""
Pure Gaze Tracking Eye Model Server
ONLY uses real gaze tracking - NO fallback
Runs on port 5001 (separate from main backend on port 5000)
"""
import os
import sys
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import base64
import numpy as np
import cv2
from datetime import datetime
import threading

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import PURE gaze tracking eye model
try:
    from model.eye_model_pure_gaze import EyeConfidenceDetector
except ImportError as e:
    print(f"❌ CRITICAL: Failed to import pure gaze eye model: {e}")
    print("Make sure dlib is installed and gaze tracking model is available")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('PureGazeServer')

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize PURE gaze detector (will fail if dlib not available)
try:
    eye_detector = EyeConfidenceDetector()
    logger.info("✅ Pure gaze detector initialized successfully")
except Exception as e:
    logger.error(f"❌ CRITICAL: Failed to initialize pure gaze detector: {e}")
    logger.error("dlib and gaze tracking model are REQUIRED for this server")
    eye_detector = None
    sys.exit(1)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Pure Gaze Tracking Server',
        'port': 5001,
        'mode': 'PURE_GAZE_TRACKING_ONLY',
        'fallback_disabled': True,
        'dlib_available': eye_detector is not None and eye_detector.model_loaded,
        'gaze_model_status': 'loaded' if eye_detector and eye_detector.model_loaded else 'failed',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/eye/detect', methods=['POST'])
def detect_eye_confidence():
    """Detect eye confidence using PURE gaze tracking"""
    if not eye_detector or not eye_detector.model_loaded:
        return jsonify({
            'error': 'Pure gaze detector not available',
            'message': 'dlib and gaze tracking model required'
        }), 500
    
    try:
        # Get image data
        if 'image' in request.files:
            file = request.files['image']
            file_bytes = np.frombuffer(file.read(), np.uint8)
            frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        elif 'frame' in request.json:
            # Decode base64 image
            frame_data = request.json['frame']
            if frame_data.startswith('data:image'):
                frame_data = frame_data.split(',')[1]
            img_bytes = base64.b64decode(frame_data)
            img_array = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        else:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Detect using PURE gaze tracking (will raise exception if fails)
        result = eye_detector.detect_confidence(frame)
        
        return jsonify({
            'success': True,
            'result': result,
            'mode': 'pure_gaze_tracking_only',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in pure gaze detection: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Pure gaze tracking failed - no fallback available'
        }), 500

@app.route('/eye/test', methods=['GET'])
def test_eye_detection():
    """Test pure gaze detection with a blank frame"""
    if not eye_detector or not eye_detector.model_loaded:
        return jsonify({
            'error': 'Pure gaze detector not available',
            'message': 'dlib and gaze tracking model required'
        }), 500
    
    try:
        # Create a test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        result = eye_detector.detect_confidence(test_frame)
        
        return jsonify({
            'success': True,
            'test_result': result,
            'mode': 'pure_gaze_tracking_test',
            'message': 'Pure gaze tracking test completed - NO fallback used',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in pure gaze detection test: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Pure gaze tracking test failed - no fallback available'
        }), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info("👤 Client connected to Pure Gaze Tracking Server")
    emit('connected', {
        'message': 'Connected to Pure Gaze Tracking Server',
        'service': 'pure_gaze_tracking',
        'port': 5001,
        'mode': 'PURE_GAZE_ONLY',
        'fallback_disabled': True,
        'dlib_loaded': eye_detector.model_loaded if eye_detector else False
    })

@socketio.on('analyze_frame')
def handle_frame_analysis(data):
    """Handle real-time frame analysis via WebSocket - PURE gaze only"""
    if not eye_detector or not eye_detector.model_loaded:
        emit('analysis_error', {
            'error': 'Pure gaze detector not available',
            'message': 'dlib and gaze tracking required'
        })
        return
    
    try:
        # Decode frame
        frame_data = data.get('frame', '')
        if frame_data.startswith('data:image'):
            frame_data = frame_data.split(',')[1]
        
        img_bytes = base64.b64decode(frame_data)
        img_array = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        # Analyze frame using PURE gaze tracking
        result = eye_detector.detect_confidence(frame)
        
        # Emit result
        emit('analysis_result', {
            'type': 'pure_gaze_confidence',
            'result': result,
            'mode': 'pure_gaze_tracking_only',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in pure gaze frame analysis: {e}")
        emit('analysis_error', {
            'error': str(e),
            'message': 'Pure gaze tracking failed - no fallback available'
        })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info("👤 Client disconnected from Pure Gaze Tracking Server")

if __name__ == '__main__':
    logger.info("🚀 Starting Pure Gaze Tracking Server...")
    logger.info("📍 Server will run on: http://localhost:5001")
    logger.info("🔄 Main backend runs on: http://localhost:5000")
    logger.info("👁️ Mode: PURE GAZE TRACKING ONLY - NO FALLBACK")
    logger.info("⚠️  Requires: dlib + gaze tracking model")
    
    if not eye_detector or not eye_detector.model_loaded:
        logger.error("❌ CRITICAL: Pure gaze detector not available")
        logger.error("Install dlib and ensure gaze tracking model is accessible")
        sys.exit(1)
    
    # Get configuration
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('EYE_MODEL_PORT', '5001'))
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"🌐 Host: {host}, Port: {port}, Debug: {debug_mode}")
    logger.info("✅ Pure gaze tracking initialized - ready for real eye tracking!")
    
    # Run the pure gaze tracking server
    socketio.run(app, host=host, port=port, debug=debug_mode, allow_unsafe_werkzeug=True, use_reloader=False)