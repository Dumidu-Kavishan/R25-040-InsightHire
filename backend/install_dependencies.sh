#!/bin/bash

# InsightHire Python 3.12 Compatible Installation Script
echo "🚀 Installing InsightHire dependencies for Python 3.12..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "📍 Python version: $python_version"

# Upgrade pip first
echo "📦 Upgrading pip..."
python3 -m pip install --upgrade pip

# Install setuptools and wheel first
echo "🔧 Installing build tools..."
python3 -m pip install --upgrade setuptools wheel

# Install critical dependencies first
echo "🎯 Installing core dependencies..."

# Install numpy first (required by many other packages)
python3 -m pip install "numpy>=1.24.0,<1.27.0"

# Install basic packages
python3 -m pip install flask==3.0.0
python3 -m pip install flask-cors==4.0.0
python3 -m pip install python-dotenv==1.0.0
python3 -m pip install requests==2.31.0

# Install computer vision packages
echo "👁️ Installing computer vision packages..."
python3 -m pip install opencv-python==4.8.1.78
python3 -m pip install Pillow>=10.0.0

# Install machine learning packages
echo "🤖 Installing machine learning packages..."
python3 -m pip install scikit-learn==1.3.2
python3 -m pip install joblib==1.3.2

# Install TensorFlow (Python 3.12 compatible)
echo "🧠 Installing TensorFlow..."
python3 -m pip install tensorflow==2.15.0

# Install audio processing (with specific versions for Python 3.12)
echo "🎵 Installing audio processing packages..."
python3 -m pip install scipy==1.11.4
python3 -m pip install llvmlite==0.41.1
python3 -m pip install numba==0.58.1
python3 -m pip install soundfile==0.12.1
python3 -m pip install librosa==0.10.1

# Install MediaPipe (Python 3.12 compatible)
echo "👋 Installing MediaPipe..."
python3 -m pip install mediapipe==0.10.8

# Install Firebase
echo "🔥 Installing Firebase..."
python3 -m pip install firebase-admin==6.4.0

# Install SocketIO
echo "🔌 Installing SocketIO..."
python3 -m pip install python-socketio==5.10.0
python3 -m pip install flask-socketio==5.3.6

# Install pandas
echo "📊 Installing pandas..."
python3 -m pip install pandas==2.1.4

echo "✅ All dependencies installed successfully!"

# Test critical imports
echo "🧪 Testing critical imports..."

python3 -c "
import sys
print(f'Python version: {sys.version}')

# Test imports
imports_to_test = [
    ('flask', 'Flask'),
    ('cv2', 'OpenCV'),
    ('numpy', 'NumPy'),
    ('tensorflow', 'TensorFlow'),
    ('librosa', 'Librosa'),
    ('mediapipe', 'MediaPipe'),
    ('firebase_admin', 'Firebase Admin'),
    ('sklearn', 'Scikit-learn'),
    ('pandas', 'Pandas')
]

failed_imports = []
for module, name in imports_to_test:
    try:
        __import__(module)
        print(f'✅ {name} imported successfully')
    except ImportError as e:
        print(f'❌ {name} import failed: {e}')
        failed_imports.append(name)

if failed_imports:
    print(f'\\n⚠️  Failed imports: {failed_imports}')
    print('You may need to install these manually or check for compatibility issues.')
else:
    print('\\n🎉 All critical packages imported successfully!')
"

echo ""
echo "🔧 Next steps:"
echo "1. Test the models: python3 -c 'from models.face_model import FaceStressDetector; print(\"Models working!\")'"
echo "2. Start the server: python3 app.py"
echo "3. In another terminal: cd ../frontend && npm start"
