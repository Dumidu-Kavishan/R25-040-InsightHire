#!/usr/bin/env python3
"""
Check database location and create documents in different instances
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from firebase_config import db
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def check_database_location():
    """Check which database instance we're actually using"""
    try:
        logger.info("🔍 Checking database instance information...")
        
        # Get database info
        logger.info(f"Database ID: {db._database_id}")
        logger.info(f"Database string: {db._database_string}")
        logger.info(f"Project ID: {db.project}")
        
        # Check the actual document we created
        console_test_ref = db.collection('console_test')
        docs = list(console_test_ref.stream())
        
        logger.info(f"📊 Documents in console_test collection: {len(docs)}")
        for doc in docs:
            doc_data = doc.to_dict()
            logger.info(f"  📄 Doc ID: {doc.id}")
            logger.info(f"  📄 Data: {doc_data}")
        
        return len(docs) > 0
        
    except Exception as e:
        logger.error(f"❌ Error checking database: {e}")
        return False

def create_document_with_metadata():
    """Create a document with detailed metadata"""
    try:
        logger.info("📝 Creating document with detailed metadata...")
        
        metadata = {
            'created_at': datetime.now().isoformat(),
            'message': 'CONSOLE VISIBILITY TEST - If you see this, console is working!',
            'database_info': {
                'database_id': db._database_id,
                'database_string': str(db._database_string),
                'project_id': db.project
            },
            'test_data': {
                'candidate_name': 'Test Candidate for Console',
                'position': 'Console Visibility Tester',
                'confidence_score': 0.95,
                'status': 'VISIBLE_TEST'
            }
        }
        
        # Add to console_test collection
        doc_ref = db.collection('console_test').add(metadata)
        doc_id = doc_ref[1].id
        
        logger.info(f"✅ Document created with ID: {doc_id}")
        
        # Also add to candidates collection for testing
        candidate_test = {
            'name': 'CONSOLE TEST CANDIDATE',
            'email': 'console.test@example.com',
            'position': 'Console Visibility Checker',
            'created_at': datetime.now().isoformat(),
            'status': 'CONSOLE_TEST',
            'test_marker': 'IF_YOU_SEE_THIS_CONSOLE_WORKS'
        }
        
        candidates_ref = db.collection('candidates').add(candidate_test)
        candidate_id = candidates_ref[1].id
        
        logger.info(f"✅ Test candidate created with ID: {candidate_id}")
        
        # Also add to analysis_results
        analysis_test = {
            'session_id': 'console-test-session',
            'timestamp': datetime.now().isoformat(),
            'test_marker': 'CONSOLE_VISIBILITY_TEST',
            'face_stress': {'level': 'test', 'confidence': 1.0},
            'overall': {'confidence_score': 1.0, 'test': True}
        }
        
        analysis_ref = db.collection('analysis_results').add(analysis_test)
        analysis_id = analysis_ref[1].id
        
        logger.info(f"✅ Test analysis created with ID: {analysis_id}")
        
        return doc_id, candidate_id, analysis_id
        
    except Exception as e:
        logger.error(f"❌ Error creating test documents: {e}")
        return None, None, None

def list_all_collections_and_docs():
    """List all collections and their document counts"""
    try:
        logger.info("📋 Listing all collections and document counts...")
        
        collections = list(db.collections())
        
        for collection in collections:
            docs = list(collection.stream())
            logger.info(f"📁 {collection.id}: {len(docs)} documents")
            
            # Show first few document IDs
            for i, doc in enumerate(docs[:3]):
                logger.info(f"   📄 {doc.id}")
            
            if len(docs) > 3:
                logger.info(f"   ... and {len(docs) - 3} more")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error listing collections: {e}")
        return False

if __name__ == '__main__':
    logger.info("🚀 Database Instance Debug...")
    logger.info("=" * 50)
    
    # Check current database
    has_data = check_database_location()
    logger.info("=" * 50)
    
    # List all collections
    list_all_collections_and_docs()
    logger.info("=" * 50)
    
    # Create new test documents
    doc_id, candidate_id, analysis_id = create_document_with_metadata()
    logger.info("=" * 50)
    
    logger.info("🎯 CONSOLE TEST INSTRUCTIONS:")
    logger.info("1. Refresh your Firebase Console")
    logger.info("2. Go back to main data view: https://console.firebase.google.com/project/insighthire-335a6/firestore/data")
    logger.info("3. Look for these new test documents:")
    logger.info(f"   - console_test collection (doc: {doc_id})")
    logger.info(f"   - candidates collection (look for 'CONSOLE TEST CANDIDATE')")
    logger.info(f"   - analysis_results collection (look for 'console-test-session')")
    logger.info("")
    logger.info("4. If you see these NEW documents but not the old ones:")
    logger.info("   → Your data is in a different database instance")
    logger.info("5. If you don't see ANY of these:")
    logger.info("   → Permission or account issue")
    logger.info("")
    logger.info("🔗 Try this main data URL again:")
    logger.info("   https://console.firebase.google.com/project/insighthire-335a6/firestore/data")
