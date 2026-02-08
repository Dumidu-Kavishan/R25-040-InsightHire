"""
Hand Model Client Integration
Updates the main backend to communicate with hand model server on port 5002
"""
import requests
import base64
import cv2
import numpy as np
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class HandModelClient:
    """Client for communicating with hand model server"""
    
    def __init__(self, server_url="http://localhost:5002"):
        self.server_url = server_url
        self.server_available = False
        self._check_server()
    
    def _check_server(self):
        """Check if hand model server is available"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.server_available = data.get('status') == 'ok'
                logger.info(f"🤝 Hand model server: {'✅ Available' if self.server_available else '⚠️ Not ready'}")
            else:
                self.server_available = False
                logger.warning(f"⚠️ Hand model server returned status {response.status_code}")
        except Exception as e:
            self.server_available = False
            logger.warning(f"⚠️ Hand model server not available: {e}")
    
    def detect_confidence(self, frame):
        """Detect hand confidence using the dedicated server"""
        try:
            if not self.server_available:
                self._check_server()  # Retry connection
                if not self.server_available:
                    return self._get_fallback_result("server_unavailable")
            
            # Convert frame to base64
            _, buffer = cv2.imencode('.jpg', frame)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Send to hand model server
            payload = {'image': image_base64}
            response = requests.post(f"{self.server_url}/analyze", json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"🤝 Hand server result: {result.get('confidence_level')} ({result.get('confidence')})")
                return result
            else:
                logger.error(f"❌ Hand server error {response.status_code}: {response.text}")
                return self._get_fallback_result("server_error")
                
        except Exception as e:
            logger.error(f"❌ Hand model client error: {e}")
            return self._get_fallback_result("client_error")
    
    def _get_fallback_result(self, error_type):
        """Return fallback result when server is unavailable"""
        return {
            'confidence_level': 'not_confident',
            'confidence': 0.0,
            'gestures_detected': [error_type],
            'hands_detected': 0,
            'method': f'hand_server_{error_type}',
            'timestamp': datetime.now().isoformat()
        }

# Global hand model client instance
hand_client = HandModelClient()