#!/usr/bin/env python3
"""
Debug Voice Feature Extraction
Test feature extraction directly in VoiceTracking environment
"""

import numpy as np
import logging
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger('VoiceDebug')

try:
    import librosa
    import tensorflow as tf
    print("✅ Successfully imported librosa and tensorflow")
    print(f"📋 Librosa version: {librosa.__version__}")
    print(f"📋 TensorFlow version: {tf.__version__}")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_feature_extraction():
    """Test the exact feature extraction process from voice_model_server.py"""
    print("\n🔍 Testing Feature Extraction Process")
    print("=" * 50)
    
    # Generate test audio similar to the test script
    print("\n1. Generating test audio...")
    duration = 3.0
    sample_rate = 22050
    frequency = 440
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    signal = 0.3 * np.sin(2 * np.pi * frequency * t)
    noise = 0.1 * np.random.normal(0, 1, len(signal))
    audio_data = signal + noise
    audio_data = audio_data.astype(np.float32)
    
    print(f"   Generated audio: {len(audio_data)} samples")
    print(f"   Range: [{audio_data.min():.3f}, {audio_data.max():.3f}]")
    print(f"   Mean: {audio_data.mean():.3f}, Std: {audio_data.std():.3f}")
    
    # Test each step of feature extraction
    try:
        print("\n2. Testing MFCC extraction...")
        mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
        mfccs_mean = np.mean(mfccs, axis=1)
        print(f"   ✅ MFCC shape: {mfccs.shape}")
        print(f"   ✅ MFCC mean shape: {mfccs_mean.shape}")
        print(f"   ✅ MFCC mean values: {mfccs_mean}")
        
        print("\n3. Testing spectral features...")
        spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
        spectral_centroids_mean = np.mean(spectral_centroids)
        print(f"   ✅ Spectral centroids: {spectral_centroids_mean}")
        
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)
        spectral_rolloff_mean = np.mean(spectral_rolloff)
        print(f"   ✅ Spectral rolloff: {spectral_rolloff_mean}")
        
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)
        spectral_bandwidth_mean = np.mean(spectral_bandwidth)
        print(f"   ✅ Spectral bandwidth: {spectral_bandwidth_mean}")
        
        print("\n4. Testing ZCR...")
        zcr = librosa.feature.zero_crossing_rate(audio_data)
        zcr_mean = np.mean(zcr)
        print(f"   ✅ ZCR: {zcr_mean}")
        
        print("\n5. Testing chroma features...")
        chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
        chroma_mean = np.mean(chroma, axis=1)
        print(f"   ✅ Chroma shape: {chroma.shape}")
        print(f"   ✅ Chroma mean shape: {chroma_mean.shape}")
        
        print("\n6. Testing tempo extraction...")
        try:
            tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            # Ensure tempo is a scalar value
            if isinstance(tempo, np.ndarray):
                tempo = float(tempo[0]) if len(tempo) > 0 else 120.0
            else:
                tempo = float(tempo)
            print(f"   ✅ Tempo: {tempo}")
        except Exception as e:
            print(f"   ⚠️ Tempo extraction failed: {e}")
            tempo = 120.0
            print(f"   📝 Using default tempo: {tempo}")
        
        print("\n7. Combining features...")
        features = np.concatenate([
            mfccs_mean,
            [spectral_centroids_mean, spectral_rolloff_mean, 
             spectral_bandwidth_mean, zcr_mean, tempo],
            chroma_mean
        ])
        
        print(f"   ✅ Combined features shape: {features.shape}")
        print(f"   ✅ Total features: {len(features)}")
        print(f"   ✅ Feature range: [{features.min():.3f}, {features.max():.3f}]")
        print(f"   ✅ Features: {features}")
        
        print("\n🎉 Feature extraction test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Feature extraction test FAILED: {e}")
        import traceback
        print(f"📋 Full traceback:")
        traceback.print_exc()
        return False

def test_model_loading():
    """Test loading the voice model and preprocessing tools"""
    print("\n🔍 Testing Model Loading")
    print("=" * 50)
    
    # Check model file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    voice_model_dir = os.path.join(project_root, 'Models', 'Voice')
    
    model_file = os.path.join(voice_model_dir, 'best_model1_weights.keras')
    scaler_file = os.path.join(voice_model_dir, 'scaler2.pickle')
    encoder_file = os.path.join(voice_model_dir, 'encoder2.pickle')
    
    print(f"📁 Voice model directory: {voice_model_dir}")
    print(f"📄 Model file: {'✅' if os.path.exists(model_file) else '❌'} {model_file}")
    print(f"📄 Scaler file: {'✅' if os.path.exists(scaler_file) else '❌'} {scaler_file}")
    print(f"📄 Encoder file: {'✅' if os.path.exists(encoder_file) else '❌'} {encoder_file}")
    
    if not all(os.path.exists(f) for f in [model_file, scaler_file, encoder_file]):
        print("❌ Missing model files!")
        return False
    
    try:
        print("\n1. Testing model loading...")
        
        # Try loading the model
        json_path = os.path.join(voice_model_dir, 'Confident_model.json')
        if os.path.exists(json_path):
            print(f"   📄 JSON architecture found: {json_path}")
            with open(json_path, 'r') as json_file:
                model_json = json_file.read()
            model = tf.keras.models.model_from_json(model_json)
            model.load_weights(model_file)
            print("   ✅ Model loaded from JSON + weights")
        else:
            print("   📄 No JSON architecture, loading weights directly")
            model = tf.keras.models.load_model(model_file)
            print("   ✅ Model loaded directly")
        
        print(f"   📊 Model summary:")
        model.summary()
        
        print("\n2. Testing preprocessing tools...")
        import pickle
        
        with open(scaler_file, 'rb') as f:
            scaler = pickle.load(f)
        print("   ✅ Scaler loaded")
        
        with open(encoder_file, 'rb') as f:
            encoder = pickle.load(f)
        print("   ✅ Encoder loaded")
        
        print("\n🎉 Model loading test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Model loading test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Voice Model Debug Test")
    print("📋 Make sure you're running this in VoiceTracking environment")
    print(f"🐍 Python version: {sys.version}")
    print(f"📁 Current directory: {os.getcwd()}")
    
    # Run tests
    feature_test = test_feature_extraction()
    model_test = test_model_loading()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Feature Extraction: {'✅ PASS' if feature_test else '❌ FAIL'}")
    print(f"   Model Loading: {'✅ PASS' if model_test else '❌ FAIL'}")
    
    if feature_test and model_test:
        print("\n🎉 All tests PASSED! Voice model should work correctly.")
    else:
        print("\n❌ Some tests FAILED. Check the errors above.")