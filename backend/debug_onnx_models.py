#!/usr/bin/env python3
"""
Debug ONNX model input/output specifications
"""

import onnxruntime as ort
import os
import numpy as np

def debug_onnx_models():
    """Debug the ONNX model specifications"""
    print("🔍 Debugging ONNX Model Specifications...")
    
    # Get model paths - go up from backend/ to project root, then to Models
    project_root = os.path.dirname(os.path.dirname(__file__))
    base_path = os.path.join(project_root, 'Models', 'Hand', 'dynamic_gestures', 'models')
    
    detector_path = os.path.join(base_path, 'hand_detector.onnx')
    classifier_path = os.path.join(base_path, 'crops_classifier.onnx')
    
    print(f"📁 Base path: {base_path}")
    print(f"🔍 Hand detector path: {detector_path}")
    print(f"🔍 Classifier path: {classifier_path}")
    print(f"📂 Hand detector exists: {os.path.exists(detector_path)}")
    print(f"📂 Classifier exists: {os.path.exists(classifier_path)}")
    
    # Debug hand detector
    if os.path.exists(detector_path):
        print("\n🤖 HAND DETECTOR MODEL:")
        session = ort.InferenceSession(detector_path)
        
        print("📥 Input specifications:")
        for i, input_info in enumerate(session.get_inputs()):
            print(f"  Input {i}: {input_info.name}")
            print(f"    Shape: {input_info.shape}")
            print(f"    Type: {input_info.type}")
        
        print("📤 Output specifications:")
        for i, output_info in enumerate(session.get_outputs()):
            print(f"  Output {i}: {output_info.name}")
            print(f"    Shape: {output_info.shape}")
            print(f"    Type: {output_info.type}")
        
        # Test with correct input
        print("\n🧪 Testing with sample input:")
        try:
            input_name = session.get_inputs()[0].name
            input_shape = session.get_inputs()[0].shape
            
            # Create sample input
            if input_shape[2] and input_shape[3]:
                sample_input = np.random.rand(1, 3, input_shape[2], input_shape[3]).astype(np.float32)
            else:
                sample_input = np.random.rand(1, 3, 240, 320).astype(np.float32)
            
            print(f"🔢 Sample input shape: {sample_input.shape}")
            
            outputs = session.run(None, {input_name: sample_input})
            
            print(f"✅ Model inference successful!")
            print(f"📊 Number of outputs: {len(outputs)}")
            for i, output in enumerate(outputs):
                print(f"  Output {i} shape: {output.shape}")
                print(f"  Output {i} type: {type(output)}")
                if hasattr(output, 'dtype'):
                    print(f"  Output {i} dtype: {output.dtype}")
                # Show sample values
                if output.size > 0:
                    print(f"  Output {i} sample values: {output.flat[:5]}")
                else:
                    print(f"  Output {i} is empty")
        
        except Exception as e:
            print(f"❌ Model test failed: {e}")
    
    # Debug gesture classifier
    if os.path.exists(classifier_path):
        print("\n🎯 GESTURE CLASSIFIER MODEL:")
        session = ort.InferenceSession(classifier_path)
        
        print("📥 Input specifications:")
        for i, input_info in enumerate(session.get_inputs()):
            print(f"  Input {i}: {input_info.name}")
            print(f"    Shape: {input_info.shape}")
            print(f"    Type: {input_info.type}")
        
        print("📤 Output specifications:")
        for i, output_info in enumerate(session.get_outputs()):
            print(f"  Output {i}: {output_info.name}")
            print(f"    Shape: {output_info.shape}")
            print(f"    Type: {output_info.type}")

if __name__ == "__main__":
    debug_onnx_models()