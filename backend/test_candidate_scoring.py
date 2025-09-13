#!/usr/bin/env python3
"""
Test candidate data and real-time scoring data saving
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from utils.database import DatabaseManager
import logging
from datetime import datetime
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def test_candidate_creation():
    """Test candidate data saving"""
    try:
        logger.info("🧪 Testing candidate data creation...")
        
        db_manager = DatabaseManager()
        
        # Test candidate data
        candidate_data = {
            'name': 'John Doe Test',
            'email': 'john.doe.test@example.com',
            'position': 'Senior Software Engineer',
            'phone': '+1-555-123-4567',
            'experience_years': 5,
            'skills': ['Python', 'JavaScript', 'React', 'Node.js'],
            'education': 'Bachelor of Computer Science',
            'notes': 'Experienced full-stack developer with strong problem-solving skills'
        }
        
        logger.info(f"📝 Creating candidate with data: {json.dumps(candidate_data, indent=2)}")
        
        # Create candidate
        candidate_id = db_manager.create_candidate(candidate_data)
        
        if candidate_id:
            logger.info(f"✅ Candidate created successfully! ID: {candidate_id}")
            
            # Try to retrieve the candidate
            retrieved = db_manager.get_candidate(candidate_id)
            if retrieved:
                logger.info(f"✅ Candidate retrieved successfully!")
                logger.info(f"📋 Retrieved data: {json.dumps(retrieved, indent=2)}")
            else:
                logger.error(f"❌ Failed to retrieve candidate {candidate_id}")
            
            return candidate_id
        else:
            logger.error(f"❌ Failed to create candidate")
            return None
            
    except Exception as e:
        logger.error(f"❌ Candidate creation test failed: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return None

def test_interview_creation_with_candidate():
    """Test interview creation with candidate"""
    try:
        logger.info("🧪 Testing interview creation with candidate...")
        
        db_manager = DatabaseManager()
        
        # Create candidate first
        candidate_data = {
            'name': 'Jane Smith Interview Test',
            'email': 'jane.smith.test@example.com',
            'position': 'Frontend Developer',
            'phone': '+1-555-987-6543',
            'experience_years': 3,
            'skills': ['React', 'Vue.js', 'CSS', 'HTML'],
            'education': 'Bachelor of Arts in Computer Science',
            'notes': 'Frontend specialist with strong UI/UX skills'
        }
        
        candidate_id = db_manager.create_candidate(candidate_data)
        if not candidate_id:
            logger.error("❌ Failed to create candidate for interview test")
            return None
        
        logger.info(f"✅ Candidate created for interview: {candidate_id}")
        
        # Create interview
        interview_data = {
            'user_id': 'test-interviewer-123',
            'candidate_id': candidate_id,
            'candidate_name': candidate_data['name'],
            'position': candidate_data['position'],
            'interview_type': 'technical',
            'platform': 'browser',
            'scheduled_at': datetime.now().isoformat(),
            'duration_minutes': 60,
            'status': 'scheduled',
            'notes': 'Frontend technical interview focusing on React and CSS',
            'questions': [
                'Explain React hooks',
                'What is CSS Grid vs Flexbox?',
                'How do you optimize web performance?'
            ],
            'evaluation_criteria': [
                'Technical knowledge',
                'Problem-solving ability',
                'Communication skills'
            ]
        }
        
        logger.info(f"📝 Creating interview with data...")
        interview_id = db_manager.create_interview(interview_data)
        
        if interview_id:
            logger.info(f"✅ Interview created successfully! ID: {interview_id}")
            
            # Try to retrieve the interview
            retrieved = db_manager.get_interview(interview_id)
            if retrieved:
                logger.info(f"✅ Interview retrieved successfully!")
                logger.info(f"📋 Interview data: {json.dumps(retrieved, indent=2)}")
            else:
                logger.error(f"❌ Failed to retrieve interview {interview_id}")
            
            return interview_id
        else:
            logger.error(f"❌ Failed to create interview")
            return None
            
    except Exception as e:
        logger.error(f"❌ Interview creation test failed: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return None

def test_real_time_scoring_data():
    """Test real-time scoring data saving"""
    try:
        logger.info("🧪 Testing real-time scoring data saving...")
        
        db_manager = DatabaseManager()
        session_id = "scoring-test-session-789"
        
        # Test comprehensive scoring data
        scoring_data = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'user_id': 'test-candidate-456',
            'candidate_id': 'test-candidate-789',
            'interview_id': 'test-interview-123',
            
            # AI Analysis Results
            'face_stress': {
                'stress_level': 'moderate_stress',
                'confidence': 0.72,
                'emotion': 'focused',
                'facial_features': {
                    'eye_movement': 'stable',
                    'micro_expressions': 'concentrated'
                }
            },
            'hand_confidence': {
                'confidence_level': 'confident',
                'confidence': 0.85,
                'gesture_type': 'explanatory',
                'hand_movement': 'purposeful'
            },
            'eye_confidence': {
                'confidence_level': 'very_confident',
                'confidence': 0.92,
                'eye_contact': 'maintained',
                'gaze_direction': 'camera_focused'
            },
            'voice_confidence': {
                'confidence_level': 'confident',
                'confidence': 0.78,
                'tone': 'clear',
                'speech_rate': 'normal',
                'vocal_quality': 'stable'
            },
            
            # Calculated Overall Scores
            'overall': {
                'confidence_score': 0.84,
                'stress_score': 0.72,
                'performance_score': 0.82,
                'communication_score': 0.80,
                'technical_score': 0.85,
                'timestamp': datetime.now().isoformat(),
                'components_used': 4
            },
            
            # Interview-specific data
            'interview_metrics': {
                'question_number': 3,
                'response_time_seconds': 45,
                'clarity_score': 0.88,
                'technical_accuracy': 0.90,
                'problem_solving_approach': 'systematic'
            },
            
            # Session metadata
            'session_metadata': {
                'duration_minutes': 25,
                'questions_answered': 3,
                'technical_demos': 1,
                'interaction_quality': 'high'
            }
        }
        
        logger.info(f"📝 Saving comprehensive scoring data for session: {session_id}")
        
        # Save to Firestore (analysis_results collection)
        result = db_manager.save_analysis_result(session_id, scoring_data)
        
        if result:
            logger.info(f"✅ Scoring data saved to Firestore! Doc ID: {result}")
            
            # Try to retrieve the saved data
            session_results = db_manager.get_session_results(session_id)
            if session_results:
                logger.info(f"✅ Scoring data retrieved successfully!")
                logger.info(f"📊 Found {len(session_results)} scoring records for session")
                
                for i, record in enumerate(session_results):
                    logger.info(f"  Record {i+1}:")
                    logger.info(f"    Overall confidence: {record.get('overall', {}).get('confidence_score', 'N/A')}")
                    logger.info(f"    Overall stress: {record.get('overall', {}).get('stress_score', 'N/A')}")
                    logger.info(f"    Performance score: {record.get('overall', {}).get('performance_score', 'N/A')}")
            else:
                logger.error(f"❌ Failed to retrieve scoring data for session {session_id}")
            
            return result
        else:
            logger.error(f"❌ Failed to save scoring data")
            return None
            
    except Exception as e:
        logger.error(f"❌ Scoring data test failed: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return None

def check_firebase_collections():
    """Check what collections exist in Firestore"""
    try:
        logger.info("🔍 Checking Firebase collections...")
        
        from firebase_config import db
        
        # Get all collections
        collections = db.collections()
        
        logger.info("📊 Firebase Collections found:")
        for collection in collections:
            logger.info(f"  📁 {collection.id}")
            
            # Get sample documents from each collection
            docs = collection.limit(3).stream()
            doc_count = 0
            for doc in docs:
                doc_count += 1
                logger.info(f"    📄 Sample doc: {doc.id}")
            
            if doc_count == 0:
                logger.info(f"    📄 No documents found in {collection.id}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking collections: {e}")
        return False

if __name__ == '__main__':
    logger.info("🚀 Starting comprehensive candidate and scoring data tests...")
    
    # Test 1: Candidate Creation
    logger.info("\n" + "="*50)
    logger.info("TEST 1: CANDIDATE DATA SAVING")
    logger.info("="*50)
    candidate_result = test_candidate_creation()
    
    # Test 2: Interview Creation
    logger.info("\n" + "="*50)
    logger.info("TEST 2: INTERVIEW CREATION WITH CANDIDATE")
    logger.info("="*50)
    interview_result = test_interview_creation_with_candidate()
    
    # Test 3: Real-time Scoring Data
    logger.info("\n" + "="*50)
    logger.info("TEST 3: REAL-TIME SCORING DATA SAVING")
    logger.info("="*50)
    scoring_result = test_real_time_scoring_data()
    
    # Test 4: Check Collections
    logger.info("\n" + "="*50)
    logger.info("TEST 4: FIREBASE COLLECTIONS CHECK")
    logger.info("="*50)
    collections_result = check_firebase_collections()
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("SUMMARY")
    logger.info("="*50)
    logger.info(f"✅ Candidate Creation: {'PASS' if candidate_result else 'FAIL'}")
    logger.info(f"✅ Interview Creation: {'PASS' if interview_result else 'FAIL'}")
    logger.info(f"✅ Scoring Data Saving: {'PASS' if scoring_result else 'FAIL'}")
    logger.info(f"✅ Collections Check: {'PASS' if collections_result else 'FAIL'}")
    
    if candidate_result and interview_result and scoring_result:
        logger.info("🎉 ALL TESTS PASSED! Data is being saved correctly.")
    else:
        logger.error("❌ Some tests failed. Check the logs above for details.")
