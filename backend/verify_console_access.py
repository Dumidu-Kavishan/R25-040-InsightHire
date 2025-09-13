#!/usr/bin/env python3
"""
Check if data exists and find the correct database instance
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

# Import our existing Firebase config
from firebase_config import db
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def check_current_data_access():
    """Check if we can access data with current config"""
    try:
        logger.info("🔍 Checking current Firebase configuration...")
        
        # Test if we can access collections
        logger.info("📊 Attempting to list collections...")
        collections = list(db.collections())
        
        if collections:
            logger.info(f"✅ Found {len(collections)} collections:")
            for collection in collections:
                docs = list(collection.limit(1).stream())
                logger.info(f"   📁 {collection.id}: {len(docs)} documents (showing 1 sample)")
                if docs:
                    doc = docs[0]
                    logger.info(f"      📄 Sample doc ID: {doc.id}")
        else:
            logger.error("❌ No collections found!")
            return False
        
        # Test specific collection access
        logger.info("\n🧪 Testing specific collection access...")
        
        # Test candidates
        candidates_ref = db.collection('candidates')
        candidates = list(candidates_ref.limit(2).stream())
        logger.info(f"🧑‍💼 Candidates: {len(candidates)} found")
        
        # Test analysis_results  
        analysis_ref = db.collection('analysis_results')
        analysis_results = list(analysis_ref.limit(2).stream())
        logger.info(f"📊 Analysis Results: {len(analysis_results)} found")
        
        if candidates or analysis_results:
            logger.info("✅ Data is accessible via our backend configuration!")
            return True
        else:
            logger.error("❌ No data found in expected collections!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error accessing data: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return False

def suggest_console_fixes():
    """Suggest fixes for console viewing"""
    logger.info("🔧 CONSOLE TROUBLESHOOTING STEPS:")
    logger.info("=" * 50)
    logger.info("")
    logger.info("1. 🔍 Check Database Instance:")
    logger.info("   - In your Firebase Console, look for a dropdown next to '(default)'")
    logger.info("   - There might be multiple database instances")
    logger.info("   - Try clicking on any dropdown to see other databases")
    logger.info("")
    logger.info("2. 🌐 Try these direct URLs:")
    logger.info("   Main: https://console.firebase.google.com/project/insighthire-335a6/firestore/data")
    logger.info("   All DBs: https://console.firebase.google.com/project/insighthire-335a6/firestore/databases")
    logger.info("")
    logger.info("3. 🔄 Clear browser cache and try again")
    logger.info("")
    logger.info("4. 👥 Check account permissions:")
    logger.info("   - Make sure you're logged into the correct Google account")
    logger.info("   - Account should have Firestore access permissions")
    logger.info("")
    logger.info("5. 🎯 Try Query Builder:")
    logger.info("   - Click 'Query builder' in your Firebase Console")
    logger.info("   - Try to query the 'candidates' collection")
    logger.info("")

def create_test_document():
    """Create a test document to verify console visibility"""
    try:
        logger.info("🧪 Creating a test document to verify console visibility...")
        
        test_data = {
            'test_message': 'Console Visibility Test',
            'created_at': '2025-09-08T13:00:00Z',
            'status': 'test_document_for_console_check'
        }
        
        # Add to a test collection
        test_ref = db.collection('console_test').add(test_data)
        doc_id = test_ref[1].id
        
        logger.info(f"✅ Test document created!")
        logger.info(f"   Collection: console_test")
        logger.info(f"   Document ID: {doc_id}")
        logger.info("")
        logger.info("🔍 NOW CHECK YOUR FIREBASE CONSOLE:")
        logger.info("   1. Refresh the console page")
        logger.info("   2. Look for a 'console_test' collection")
        logger.info("   3. If you see it, then the console is working!")
        logger.info("   4. If not, there's a permission or account issue")
        logger.info("")
        logger.info("🔗 Direct link to test collection:")
        logger.info("   https://console.firebase.google.com/project/insighthire-335a6/firestore/data/~2Fconsole_test")
        
        return doc_id
        
    except Exception as e:
        logger.error(f"❌ Error creating test document: {e}")
        return None

if __name__ == '__main__':
    logger.info("🚀 Starting data access verification...")
    logger.info("")
    
    # Check if we can access data via backend
    data_accessible = check_current_data_access()
    logger.info("")
    
    if data_accessible:
        logger.info("✅ DATA IS ACCESSIBLE VIA BACKEND!")
        logger.info("The issue is with console viewing, not data storage.")
        logger.info("")
        
        # Create test document
        test_doc_id = create_test_document()
        logger.info("")
        
        # Provide troubleshooting steps
        suggest_console_fixes()
        
    else:
        logger.error("❌ DATA NOT ACCESSIBLE!")
        logger.error("There might be a configuration issue.")
        
    logger.info("=" * 60)
