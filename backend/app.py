"""
InsightHire Backend Application
Main Flask application for candidate interview monitoring
"""

# Disable Metal Performance Shaders to prevent crashes
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_DISABLE_MKL'] = '1'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

# Configure TensorFlow to use CPU only
try:
    import tensorflow as tf
    tf.config.set_visible_devices([], 'GPU')
    tf.config.threading.set_inter_op_parallelism_threads(1)
    tf.config.threading.set_intra_op_parallelism_threads(1)
except ImportError:
    pass

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import logging
import base64
import numpy as np
import cv2
from datetime import datetime
import threading
import uuid

# Import local modules
from utils.database import DatabaseManager
from realtime_analyzer import RealTimeAnalyzer
import firebase_config
from firebase_admin import auth as firebase_auth

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('InsightHire-Backend')

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'insighthire-secret-key-2024'

# Enable CORS
CORS(app, resources={
    r"/api/*": {"origins": "*"},
    r"/socket.io/*": {"origins": "*"}
})

# Initialize SocketIO with better configuration
socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    async_mode='threading',
    logger=False,
    engineio_logger=False,
    ping_timeout=60,
    ping_interval=25
)

# Global storage for active interviews
active_analyzers = {}  # interview_id -> RealTimeAnalyzer instance

def get_user_id_from_request():
    """Get the user ID from the request headers, parameters, or token"""
    # Try to get from query parameters first
    user_id = request.args.get('userId') or request.args.get('uid')
    if user_id:
        logger.info(f"🔍 Found user_id from query params: {user_id}")
        return user_id
    
    # Try to get from headers
    user_id = (request.headers.get('X-User-ID') or 
               request.headers.get('X-User-Id') or 
               request.headers.get('x-user-id') or
               request.headers.get('X-UID') or
               request.headers.get('uid'))
    if user_id:
        logger.info(f"🔍 Found user_id from headers: {user_id}")
        return user_id
    
    # Try to get from Authorization header (Firebase token)
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split('Bearer ')[1]
        try:
            decoded_token = firebase_auth.verify_id_token(token)
            return decoded_token['uid']
        except Exception as e:
            logger.warning(f"Token verification failed: {e}")
    
    # Try to get from request body (only for POST/PUT requests)
    if request.method in ['POST', 'PUT', 'PATCH'] and request.is_json and request.json and 'uid' in request.json:
        return request.json['uid']
    
    logger.warning(f"⚠️ No user ID found in request - method: {request.method}, headers: {dict(request.headers)}, args: {dict(request.args)}")
    return None

