"""
Test Hand Model Server Integration
Tests the new hand model server on port 5002
"""
import sys
import os
import requests
import numpy as np
import cv2
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_hand_server():
    """Test hand model server connectivity and functionality"""
    server_url = "http://localhost:5002"
    
    logger.info("🧪 Testing Hand Model Server Integration...")
    
    # Test 1: Health check
    try:
        response = requests.get(f"{server_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            logger.info(f"✅ Health check passed: {health_data}")
        else:
            logger.error(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Test endpoint
    try:
        response = requests.get(f"{server_url}/test", timeout=10)
        if response.status_code == 200:
            test_data = response.json()
            logger.info(f"✅ Test endpoint passed: {test_data['test_result']}")
        else:
            logger.error(f"❌ Test endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Test endpoint error: {e}")
        return False
    
    # Test 3: Real frame analysis
    try:
        # Create a test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Add some visual elements to make it more realistic
        cv2.rectangle(test_frame, (100, 100), (200, 200), (255, 255, 255), -1)
        
        # Convert to base64
        _, buffer = cv2.imencode('.jpg', test_frame)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Send analysis request
        payload = {'image': image_base64}
        response = requests.post(f"{server_url}/analyze", json=payload, timeout=15)
        
        if response.status_code == 200:
            analysis_result = response.json()
            logger.info(f"✅ Frame analysis passed:")
            logger.info(f"   - Method: {analysis_result.get('method')}")
            logger.info(f"   - Confidence: {analysis_result.get('confidence')}")
            logger.info(f"   - Level: {analysis_result.get('confidence_level')}")
            logger.info(f"   - Gestures: {analysis_result.get('gestures_detected')}")
            logger.info(f"   - Hands detected: {analysis_result.get('hands_detected')}")
        else:
            logger.error(f"❌ Frame analysis failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Frame analysis error: {e}")
        return False
    
    logger.info("🎉 All hand model server tests passed!")
    return True

def test_hand_client():
    """Test the hand model client"""
    logger.info("🧪 Testing Hand Model Client...")
    
    try:
        from hand_model_client import hand_client
        
        # Create test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Test client
        result = hand_client.detect_confidence(test_frame)
        
        logger.info(f"✅ Hand client test result:")
        logger.info(f"   - Method: {result.get('method')}")
        logger.info(f"   - Confidence: {result.get('confidence')}")
        logger.info(f"   - Level: {result.get('confidence_level')}")
        logger.info(f"   - Server available: {hand_client.server_available}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Hand client test error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 HAND MODEL SERVER INTEGRATION TEST")
    logger.info("=" * 60)
    
    # Test server directly
    server_success = test_hand_server()
    
    # Test client integration
    client_success = test_hand_client()
    
    logger.info("=" * 60)
    logger.info("📋 TEST SUMMARY")
    logger.info(f"   Server Tests: {'✅ PASS' if server_success else '❌ FAIL'}")
    logger.info(f"   Client Tests: {'✅ PASS' if client_success else '❌ FAIL'}")
    
    if server_success and client_success:
        logger.info("🎉 ALL TESTS PASSED - Hand model server integration is working!")
        logger.info("🔧 Main backend can now communicate with hand model server on port 5002")
    else:
        logger.info("💥 SOME TESTS FAILED - Check the logs above")
    
    logger.info("=" * 60)