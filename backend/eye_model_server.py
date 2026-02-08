"""
Eye Model Server for EyeTracking_Env
Runs on port 5001 (separate from main backend on port 5000)
Focuses only on eye tracking and gaze detection
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

# Import eye model
try:
    from model.eye_model import EyeConfidenceDetector
except ImportError as e:
    print(f"❌ Failed to import eye model: {e}")
    print("Make sure you're in the EyeTracking_Env and eye_model.py exists")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('EyeModelServer')

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize eye detector
try:
    eye_detector = EyeConfidenceDetector()
    logger.info("✅ Eye detector initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize eye detector: {e}")
    eye_detector = None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Eye Model Server',
        'port': 5001,
        'eye_detector_loaded': eye_detector is not None,
        'gaze_model_status': 'loaded' if eye_detector and eye_detector.model_loaded else 'opencv_fallback',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/eye/detect', methods=['POST'])
def detect_eye_confidence():
    """Detect eye confidence from uploaded image"""
    if not eye_detector:
        return jsonify({'error': 'Eye detector not initialized'}), 500
    
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
        
        # Detect eye confidence
        result = eye_detector.detect_confidence(frame)
        
        return jsonify({
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in eye detection: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/eye/test', methods=['GET'])
def test_eye_detection():
    """Test eye detection with a blank frame"""
    if not eye_detector:
        return jsonify({'error': 'Eye detector not initialized'}), 500
    
    try:
        # Create a test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        result = eye_detector.detect_confidence(test_frame)
        
        return jsonify({
            'success': True,
            'test_result': result,
            'message': 'Eye detection test completed',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in eye detection test: {e}")
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info("👤 Client connected to Eye Model Server")
    emit('connected', {
        'message': 'Connected to Eye Model Server',
        'service': 'eye_tracking',
        'port': 5001,
        'gaze_model_loaded': eye_detector.model_loaded if eye_detector else False
    })

@socketio.on('analyze_frame')
def handle_frame_analysis(data):
    """Handle real-time frame analysis via WebSocket"""
    if not eye_detector:
        emit('analysis_error', {'error': 'Eye detector not initialized'})
        return
    
    try:
        # Decode frame
        frame_data = data.get('frame', '')
        if frame_data.startswith('data:image'):
            frame_data = frame_data.split(',')[1]
        
        img_bytes = base64.b64decode(frame_data)
        img_array = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        # Analyze frame
        result = eye_detector.detect_confidence(frame)
        
        # Emit result
        emit('analysis_result', {
            'type': 'eye_confidence',
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in frame analysis: {e}")
        emit('analysis_error', {'error': str(e)})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info("👤 Client disconnected from Eye Model Server")

if __name__ == '__main__':
    logger.info("🚀 Starting Eye Model Server...")
    logger.info("📍 Server will run on: http://localhost:5001")
    logger.info("🔄 Main backend runs on: http://localhost:5000")
    logger.info("👁️ Eye model environment: EyeTracking_Env")
    
    # Get configuration
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('EYE_MODEL_PORT', '5001'))  # Different port for eye model
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"🌐 Host: {host}, Port: {port}, Debug: {debug_mode}")
    
    # Run the eye model server
    socketio.run(app, host=host, port=port, debug=debug_mode, allow_unsafe_werkzeug=True, use_reloader=False)