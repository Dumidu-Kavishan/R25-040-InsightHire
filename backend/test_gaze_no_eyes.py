#!/usr/bin/env python3
"""
Test script to verify gaze server behavior when no eyes are present
Creates a blank frame and tests what the gaze server returns
"""
import cv2
import numpy as np
import requests
import base64
import json

def test_gaze_with_no_eyes():
    """Test gaze server with a blank frame (no eyes)"""
    print("🧪 Testing gaze server with blank frame (no eyes)")
    
    # Create a blank frame (480x640 black image)
    blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Convert to base64
    _, buffer = cv2.imencode('.jpg', blank_frame)
    frame_base64 = base64.b64encode(buffer).decode('utf-8')
    
    try:
        # Test gaze server
        response = requests.post(
            "http://localhost:5001/detect_gaze",
            json={'image': f"data:image/jpeg;base64,{frame_base64}"},
            timeout=5.0
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Gaze server response:")
            print(json.dumps(result, indent=2))
            
            # Check key fields
            gaze_detected = result.get('gaze_detected', 'NOT_SET')
            eyes_detected = result.get('eyes_detected', 'NOT_SET')
            gaze_analysis = result.get('gaze_analysis', {})
            
            print(f"\n🔍 Key fields:")
            print(f"  gaze_detected: {gaze_detected}")
            print(f"  eyes_detected: {eyes_detected}")
            print(f"  gaze_analysis: {gaze_analysis}")
            
            # Test expected behavior
            if gaze_detected is True or eyes_detected is True:
                print("❌ PROBLEM: Server reports eyes/gaze detected in blank frame!")
                return False
            else:
                print("✅ GOOD: Server correctly reports no eyes/gaze in blank frame")
                return True
                
        else:
            print(f"❌ Gaze server error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to gaze server on port 5001")
        print("   Make sure a gaze server is running!")
        return False
    except Exception as e:
        print(f"❌ Error testing gaze server: {e}")
        return False

def test_gaze_server_health():
    """Test if gaze server is running"""
    try:
        response = requests.get("http://localhost:5001/health", timeout=3.0)
        if response.status_code == 200:
            health = response.json()
            print("✅ Gaze server health:")
            print(json.dumps(health, indent=2))
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

if __name__ == '__main__':
    print("="*60)
    print("🔬 GAZE SERVER TEST - NO EYES SCENARIO")
    print("="*60)
    
    # Test server health first
    print("1. Testing gaze server health...")
    if test_gaze_server_health():
        print("\n2. Testing gaze detection with no eyes...")
        success = test_gaze_with_no_eyes()
        
        print("\n" + "="*60)
        if success:
            print("🎉 Test PASSED: Gaze server correctly handles no-eyes scenario")
        else:
            print("💥 Test FAILED: Gaze server has false positive detection")
        print("="*60)
    else:
        print("\n❌ Cannot proceed - gaze server not available")
        print("   Please start a gaze server on port 5001 first")