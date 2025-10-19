# InsightHire

InsightHire is an AI-powered candidate interview monitoring platform that analyzes candidate behavior in real-time using four key components: face (stress detection), hand gestures (confidence), eye tracking (confidence), and voice analysis (confidence).

## Features

- **Real-time AI Analysis**: Monitor candidates using four AI models simultaneously
- **Face Analysis**: Detect stress levels from facial expressions
- **Hand Gesture Recognition**: Analyze confidence through hand movements
- **Eye Tracking**: Monitor gaze patterns for confidence assessment
- **Voice Analysis**: Evaluate confidence through speech patterns
- **Live Dashboard**: Real-time monitoring with charts and analytics
- **Session Management**: Create, start, stop, and review interview sessions
- **Multi-platform Support**: Works with Zoom, Google Meet, Microsoft Teams, and browser-based interviews

## Technology Stack

### Backend
- **Flask**: Web framework with Socket.IO for real-time communication
- **TensorFlow/Keras**: Machine learning models
- **OpenCV**: Computer vision processing
- **MediaPipe**: Hand and face detection
- **Librosa**: Audio processing
- **Firebase**: Database and authentication

### Frontend
- **React**: Modern UI framework
- **Material-UI**: Beautiful, responsive components
- **Socket.IO Client**: Real-time communication
- **Chart.js**: Data visualization
- **React Webcam**: Camera integration

## Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the backend server:
```bash
python start.py
```

Or manually:
```bash
python app.py
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend: http://localhost:5000

## Usage

### 1. User Registration/Login
- Create an account or login with existing credentials
- Firebase authentication ensures secure access

### 2. Create Interview Session
- Click "New Interview Session" on the dashboard
- Enter candidate details (name, position, platform, notes)
- Session is created and ready to start

### 3. Start Interview Monitoring
- Click "Start" on a session to begin real-time monitoring
- Allow camera and microphone access when prompted
- AI models will begin analyzing in real-time

### 4. Monitor in Real-time
- **Face Stress**: Green = calm, Red = stressed
- **Hand Confidence**: Positive gestures increase confidence score
- **Eye Confidence**: Direct gaze indicates confidence
- **Voice Confidence**: Tone and clarity analysis
- **Live Charts**: Visual trends of confidence and stress over time

### 5. Review Results
- Stop the session to view comprehensive analysis
- Export reports and recommendations
- Historical data available for comparison

## AI Models

### Face Model (Stress Detection)
- Uses CNN for facial emotion recognition
- Detects stress levels from facial expressions
- Real-time processing at 1 FPS

### Hand Model (Confidence Detection)
- MediaPipe for hand landmark detection
- Analyzes gesture patterns for confidence indicators
- Processes hand movements and positions

### Eye Model (Confidence Detection)
- Eye tracking using OpenCV cascades
- Analyzes gaze direction and eye contact
- Confidence based on direct vs. wandering gaze

### Voice Model (Confidence Detection)
- Audio feature extraction using Librosa
- MFCC, spectral, and prosodic features
- Real-time confidence scoring

## API Endpoints

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update user profile

### Sessions
- `POST /api/sessions` - Create new session
- `GET /api/sessions` - Get all user sessions
- `GET /api/sessions/{id}` - Get specific session
- `POST /api/sessions/{id}/start` - Start session
- `POST /api/sessions/{id}/stop` - Stop session
- `GET /api/sessions/{id}/results` - Get session results

### WebSocket Events
- `join_session` - Join session room
- `video_frame` - Send video frame for analysis
- `audio_data` - Send audio data for analysis
- `live_results` - Receive real-time analysis results

## Configuration

### Firebase Setup
1. Create a Firebase project
2. Download service account key
3. Replace `firebase.json` with your credentials
4. Update Firebase config in frontend

### Environment Variables
```bash
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_SOCKET_URL=http://localhost:5000
```

## Architecture

```
InsightHire/
├── backend/
│   ├── models/          # AI model implementations
│   │   ├── face_model.py
│   │   ├── hand_model.py
│   │   ├── eye_model.py
│   │   └── voice_model.py
│   ├── utils/           # Database and utilities
│   │   └── database.py
│   ├── app.py          # Main Flask application
│   ├── realtime_analyzer.py  # Real-time analysis engine
│   ├── firebase_config.py    # Firebase configuration
│   ├── start.py        # Startup script
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Application pages
│   │   ├── contexts/    # React contexts
│   │   └── services/    # API and socket services
│   └── package.json
└── Models/             # Pre-trained AI models
    ├── Face/           # Stress detection model
    ├── Hand/           # Hand confidence model
    ├── Eye/            # Eye tracking model
    └── Voice/          # Voice analysis model
```

## Features in Detail

### Real-time Processing
- Video frames processed at 1 FPS
- Audio analysis every 2 seconds
- Live updates sent to frontend every 3 seconds
- Efficient queue management for smooth performance

### Security
- Firebase Authentication
- Secure WebSocket connections
- User session isolation
- Data encryption in transit

### Scalability
- Threaded processing for multiple sessions
- Queue-based frame processing
- Background tasks for periodic updates
- Efficient memory management

## Troubleshooting

### Common Issues

1. **Camera/Microphone Access Denied**
   - Ensure browser permissions are granted
   - Check system privacy settings
   - Try HTTPS if on remote server

2. **Model Loading Errors**
   - Verify all model files are present in Models/ directory
   - Check file paths in model implementations
   - Ensure proper TensorFlow/Keras versions

3. **Socket Connection Issues**
   - Check firewall settings
   - Verify correct server URL
   - Ensure backend is running

4. **Firebase Authentication Errors**
   - Verify Firebase credentials
   - Check project configuration
   - Ensure proper API keys

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please contact the development team or create an issue in the repository.

---

**InsightHire** - Revolutionizing interview monitoring with AI-powered insights.
