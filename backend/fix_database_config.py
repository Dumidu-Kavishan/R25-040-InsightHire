#!/usr/bin/env python3
"""
Fix database configuration mismatch by updating to correct database instance
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def create_correct_firebase_config():
    """Create updated Firebase configuration to match console database"""
    try:
        logger.info("🔧 CREATING CORRECTED FIREBASE CONFIGURATION...")
        
        # Read current service account
        with open('serviceAccountKey.json', 'r') as f:
            service_account = json.load(f)
        
        project_id = service_account.get('project_id')
        
        # Create new firebase_config.py that explicitly targets the default database
        new_config = '''"""
Firebase Configuration for InsightHire - Fixed for Console Database
"""
import firebase_admin
from firebase_admin import credentials, firestore, auth, db as realtime_db
import json
import os

def initialize_firebase():
    """Initialize Firebase Admin SDK with explicit database targeting"""
    try:
        # Check if Firebase is already initialized
        app = firebase_admin.get_app()
        print("Firebase already initialized")
        return firestore.client(app), realtime_db
    except ValueError:
        # Initialize Firebase if not already done
        try:
            # Load credentials from the serviceAccountKey.json file
            cred_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
            print(f"🔑 Loading credentials from: {cred_path}")
            cred = credentials.Certificate(cred_path)
            
            # Initialize Firebase with explicit database configuration
            app = firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://insighthire-335a6-default-rtdb.asia-southeast1.firebasedatabase.app',
                'projectId': 'insighthire-335a6'
            })
            print("✅ Firebase initialized successfully with explicit config")
            
            # Create Firestore client explicitly targeting (default) database
            db_client = firestore.client(app, database='(default)')
            
            print("✅ Firestore client created targeting (default) database")
            
            return db_client, realtime_db
        except Exception as e:
            print(f"❌ Error initializing Firebase: {e}")
            raise e

# Initialize Firebase when this module is imported
try:
    db, rtdb = initialize_firebase()
    print("✅ Firebase configuration loaded successfully - targeting (default) database")
except Exception as e:
    print(f"❌ Failed to load Firebase configuration: {e}")
    db, rtdb = None, None
'''
        
        # Backup current config
        if os.path.exists('firebase_config.py'):
            os.rename('firebase_config.py', 'firebase_config_backup.py')
            logger.info("📋 Backed up current firebase_config.py to firebase_config_backup.py")
        
        # Write new config
        with open('firebase_config.py', 'w') as f:
            f.write(new_config)
        
        logger.info("✅ Created new firebase_config.py targeting (default) database")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating new config: {e}")
        return False

def test_new_configuration():
    """Test the new configuration"""
    try:
        logger.info("🧪 TESTING NEW CONFIGURATION...")
        
        # Restart Python to reload the module
        logger.info("📝 Note: You'll need to restart your backend after this fix")
        
        # Create a test script to verify
        test_script = '''#!/usr/bin/env python3
"""
Test new Firebase configuration
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from firebase_config import db
from datetime import datetime

def test_fixed_config():
    """Test if the new config works with console database"""
    try:
        print("🧪 Testing fixed Firebase configuration...")
        
        # Create test document
        test_data = {
            'message': 'FIXED CONFIGURATION TEST',
            'timestamp': datetime.now().isoformat(),
            'database_target': '(default)',
            'should_appear_in_console': True
        }
        
        result = db.collection('FIXED_CONFIG_TEST').add(test_data)
        doc_id = result[1].id
        
        print(f"✅ Test document created in FIXED_CONFIG_TEST collection")
        print(f"   Document ID: {doc_id}")
        print("")
        print("🔍 CHECK CONSOLE NOW:")
        print("   https://console.firebase.google.com/project/insighthire-335a6/firestore/data")
        print("   Look for 'FIXED_CONFIG_TEST' collection")
        print("   If you see it with the document, the fix worked!")
        
        return doc_id
        
    except Exception as e:
        print(f"❌ Error testing config: {e}")
        return None

if __name__ == '__main__':
    test_fixed_config()
'''
        
        with open('test_fixed_config.py', 'w') as f:
            f.write(test_script)
        
        logger.info("✅ Created test_fixed_config.py")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating test script: {e}")
        return False

def provide_instructions():
    """Provide step-by-step instructions to complete the fix"""
    logger.info("📋 STEP-BY-STEP FIX INSTRUCTIONS:")
    logger.info("=" * 60)
    logger.info("")
    logger.info("1. 🔄 RESTART YOUR BACKEND:")
    logger.info("   - Stop your current backend server (Ctrl+C)")
    logger.info("   - Run: python3 app.py")
    logger.info("")
    logger.info("2. 🧪 TEST THE FIX:")
    logger.info("   - Run: python3 test_fixed_config.py")
    logger.info("   - Check console for 'FIXED_CONFIG_TEST' collection")
    logger.info("")
    logger.info("3. ✅ IF THE TEST WORKS:")
    logger.info("   - Your new candidate data will now save to console database")
    logger.info("   - Start a new interview session to test")
    logger.info("")
    logger.info("4. 📊 VERIFY DATA SAVING:")
    logger.info("   - Run an interview with the AI analysis")
    logger.info("   - Check console for new documents in:")
    logger.info("     * candidates collection")
    logger.info("     * analysis_results collection")
    logger.info("     * interviews collection")
    logger.info("")
    logger.info("5. 🔄 IF TEST FAILS:")
    logger.info("   - Restore backup: mv firebase_config_backup.py firebase_config.py")
    logger.info("   - Let me know and I'll try a different approach")
    logger.info("")

if __name__ == '__main__':
    logger.info("🚀 FIXING DATABASE CONFIGURATION MISMATCH...")
    logger.info("=" * 60)
    
    # Create new config
    config_created = create_correct_firebase_config()
    
    if config_created:
        # Create test script
        test_created = test_new_configuration()
        
        if test_created:
            # Provide instructions
            provide_instructions()
            
            logger.info("=" * 60)
            logger.info("🎯 SUMMARY:")
            logger.info("✅ Created new firebase_config.py targeting (default) database")
            logger.info("✅ Backed up old config to firebase_config_backup.py")
            logger.info("✅ Created test script: test_fixed_config.py")
            logger.info("")
            logger.info("🔄 NEXT: Restart your backend and run the test!")
            logger.info("=" * 60)
        else:
            logger.error("❌ Failed to create test script")
    else:
        logger.error("❌ Failed to create new configuration")
