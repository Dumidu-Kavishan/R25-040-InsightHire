#!/usr/bin/env python3
"""
Test the exact database save_realtime_analysis method
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from utils.database import DatabaseManager
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def test_exact_save_method():
    """Test the exact save_realtime_analysis method that's failing"""
    try:
        logger.info("🧪 Testing exact DatabaseManager.save_realtime_analysis method...")
        
        # Create database manager
        db_manager = DatabaseManager(user_id="test-user-123")
        
        # Test data similar to what's being saved in real app
        session_id = "test-session-456"
        analysis_data = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'user_id': 'test-user-123',
            'face_stress': {
                'stress_level': 'low_stress',
                'confidence': 0.65
            },
            'hand_confidence': {
                'confidence_level': 'not_confident',
                'confidence': 0.00
            },
            'eye_confidence': {
                'confidence_level': 'confident',
                'confidence': 1.00
            },
            'voice_confidence': {
                'confidence_level': 'neutral',
                'confidence': 0.50
            },
            'overall': {
                'confidence_score': 0.75,
                'stress_score': 0.65,
                'timestamp': datetime.now().isoformat(),
                'components_used': 3
            }
        }
        
        logger.info(f"📝 Testing save_realtime_analysis with session_id: {session_id}")
        
        # Call the exact method that's failing
        result = db_manager.save_realtime_analysis(session_id, analysis_data)
        
        if result:
            logger.info(f"✅ save_realtime_analysis SUCCESS! Returned key: {result}")
        else:
            logger.error(f"❌ save_realtime_analysis FAILED! Returned: {result}")
        
        # Also test the save_analysis_result method (Firestore)
        logger.info(f"📝 Testing save_analysis_result (Firestore)...")
        firestore_result = db_manager.save_analysis_result(session_id, analysis_data)
        
        if firestore_result:
            logger.info(f"✅ save_analysis_result SUCCESS! Doc ID: {firestore_result}")
        else:
            logger.error(f"❌ save_analysis_result FAILED! Returned: {firestore_result}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == '__main__':
    logger.info("🚀 Starting exact method test...")
    
    if test_exact_save_method():
        logger.info("✅ Test completed successfully!")
    else:
        logger.error("❌ Test failed!")