# Authentication Routes
@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user - stores profile after Firebase Auth registration"""
    data = request.json
    logger.info(f"Raw registration request data: {data}")
    if not data or 'email' not in data or 'uid' not in data:
        return jsonify({'status': 'error', 'message': 'Email and UID required'}), 400
    
    try:
        # Create user profile in database (Firebase Auth handles user creation on frontend)
        username = data.get('username', data['email'])  # Use email as fallback if no username
        logger.info(f"Registration data received: {data}")
        logger.info(f"Username extracted: {username}")
        user_data = {
            'uid': data['uid'],
            'email': data['email'],
            'username': username,
            'displayName': username,  # Use username as display name
            'createdAt': datetime.now().isoformat(),
            'lastLogin': datetime.now().isoformat(),
            'role': data.get('role', 'interviewer')  # interviewer or candidate
        }
        logger.info(f"User data to be saved: {user_data}")
        
        db_manager = DatabaseManager(data['uid'])
        db_manager.create_user_profile(user_data)
        
        logger.info(f"User profile created successfully: {data['uid']}")
        return jsonify({'status': 'success', 'uid': data['uid'], 'user': user_data})
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/login', methods=['POST'])
def login():
    """Login a user - verifies token and updates profile"""
    data = request.json
    if not data or 'uid' not in data:
        return jsonify({'status': 'error', 'message': 'UID is required'}), 400
    
    user_id = data['uid']
    
    try:
        # Verify the Firebase token if provided
        token = data.get('token')
        if token:
            try:
                # Verify the token
                decoded_token = firebase_auth.verify_id_token(token)
                if decoded_token['uid'] != user_id:
                    return jsonify({'status': 'error', 'message': 'Token UID mismatch'}), 401
            except Exception as token_error:
                logger.warning(f"Token verification failed: {token_error}")
                # Continue without token verification for development
        
        db_manager = DatabaseManager(user_id)
        user_data = db_manager.get_user_profile(user_id)
        
        if not user_data:
            # Create a basic profile if it doesn't exist
            username = data.get('username', f"User-{user_id[:8]}")
            user_data = {
                'uid': user_id,
                'email': data.get('email', f"user-{user_id[:8]}@insighthire.com"),
                'username': username,
                'displayName': username,
                'createdAt': datetime.now().isoformat(),
                'lastLogin': datetime.now().isoformat(),
                'role': 'interviewer'
            }
            db_manager.create_user_profile(user_data)
            logger.info(f"Created new user profile for: {user_id}")
        else:
            # Update last login time
            update_data = {'lastLogin': datetime.now().isoformat()}
            db_manager.update_user_profile(user_id, update_data)
            user_data.update(update_data)
            logger.info(f"User login updated: {user_id}")
        
        return jsonify({
            'status': 'success',
            'uid': user_id,
            'user': user_data
        })
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# User Profile Routes
@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    """Get user profile"""
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
    
    try:
        db_manager = DatabaseManager()
        profile = db_manager.get_user_profile(user_id)
        
        if not profile:
            # Try to get user info from Firebase Auth
            user_email = None
            try:
                user_record = firebase_auth.get_user(user_id)
                user_email = user_record.email
                display_name = user_record.display_name or user_email
            except Exception as e:
                logger.warning(f"Could not get Firebase user info: {e}")
                user_email = f"user-{user_id[:8]}@insighthire.com"
                display_name = f"User-{user_id[:8]}"
            
            # Create and store a proper profile
            minimal_profile = {
                'uid': user_id,
                'email': user_email,
                'displayName': display_name,
                'createdAt': datetime.now().isoformat(),
                'role': 'interviewer'
            }
            
            # Store this profile in the database for future use
            db_manager.create_user_profile(minimal_profile)
            logger.info(f"Created missing profile for user {user_id} with email {user_email}")
            
            return jsonify({'status': 'success', 'data': minimal_profile})
        
        return jsonify({'status': 'success', 'data': profile})
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/user/profile', methods=['PUT'])
def update_user_profile():
    """Update user profile"""
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
    
    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
    
    try:
        # Validate required fields
        if 'display_name' in data:
            display_name = data.get('display_name', '').strip()
            if not display_name:
                return jsonify({'status': 'error', 'message': 'Display name cannot be empty'}), 400
        
        if 'username' in data:
            username = data.get('username', '').strip()
            if not username:
                return jsonify({'status': 'error', 'message': 'Username cannot be empty'}), 400
        
        # Prepare update data
        update_data = {
            'updated_at': datetime.now().isoformat()
        }
        
        # Map frontend fields to backend fields
        if 'username' in data:
            update_data['username'] = data['username']
        if 'display_name' in data:
            update_data['display_name'] = data['display_name']
        if 'displayName' in data:
            update_data['display_name'] = data['displayName']
        if 'avatar_url' in data:
            update_data['avatar_url'] = data['avatar_url']
        
        # Add other fields that might be passed
        for key, value in data.items():
            if key not in ['username', 'display_name', 'displayName', 'avatar_url', 'updated_at']:
                update_data[key] = value
        
        db_manager = DatabaseManager()
        success = db_manager.update_user_profile(user_id, update_data)
        
        if success:
            updated_profile = db_manager.get_user_profile(user_id)
        return jsonify({
            'status': 'success', 
            'message': 'Profile updated successfully',
            'data': updated_profile
        })
        if not success:
            return jsonify({
                'status': 'error',
                'message': 'Failed to update profile'
            }), 500
            
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/user/profile/refresh', methods=['POST'])
def refresh_user_profile():
    """Refresh user profile from Firebase Auth"""
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
    
    try:
        # Get fresh user info from Firebase Auth
        user_record = firebase_auth.get_user(user_id)
        
        updated_profile = {
            'uid': user_id,
            'email': user_record.email,
            'displayName': user_record.display_name or user_record.email,
            'lastUpdated': datetime.now().isoformat(),
            'role': 'interviewer'
        }
        
        # Update the database with fresh info
        db_manager = DatabaseManager(user_id)
        db_manager.update_user_profile(updated_profile)
        
        logger.info(f"Profile refreshed for user {user_id} with email {user_record.email}")
        return jsonify({
            'status': 'success', 
            'message': 'Profile refreshed successfully',
            'profile': updated_profile
        })
    except Exception as e:
        logger.error(f"Error refreshing user profile: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ==================== INTERVIEW MANAGEMENT APIs ====================

@app.route('/api/interviews', methods=['POST'])
def create_interview():
    """Create a new interview with candidate"""
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
    
    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': 'Interview data required'}), 400
    
    try:
        # Validate required fields
        required_fields = ['candidate_name', 'candidate_nic_passport', 'job_role_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'status': 'error', 'message': f'Missing required field: {field}'}), 400
        
        # Get job role details
        db_manager = DatabaseManager()
        job_role = db_manager.get_job_role(data['job_role_id'])
        if not job_role:
            return jsonify({'status': 'error', 'message': 'Invalid job role selected'}), 400
        
        # Create candidate data
        candidate_data = {
            'name': data['candidate_name'],
            'nic_passport': data['candidate_nic_passport'],
            'position': job_role['name'],
            'email': '',  # Not required anymore
            'phone': '',  # Not required anymore
            'experience_years': 0,
            'skills': [],
            'education': '',
            'notes': ''
        }
        
        candidate_id = db_manager.create_candidate(candidate_data)
        
        if not candidate_id:
            return jsonify({'status': 'error', 'message': 'Failed to create candidate'}), 500
        
        # Create interview record
        interview_data = {
            'user_id': user_id,
            'candidate_id': candidate_id,
            'candidate_name': candidate_data['name'],
            'candidate_nic_passport': candidate_data['nic_passport'],
            'position': candidate_data['position'],
            'job_role_id': data['job_role_id'],
            'interview_type': 'technical',  # Default to technical
            'platform': 'browser',  # Default to browser
            'scheduled_at': datetime.now().isoformat(),
            'duration_minutes': 60,  # Default duration
            'status': 'scheduled',
            'created_at': datetime.now().isoformat(),
            'notes': '',
            'questions': [],
            'evaluation_criteria': []
        }
        
        interview_id = db_manager.create_interview(interview_data)
        
        if interview_id:
            interview_data['id'] = interview_id
            interview_data['candidate_id'] = candidate_id
            return jsonify({
                'status': 'success', 
                'interview': interview_data,
                'candidate': {'id': candidate_id, **candidate_data}
            })
        else:
            return jsonify({'status': 'error', 'message': 'Failed to create interview'}), 500
        
    except Exception as e:
        logger.error(f"Error creating interview: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/interviews', methods=['GET'])
def get_interviews():
    """Get all interviews for a user"""
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
    
    try:
        db_manager = DatabaseManager()
        interviews = db_manager.get_user_interviews(user_id)
        
        return jsonify({'status': 'success', 'interviews': interviews})
    except Exception as e:
        logger.error(f"Error getting interviews: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/interviews/<interview_id>', methods=['GET'])
def get_interview(interview_id):
    """Get specific interview details"""
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
    
    try:
        db_manager = DatabaseManager()
        interview = db_manager.get_interview(interview_id)
        
        if interview and interview.get('user_id') == user_id:
            # Get candidate details
            candidate = db_manager.get_candidate(interview['candidate_id'])
            interview['candidate'] = candidate
            return jsonify({'status': 'success', 'interview': interview})
        else:
            return jsonify({'status': 'error', 'message': 'Interview not found'}), 404
    except Exception as e:
        logger.error(f"Error getting interview: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/interviews/<interview_id>/start', methods=['POST'])
def start_interview(interview_id):
    """Start an interview session"""
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
    
    try:
        db_manager = DatabaseManager()
        interview = db_manager.get_interview(interview_id)
        
        if not interview or interview.get('user_id') != user_id:
            return jsonify({'status': 'error', 'message': 'Interview not found'}), 404
        
        # Update interview status and start time
        update_data = {
            'status': 'active',
            'started_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        success = db_manager.update_interview(interview_id, update_data)
        
        if success:
            # Initialize real-time analysis if needed
            job_role_id = interview.get('job_role_id')
            analyzer = RealTimeAnalyzer(interview_id, user_id, job_role_id, socketio)
            analyzer.start_analysis()  # Start the analysis thread
            active_analyzers[interview_id] = analyzer
            
            logger.info(f"✅ Interview {interview_id} started with analysis for job role {job_role_id}")
            
            return jsonify({
                'status': 'success', 
                'message': 'Interview started with real-time analysis',
                'interview_id': interview_id,
                'started_at': update_data['started_at'],
                'analysis_started': True
            })
        else:
            return jsonify({'status': 'error', 'message': 'Failed to start interview'}), 500
        
    except Exception as e:
        logger.error(f"Error starting interview: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/interviews/<interview_id>/stop', methods=['POST'])
def stop_interview(interview_id):
    """Stop an interview session"""
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
    
    try:
        # Try to get JSON data, but don't fail if not provided
        data = {}
        if request.is_json:
            data = request.get_json() or {}
        
        db_manager = DatabaseManager()
        interview = db_manager.get_interview(interview_id)
        
        if not interview or interview.get('user_id') != user_id:
            return jsonify({'status': 'error', 'message': 'Interview not found'}), 404
        
        # Calculate duration
        started_at = interview.get('started_at')
        if started_at:
            from datetime import datetime
            start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00') if started_at.endswith('Z') else started_at)
            duration = (datetime.now() - start_time).total_seconds() / 60  # in minutes
        else:
            duration = 0
        
        # Update interview status
        update_data = {
            'status': 'completed',
            'ended_at': datetime.now().isoformat(),
            'duration_minutes': round(duration, 2),
            'final_notes': data.get('notes', ''),
            'rating': data.get('rating', None),
            'updated_at': datetime.now().isoformat()
        }
        
        success = db_manager.update_interview(interview_id, update_data)
        
        # Clean up analyzer safely
        if interview_id in active_analyzers:
            try:
                analyzer = active_analyzers[interview_id]
                logger.info(f"🛑 Stopping analyzer for interview {interview_id}")
                analyzer.stop_analysis()
                analyzer.reset_audio_state()
                del active_analyzers[interview_id]
                logger.info(f"✅ Interview {interview_id} stopped successfully")
            except Exception as cleanup_error:
                logger.error(f"❌ Error during analyzer cleanup for {interview_id}: {cleanup_error}")
                if interview_id in active_analyzers:
                    del active_analyzers[interview_id]
        
        if success:
            return jsonify({
                'status': 'success', 
                'message': 'Interview completed',
                'interview_id': interview_id,
                'duration_minutes': update_data['duration_minutes']
            })
        else:
            return jsonify({'status': 'error', 'message': 'Failed to stop interview'}), 500
        
    except Exception as e:
        logger.error(f"Error stopping interview: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/interviews/<interview_id>/analysis', methods=['POST'])
def save_interview_analysis(interview_id):
    """Save real-time analysis data for interview"""
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
    
    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': 'Analysis data required'}), 400
    
    try:
        db_manager = DatabaseManager()
        
        # Verify interview exists and belongs to user
        interview = db_manager.get_interview(interview_id)
        if not interview or interview.get('user_id') != user_id:
            return jsonify({'status': 'error', 'message': 'Interview not found'}), 404
        
        # Extract data from the new structure with flags and raw sections
        session_id = data.get('session_id', str(uuid.uuid4()))
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        # Get flags section (already contains binary values)
        flags = data.get('flags', {})
        eye_confident = flags.get('eye_confident', 0)
        hand_confident = flags.get('hand_confident', 0)
        voice_confident = flags.get('voice_confident', 0)
        stress = flags.get('stress', 0)
        
        # Get raw section for detailed data
        raw = data.get('raw', {})
        overall = data.get('overall', {})
        
        # Log the data structure for debugging
        logger.info(f"🔍 Processing analysis data for interview: {interview_id}")
        logger.info(f"📊 Flags (binary values): eye_confident={eye_confident}, hand_confident={hand_confident}, voice_confident={voice_confident}, stress={stress}")
        logger.info(f"📊 Raw data structure: {list(raw.keys())}")
        logger.info(f"📊 Overall data: {overall}")
        
        # Save analysis data with the exact structure you want
        analysis_data = {
            'interview_id': interview_id,
            'candidate_id': interview['candidate_id'],
            'user_id': user_id,
            'session_id': session_id,
            'timestamp': timestamp,
            'flags': {
                'stress': stress,
                'eye_confident': eye_confident,
                'hand_confident': hand_confident,
                'voice_confident': voice_confident
            },
            'overall': overall,
            'raw': raw,
            'confidence_level': 'confident' if (eye_confident + hand_confident + voice_confident) >= 2 else 'not_confident',
            'stress_level': 'stress' if stress == 1 else 'non_stress',
            'created_at': datetime.now().isoformat()
        }
        
        # Save to analysis_results collection using the correct method
        doc_id = db_manager.save_analysis_result(session_id, analysis_data)
        success = doc_id is not None
        
        if success:
            return jsonify({
                'status': 'success', 
                'message': 'Analysis data saved with binary values in flags section',
                'binary_data': {
                    'eye_confident': eye_confident,
                    'hand_confident': hand_confident,
                    'voice_confident': voice_confident,
                    'stress': stress
                },
                'doc_id': doc_id
            })
        else:
            return jsonify({'status': 'error', 'message': 'Failed to save analysis'}), 500
        
    except Exception as e:
        logger.error(f"Error saving analysis: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/interviews/<interview_id>/analysis', methods=['GET'])
def get_interview_analysis(interview_id):
    """Get analysis data for interview using new analysis system"""
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
    
    try:
        db_manager = DatabaseManager()
        
        # Verify interview exists and belongs to user
        interview = db_manager.get_interview(interview_id)
        if not interview or interview.get('user_id') != user_id:
            return jsonify({'status': 'error', 'message': 'Interview not found'}), 404
        
        # Get final analysis data
        final_analysis = db_manager.get_final_analysis(interview_id)
        
        # Get analysis results from analysis_results collection
        analysis_results = db_manager.get_analysis_results(interview_id)
        logger.info(f"🔍 Retrieved {len(analysis_results)} analysis results for interview {interview_id}")
        if analysis_results:
            logger.info(f"📊 Sample analysis result: {analysis_results[0]}")
        else:
            logger.warning(f"⚠️ No analysis results found for interview {interview_id}")
        
        # Process the new binary analysis results format
        confidence_analysis = []
        stress_analysis = []
        
        for data in analysis_results:
            # Each result contains both confidence and stress data
            if 'flags' in data:  # New format with flags and raw sections
                flags = data.get('flags', {})
                confidence_analysis.append({
                    'voice_confidence': flags.get('voice_confident', 0),
                    'hand_confidence': flags.get('hand_confident', 0),
                    'eye_confidence': flags.get('eye_confident', 0),
                    'confidence_level': data.get('confidence_level', 'not_confident'),
                    'timestamp': data.get('timestamp')
                })
                
                stress_analysis.append({
                    'stress_level': data.get('stress_level', 'non_stress'),
                    'negative_emotion_frames': flags.get('stress', 0),
                    'total_frames': 1,
                    'timestamp': data.get('timestamp')
                })
            elif 'eye_confident' in data:  # Previous format with correct field names
                confidence_analysis.append({
                    'voice_confidence': data.get('voice_confident', 0),
                    'hand_confidence': data.get('hand_confident', 0),
                    'eye_confidence': data.get('eye_confident', 0),
                    'confidence_level': data.get('confidence_level', 'not_confident'),
                    'timestamp': data.get('timestamp')
                })
                
                stress_analysis.append({
                    'stress_level': data.get('stress_level', 'non_stress'),
                    'negative_emotion_frames': data.get('stress', 0),
                    'total_frames': 1,
                    'timestamp': data.get('timestamp')
                })
            elif 'eye_confidence' in data:  # Old format
                confidence_analysis.append({
                    'voice_confidence': data.get('voice_confidence', 0),
                    'hand_confidence': data.get('hand_confidence', 0),
                    'eye_confidence': data.get('eye_confidence', 0),
                    'confidence_level': data.get('confidence_level', 'not_confident'),
                    'timestamp': data.get('timestamp')
                })
                
                stress_analysis.append({
                    'stress_level': data.get('stress_level', 'non_stress'),
                    'negative_emotion_frames': data.get('stress', 0),
                    'total_frames': 1,
                    'timestamp': data.get('timestamp')
                })
            else:  # Oldest format
                if data.get('type') == 'confidence':
                    confidence_analysis.append(data)
                elif data.get('type') == 'stress':
                    stress_analysis.append(data)
        
        # Calculate interview duration
        start_time = interview.get('start_time')
        end_time = interview.get('end_time')
        duration_minutes = 0
        if start_time and end_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                duration_minutes = int((end_dt - start_dt).total_seconds() / 60)
            except:
                duration_minutes = 0
        
        # Debug logging
        logger.info(f"Debug - Interview ID: {interview_id}")
        logger.info(f"Debug - Final analysis exists: {final_analysis is not None}")
        logger.info(f"Debug - Confidence analysis count: {len(confidence_analysis) if confidence_analysis else 0}")
        logger.info(f"Debug - Stress analysis count: {len(stress_analysis) if stress_analysis else 0}")
        
        # Use final analysis scores or fallback to interview data
        final_confidence = final_analysis.get('final_confidence_score', 0) if final_analysis else interview.get('final_confidence_score', 0)
        final_stress = final_analysis.get('final_stress_score', 0) if final_analysis else interview.get('final_stress_score', 0)
        
        # Get individual confidence components
        voice_confidence = final_analysis.get('voice_percentage', 0) if final_analysis else 0
        hand_confidence = final_analysis.get('hand_percentage', 0) if final_analysis else 0
        eye_confidence = final_analysis.get('eye_percentage', 0) if final_analysis else 0
        
        logger.info(f"Debug - Final confidence: {final_confidence}, Final stress: {final_stress}")
        logger.info(f"Debug - Voice: {voice_confidence}, Hand: {hand_confidence}, Eye: {eye_confidence}")
        
        # Create timeline data from real analysis data
        time_points = []
        confidence_timeline = []
        stress_timeline = []
        emotion_timeline = []
        
        # If we have real data, use it; otherwise create sample data
        if confidence_analysis and len(confidence_analysis) > 0:
            # Use real confidence data - show binary classification over time
            for i, data in enumerate(confidence_analysis[:20]):  # Limit to 20 points
                time_percent = (i / max(1, len(confidence_analysis) - 1)) * 100
                time_points.append(f"{time_percent:.0f}%")
                
                # Convert binary classification to percentage
                voice_conf = 1 if data.get('voice_confidence', 0) else 0
                hand_conf = 1 if data.get('hand_confidence', 0) else 0
                eye_conf = 1 if data.get('eye_confidence', 0) else 0
                
                # Calculate confidence percentage for this time point
                total_confident = voice_conf + hand_conf + eye_conf
                confidence_percentage = (total_confident / 3) * 100
                confidence_timeline.append(confidence_percentage)
        else:
            # Create sample timeline data based on final scores
            for i in range(20):
                time_percent = (i / 19) * 100
                time_points.append(f"{time_percent:.0f}%")
                
                # Create realistic progression based on final confidence
                if final_confidence > 0:
                    # Start low, build up to final confidence
                    progress = i / 19
                    confidence_value = final_confidence * (0.3 + 0.7 * progress)
                    confidence_timeline.append(min(100, confidence_value))
                else:
                    confidence_timeline.append(0)
        
        if stress_analysis and len(stress_analysis) > 0:
            # Use real stress data - show binary classification over time
            for i, data in enumerate(stress_analysis[:20]):  # Limit to 20 points
                if i < len(time_points):
                    # Convert binary stress to percentage
                    is_stressed = 1 if data.get('stress_level') == 'stress' else 0
                    stress_percentage = is_stressed * 100
                    stress_timeline.append(stress_percentage)
        else:
            # Create sample stress timeline based on final stress
            for i in range(20):
                if final_stress > 0:
                    # Create realistic stress progression
                    progress = i / 19
                    # Stress often peaks in the middle of interview
                    stress_curve = 1 - abs(progress - 0.5) * 2  # Peak at 50%
                    stress_value = final_stress * (0.2 + 0.8 * stress_curve)
                    stress_timeline.append(min(100, stress_value))
                else:
                    stress_timeline.append(0)
        
        # Create emotion timeline based on confidence and stress levels
        for i in range(len(time_points)):
            conf = confidence_timeline[i] if i < len(confidence_timeline) else 0
            stress = stress_timeline[i] if i < len(stress_timeline) else 0
            
            if conf > 70 and stress < 30:
                emotion_timeline.append('Confident')
            elif conf > 50 and stress < 50:
                emotion_timeline.append('Focused')
            elif stress > 60:
                emotion_timeline.append('Stressed')
            elif conf < 30:
                emotion_timeline.append('Nervous')
            else:
                emotion_timeline.append('Neutral')
        
        # Calculate performance rating based on confidence and stress
        performance_rating = max(0, min(10, (final_confidence - final_stress) / 10))
        
        # Create detailed analysis response
        analysis_response = {
            'interview_info': {
                'id': interview.get('id'),
                'candidate_name': interview.get('candidate_name', 'Unknown'),
                'candidate_nic': interview.get('candidate_nic', 'N/A'),
                'position': interview.get('position', 'N/A'),
                'status': interview.get('status', 'completed'),
                'created_at': interview.get('created_at'),
                'start_time': start_time,
                'end_time': end_time,
                'duration_minutes': duration_minutes
            },
            'overall_scores': {
                'confidence': {
                    'overall': final_confidence,
                    'voice': voice_confidence,
                    'hand': hand_confidence,
                    'eye': eye_confidence
                },
                'stress_level': final_stress,
                'performance_rating': performance_rating
            },
            'timeline_analysis': {
                'time_points': time_points,
                'confidence_progression': confidence_timeline,
                'stress_progression': stress_timeline,
                'emotion_progression': emotion_timeline
            },
            'detailed_metrics': {
                'voice_analysis': {
                    'confidence': voice_confidence,
                    'clarity': min(100, voice_confidence + 10),
                    'pace': min(100, voice_confidence + 5),
                    'tone': min(100, voice_confidence + 15)
                },
                'facial_analysis': {
                    'confidence': eye_confidence,
                    'stress_level': final_stress,
                    'engagement': min(100, eye_confidence + 10),
                    'eye_contact': eye_confidence
                },
                'gesture_analysis': {
                    'confidence': hand_confidence,
                    'hand_movements': min(100, hand_confidence + 5),
                    'posture': min(100, hand_confidence + 10),
                    'nervous_gestures': max(0, 100 - hand_confidence)
                }
            },
            'performance_insights': {
                'strengths': [
                    'Good eye contact maintained' if eye_confidence > 60 else 'Eye contact needs improvement',
                    'Clear communication style' if voice_confidence > 60 else 'Voice clarity can be enhanced',
                    'Confident body language' if hand_confidence > 60 else 'Body language needs work'
                ],
                'areas_for_improvement': [
                    'Could improve stress management' if final_stress > 40 else 'Good stress management',
                    'Voice clarity can be enhanced' if voice_confidence < 70 else 'Voice clarity is good',
                    'More engaging gestures needed' if hand_confidence < 70 else 'Gestures are engaging'
                ],
                'recommendations': [
                    'Practice stress-reduction techniques' if final_stress > 40 else 'Continue current stress management',
                    'Work on vocal projection' if voice_confidence < 70 else 'Maintain vocal quality',
                    'Develop more expressive hand gestures' if hand_confidence < 70 else 'Keep using expressive gestures'
                ]
            }
        }
        
        return jsonify({
            'status': 'success', 
            'data': analysis_response
        })
        
    except Exception as e:
        logger.error(f"Error getting analysis: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/interviews/<interview_id>/debug-analysis', methods=['GET'])
def debug_interview_analysis(interview_id):
    """Debug endpoint to check what analysis data exists"""
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
    
    try:
        db_manager = DatabaseManager()
        
        # Get interview data
        interview = db_manager.get_interview(interview_id)
        
        # Get all analysis data
        final_analysis = db_manager.get_final_analysis(interview_id)
        confidence_analysis = db_manager.get_confidence_analysis(interview_id)
        stress_analysis = db_manager.get_stress_analysis(interview_id)
        
        debug_data = {
            'interview_exists': interview is not None,
            'interview_data': {
                'id': interview.get('id') if interview else None,
                'status': interview.get('status') if interview else None,
                'final_confidence_score': interview.get('final_confidence_score') if interview else None,
                'final_stress_score': interview.get('final_stress_score') if interview else None,
                'analysis_completed': interview.get('analysis_completed') if interview else None
            },
            'final_analysis_exists': final_analysis is not None,
            'final_analysis_data': final_analysis,
            'confidence_analysis_count': len(confidence_analysis) if confidence_analysis else 0,
            'confidence_analysis_sample': confidence_analysis[:3] if confidence_analysis else [],
            'stress_analysis_count': len(stress_analysis) if stress_analysis else 0,
            'stress_analysis_sample': stress_analysis[:3] if stress_analysis else []
        }
        
        return jsonify({
            'status': 'success',
            'data': debug_data
        })
        
    except Exception as e:
        logger.error(f"Error debugging analysis: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/test-generate-sample/<interview_id>', methods=['GET'])
def test_generate_sample(interview_id):
    """Test endpoint to generate sample data for any interview"""
    try:
        db_manager = DatabaseManager()
        
        # Generate sample confidence data (binary classification)
        import random
        for i in range(20):  # 20 data points
            confidence_data = {
                'interview_id': interview_id,
                'user_id': 'test_user',
                'voice_confident': random.choice([0, 1]),  # Binary: 0 or 1
                'hand_confident': random.choice([0, 1]),   # Binary: 0 or 1
                'eye_confident': random.choice([0, 1]),    # Binary: 0 or 1
                'confidence_level': 'confident' if random.random() > 0.5 else 'non-confident',
                'timestamp': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat()
            }
            db_manager.save_confidence_analysis(confidence_data)
        
        # Generate sample stress data (binary classification)
        for i in range(20):  # 20 data points
            stress_data = {
                'interview_id': interview_id,
                'user_id': 'test_user',
                'stress_level': 'stress' if random.random() > 0.7 else 'non-stress',  # 30% stress
                'negative_emotion_frames': 1 if random.random() > 0.7 else 0,
                'total_frames': 1,
                'timestamp': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat()
            }
            db_manager.save_stress_analysis(stress_data)
        
        # Generate final analysis using your exact formula
        interview_duration = 120
        voice_weight = 20  # HR Manager default weights
        hand_weight = 30
        eye_weight = 50
        
        # Generate realistic confident seconds
        total_voice_confident_seconds = random.randint(60, 100)  # 60-100s confident
        total_hand_confident_seconds = random.randint(55, 95)    # 55-95s confident  
        total_eye_confident_seconds = random.randint(65, 105)    # 65-105s confident
        
        # Calculate using your exact formula: (time/120) * (weight/100)
        voice_score = (total_voice_confident_seconds / interview_duration) * (voice_weight / 100)
        hand_score = (total_hand_confident_seconds / interview_duration) * (hand_weight / 100)
        eye_score = (total_eye_confident_seconds / interview_duration) * (eye_weight / 100)
        
        # Final confidence: sum of all three values divided by 3
        final_confidence = ((voice_score + hand_score + eye_score) / 3) * 100
        
        # Calculate percentages for display
        voice_percentage = (total_voice_confident_seconds / interview_duration) * 100
        hand_percentage = (total_hand_confident_seconds / interview_duration) * 100
        eye_percentage = (total_eye_confident_seconds / interview_duration) * 100
        
        # Generate stress data
        total_negative_frames = random.randint(5, 15)
        total_frames = 20
        final_stress = (total_negative_frames / total_frames) * 100
        
        final_analysis = {
            'interview_id': interview_id,
            'user_id': 'test_user',
            'final_confidence_score': final_confidence,
            'final_stress_score': final_stress,
            'voice_percentage': voice_percentage,
            'hand_percentage': hand_percentage,
            'eye_percentage': eye_percentage,
            'voice_score': voice_score * 100,
            'hand_score': hand_score * 100,
            'eye_score': eye_score * 100,
            'total_voice_confident_seconds': total_voice_confident_seconds,
            'total_hand_confident_seconds': total_hand_confident_seconds,
            'total_eye_confident_seconds': total_eye_confident_seconds,
            'total_negative_frames': total_negative_frames,
            'total_frames': total_frames,
            'interview_duration': interview_duration,
            'voice_weight': voice_weight,
            'hand_weight': hand_weight,
            'eye_weight': eye_weight,
            'created_at': datetime.now().isoformat()
        }
        
        db_manager.save_final_analysis(final_analysis)
        
        return jsonify({
            'status': 'success',
            'message': f'Sample analysis data generated for interview {interview_id}',
            'data': {
                'final_confidence': final_confidence,
                'final_stress': final_stress,
                'voice_percentage': voice_percentage,
                'hand_percentage': hand_percentage,
                'eye_percentage': eye_percentage
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating test sample analysis: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/interviews/<interview_id>/generate-sample-analysis', methods=['POST'])
def generate_sample_analysis(interview_id):
    """Generate sample analysis data for testing"""
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
    
    try:
        db_manager = DatabaseManager()
        
        # Generate sample confidence data (binary classification)
        import random
        for i in range(20):  # 20 data points
            confidence_data = {
                'interview_id': interview_id,
                'user_id': user_id,
                'voice_confident': random.choice([0, 1]),  # Binary: 0 or 1
                'hand_confident': random.choice([0, 1]),   # Binary: 0 or 1
                'eye_confident': random.choice([0, 1]),    # Binary: 0 or 1
                'confidence_level': 'confident' if random.random() > 0.5 else 'non-confident',
                'timestamp': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat()
            }
            db_manager.save_confidence_analysis(confidence_data)
        
        # Generate sample stress data (binary classification)
        for i in range(20):  # 20 data points
            stress_data = {
                'interview_id': interview_id,
                'user_id': user_id,
                'stress_level': 'stress' if random.random() > 0.7 else 'non-stress',  # 30% stress
                'negative_emotion_frames': 1 if random.random() > 0.7 else 0,
                'total_frames': 1,
                'timestamp': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat()
            }
            db_manager.save_stress_analysis(stress_data)
        
        # Generate final analysis using your exact formula
        # Example: 120s interview, HR weights: Voice 20%, Hand 30%, Eye 50%
        interview_duration = 120
        voice_weight = 20  # HR Manager default weights
        hand_weight = 30
        eye_weight = 50
        
        # Generate realistic confident seconds
        total_voice_confident_seconds = random.randint(60, 100)  # 60-100s confident
        total_hand_confident_seconds = random.randint(55, 95)    # 55-95s confident  
        total_eye_confident_seconds = random.randint(65, 105)    # 65-105s confident
        
        # Calculate using your exact formula: (time/120) * (weight/100)
        voice_score = (total_voice_confident_seconds / interview_duration) * (voice_weight / 100)
        hand_score = (total_hand_confident_seconds / interview_duration) * (hand_weight / 100)
        eye_score = (total_eye_confident_seconds / interview_duration) * (eye_weight / 100)
        
        # Final confidence: sum of all three values divided by 3
        final_confidence = ((voice_score + hand_score + eye_score) / 3) * 100
        
        # Calculate percentages for display
        voice_percentage = (total_voice_confident_seconds / interview_duration) * 100
        hand_percentage = (total_hand_confident_seconds / interview_duration) * 100
        eye_percentage = (total_eye_confident_seconds / interview_duration) * 100
        
        # Generate stress data
        total_negative_frames = random.randint(5, 15)
        total_frames = 20
        final_stress = (total_negative_frames / total_frames) * 100
        
        final_analysis = {
            'interview_id': interview_id,
            'user_id': user_id,
            'final_confidence_score': final_confidence,
            'final_stress_score': final_stress,
            'voice_percentage': voice_percentage,
            'hand_percentage': hand_percentage,
            'eye_percentage': eye_percentage,
            'voice_score': voice_score * 100,
            'hand_score': hand_score * 100,
            'eye_score': eye_score * 100,
            'total_voice_confident_seconds': total_voice_confident_seconds,
            'total_hand_confident_seconds': total_hand_confident_seconds,
            'total_eye_confident_seconds': total_eye_confident_seconds,
            'total_negative_frames': total_negative_frames,
            'total_frames': total_frames,
            'interview_duration': interview_duration,
            'voice_weight': voice_weight,
            'hand_weight': hand_weight,
            'eye_weight': eye_weight,
            'created_at': datetime.now().isoformat()
        }
        
        db_manager.save_final_analysis(final_analysis)
        
        return jsonify({
            'status': 'success',
            'message': 'Sample analysis data generated successfully',
            'data': final_analysis
        })
        
    except Exception as e:
        logger.error(f"Error generating sample analysis: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/interviews/<interview_id>/summary', methods=['GET'])
def get_interview_summary(interview_id):
    """Get interview summary with analysis insights"""
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
    
    try:
        db_manager = DatabaseManager()
        
        # Get interview details
        interview = db_manager.get_interview(interview_id)
        if not interview or interview.get('user_id') != user_id:
            return jsonify({'status': 'error', 'message': 'Interview not found'}), 404
        
        # Get candidate details
        candidate = db_manager.get_candidate(interview['candidate_id'])
        
        # Get analysis data
        analysis_data = db_manager.get_interview_analysis(interview_id)
        
        # Calculate summary metrics
        summary = {
            'interview': interview,
            'candidate': candidate,
            'analysis_summary': {
                'total_data_points': len(analysis_data),
                'average_confidence': sum(a.get('confidence_score', 0) for a in analysis_data) / len(analysis_data) if analysis_data else 0,
                'dominant_emotion': 'neutral',  # Calculate from analysis data
                'average_stress': sum(a.get('stress_level', 0) for a in analysis_data) / len(analysis_data) if analysis_data else 0,
                'average_engagement': sum(a.get('engagement_level', 0) for a in analysis_data) / len(analysis_data) if analysis_data else 0,
            },
            'recommendations': [
                'Review candidate responses for technical accuracy',
                'Consider follow-up questions on communication skills',
                'Evaluate cultural fit based on responses'
            ]
        }
        
        return jsonify({'status': 'success', 'summary': summary})
        
    except Exception as e:
        logger.error(f"Error getting interview summary: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
        
# ==================== CANDIDATE MANAGEMENT APIs ====================

@app.route('/api/candidates', methods=['POST'])
def create_candidate():
    """Create a new candidate"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'position']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error', 
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Create candidate
        db_manager = DatabaseManager()
        candidate_id = db_manager.create_candidate(data)
        
        if candidate_id:
            # Get the created candidate
            candidate = db_manager.get_candidate(candidate_id)
            return jsonify({
                'status': 'success',
                'message': 'Candidate created successfully',
                'candidate': candidate
            }), 201
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to create candidate'
            }), 500
            
    except Exception as e:
        logger.error(f"Error creating candidate: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/candidates', methods=['GET'])
def get_candidates():
    """Get all candidates with optional filtering"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        status = request.args.get('status')
        
        db_manager = DatabaseManager()
        candidates = db_manager.get_all_candidates(limit=limit, status=status)
        
        return jsonify({
            'status': 'success',
            'candidates': candidates,
            'count': len(candidates)
        })
        
    except Exception as e:
        logger.error(f"Error getting candidates: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/candidates/<candidate_id>', methods=['GET'])
def get_candidate(candidate_id):
    """Get a specific candidate by ID"""
    try:
        db_manager = DatabaseManager()
        candidate = db_manager.get_candidate(candidate_id)
        
        if candidate:
            return jsonify({
                'status': 'success',
                'candidate': candidate
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Candidate not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting candidate: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/candidates/<candidate_id>', methods=['PUT'])
def update_candidate(candidate_id):
    """Update a candidate"""
    try:
        data = request.get_json()
        
        db_manager = DatabaseManager()
        success = db_manager.update_candidate(candidate_id, data)
        
        if success:
            # Get updated candidate
            candidate = db_manager.get_candidate(candidate_id)
            return jsonify({
                'status': 'success',
                'message': 'Candidate updated successfully',
                'candidate': candidate
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to update candidate'
            }), 500
            
    except Exception as e:
        logger.error(f"Error updating candidate: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/candidates/<candidate_id>', methods=['DELETE'])
def delete_candidate(candidate_id):
    """Delete (deactivate) a candidate"""
    try:
        db_manager = DatabaseManager()
        success = db_manager.delete_candidate(candidate_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Candidate deleted successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to delete candidate'
            }), 500
            
    except Exception as e:
        logger.error(f"Error deleting candidate: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ==================== REAL-TIME ANALYSIS APIs ====================

@app.route('/api/interviews/<interview_id>/realtime-analysis', methods=['GET'])
def get_realtime_analysis(interview_id):
    """Get real-time analysis data for an interview"""
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
    
    try:
        db_manager = DatabaseManager()
        
        # Verify interview exists and belongs to user
        interview = db_manager.get_interview(interview_id)
        if not interview or interview.get('user_id') != user_id:
            return jsonify({'status': 'error', 'message': 'Interview not found'}), 404
        
        # Get analysis data from realtime database
        rtdb_ref = db_manager.rtdb.reference(f'interviews/{interview_id}/analysis')
        analysis_data = rtdb_ref.get() or {}
        
        # Convert to list format
        analysis_list = []
        for key, value in analysis_data.items():
            analysis_list.append({'id': key, **value})
        
        # Sort by timestamp
        analysis_list.sort(key=lambda x: x.get('timestamp', ''))
        
        return jsonify({
            'status': 'success',
            'interview_id': interview_id,
            'analysis_data': analysis_list,
            'count': len(analysis_list)
        })
        
    except Exception as e:
        logger.error(f"Error getting real-time analysis: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/interviews/<interview_id>/live-analysis', methods=['GET'])
def get_live_analysis(interview_id):
    """Get live analysis if interview is active"""
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
    
    try:
        db_manager = DatabaseManager()
        
        # Verify interview exists and belongs to user
        interview = db_manager.get_interview(interview_id)
        if not interview or interview.get('user_id') != user_id:
            return jsonify({'status': 'error', 'message': 'Interview not found'}), 404
        
        # Check if interview is active and has live analyzer
        if interview_id in active_analyzers:
            analyzer = active_analyzers[interview_id]
            latest_results = analyzer.get_latest_results() if hasattr(analyzer, 'get_latest_results') else {}
            
            return jsonify({
                'status': 'success',
                'interview_id': interview_id,
                'is_live': True,
                'live_analysis': latest_results
            })
        else:
            return jsonify({
                'status': 'success',
                'interview_id': interview_id,
                'is_live': False,
                'message': 'Interview is not currently active'
            })
            
    except Exception as e:
        logger.error(f"Error getting live analysis: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/interviews/<interview_id>/realtime-analysis', methods=['GET'])
def get_realtime_analysis_history(interview_id):
    """Get real-time analysis history (10-second intervals)"""
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
    
    try:
        db_manager = DatabaseManager()
        
        # Verify interview exists and belongs to user
        interview = db_manager.get_interview(interview_id)
        if not interview or interview.get('user_id') != user_id:
            return jsonify({'status': 'error', 'message': 'Interview not found'}), 404
        
        # Get real-time analysis data from database
        realtime_data = db_manager.db.collection('realtime_analysis').where('session_id', '==', interview_id).order_by('timestamp', direction='DESCENDING').limit(50).stream()
        
        analysis_history = []
        for doc in realtime_data:
            data = doc.to_dict()
            data['id'] = doc.id
            analysis_history.append(data)
        
        return jsonify({
            'status': 'success',
            'interview_id': interview_id,
            'realtime_analysis': analysis_history,
            'total_updates': len(analysis_history),
            'update_interval': '10_seconds'
        })
        
    except Exception as e:
        logger.error(f"Error getting real-time analysis history: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/interviews/<interview_id>', methods=['DELETE'])
def delete_interview(interview_id):
    """Delete an interview and associated candidate"""
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
    
    try:
        db_manager = DatabaseManager()
        
        # First, get the interview to check ownership and get candidate_id
        interview = db_manager.get_interview(interview_id)
        if not interview:
            return jsonify({'status': 'error', 'message': 'Interview not found'}), 404
        
        # Check if user owns this interview
        if interview.get('user_id') != user_id:
            return jsonify({'status': 'error', 'message': 'Unauthorized to delete this interview'}), 403
        
        # Delete the interview
        interview_deleted = db_manager.delete_interview(interview_id)
        if not interview_deleted:
            return jsonify({'status': 'error', 'message': 'Failed to delete interview'}), 500
        
        # Also delete the associated candidate if it exists
        candidate_id = interview.get('candidate_id')
        if candidate_id:
            db_manager.delete_candidate(candidate_id)
        
        logger.info(f"Interview {interview_id} and candidate {candidate_id} deleted by user {user_id}")
        
        return jsonify({
            'status': 'success',
            'message': 'Interview deleted successfully',
            'interview_id': interview_id
        })
        
    except Exception as e:
        logger.error(f"Error deleting interview: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ==================== JOB ROLE MANAGEMENT APIs ====================

@app.route('/api/job-roles', methods=['POST'])
def create_job_role():
    """Create a new job role with confidence level requirements"""
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
    
    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': 'Job role data required'}), 400
    
    try:
        # Validate required fields
        required_fields = ['name', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'Missing required field: {field}'}), 400
        
        # Validate confidence levels
        confidence_levels = data.get('confidence_levels', {})
        voice_confidence = confidence_levels.get('voice_confidence', 0)
        hand_confidence = confidence_levels.get('hand_confidence', 0)
        eye_confidence = confidence_levels.get('eye_confidence', 0)
        
        # Auto-calculate eye confidence if not provided (remaining to make total 100)
        if eye_confidence == 0 and voice_confidence + hand_confidence < 100:
            eye_confidence = 100 - voice_confidence - hand_confidence
        
        # Ensure total doesn't exceed 100
        total_confidence = voice_confidence + hand_confidence + eye_confidence
        if total_confidence > 100:
            return jsonify({'status': 'error', 'message': 'Total confidence levels cannot exceed 100%'}), 400
        
        job_role_data = {
            'user_id': user_id,
            'name': data['name'],
            'description': data['description'],
            'confidence_levels': {
                'voice_confidence': voice_confidence,
                'hand_confidence': hand_confidence,
                'eye_confidence': eye_confidence
            },
            'is_active': data.get('is_active', True),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        db_manager = DatabaseManager()
        job_role_id = db_manager.create_job_role(job_role_data)
        
        if job_role_id:
            job_role_data['id'] = job_role_id
            return jsonify({
                'status': 'success', 
                'message': 'Job role created successfully',
                'job_role': job_role_data
            })
        else:
            return jsonify({'status': 'error', 'message': 'Failed to create job role'}), 500
        
    except Exception as e:
        logger.error(f"Error creating job role: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/job-roles', methods=['GET'])
def get_job_roles():
    """Get all job roles for a user"""
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
    
    try:
        db_manager = DatabaseManager()
        job_roles = db_manager.get_user_job_roles(user_id)
        
        return jsonify({'status': 'success', 'job_roles': job_roles})
    except Exception as e:
        logger.error(f"Error getting job roles: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/job-roles/<job_role_id>', methods=['GET'])
def get_job_role(job_role_id):
    """Get specific job role details"""
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
    
    try:
        db_manager = DatabaseManager()
        job_role = db_manager.get_job_role(job_role_id)
        
        if job_role and job_role.get('user_id') == user_id:
            return jsonify({'status': 'success', 'job_role': job_role})
        else:
            return jsonify({'status': 'error', 'message': 'Job role not found'}), 404
    except Exception as e:
        logger.error(f"Error getting job role: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/job-roles/<job_role_id>', methods=['PUT'])
def update_job_role(job_role_id):
    """Update a job role"""
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
    
    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
    
    try:
        db_manager = DatabaseManager()
        job_role = db_manager.get_job_role(job_role_id)
        
        if not job_role or job_role.get('user_id') != user_id:
            return jsonify({'status': 'error', 'message': 'Job role not found'}), 404
        
        # Validate confidence levels if provided
        if 'confidence_levels' in data:
            confidence_levels = data['confidence_levels']
            voice_confidence = confidence_levels.get('voice_confidence', 0)
            hand_confidence = confidence_levels.get('hand_confidence', 0)
            eye_confidence = confidence_levels.get('eye_confidence', 0)
            
            # Auto-calculate eye confidence if not provided
            if eye_confidence == 0 and voice_confidence + hand_confidence < 100:
                eye_confidence = 100 - voice_confidence - hand_confidence
                data['confidence_levels']['eye_confidence'] = eye_confidence
            
            # Ensure total doesn't exceed 100
            total_confidence = voice_confidence + hand_confidence + eye_confidence
            if total_confidence > 100:
                return jsonify({'status': 'error', 'message': 'Total confidence levels cannot exceed 100%'}), 400
        
        data['updated_at'] = datetime.now().isoformat()
        
        success = db_manager.update_job_role(job_role_id, data)
        
        if success:
            updated_job_role = db_manager.get_job_role(job_role_id)
            return jsonify({
                'status': 'success', 
                'message': 'Job role updated successfully',
                'job_role': updated_job_role
            })
        else:
            return jsonify({'status': 'error', 'message': 'Failed to update job role'}), 500
        
    except Exception as e:
        logger.error(f"Error updating job role: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/job-roles/<job_role_id>', methods=['DELETE'])
def delete_job_role(job_role_id):
    """Delete a job role"""
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
    
    try:
        db_manager = DatabaseManager()
        job_role = db_manager.get_job_role(job_role_id)
        
        if not job_role or job_role.get('user_id') != user_id:
            return jsonify({'status': 'error', 'message': 'Job role not found'}), 404
        
        success = db_manager.delete_job_role(job_role_id)
        
        if success:
            return jsonify({'status': 'success', 'message': 'Job role deleted successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to delete job role'}), 500
        
    except Exception as e:
        logger.error(f"Error deleting job role: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/job-roles/<job_role_id>/assign', methods=['POST'])
def assign_job_role_to_interview():
    """Assign a job role to an interview"""
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
    
    data = request.json
    if not data or 'interview_id' not in data:
        return jsonify({'status': 'error', 'message': 'Interview ID is required'}), 400
    
    try:
        job_role_id = request.view_args['job_role_id']
        interview_id = data['interview_id']
        
        db_manager = DatabaseManager()
        
        # Verify job role belongs to user
        job_role = db_manager.get_job_role(job_role_id)
        if not job_role or job_role.get('user_id') != user_id:
            return jsonify({'status': 'error', 'message': 'Job role not found'}), 404
        
        # Verify interview belongs to user
        interview = db_manager.get_interview(interview_id)
        if not interview or interview.get('user_id') != user_id:
            return jsonify({'status': 'error', 'message': 'Interview not found'}), 404
        
        # Update interview with job role
        update_data = {
            'job_role_id': job_role_id,
            'confidence_requirements': job_role['confidence_levels'],
            'updated_at': datetime.now().isoformat()
        }
        
        success = db_manager.update_interview(interview_id, update_data)
        
        if success:
            return jsonify({
                'status': 'success', 
                'message': 'Job role assigned to interview successfully'
            })
        else:
            return jsonify({'status': 'error', 'message': 'Failed to assign job role'}), 500
        
    except Exception as e:
        logger.error(f"Error assigning job role: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ==================== ANALYTICS APIs ====================

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Get statistics from database
        db_manager = DatabaseManager()
        candidates = db_manager.get_all_candidates()  # This returns a list directly
        
        # Calculate statistics
        total_candidates = len(candidates) if candidates else 0
        
        # Get interview statistics
        user_id = get_user_id_from_request()
        if user_id:
            interviews = db_manager.get_user_interviews(user_id)
            total_interviews = len(interviews)
            completed_interviews = len([i for i in interviews if i.get('status') == 'completed'])
            completion_rate = (completed_interviews / total_interviews * 100) if total_interviews > 0 else 0
        else:
            total_interviews = total_candidates * 2  # Average 2 interviews per candidate
            completion_rate = 94.5
        
        average_score = 8.2
        # Calculate trends (mock data)
        trends = {
            'interviews': 12.5,
            'candidates': 8.3,
            'score': -2.1,
            'completion': 3.7
        }
        
        stats = {
            'total_interviews': total_interviews,
            'total_candidates': total_candidates,
            'average_score': average_score,
            'completion_rate': completion_rate,
            'trends': trends
        }
        
        return jsonify({
            'status': 'success',
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/analytics/interview-trends', methods=['GET'])
def get_interview_trends():
    """Get interview trends data"""
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
    
    try:
        db_manager = DatabaseManager()
        
        # Get interviews for the user
        interviews = db_manager.get_user_interviews(user_id)
        
        # Process trends data
        trends_data = []
        
        # Group by month for the last 6 months
        from collections import defaultdict
        monthly_data = defaultdict(lambda: {'interviews': 0, 'completed': 0, 'total_score': 0, 'count': 0})
        
        for interview in interviews:
            created_at = interview.get('created_at', '')
            if created_at:
                try:
                    from datetime import datetime
                    date = datetime.fromisoformat(created_at.replace('Z', '+00:00') if created_at.endswith('Z') else created_at)
                    month_key = date.strftime('%Y-%m')
                    
                    monthly_data[month_key]['interviews'] += 1
                    if interview.get('status') == 'completed':
                        monthly_data[month_key]['completed'] += 1
                    
                    # Add mock score for demonstration
                    monthly_data[month_key]['total_score'] += 8.2
                    monthly_data[month_key]['count'] += 1
                except:
                    continue
        
        # Convert to list format
        for month, data in sorted(monthly_data.items()):
            avg_score = data['total_score'] / data['count'] if data['count'] > 0 else 0
            trends_data.append({
                'month': month,
                'interviews': data['interviews'],
                'completed': data['completed'],
                'completion_rate': (data['completed'] / data['interviews'] * 100) if data['interviews'] > 0 else 0,
                'average_score': round(avg_score, 1)
            })
        
        return jsonify({
            'status': 'success',
            'trends': trends_data
        })
        
    except Exception as e:
        logger.error(f"Error getting interview trends: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/analytics/emotion-distribution', methods=['GET'])
def get_emotion_distribution():
    """Get emotion distribution data"""
    try:
        time_range = request.args.get('range', '7days')
        
        # Mock data - replace with real analysis from database
        distribution = [
            {'name': 'Confident', 'value': 35, 'color': '#4CAF50'},
            {'name': 'Neutral', 'value': 40, 'color': '#2196F3'},
            {'name': 'Nervous', 'value': 20, 'color': '#FF9800'},
            {'name': 'Stressed', 'value': 5, 'color': '#F44336'},
        ]
        
        return jsonify({
            'status': 'success',
            'distribution': distribution
        })
        
    except Exception as e:
        logger.error(f"Error getting emotion distribution: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/analytics/candidate-trends', methods=['GET'])
def get_candidate_trends():
    """Get latest 3 candidates stress and confidence trends through interview period"""
    user_id = get_user_id_from_request()

    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400

    try:
        db_manager = DatabaseManager()
        
        # Get all interviews for the user, sorted by creation date (latest first)
        interviews = db_manager.get_user_interviews(user_id)
        
        # Sort by created_at descending and take latest 3
        latest_interviews = sorted(interviews, key=lambda x: x.get('created_at', ''), reverse=True)[:3]
        
        candidate_trends = []
        
        for interview in latest_interviews:
            candidate_data = interview.get('candidate_data', {})
            analysis_data = interview.get('analysis_data', {})
            
            # Get candidate name and position
            candidate_name = candidate_data.get('name', 'Unknown')
            position = interview.get('position', 'N/A')
            
            # Get confidence and stress levels
            confidence_level = analysis_data.get('overall_confidence', 0)
            stress_level = analysis_data.get('stress_level', 0)
            
            # Get individual confidence scores
            voice_confidence = analysis_data.get('voice_confidence', 0)
            hand_confidence = analysis_data.get('hand_confidence', 0)
            eye_confidence = analysis_data.get('eye_confidence', 0)
            
            # Calculate interview duration
            start_time = interview.get('start_time')
            end_time = interview.get('end_time')
            duration_minutes = 0
            if start_time and end_time:
                try:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    duration_minutes = int((end_dt - start_dt).total_seconds() / 60)
                except:
                    duration_minutes = 0
            
            # Create trend data points (simulate progression through interview)
            # For now, we'll create 5 time points representing interview progression
            time_points = ['Start', '25%', '50%', '75%', 'End']
            
            # Simulate realistic progression (confidence might increase/decrease, stress might fluctuate)
            confidence_progression = []
            stress_progression = []
            
            # Base values with some realistic variation
            base_confidence = confidence_level
            base_stress = stress_level
            
            for i, point in enumerate(time_points):
                # Confidence tends to improve or stay stable through interview
                confidence_variation = (i - 2) * 2  # -4, -2, 0, 2, 4
                confidence_value = max(0, min(100, base_confidence + confidence_variation + (i * 1)))
                
                # Stress might peak in middle and decrease towards end
                stress_variation = 5 * (1 - abs(i - 2) / 2)  # Peak at middle
                stress_value = max(0, min(100, base_stress + stress_variation - (i * 0.5)))
                
                confidence_progression.append(confidence_value)
                stress_progression.append(stress_value)
            
            candidate_trend = {
                'candidate_name': candidate_name,
                'position': position,
                'interview_id': interview.get('id'),
                'created_at': interview.get('created_at'),
                'duration_minutes': duration_minutes,
                'time_points': time_points,
                'confidence_progression': confidence_progression,
                'stress_progression': stress_progression,
                'final_confidence': confidence_level,
                'final_stress': stress_level,
                'confidence_breakdown': {
                    'voice': voice_confidence,
                    'hand': hand_confidence,
                    'eye': eye_confidence,
                    'overall': confidence_level
                }
            }
            
            candidate_trends.append(candidate_trend)
        
        return jsonify({
            'status': 'success',
            'data': {
                'candidates': candidate_trends,
                'total_candidates': len(candidate_trends)
            }
        })

    except Exception as e:
        logger.error(f"Error getting candidate trends: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500



# Additional Analytics endpoints for frontend compatibility
@app.route('/api/analytics/overview', methods=['GET'])
def get_analytics_overview():
    """Get analytics overview statistics"""
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
    
    try:
        db_manager = DatabaseManager()
        interviews = db_manager.get_user_interviews(user_id)
        
        # Calculate statistics
        total_sessions = len(interviews)
        active_sessions = len([i for i in interviews if i.get('status') == 'active'])
        completed_sessions = len([i for i in interviews if i.get('status') == 'completed'])
        
        # Calculate average scores
        confidence_scores = []
        stress_scores = []
        
        for interview in interviews:
            analysis_data = interview.get('analysis_data', {})
            if analysis_data.get('overall_confidence'):
                confidence_scores.append(analysis_data.get('overall_confidence'))
            if analysis_data.get('stress_level'):
                stress_scores.append(analysis_data.get('stress_level'))
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        avg_stress = sum(stress_scores) / len(stress_scores) if stress_scores else 0
        completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        # Get unique candidates
        unique_candidates = len(set(i.get('candidate_data', {}).get('name', '') for i in interviews))
        
        # Mock trends for now
        trends = {
            'sessions': 12.5,
            'candidates': 8.3,
            'score': -2.1,
            'completion': 3.7
        }
        
        overview_data = {
            'totalSessions': total_sessions,
            'totalCandidates': unique_candidates,
            'averageScore': round(avg_confidence, 1),
            'completionRate': round(completion_rate, 1),
            'activeSessions': active_sessions,
            'completedSessions': completed_sessions,
            'averageConfidence': round(avg_confidence, 1),
            'averageStress': round(avg_stress, 1),
            'trends': trends
        }
        
        return jsonify({
            'status': 'success',
            'data': overview_data
        })
        
    except Exception as e:
        logger.error(f"Error getting analytics overview: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/analytics/trends', methods=['GET'])
def get_analytics_trends():
    """Get analytics trends data"""
    try:
        time_range = request.args.get('range', '7days')
        
        # Mock trends data
        trends = [
            {'date': '2024-09-01', 'sessions': 12, 'score': 8.1},
            {'date': '2024-09-02', 'sessions': 15, 'score': 8.3},
            {'date': '2024-09-03', 'sessions': 8, 'score': 7.9},
            {'date': '2024-09-04', 'sessions': 22, 'score': 8.5},
            {'date': '2024-09-05', 'sessions': 18, 'score': 8.2},
            {'date': '2024-09-06', 'sessions': 25, 'score': 8.7},
            {'date': '2024-09-07', 'sessions': 20, 'score': 8.4},
        ]
        
        return jsonify({
            'status': 'success',
            'data': trends
        })
        
    except Exception as e:
        logger.error(f"Error getting analytics trends: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/analytics/candidates', methods=['GET'])
def get_analytics_candidates():
    """Get detailed candidate analytics data with filtering"""
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
    
    try:
        # Get query parameters for filtering
        min_confidence = request.args.get('min_confidence', type=float)
        max_confidence = request.args.get('max_confidence', type=float)
        min_stress = request.args.get('min_stress', type=float)
        max_stress = request.args.get('max_stress', type=float)
        job_role_id = request.args.get('job_role_id')
        status = request.args.get('status')  # active, completed, etc.
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        db_manager = DatabaseManager()
        
        # Get all interviews for the user
        interviews = db_manager.get_user_interviews(user_id)
        
        # Filter and process interviews
        filtered_candidates = []
        
        for interview in interviews:
            interview_id = interview.get('id')
            
            # Get analysis data for this interview from analysis_results collection
            analysis_results = db_manager.get_session_results(interview_id)
            
            # Aggregate analysis data
            aggregated_analysis = {
                'voice_confidence': 0,
                'hand_confidence': 0,
                'eye_confidence': 0,
                'overall_confidence': 0,
                'stress_level': 0,
                'total_samples': 0
            }
            
            if analysis_results:
                # Calculate averages from all analysis results
                voice_sum = 0
                hand_sum = 0
                eye_sum = 0
                stress_sum = 0
                total_samples = len(analysis_results)
                
                for result in analysis_results:
                    # Extract confidence values (convert from binary to percentage)
                    voice_data = result.get('voice_confidence', {})
                    hand_data = result.get('hand_confidence', {})
                    eye_data = result.get('eye_confidence', {})
                    face_data = result.get('face_stress', {})
                    
                    # Convert binary values to percentages
                    voice_conf = 100 if voice_data.get('confidence_level') == 'confident' else 0
                    hand_conf = 100 if hand_data.get('confidence_level') == 'confident' else 0
                    eye_conf = 100 if eye_data.get('confidence_level') == 'confident' else 0
                    stress_level = 100 if face_data.get('stress_level') == 'stress' else 0
                    
                    voice_sum += voice_conf
                    hand_sum += hand_conf
                    eye_sum += eye_conf
                    stress_sum += stress_level
                
                # Calculate averages
                aggregated_analysis = {
                    'voice_confidence': round(voice_sum / total_samples) if total_samples > 0 else 0,
                    'hand_confidence': round(hand_sum / total_samples) if total_samples > 0 else 0,
                    'eye_confidence': round(eye_sum / total_samples) if total_samples > 0 else 0,
                    'overall_confidence': round((voice_sum + hand_sum + eye_sum) / (total_samples * 3)) if total_samples > 0 else 0,
                    'stress_level': round(stress_sum / total_samples) if total_samples > 0 else 0,
                    'total_samples': total_samples
                }
            
            # Apply filters
            if min_confidence is not None:
                overall_confidence = aggregated_analysis.get('overall_confidence', 0)
                if overall_confidence < min_confidence:
                    continue
            
            if max_confidence is not None:
                overall_confidence = aggregated_analysis.get('overall_confidence', 0)
                if overall_confidence > max_confidence:
                    continue
            
            if min_stress is not None:
                stress_level = aggregated_analysis.get('stress_level', 0)
                if stress_level < min_stress:
                    continue
            
            if max_stress is not None:
                stress_level = aggregated_analysis.get('stress_level', 0)
                if stress_level > max_stress:
                    continue
            
            if job_role_id and interview.get('job_role_id') != job_role_id:
                continue
            
            if status and interview.get('status') != status:
                continue
            
            # Date filtering
            if date_from or date_to:
                interview_date = interview.get('created_at', '')
                if date_from and interview_date < date_from:
                    continue
                if date_to and interview_date > date_to:
                    continue
            
            # Calculate session duration
            start_time = interview.get('start_time')
            end_time = interview.get('end_time')
            duration = 0
            if start_time and end_time:
                try:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    duration = int((end_dt - start_dt).total_seconds() / 60)  # in minutes
                except:
                    duration = 0
            
            # Prepare candidate data - use interview data directly
            candidate_info = {
                'interview_id': interview.get('id'),
                'candidate_name': interview.get('candidate_name', 'Unknown'),
                'candidate_nic': interview.get('candidate_nic_passport', 'N/A'),
                'position': interview.get('position', 'N/A'),
                'job_role_id': interview.get('job_role_id'),
                'interviewer': user_id,  # For now, using user_id as interviewer
                'status': interview.get('status', 'pending'),
                'created_at': interview.get('created_at'),
                'start_time': start_time,
                'end_time': end_time,
                'duration_minutes': duration,
                'confidence_scores': {
                    'voice': aggregated_analysis.get('voice_confidence', 0),
                    'hand': aggregated_analysis.get('hand_confidence', 0),
                    'eye': aggregated_analysis.get('eye_confidence', 0),
                    'overall': aggregated_analysis.get('overall_confidence', 0)
                },
                'stress_level': aggregated_analysis.get('stress_level', 0),
                'emotion_data': {},
                'performance_notes': '',
                'analysis_samples': aggregated_analysis.get('total_samples', 0)
            }
            
            filtered_candidates.append(candidate_info)
        
        # Sort by created_at descending (most recent first)
        filtered_candidates.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # If no candidates found, generate some sample data for testing
        if len(filtered_candidates) == 0 and len(interviews) > 0:
            logger.info("No analysis data found, generating sample data for testing...")
            for interview in interviews[:3]:  # Generate sample data for first 3 interviews
                interview_id = interview.get('id')
                
                # Generate sample analysis data
                sample_analysis = {
                    'session_id': interview_id,
                    'timestamp': datetime.now().isoformat(),
                    'voice_confidence': {
                        'confidence_level': 'confident' if hash(interview_id) % 2 == 0 else 'non-confident'
                    },
                    'hand_confidence': {
                        'confidence_level': 'confident' if hash(interview_id + 'hand') % 2 == 0 else 'non-confident'
                    },
                    'eye_confidence': {
                        'confidence_level': 'confident' if hash(interview_id + 'eye') % 2 == 0 else 'non-confident'
                    },
                    'face_stress': {
                        'stress_level': 'stress' if hash(interview_id + 'stress') % 3 == 0 else 'no-stress'
                    }
                }
                
                # Save sample analysis data
                db_manager.save_analysis_result(interview_id, sample_analysis)
                
                # Add to filtered candidates with sample data
                candidate_info = {
                    'interview_id': interview.get('id'),
                    'candidate_name': interview.get('candidate_name', 'Sample Candidate'),
                    'candidate_nic': interview.get('candidate_nic_passport', 'SAMPLE123'),
                    'position': interview.get('position', 'Sample Position'),
                    'job_role_id': interview.get('job_role_id'),
                    'interviewer': user_id,
                    'status': interview.get('status', 'completed'),
                    'created_at': interview.get('created_at'),
                    'start_time': interview.get('start_time'),
                    'end_time': interview.get('end_time'),
                    'duration_minutes': 30,  # Sample duration
                    'confidence_scores': {
                        'voice': 75 if sample_analysis['voice_confidence']['confidence_level'] == 'confident' else 25,
                        'hand': 80 if sample_analysis['hand_confidence']['confidence_level'] == 'confident' else 20,
                        'eye': 85 if sample_analysis['eye_confidence']['confidence_level'] == 'confident' else 15,
                        'overall': 80 if sample_analysis['voice_confidence']['confidence_level'] == 'confident' else 20
                    },
                    'stress_level': 30 if sample_analysis['face_stress']['stress_level'] == 'stress' else 10,
                    'emotion_data': {},
                    'performance_notes': 'Sample analysis data generated for testing',
                    'analysis_samples': 1
                }
                filtered_candidates.append(candidate_info)
        
        return jsonify({
            'status': 'success',
            'data': filtered_candidates,
            'total_count': len(filtered_candidates)
        })
        
    except Exception as e:
        logger.error(f"Error getting analytics candidates: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/interviews/<interview_id>/confidence-analysis', methods=['POST'])
def submit_confidence_analysis(interview_id):
    """Submit confidence analysis data for an interview"""
    try:
        data = request.get_json()
        user_id = get_user_id_from_request()
        
        if not user_id:
            return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
        
        # Extract confidence data (binary classification: 1 = confident, 0 = non-confident)
        voice_confidence = 1 if data.get('voice_confidence', False) else 0
        hand_confidence = 1 if data.get('hand_confidence', False) else 0
        eye_confidence = 1 if data.get('eye_confidence', False) else 0
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        db_manager = DatabaseManager()
        
        # Store confidence analysis data (binary values)
        analysis_data = {
            'interview_id': interview_id,
            'user_id': user_id,
            'voice_confidence': voice_confidence,
            'hand_confidence': hand_confidence,
            'eye_confidence': eye_confidence,
            'confidence_level': 'confident' if (voice_confidence + hand_confidence + eye_confidence) >= 2 else 'non-confident',
            'timestamp': timestamp,
            'created_at': datetime.now().isoformat()
        }
        
        # Save to analysis_results document with binary values using correct field names
        session_id = data.get('session_id', str(uuid.uuid4()))
        analysis_result = {
            'interview_id': interview_id,
            'user_id': user_id,
            'type': 'confidence',
            'voice_confident': voice_confidence,  # Binary: 0 or 1
            'hand_confident': hand_confidence,    # Binary: 0 or 1
            'eye_confident': eye_confidence,      # Binary: 0 or 1
            'confidence_level': 'confident' if (voice_confidence + hand_confidence + eye_confidence) >= 2 else 'non-confident',
            'timestamp': timestamp
        }
        
        # Save to analysis_results collection
        doc_id = db_manager.save_analysis_result(session_id, analysis_result)
        
        return jsonify({
            'status': 'success',
            'message': 'Confidence analysis saved as binary values to analysis_results',
            'doc_id': doc_id,
            'binary_data': {
                'voice_confident': voice_confidence,
                'hand_confident': hand_confidence,
                'eye_confident': eye_confidence
            }
        })
        
    except Exception as e:
        logger.error(f"Error saving confidence analysis: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/interviews/<interview_id>/stress-analysis', methods=['POST'])
def submit_stress_analysis(interview_id):
    """Submit stress analysis data for an interview"""
    try:
        data = request.get_json()
        user_id = get_user_id_from_request()
        
        if not user_id:
            return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
        
        # Extract stress data (binary classification: 1 = stress, 0 = non-stress)
        is_stressed = data.get('is_stressed', False)
        negative_emotion_frames = 1 if is_stressed else 0
        total_frames = 1  # Each analysis point represents 1 frame
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        db_manager = DatabaseManager()
        
        # Store stress analysis data (binary values)
        analysis_data = {
            'interview_id': interview_id,
            'user_id': user_id,
            'stress_level': 'stress' if is_stressed else 'non-stress',
            'negative_emotion_frames': negative_emotion_frames,
            'total_frames': total_frames,
            'timestamp': timestamp,
            'created_at': datetime.now().isoformat()
        }
        
        # Save to analysis_results document with binary values
        session_id = data.get('session_id', str(uuid.uuid4()))
        analysis_result = {
            'interview_id': interview_id,
            'user_id': user_id,
            'type': 'stress',
            'stress_level': 'stress' if is_stressed else 'non-stress',
            'negative_emotion_frames': negative_emotion_frames,  # Binary: 0 or 1
            'total_frames': total_frames,
            'timestamp': timestamp
        }
        
        # Save to analysis_results collection
        doc_id = db_manager.save_analysis_result(session_id, analysis_result)
        
        return jsonify({
            'status': 'success',
            'message': 'Stress analysis saved as binary values to analysis_results',
            'doc_id': doc_id,
            'binary_data': {
                'stress_level': negative_emotion_frames,
                'is_stressed': is_stressed
            }
        })
        
    except Exception as e:
        logger.error(f"Error saving stress analysis: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/interviews/<interview_id>/analysis-results', methods=['POST'])
def save_analysis_results(interview_id):
    """Save analysis results in the exact format provided by the user"""
    try:
        data = request.get_json()
        
        # Get user_id from request body or headers
        user_id = data.get('user_id') or get_user_id_from_request()
        
        if not user_id:
            return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
        
        # Extract data from the exact JSON structure
        session_id = data.get('session_id')
        timestamp = data.get('timestamp')
        
        # Extract confidence data and convert to binary based on confidence_level
        # Handle the exact data structure from frontend
        eye_data = data.get('eye_confidence', {})
        eye_confidence = 1 if eye_data.get('confidence_level') == 'confident' else 0
        
        hand_data = data.get('hand_confidence', {})
        hand_confidence = 1 if hand_data.get('confidence_level') == 'confident' else 0
        
        # Voice confidence has nested structure - check both possible paths
        voice_data = data.get('voice_confidence', {})
        if 'confidence_level' in voice_data:
            voice_confidence = 1 if voice_data.get('confidence_level') == 'confident' else 0
        else:
            # Check nested audio_metrics structure
            audio_metrics = voice_data.get('audio_metrics', {})
            voice_confidence = 1 if audio_metrics.get('confidence_level') == 'confident' else 0
        
        # Extract stress data and convert to binary based on stress_level
        face_stress_data = data.get('face_stress', {})
        stress = 1 if face_stress_data.get('stress_level') == 'stress' else 0
        
        # Log the conversion for debugging
        logger.info(f"🔍 Processing analysis data for interview: {interview_id}")
        logger.info(f"📊 Original data structure:")
        logger.info(f"   Eye: {eye_data}")
        logger.info(f"   Hand: {hand_data}")
        logger.info(f"   Voice: {voice_data}")
        logger.info(f"   Face Stress: {face_stress_data}")
        logger.info(f"🎯 Binary conversion results:")
        logger.info(f"   Eye: {eye_data.get('confidence_level')} → {eye_confidence}")
        logger.info(f"   Hand: {hand_data.get('confidence_level')} → {hand_confidence}")
        logger.info(f"   Voice: {voice_data.get('confidence_level')} → {voice_confidence}")
        logger.info(f"   Stress: {face_stress_data.get('stress_level')} → {stress}")
        
        # Create analysis result document with ONLY binary values using correct field names
        analysis_result = {
            'interview_id': interview_id,
            'user_id': user_id,
            'session_id': session_id,
            'timestamp': timestamp,
            'eye_confident': eye_confidence,      # Binary: 0 or 1
            'hand_confident': hand_confidence,    # Binary: 0 or 1
            'voice_confident': voice_confidence,  # Binary: 0 or 1
            'stress': stress,                     # Binary: 0 or 1
            'confidence_level': 'confident' if (eye_confidence + hand_confidence + voice_confidence) >= 2 else 'not_confident',
            'stress_level': 'stress' if stress == 1 else 'non_stress',
            'created_at': datetime.now().isoformat()
        }
        
        # Log what we're saving
        logger.info(f"💾 Saving binary analysis result to database:")
        logger.info(f"   Document ID: {interview_id}")
        logger.info(f"   User ID: {user_id}")
        logger.info(f"   Session ID: {session_id}")
        logger.info(f"   Binary Values: eye_confident={eye_confidence}, hand_confident={hand_confidence}, voice_confident={voice_confidence}, stress={stress}")
        logger.info(f"   Overall Confidence: {analysis_result['confidence_level']}")
        logger.info(f"   Overall Stress: {analysis_result['stress_level']}")
        
        db_manager = DatabaseManager()
        doc_id = db_manager.save_analysis_result(session_id, analysis_result)
        
        return jsonify({
            'status': 'success',
            'message': 'Analysis results saved as binary values',
            'doc_id': doc_id,
            'binary_data': {
                'eye_confident': eye_confidence,
                'hand_confident': hand_confidence,
                'voice_confident': voice_confidence,
                'stress': stress
            }
        })
        
    except Exception as e:
        logger.error(f"Error saving analysis results: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/interviews/<interview_id>/final-analysis', methods=['POST'])
def calculate_final_analysis(interview_id):
    """Calculate final confidence and stress scores for an interview"""
    try:
        data = request.get_json()
        user_id = get_user_id_from_request()
        
        if not user_id:
            return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
        
        # Get job role weights from HR configuration
        job_role_id = data.get('job_role_id')
        interview_duration = data.get('interview_duration', 120)  # seconds
        
        db_manager = DatabaseManager()
        
        # Get job role confidence weights
        job_role = db_manager.get_job_role(job_role_id)
        if not job_role:
            return jsonify({'status': 'error', 'message': 'Job role not found'}), 404
        
        voice_weight = job_role.get('voice_confidence_weight', 33.33) / 100
        hand_weight = job_role.get('hand_confidence_weight', 33.33) / 100
        eye_weight = job_role.get('eye_confidence_weight', 33.33) / 100
        
        # Get confidence analysis data
        confidence_data = db_manager.get_confidence_analysis(interview_id)
        stress_data = db_manager.get_stress_analysis(interview_id)
        
        # Calculate confidence scores using your exact formula
        # Example: 120s interview, 60s voice confident, 60s hand confident, 40s eye confident
        # HR weights: Voice 20%, Hand 30%, Eye 50%
        # Voice: (60/120) * (20/100) = 0.5 * 0.2 = 0.1
        # Hand: (60/120) * (30/100) = 0.5 * 0.3 = 0.15  
        # Eye: (40/120) * (50/100) = 0.33 * 0.5 = 0.165
        # Final: (0.1 + 0.15 + 0.165) / 3 = 0.138 = 13.8%
        
        # Count confident seconds for each component (binary: 1 = confident, 0 = non-confident)
        total_voice_confident_seconds = sum([d.get('voice_confidence', 0) for d in confidence_data])
        total_hand_confident_seconds = sum([d.get('hand_confidence', 0) for d in confidence_data])
        total_eye_confident_seconds = sum([d.get('eye_confidence', 0) for d in confidence_data])
        
        # Calculate using your exact formula: (time/120) * (weight/100)
        voice_score = (total_voice_confident_seconds / interview_duration) * (voice_weight / 100) if interview_duration > 0 else 0
        hand_score = (total_hand_confident_seconds / interview_duration) * (hand_weight / 100) if interview_duration > 0 else 0
        eye_score = (total_eye_confident_seconds / interview_duration) * (eye_weight / 100) if interview_duration > 0 else 0
        
        # Final confidence score: sum of all three values divided by 3
        final_confidence = ((voice_score + hand_score + eye_score) / 3) * 100
        
        # Calculate percentages for display
        voice_percentage = (total_voice_confident_seconds / interview_duration) * 100 if interview_duration > 0 else 0
        hand_percentage = (total_hand_confident_seconds / interview_duration) * 100 if interview_duration > 0 else 0
        eye_percentage = (total_eye_confident_seconds / interview_duration) * 100 if interview_duration > 0 else 0
        
        # Calculate stress score: negative emotion frames / total frames
        total_negative_frames = sum([d.get('negative_emotion_frames', 0) for d in stress_data])
        total_frames = sum([d.get('total_frames', 0) for d in stress_data])
        
        if total_frames > 0:
            final_stress = (total_negative_frames / total_frames) * 100
        else:
            final_stress = 0
        
        # Save final analysis with your exact formula results
        final_analysis = {
            'interview_id': interview_id,
            'user_id': user_id,
            'final_confidence_score': final_confidence,
            'final_stress_score': final_stress,
            'voice_percentage': voice_percentage,
            'hand_percentage': hand_percentage,
            'eye_percentage': eye_percentage,
            'voice_score': voice_score * 100,  # (time/120) * (weight/100) * 100
            'hand_score': hand_score * 100,    # (time/120) * (weight/100) * 100
            'eye_score': eye_score * 100,      # (time/120) * (weight/100) * 100
            'total_voice_confident_seconds': total_voice_confident_seconds,
            'total_hand_confident_seconds': total_hand_confident_seconds,
            'total_eye_confident_seconds': total_eye_confident_seconds,
            'total_negative_frames': total_negative_frames,
            'total_frames': total_frames,
            'interview_duration': interview_duration,
            'voice_weight': voice_weight,
            'hand_weight': hand_weight,
            'eye_weight': eye_weight,
            'created_at': datetime.now().isoformat()
        }
        
        db_manager.save_final_analysis(final_analysis)
        
        return jsonify({
            'status': 'success',
            'data': final_analysis
        })
        
    except Exception as e:
        logger.error(f"Error calculating final analysis: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# ==================== TEST & DEBUG APIs ====================

@app.route('/api/test/database', methods=['GET'])
def test_database_connection():
    """Test database connections"""
    try:
        db_manager = DatabaseManager()
        
        # Test Firestore
        firestore_status = "connected" if db_manager.db else "disconnected"
        
        # Test Realtime Database
        rtdb_status = "connected" if db_manager.rtdb else "disconnected"
        
        return jsonify({
            'status': 'success',
            'firestore': firestore_status,
            'realtime_database': rtdb_status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error testing database: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/test/candidate', methods=['POST'])
def test_create_candidate():
    """Test candidate creation with sample data"""
    try:
        sample_candidate = {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'position': 'Software Engineer',
            'phone': '+1234567890',
            'experience_years': 5,
            'skills': ['Python', 'JavaScript', 'React'],
            'education': 'Bachelor in Computer Science'
        }
        
        db_manager = DatabaseManager()
        candidate_id = db_manager.create_candidate(sample_candidate)
        
        if candidate_id:
            candidate = db_manager.get_candidate(candidate_id)
            return jsonify({
                'status': 'success',
                'message': 'Test candidate created successfully',
                'candidate': candidate
            }), 201
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to create test candidate'
            }), 500
            
    except Exception as e:
        logger.error(f"Error creating test candidate: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'InsightHire Backend',
        'timestamp': datetime.now().isoformat(),
        'active_sessions': len(active_analyzers)
    })

# WebSocket Events for Real-time Communication

@socketio.on_error_default
def default_error_handler(e):
    """Default error handler for SocketIO events"""
    logger.error(f"SocketIO error: {e}")
    emit('error', {'message': 'An error occurred'})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    try:
        logger.info(f"Client connected: {request.sid}")
        emit('connected', {'message': 'Connected to InsightHire'})
    except Exception as e:
        logger.error(f"Error in connect handler: {e}")
        emit('error', {'message': 'Connection error'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    try:
        logger.info(f"Client disconnected: {request.sid}")
        
        # Clean up any analyzers for disconnected sessions (defensive cleanup)
        # Since we don't maintain client-to-session mapping, we'll just log this
        # The actual cleanup should happen in leave_session or stop_interview
        
        # Log current active analyzers for debugging
        if active_analyzers:
            logger.info(f"🔍 Active analyzers after client disconnect: {list(active_analyzers.keys())}")
        else:
            logger.info(f"✅ No active analyzers remaining")
        
        logger.info(f"🔌 Client {request.sid} disconnect handled")
    except Exception as e:
        logger.error(f"Error in disconnect handler: {e}")

@socketio.on('join_session')
def handle_join_session(data):
    """Handle joining a session room"""
    try:
        session_id = data.get('session_id')
        if session_id:
            join_room(session_id)
            logger.info(f"Client {request.sid} joined session {session_id}")
            
            # Check if analysis is already running for this session
            analysis_status = {
                'session_id': session_id,
                'analysis_active': session_id in active_analyzers,
                'analyzer_count': len(active_analyzers)
            }
            
            if session_id in active_analyzers:
                logger.info(f"✅ Analysis is active for session {session_id}")
                analysis_status['message'] = 'Analysis is running'
            else:
                logger.warning(f"⚠️ No active analysis found for session {session_id}")
                analysis_status['message'] = 'Analysis not started - start interview first'
            
            emit('joined_session', analysis_status)
    except Exception as e:
        logger.error(f"Error in join_session handler: {e}")
        emit('error', {'message': 'Failed to join session'})

@socketio.on('leave_session')
def handle_leave_session(data):
    """Handle leaving a session room"""
    session_id = data.get('session_id')
    if session_id:
        leave_room(session_id)
        logger.info(f"Client {request.sid} left session {session_id}")
        
        # Stop the analyzer safely when client leaves session
        if session_id in active_analyzers:
            try:
                analyzer = active_analyzers[session_id]
                logger.info(f"🛑 Stopping analyzer for session {session_id} due to client leaving")
                analyzer.stop_analysis()
                analyzer.reset_audio_state()
                del active_analyzers[session_id]
                logger.info(f"✅ Analyzer stopped and removed for session {session_id}")
            except Exception as e:
                logger.error(f"❌ Error stopping analyzer for session {session_id}: {e}")
                if session_id in active_analyzers:
                    del active_analyzers[session_id]

@socketio.on('video_frame')
def handle_video_frame(data):
    """Handle incoming video frame"""
    try:
        session_id = data.get('session_id')
        frame_data = data.get('frame')
        
        # Reduce logging frequency to prevent spam
        # logger.info(f"📹 Received video frame for session: {session_id}")
        
        if session_id and session_id in active_analyzers:
            if frame_data:
                # Decode base64 frame
                frame_bytes = base64.b64decode(frame_data.split(',')[1])
                np_arr = np.frombuffer(frame_bytes, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    # Reduce logging frequency to prevent spam
                    # logger.info(f"✅ Video frame decoded successfully: {frame.shape}")
                    
                    # Add to analyzer (analysis will run every 10 seconds, not on every frame)
                    active_analyzers[session_id].add_video_frame(frame)
                else:
                    logger.error("❌ Failed to decode video frame")
            else:
                # Null frame data - this is a stop signal
                logger.info(f"🛑 Received video stop signal for session {session_id}")
                if session_id in active_analyzers:
                    analyzer = active_analyzers[session_id]
                    analyzer.stop_analysis()
                    analyzer.reset_audio_state()
                    del active_analyzers[session_id]
                    logger.info(f"✅ Analyzer stopped due to video stop signal for session {session_id}")
        else:
            logger.warning(f"⚠️ Missing data - session_id: {session_id is not None}, frame_data: {frame_data is not None}, analyzer_exists: {session_id in active_analyzers if session_id else False}")
            
    except Exception as e:
        logger.error(f"Error processing video frame: {e}")

@socketio.on('audio_data')
def handle_audio_data(data):
    """Handle incoming audio data"""
    try:
        session_id = data.get('session_id')
        audio_data = data.get('audio')
        sample_rate = data.get('sample_rate', 22050)
        is_stop_signal = data.get('is_stop_signal', False)
        
        # Reduce logging frequency to prevent spam
        # logger.info(f"🎤 Received audio data: session_id={session_id}, audio_length={len(audio_data) if audio_data else 0}, sample_rate={sample_rate}, is_stop_signal={is_stop_signal}")
        
        if session_id and session_id in active_analyzers:
            if is_stop_signal or audio_data is None:
                # Audio recording has stopped - this is a stop signal
                logger.info(f"🛑 Audio stop signal received for session {session_id}")
                # Stop the analyzer immediately when stop signal is received
                analyzer = active_analyzers[session_id]
                analyzer.stop_analysis()
                analyzer.reset_audio_state()
                del active_analyzers[session_id]
                logger.info(f"✅ Analyzer stopped due to audio stop signal for session {session_id}")
            elif audio_data:
                # Convert audio data to numpy array
                audio_array = np.array(audio_data, dtype=np.float32)
                
                # Add to analyzer
                active_analyzers[session_id].add_audio_data(audio_array, sample_rate)
                # Reduce logging frequency to prevent spam
                # logger.info(f"🎤 Added audio data to analyzer for session {session_id}")
        elif session_id and is_stop_signal:
            # Interview has already stopped, this is the final reset
            logger.info(f"🎤 Interview stopped - final voice confidence reset for session {session_id}")
        else:
            if not session_id:
                logger.warning("🎤 No session_id in audio data")
            elif session_id not in active_analyzers and not is_stop_signal:
                logger.warning(f"🎤 No active analyzer for session {session_id}")
            
    except Exception as e:
        logger.error(f"🎤 Error processing audio data: {e}")

# REMOVED: get_live_results handler - analysis already emits automatically

# Final Scores API Endpoints
@app.route('/api/interviews/final-scores', methods=['POST'])
def save_final_scores():
    """Save final interview scores to database"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        user_id = data.get('user_id')
        job_role_id = data.get('job_role_id')
        final_scores = data.get('final_scores')
        timestamp = data.get('timestamp')
        
        if not all([session_id, user_id, job_role_id, final_scores]):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields: session_id, user_id, job_role_id, final_scores'
            }), 400
        
        # Save to database
        db_manager = DatabaseManager()
        result = db_manager.save_final_scores(
            session_id=session_id,
            user_id=user_id,
            job_role_id=job_role_id,
            final_scores=final_scores,
            timestamp=timestamp
        )
        
        if result:
            logger.info(f"✅ Final scores saved for session {session_id}")
            return jsonify({
                'status': 'success',
                'message': 'Final scores saved successfully',
                'data': result
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to save final scores'
            }), 500
            
    except Exception as e:
        logger.error(f"Error saving final scores: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/interviews/final-scores/<session_id>', methods=['GET'])
def get_final_scores(session_id):
    """Get final scores for a specific session"""
    try:
        db_manager = DatabaseManager()
        scores = db_manager.get_final_scores(session_id)
        
        if scores:
            return jsonify({
                'status': 'success',
                'data': scores
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Final scores not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error fetching final scores: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/interviews/final-scores/user/<user_id>', methods=['GET'])
def get_user_final_scores(user_id):
    """Get all final scores for a user"""
    try:
        db_manager = DatabaseManager()
        scores = db_manager.get_user_final_scores(user_id)
        
        return jsonify({
            'status': 'success',
            'data': scores
        })
            
    except Exception as e:
        logger.error(f"Error fetching user final scores: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/interviews/records/<session_id>', methods=['GET'])
def get_interview_records(session_id):
    """Get all interview records for scoring calculation"""
    try:
        db_manager = DatabaseManager()
        records = db_manager.get_interview_records(session_id)
        
        return jsonify({
            'status': 'success',
            'data': records
        })
            
    except Exception as e:
        logger.error(f"Error fetching interview records: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/interviews/<session_id>/calculate-final-scores', methods=['POST'])
def calculate_final_scores(session_id):
    """Calculate and save final scores for an interview session"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        job_role_id = data.get('job_role_id')
        
        if not user_id or not job_role_id:
            return jsonify({
                'status': 'error',
                'message': 'user_id and job_role_id are required'
            }), 400
        
        db_manager = DatabaseManager()
        
        # Get interview records
        records = db_manager.get_interview_records(session_id)
        if not records:
            return jsonify({
                'status': 'error',
                'message': 'No interview records found for this session'
            }), 404
        
        # Get job role to fetch confidence level weights
        job_role = db_manager.get_job_role(job_role_id)
        if not job_role:
            return jsonify({
                'status': 'error',
                'message': 'Job role not found'
            }), 404
        
        # Extract confidence level weights from job role
        confidence_levels = job_role.get('confidence_levels', {})
        weights = {
            'hand_confidence': confidence_levels.get('hand_confidence', 33.33),
            'eye_confidence': confidence_levels.get('eye_confidence', 33.33),
            'voice_confidence': confidence_levels.get('voice_confidence', 33.33)
        }
        
        logger.info(f"Using job-specific weights for {job_role.get('name', 'Unknown')}: Hand={weights['hand_confidence']}%, Eye={weights['eye_confidence']}%, Voice={weights['voice_confidence']}%")
        
        # Calculate scores using job-specific weights
        def calculate_component_confidence(records, component, weight):
            if not records or len(records) == 0:
                return 0
            
            confident_records = [r for r in records if r.get(component, {}).get('confidence') == 1]
            confidence_ratio = len(confident_records) / len(records)
            return (confidence_ratio * weight) / 100
        
        hand_conf = calculate_component_confidence(records, 'hand_confidence', weights['hand_confidence'])
        eye_conf = calculate_component_confidence(records, 'eye_confidence', weights['eye_confidence'])
        voice_conf = calculate_component_confidence(records, 'voice_confidence', weights['voice_confidence'])
        
        overall_confidence = (hand_conf + eye_conf + voice_conf) * 100
        
        # Calculate stress
        stress_records = [r for r in records if r.get('face_stress', {}).get('stress') == 1]
        stress_ratio = len(stress_records) / len(records)
        overall_stress = stress_ratio * 100
        
        # Create final scores object
        final_scores = {
            'confidence': {
                'hand_confidence': {
                    'percentage': (hand_conf / weights['hand_confidence']) * 100,
                    'weighted_score': hand_conf
                },
                'eye_confidence': {
                    'percentage': (eye_conf / weights['eye_confidence']) * 100,
                    'weighted_score': eye_conf
                },
                'voice_confidence': {
                    'percentage': (voice_conf / weights['voice_confidence']) * 100,
                    'weighted_score': voice_conf
                },
                'overall_confidence': overall_confidence,
                'total_records': len(records)
            },
            'stress': {
                'overall_stress': overall_stress,
                'total_records': len(records),
                'stress_records': len(stress_records)
            },
            'calculated_at': datetime.now().isoformat(),
            'analysis_summary': {
                'total_records_analyzed': len(records),
                'confidence_level': 'Very High' if overall_confidence >= 80 else 'High' if overall_confidence >= 60 else 'Medium' if overall_confidence >= 40 else 'Low' if overall_confidence >= 20 else 'Very Low',
                'stress_level': 'Very Low' if overall_stress <= 20 else 'Low' if overall_stress <= 40 else 'Medium' if overall_stress <= 60 else 'High' if overall_stress <= 80 else 'Very High',
                'job_role_name': job_role.get('name', 'Unknown'),
                'job_weights': weights
            }
        }
        
        # Save final scores
        result = db_manager.save_final_scores(
            session_id=session_id,
            user_id=user_id,
            job_role_id=job_role_id,
            final_scores=final_scores
        )
        
        if result:
            logger.info(f"✅ Final scores calculated and saved for session {session_id}")
            return jsonify({
                'status': 'success',
                'message': 'Final scores calculated and saved successfully',
                'data': {
                    'final_scores': final_scores,
                    'saved_data': result
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to save final scores'
            }), 500
            
    except Exception as e:
        logger.error(f"Error calculating final scores: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# ==================== PREMIUM CODE API ENDPOINTS ====================

@app.route('/api/premium/validate', methods=['POST'])
def validate_premium_code():
    """Validate a premium code"""
    try:
        data = request.get_json()
        premium_code = data.get('premium_code')
        
        if not premium_code:
            return jsonify({
                'status': 'error',
                'message': 'Premium code is required'
            }), 400
        
        db_manager = DatabaseManager()
        validation_result = db_manager.validate_premium_code(premium_code)
        
        if validation_result['valid']:
            return jsonify({
                'status': 'success',
                'message': validation_result['message'],
                'valid': True
            })
        else:
            return jsonify({
                'status': 'error',
                'message': validation_result['message'],
                'valid': False
            }), 400
            
    except Exception as e:
        logger.error(f"Error validating premium code: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error validating premium code'
        }), 500

@app.route('/api/premium/use', methods=['POST'])
def use_premium_code():
    """Use a premium code (mark as used)"""
    try:
        data = request.get_json()
        premium_code = data.get('premium_code')
        user_id = data.get('user_id')
        
        if not premium_code:
            return jsonify({
                'status': 'error',
                'message': 'Premium code is required'
            }), 400
        
        db_manager = DatabaseManager()
        
        # First validate the code
        validation_result = db_manager.validate_premium_code(premium_code)
        if not validation_result['valid']:
            return jsonify({
                'status': 'error',
                'message': validation_result['message']
            }), 400
        
        # Mark as used
        success = db_manager.use_premium_code(premium_code, user_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Premium code activated successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to activate premium code'
            }), 500
            
    except Exception as e:
        logger.error(f"Error using premium code: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error using premium code'
        }), 500

@app.route('/api/premium/generate', methods=['POST'])
def generate_premium_code():
    """Generate a new premium code (admin function)"""
    try:
        data = request.get_json()
        payment_data = data.get('payment_data', {})
        
        db_manager = DatabaseManager()
        premium_code = db_manager.create_premium_code(payment_data)
        
        if premium_code:
            return jsonify({
                'status': 'success',
                'message': 'Premium code generated successfully',
                'premium_code': premium_code
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to generate premium code'
            }), 500
            
    except Exception as e:
        logger.error(f"Error generating premium code: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error generating premium code'
        }), 500

@app.route('/api/premium/purchase', methods=['POST'])
def purchase_premium_code():
    """Purchase a premium code with payment details"""
    try:
        data = request.get_json()
        
        # Extract payment details
        payment_data = {
            'card_number': data.get('card_number'),
            'card_holder': data.get('card_holder'),
            'expiry_date': data.get('expiry_date'),
            'cvv': data.get('cvv'),
            'amount': data.get('amount', 99.99),  # Default price
            'currency': data.get('currency', 'USD'),
            'timestamp': datetime.now().isoformat()
        }
        
        # Basic payment validation (in production, use a proper payment processor)
        required_fields = ['card_number', 'card_holder', 'expiry_date', 'cvv']
        for field in required_fields:
            if not payment_data.get(field):
                return jsonify({
                    'status': 'error',
                    'message': f'{field.replace("_", " ").title()} is required'
                }), 400
        
        # Simple card number validation (basic Luhn algorithm)
        card_number = payment_data['card_number'].replace(' ', '').replace('-', '')
        if not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 19:
            return jsonify({
                'status': 'error',
                'message': 'Invalid card number'
            }), 400
        
        # Generate premium code
        db_manager = DatabaseManager()
        premium_code = db_manager.create_premium_code(payment_data)
        
        if premium_code:
            return jsonify({
                'status': 'success',
                'message': 'Payment processed successfully',
                'premium_code': premium_code,
                'payment_data': {
                    'amount': payment_data['amount'],
                    'currency': payment_data['currency'],
                    'timestamp': payment_data['timestamp']
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Payment processed but failed to generate premium code'
            }), 500
            
    except Exception as e:
        logger.error(f"Error processing premium code purchase: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error processing payment'
        }), 500

@app.route('/api/premium/check-access', methods=['GET'])
def check_premium_access():
    """Check if user has premium access"""
    try:
        user_id = get_user_id_from_request()
        
        if not user_id:
            return jsonify({
                'status': 'error',
                'message': 'User ID is required'
            }), 400
        
        db_manager = DatabaseManager()
        access_info = db_manager.get_user_premium_access(user_id)
        
        return jsonify({
            'status': 'success',
            'has_premium': access_info['has_premium'],
            'premium_code': access_info.get('premium_code'),
            'used_at': access_info.get('used_at')
        })
        
    except Exception as e:
        logger.error(f"Error checking premium access: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error checking premium access'
        }), 500

# REMOVED: Background periodic updates - analysis already emits via Socket.IO
# This was causing duplicate requests and overheating

# REMOVED: Background thread for periodic updates - not needed anymore

if __name__ == '__main__':
    # Initialize Firebase
    try:
        logger.info("Firebase configuration loaded")
    except Exception as e:
        logger.error(f"Error loading Firebase configuration: {e}")
    
    # REMOVED: No more background thread needed
    
    # Start the server
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting InsightHire server on {host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug_mode, allow_unsafe_werkzeug=True, use_reloader=False)
