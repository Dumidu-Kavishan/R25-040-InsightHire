# InsightHire - Quick Start Guide

## 🚀 Welcome to InsightHire!

InsightHire is a complete AI-powered candidate interview monitoring platform that analyzes candidates in real-time using four key components:

1. **Face Analysis (Stress Detection)** - Detects stress from facial expressions
2. **Hand Gesture Recognition (Confidence)** - Analyzes confidence through hand movements  
3. **Eye Tracking (Confidence)** - Monitors gaze patterns for confidence assessment
4. **Voice Analysis (Confidence)** - Evaluates confidence through speech patterns

## 📋 Prerequisites

- **Python 3.8+** (for backend)
- **Node.js 16+** (for frontend)
- **npm** (comes with Node.js)
- **Webcam and microphone** (for real-time analysis)

## 🛠️ Installation

### Option 1: Quick Demo
Open `demo.html` in your browser to see a live demonstration of the application's features.

### Option 2: Full Application Setup

#### Backend Setup (Flask + AI Models)

```bash
# Navigate to backend directory
cd InsightHire/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
python app.py
```

The backend will be available at: **http://localhost:5000**

#### Frontend Setup (React Application)

```bash
# Navigate to frontend directory
cd InsightHire/frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend will be available at: **http://localhost:3000**

## 🎯 Quick Usage

1. **Open the application** in your browser at http://localhost:3000
2. **Register/Login** with your credentials
3. **Create a new interview session** from the dashboard
4. **Start the session** and allow camera/microphone access
5. **Monitor real-time analysis** as the AI models process:
   - Face expressions for stress detection
   - Hand gestures for confidence analysis
   - Eye movements for confidence tracking
   - Voice patterns for confidence assessment
6. **View comprehensive results** and recommendations

## 📊 Features

### Real-time Analysis
- **Live video feed** with AI processing
- **Real-time metrics** updating every few seconds
- **Visual indicators** for confidence and stress levels
- **Trend charts** showing performance over time

### AI Models
- **Face Model**: CNN-based facial emotion recognition
- **Hand Model**: MediaPipe hand landmark detection
- **Eye Model**: Gaze tracking with OpenCV
- **Voice Model**: Audio feature extraction with Librosa

### Dashboard Features
- **Session Management**: Create, start, stop, and review sessions
- **Live Monitoring**: Real-time analysis with visual feedback
- **Historical Data**: View past sessions and trends
- **Comprehensive Reports**: Detailed analysis and recommendations

### Multi-platform Support
- **Browser-based interviews**
- **Zoom integration** (via screen recording)
- **Microsoft Teams support**
- **Google Meet compatibility**

## 🔧 Configuration

### Firebase Setup
1. The application uses the existing Firebase configuration in `firebase.json`
2. For production, replace with your own Firebase project credentials
3. Update the configuration in `frontend/src/firebase.js`

### Environment Variables
Copy `.env.example` to `.env` and update as needed:
```bash
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_SOCKET_URL=http://localhost:5000
```

## 🎨 Theme Colors
The application uses a light blue and white theme as requested:
- **Primary Blue**: #2196F3 (Material Design Blue)
- **Dark Blue**: #1976D2 
- **Light Blue**: #E3F2FD
- **White**: #FFFFFF

## 🚨 Troubleshooting

### Common Issues

**Camera/Microphone Access Denied**
- Ensure browser permissions are granted
- Check system privacy settings
- Use HTTPS in production

**Backend Connection Issues**
- Verify Flask server is running on port 5000
- Check firewall settings
- Ensure all dependencies are installed

**Model Loading Errors**
- Verify model files exist in `Models/` directory
- Check file paths in model implementations
- Ensure TensorFlow is properly installed

**Frontend Build Issues**
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version compatibility

## 📱 Browser Compatibility
- **Chrome** (recommended for WebRTC support)
- **Firefox** (full support)
- **Safari** (limited WebRTC support)
- **Edge** (full support)

## 🔒 Security Features
- **Firebase Authentication**
- **Secure WebSocket connections**
- **User session isolation**
- **Data encryption in transit**

## 📈 Performance Tips
- **Use Chrome** for best WebRTC performance
- **Close other tabs** to free up resources
- **Ensure stable internet** for real-time processing
- **Use good lighting** for better face detection

## 🤝 Support

For technical support or questions:
1. Check the main `README.md` for detailed documentation
2. Review the troubleshooting section above
3. Examine console logs for error messages
4. Verify all prerequisites are installed

## 🎉 What's Next?

After setup, you can:
- **Create your first interview session**
- **Test with different lighting conditions**
- **Explore the analytics dashboard**
- **Review generated reports**
- **Customize the interface** as needed

---

**Happy Interviewing with InsightHire! 🎯**
