#!/usr/bin/env python3
"""
Mock Pure Gaze Tracking Eye Model Server
Provides API endpoints for gaze tracking without DLL dependencies
Runs on port 5001 - Can be upgraded to real gaze tracking once DLL issues resolved
"""

import sys
import os
import json
import base64
import random
from io import BytesIO

# Try to import Flask from conda environment
try:
    sys.path.insert(0, r'C:\Users\PM_User\miniconda3\envs\GazeTracking\Lib\site-packages')
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    print("✅ Flask imported successfully from GazeTracking environment!")
except ImportError as e:
    print(f"❌ Failed to import Flask: {e}")
    # Fallback to system Flask if available
    try:
        from flask import Flask, request, jsonify
        from flask_cors import CORS
        print("✅ Flask imported from system!")
    except ImportError:
        print("❌ Flask not available anywhere")
        sys.exit(1)

app = Flask(__name__)
CORS(app)

print("🔄 Initializing MOCK gaze tracking server...")
print("✅ Mock gaze tracking server initialized!")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'mock_gaze_tracking',
        'message': 'Mock gaze tracking server - ready for real implementation'
    })

@app.route('/detect_gaze', methods=['POST'])
def detect_gaze():
    """Mock gaze tracking detection - simulates real gaze analysis"""
    try:
        data = request.json
        
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Mock gaze analysis results (realistic simulation)
        # 🔧 FIXED: Actually simulate real behavior - sometimes no gaze detected
        gaze_detected = random.choice([True, True, True, False])  # 75% chance of detection
        
        if gaze_detected:
            mock_results = {
                'model_type': 'MOCK_GAZE_TRACKING',
                'fallback_used': False,
                'gaze_detected': True,
                'confidence': round(random.uniform(0.85, 0.98), 2),
                'gaze_analysis': {
                    'is_blinking': random.choice([True, False]),
                    'is_right': random.choice([True, False, None]),
                    'is_left': random.choice([True, False, None]),
                    'is_center': random.choice([True, False]),
                    'horizontal_ratio': round(random.uniform(0.2, 0.8), 3),
                    'vertical_ratio': round(random.uniform(0.3, 0.7), 3),
                    'left_pupil': (random.randint(100, 200), random.randint(100, 200)),
                    'right_pupil': (random.randint(400, 500), random.randint(100, 200))
                },
                'note': 'Mock data - upgrade to real gaze tracking when DLL issues resolved'
            }
        else:
            # 🔧 NO GAZE DETECTED - realistic response for blank frames or no eyes
            mock_results = {
                'model_type': 'MOCK_GAZE_TRACKING',
                'fallback_used': False,
                'gaze_detected': False,
                'confidence': 0.0,
                'gaze_analysis': {
                    'is_blinking': None,
                    'is_right': None,
                    'is_left': None,
                    'is_center': None,
                    'horizontal_ratio': None,
                    'vertical_ratio': None,
                    'left_pupil': None,
                    'right_pupil': None
                },
                'note': 'No gaze detected - mock simulation'
            }
        
        print(f"🎯 Mock gaze tracking result: {mock_results['gaze_analysis']}")
        return jsonify(mock_results)
        
    except Exception as e:
        print(f"❌ Error in mock gaze detection: {e}")
        return jsonify({
            'error': 'Mock gaze detection failed',
            'details': str(e),
            'model_type': 'MOCK_GAZE_TRACKING'
        }), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get model status"""
    return jsonify({
        'model_type': 'MOCK_GAZE_TRACKING',
        'status': 'active',
        'description': 'Mock gaze tracking server - placeholder for real implementation',
        'port': 5001,
        'endpoints': ['/health', '/detect_gaze', '/status'],
        'upgrade_path': 'Install real gaze tracking when DLL compatibility resolved'
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 MOCK GAZE TRACKING EYE MODEL SERVER")
    print("="*60)
    print("✅ Model: Mock gaze tracking (placeholder)")
    print("✅ Purpose: Provide API endpoints while resolving DLL issues")
    print("✅ Port: 5001")
    print("✅ Status: READY")
    print("🔄 Upgrade to real gaze tracking when DLL compatibility fixed")
    print("="*60)
    
    try:
        app.run(host='0.0.0.0', port=5001, debug=True)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")