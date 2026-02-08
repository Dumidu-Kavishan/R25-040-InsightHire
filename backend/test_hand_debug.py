#!/usr/bin/env python3
"""
Test script for hand model server debugging
"""

import requests
import base64
import cv2
import numpy as np
import json

def test_hand_server():
    """Test the hand model server with a dummy image"""
    
    # Create a test image (simple white background)
    test_image = np.ones((480, 640, 3), dtype=np.uint8) * 255
    
    # Encode as base64
    _, buffer = cv2.imencode('.jpg', test_image)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    # Test the server
    url = "http://localhost:5002/analyze"
    payload = {
        "image": f"data:image/jpeg;base64,{img_base64}"
    }
    
    try:
        print("🧪 Testing hand model server...")
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Server response:")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Server error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_hand_server()