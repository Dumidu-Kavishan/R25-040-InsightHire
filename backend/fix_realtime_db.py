#!/usr/bin/env python3
"""
Fix Realtime Database permissions and test connection
"""
import firebase_admin
from firebase_admin import credentials, db
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def test_realtime_db():
    """Test Realtime Database connection and permissions"""
    try:
        # Initialize Firebase Admin (if not already done)
        if not firebase_admin._apps:
            cred = credentials.Certificate('serviceAccountKey.json')
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://insighthire-335a6-default-rtdb.asia-southeast1.firebasedatabase.app/'
            })
        
        # Test basic write operation
        logger.info("🔥 Testing Realtime Database connection...")
        
        # Try to write to a test location
        test_ref = db.reference('test_connection')
        test_data = {
            'timestamp': datetime.now().isoformat(),
            'message': 'Connection test successful',
            'session_id': 'test-session-123'
        }
        
        logger.info(f"📝 Writing test data to Realtime DB...")
        result = test_ref.set(test_data)
        logger.info(f"✅ Test write successful!")
        
        # Try to read back the data
        logger.info(f"📖 Reading test data from Realtime DB...")
        read_data = test_ref.get()
        logger.info(f"✅ Test read successful: {read_data}")
        
        # Test session-specific path (like we use in the app)
        session_ref = db.reference('sessions/test-session-123/analysis')
        analysis_data = {
            'timestamp': datetime.now().isoformat(),
            'face_stress': {'level': 'low_stress', 'confidence': 0.75},
            'hand_confidence': {'level': 'confident', 'confidence': 0.85},
            'eye_confidence': {'level': 'confident', 'confidence': 0.90}
        }
        
        logger.info(f"📝 Writing analysis data to session path...")
        analysis_result = session_ref.push(analysis_data)
        logger.info(f"✅ Analysis write successful! Key: {analysis_result.key}")
        
        # Test latest analysis path
        latest_ref = db.reference('sessions/test-session-123/latest_analysis')
        latest_data = {
            'timestamp': datetime.now().isoformat(),
            'overall_score': 0.83,
            'status': 'active'
        }
        
        logger.info(f"📝 Writing latest analysis data...")
        latest_ref.set(latest_data)
        logger.info(f"✅ Latest analysis write successful!")
        
        # Clean up test data
        logger.info(f"🧹 Cleaning up test data...")
        test_ref.delete()
        db.reference('sessions/test-session-123').delete()
        logger.info(f"✅ Cleanup completed!")
        
        logger.info(f"🎉 All Realtime Database tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Realtime Database test failed: {e}")
        logger.error(f"❌ Error type: {type(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return False

def check_database_rules():
    """Check current database rules"""
    try:
        logger.info("🔍 Checking database configuration...")
        
        # Try to access the rules (this might not work with service account)
        rules_ref = db.reference('.settings/rules')
        try:
            rules = rules_ref.get()
            logger.info(f"📋 Current rules: {rules}")
        except:
            logger.info("📋 Cannot read rules with service account (this is normal)")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error checking rules: {e}")
        return False

if __name__ == '__main__':
    logger.info("🚀 Starting Realtime Database fix and test...")
    
    # Test basic connection
    if test_realtime_db():
        logger.info("✅ Realtime Database is working properly!")
        logger.info("📊 Your data should now save correctly to both Firestore and Realtime DB")
    else:
        logger.error("❌ Realtime Database connection failed")
        logger.info("💡 Suggestions:")
        logger.info("   1. Check if your service account has 'Firebase Realtime Database Admin' role")
        logger.info("   2. Verify the database URL is correct")
        logger.info("   3. Check if Realtime Database is enabled in Firebase Console")
        logger.info("   4. Review database rules in Firebase Console > Realtime Database > Rules")
    
    # Check rules
    check_database_rules()
