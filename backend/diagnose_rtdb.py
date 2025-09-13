#!/usr/bin/env python3
"""
Diagnose Realtime Database permissions and suggest fixes
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

import firebase_admin
from firebase_admin import credentials, db
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def check_service_account_permissions():
    """Check service account and suggest permission fixes"""
    try:
        # Load service account key to check permissions
        with open('serviceAccountKey.json', 'r') as f:
            service_account = json.load(f)
        
        logger.info(f"🔑 Service Account Email: {service_account.get('client_email')}")
        logger.info(f"🏗️ Project ID: {service_account.get('project_id')}")
        logger.info(f"🆔 Client ID: {service_account.get('client_id')}")
        
        # Test direct DB operations
        logger.info("🧪 Testing direct Firebase Realtime DB operations...")
        
        # Initialize Firebase if not already done
        if not firebase_admin._apps:
            cred = credentials.Certificate('serviceAccountKey.json')
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://insighthire-335a6-default-rtdb.asia-southeast1.firebasedatabase.app/'
            })
        
        # Test with different path structures
        test_paths = [
            'test_simple',
            'sessions/test-session/analysis',
            'analysis_data/test',
            'realtime_analysis/test'
        ]
        
        for path in test_paths:
            try:
                logger.info(f"🧪 Testing path: {path}")
                ref = db.reference(path)
                
                # Try to write
                test_data = {
                    'timestamp': datetime.now().isoformat(),
                    'test': True,
                    'path': path
                }
                
                result = ref.set(test_data)
                logger.info(f"✅ Write successful for path: {path}")
                
                # Try to read
                read_data = ref.get()
                logger.info(f"✅ Read successful for path: {path}, data: {read_data}")
                
                # Clean up
                ref.delete()
                logger.info(f"✅ Cleanup successful for path: {path}")
                
            except Exception as e:
                logger.error(f"❌ Failed for path {path}: {e}")
        
        # Test the exact path structure used in app
        logger.info("🧪 Testing exact app path structure...")
        session_id = "test-session-permissions"
        
        # Test sessions path
        try:
            sessions_ref = db.reference(f'sessions/{session_id}/analysis')
            push_result = sessions_ref.push({
                'timestamp': datetime.now().isoformat(),
                'test_data': 'exact_app_structure',
                'face_stress': {'level': 'low_stress', 'confidence': 0.75}
            })
            logger.info(f"✅ Sessions path test successful, key: {push_result.key}")
            
            # Test latest analysis
            latest_ref = db.reference(f'sessions/{session_id}/latest_analysis')
            latest_ref.set({
                'timestamp': datetime.now().isoformat(),
                'status': 'test_successful'
            })
            logger.info(f"✅ Latest analysis path test successful")
            
            # Cleanup
            db.reference(f'sessions/{session_id}').delete()
            logger.info(f"✅ Cleanup successful")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ App path structure test failed: {e}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Permission check failed: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return False

def suggest_fixes():
    """Suggest fixes for permission issues"""
    logger.info("💡 SUGGESTIONS TO FIX REALTIME DATABASE PERMISSIONS:")
    logger.info("")
    logger.info("1. 🔧 Check Firebase Console > Realtime Database > Rules:")
    logger.info("   Visit: https://console.firebase.google.com/project/insighthire-335a6/database/rules")
    logger.info("   Current rules might be too restrictive")
    logger.info("")
    logger.info("2. 📝 Recommended Database Rules for development:")
    logger.info('   {')
    logger.info('     "rules": {')
    logger.info('       ".read": "auth != null",')
    logger.info('       ".write": "auth != null"')
    logger.info('     }')
    logger.info('   }')
    logger.info("")
    logger.info("3. 🔑 Check Service Account IAM Permissions:")
    logger.info("   Visit: https://console.cloud.google.com/iam-admin/iam")
    logger.info("   Your service account should have 'Firebase Realtime Database Admin' role")
    logger.info("")
    logger.info("4. 🔄 Alternative: Disable Realtime DB saves (keep Firestore only)")
    logger.info("   Modify save_results method to skip Realtime DB if it fails")

if __name__ == '__main__':
    logger.info("🚀 Starting Realtime Database permission diagnosis...")
    
    if check_service_account_permissions():
        logger.info("✅ Realtime Database permissions are working!")
        logger.info("The issue might be in the specific method implementation")
    else:
        logger.error("❌ Realtime Database permission issues detected")
        suggest_fixes()
