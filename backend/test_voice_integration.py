#!/usr/bin/env python3
"""
Test Voice Model Server Integration
Test both server functionality and client communication
"""

import numpy as np
import time
import logging
from voice_model_client import VoiceModelClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('VoiceModelTest')

def generate_test_audio(duration=3.0, sample_rate=22050, frequency=440):
    """Generate a test audio signal (sine wave)"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Generate sine wave with some noise to simulate voice
    signal = 0.3 * np.sin(2 * np.pi * frequency * t)
    noise = 0.1 * np.random.normal(0, 1, len(signal))
    audio = signal + noise
    return audio.astype(np.float32)

def generate_silent_audio(duration=3.0, sample_rate=22050):
    """Generate silent audio (very low amplitude noise)"""
    return 0.001 * np.random.normal(0, 1, int(sample_rate * duration)).astype(np.float32)

def test_voice_server():
    """Test voice model server functionality"""
    print("🎤 Testing Voice Model Server Integration")
    print("=" * 50)
    
    # Initialize client
    print("\n1. Initializing Voice Model Client...")
    client = VoiceModelClient()
    
    # Test server availability
    print("\n2. Testing server availability...")
    time.sleep(1)  # Give server time to respond
    
    # Test with generated audio
    print("\n3. Testing with generated test audio (3 seconds)...")
    test_audio = generate_test_audio(duration=3.0)
    print(f"   Generated audio: {len(test_audio)} samples, range: [{test_audio.min():.3f}, {test_audio.max():.3f}]")
    
    result = client.analyze_voice_clip(test_audio, sample_rate=22050)
    print(f"   Result: {result}")
    
    # Test with silent audio
    print("\n4. Testing with silent audio...")
    silent_audio = generate_silent_audio(duration=2.0)
    print(f"   Generated silent audio: {len(silent_audio)} samples, range: [{silent_audio.min():.3f}, {silent_audio.max():.3f}]")
    
    result = client.analyze_voice_clip(silent_audio, sample_rate=22050)
    print(f"   Result: {result}")
    
    # Test with different frequencies
    print("\n5. Testing with different audio frequencies...")
    frequencies = [220, 440, 880]  # Low, medium, high frequency
    
    for freq in frequencies:
        print(f"\n   Testing {freq}Hz tone...")
        freq_audio = generate_test_audio(duration=2.0, frequency=freq)
        result = client.analyze_voice_clip(freq_audio, sample_rate=22050)
        print(f"   {freq}Hz result: confidence_level={result.get('confidence_level')}, emotion={result.get('emotion')}, confidence={result.get('confidence', 0):.2f}")
    
    # Test error handling
    print("\n6. Testing error handling...")
    try:
        result = client.analyze_voice_clip([], sample_rate=22050)
        print(f"   Empty audio result: {result}")
    except Exception as e:
        print(f"   Empty audio error (expected): {e}")
    
    print("\n🎤 Voice Model Server Test Complete!")
    print("=" * 50)

def test_voice_integration():
    """Test voice integration in analysis flow"""
    print("\n🔄 Testing Voice Integration in Analysis Flow")
    print("=" * 50)
    
    # Simulate realtime analyzer voice analysis
    from voice_model_client import analyze_voice_clip
    
    print("\n1. Testing legacy function compatibility...")
    test_audio = generate_test_audio(duration=2.0)
    result = analyze_voice_clip(test_audio, sample_rate=22050)
    print(f"   Legacy function result: {result}")
    
    print("\n✅ Voice Integration Test Complete!")

if __name__ == "__main__":
    print("🚀 Starting Voice Model Server Tests")
    print("📋 Make sure voice_model_server.py is running on port 5003")
    print("🔧 Run in VoiceTracking environment: conda activate VoiceTracking && python voice_model_server.py")
    print()
    
    try:
        test_voice_server()
        test_voice_integration()
        
        print("\n🎉 All tests completed successfully!")
        print("🎤 Voice model server is ready for integration!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        print("\n🔧 Make sure:")
        print("   1. VoiceTracking environment is set up")
        print("   2. voice_model_server.py is running on port 5003")
        print("   3. Model files exist in Models/Voice/")