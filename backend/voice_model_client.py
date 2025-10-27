"""
Voice Model Client Integration
Updates the main backend to communicate with voice model server on port 5003
"""
import requests
import numpy as np
import logging
from datetime import datetime
import base64

logger = logging.getLogger(__name__)

class VoiceModelClient:
    """Client for communicating with voice model server"""
    
    def __init__(self, server_url="http://localhost:5003"):
        self.server_url = server_url
        self.server_available = False
        self._check_server()
    
    def _check_server(self):
        """Check if voice model server is available"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.server_available = data.get('status') == 'ok'
                logger.info(f"🎤 Voice model server: {'✅ Available' if self.server_available else '⚠️ Not ready'}")
            else:
                self.server_available = False
                logger.warning(f"⚠️ Voice model server returned status {response.status_code}")
        except Exception as e:
            self.server_available = False
            logger.warning(f"⚠️ Voice model server not available: {e}")
    
    def analyze_voice_clip(self, audio_data, sample_rate=22050):
        """Analyze voice clip using the dedicated server"""
        try:
            if not self.server_available:
                self._check_server()  # Retry connection
                if not self.server_available:
                    return self._get_fallback_result("server_unavailable")
            
            # Prepare audio data
            if isinstance(audio_data, list):
                audio_data = np.array(audio_data, dtype=np.float32)
            elif isinstance(audio_data, np.ndarray):
                audio_data = audio_data.astype(np.float32)
            
            # Send to voice model server
            payload = {
                'audio_data': audio_data.tolist(),
                'sample_rate': sample_rate
            }
            
            response = requests.post(f"{self.server_url}/analyze_voice", json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"🎤 Voice server result: {result.get('confidence_level')} - {result.get('emotion')} ({result.get('confidence', 0.0):.2f})")
                return result
            else:
                logger.error(f"❌ Voice server error {response.status_code}: {response.text}")
                return self._get_fallback_result("server_error")
                
        except requests.exceptions.Timeout:
            logger.error("❌ Voice server timeout")
            return self._get_fallback_result("timeout")
        except requests.exceptions.ConnectionError:
            logger.error("❌ Voice server connection error")
            self.server_available = False
            return self._get_fallback_result("connection_error")
        except Exception as e:
            logger.error(f"❌ Error calling voice server: {e}")
            return self._get_fallback_result("client_error")
    
    def analyze_voice_base64(self, audio_base64, sample_rate=22050):
        """Analyze voice clip from base64 encoded audio"""
        try:
            if not self.server_available:
                self._check_server()
                if not self.server_available:
                    return self._get_fallback_result("server_unavailable")
            
            payload = {
                'audio_base64': audio_base64,
                'sample_rate': sample_rate
            }
            
            response = requests.post(f"{self.server_url}/analyze_voice", json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"🎤 Voice server result (base64): {result.get('confidence_level')} - {result.get('emotion')} ({result.get('confidence', 0.0):.2f})")
                return result
            else:
                logger.error(f"❌ Voice server error {response.status_code}: {response.text}")
                return self._get_fallback_result("server_error")
                
        except Exception as e:
            logger.error(f"❌ Error calling voice server with base64: {e}")
            return self._get_fallback_result("client_error")
    
    def _get_fallback_result(self, error_type):
        """Get fallback result when server is unavailable"""
        fallback_results = {
            "server_unavailable": {
                'confidence_level': 'server_unavailable',
                'confidence': 0.0,
                'emotion': 'unknown',
                'method': 'fallback',
                'error': 'Voice model server not available',
                'timestamp': datetime.now().isoformat()
            },
            "server_error": {
                'confidence_level': 'server_error',
                'confidence': 0.0,
                'emotion': 'unknown',
                'method': 'fallback',
                'error': 'Voice model server returned error',
                'timestamp': datetime.now().isoformat()
            },
            "timeout": {
                'confidence_level': 'timeout',
                'confidence': 0.0,
                'emotion': 'unknown',
                'method': 'fallback',
                'error': 'Voice model server timeout',
                'timestamp': datetime.now().isoformat()
            },
            "connection_error": {
                'confidence_level': 'connection_error',
                'confidence': 0.0,
                'emotion': 'unknown',
                'method': 'fallback',
                'error': 'Cannot connect to voice model server',
                'timestamp': datetime.now().isoformat()
            },
            "client_error": {
                'confidence_level': 'client_error',
                'confidence': 0.0,
                'emotion': 'unknown',
                'method': 'fallback',
                'error': 'Voice client error',
                'timestamp': datetime.now().isoformat()
            }
        }
        
        return fallback_results.get(error_type, fallback_results["client_error"])

# Helper function for backward compatibility
def analyze_voice_clip(audio_data, sample_rate=22050):
    """Legacy function for direct voice analysis"""
    client = VoiceModelClient()
    return client.analyze_voice_clip(audio_data, sample_rate)