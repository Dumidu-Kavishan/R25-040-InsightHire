#!/bin/bash

# InsightHire Model Setup and Installation Script
# This script installs dependencies and tests model loading

echo "🚀 Setting up InsightHire AI Models..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check if Models directory exists
if [ ! -d "../Models" ]; then
    echo "❌ Error: Models directory not found. Please ensure the Models folder is in the parent directory."
    exit 1
fi

echo "✅ Models directory found"

# List available models
echo "📋 Available models:"
find ../Models -name "*.h5" -o -name "*.keras" -o -name "*.pkl" -o -name "*.pickle" | while read model; do
    echo "  📄 $model"
done

# Test model loading
echo "🧪 Testing model loading..."

# Test Face Model
echo "  Testing Face Stress Detection..."
python3 -c "
import sys
sys.path.append('model_scripts')
try:
    from face_stress_detection import FaceStressDetector
    detector = FaceStressDetector()
    if detector.model is not None:
        print('  ✅ Face model loaded successfully')
    else:
        print('  ⚠️  Face model not loaded (file may be missing)')
except Exception as e:
    print(f'  ❌ Face model error: {e}')
"

# Test Hand Model
echo "  Testing Hand Confidence Detection..."
python3 -c "
try:
    from models.hand_model import HandConfidenceDetector
    detector = HandConfidenceDetector()
    if detector.model is not None:
        print('  ✅ Hand model loaded successfully')
    else:
        print('  ⚠️  Hand model not loaded (file may be missing)')
except Exception as e:
    print(f'  ❌ Hand model error: {e}')
"

# Test Eye Model
echo "  Testing Eye Confidence Detection..."
python3 -c "
import sys
sys.path.append('model_scripts')
try:
    from eye_confidence_detection import EyeConfidenceDetector
    detector = EyeConfidenceDetector()
    if detector.model is not None:
        print('  ✅ Eye model loaded successfully')
    else:
        print('  ⚠️  Eye model not loaded (file may be missing)')
except Exception as e:
    print(f'  ❌ Eye model error: {e}')
"

# Test Voice Model
echo "  Testing Voice Confidence Detection..."
python3 -c "
try:
    from models.voice_model import VoiceConfidenceDetector
    detector = VoiceConfidenceDetector()
    if detector.model is not None:
        print('  ✅ Voice model loaded successfully')
    else:
        print('  ⚠️  Voice model not loaded (file may be missing)')
except Exception as e:
    print(f'  ❌ Voice model error: {e}')
"

# Test Real-time Analyzer
echo "  Testing Real-time Analyzer Integration..."
python3 -c "
try:
    from realtime_analyzer import RealTimeAnalyzer
    analyzer = RealTimeAnalyzer('test_session', 'test_user')
    print('  ✅ Real-time analyzer initialized successfully')
except Exception as e:
    print(f'  ❌ Real-time analyzer error: {e}')
"

echo ""
echo "🎉 Model setup complete!"
echo ""
echo "📋 Setup Summary:"
echo "  - Dependencies installed"
echo "  - Model files checked"
echo "  - Model loading tested"
echo ""
echo "🔧 Next steps:"
echo "  1. Start the Flask server: python app.py"
echo "  2. Start the frontend: cd ../frontend && npm start"
echo "  3. Test the screen recording functionality"
echo ""
echo "💡 Tips:"
echo "  - Make sure your webcam/microphone permissions are enabled"
echo "  - Check the browser console for any errors"
echo "  - Monitor the Flask server logs for analysis results"
