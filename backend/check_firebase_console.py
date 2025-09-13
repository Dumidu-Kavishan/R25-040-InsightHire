#!/usr/bin/env python3
"""
Check Firebase Console URLs and verify data visibility
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from firebase_config import db
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def get_project_info():
    """Get project information from service account"""
    try:
        with open('serviceAccountKey.json', 'r') as f:
            service_account = json.load(f)
        
        project_id = service_account.get('project_id')
        client_email = service_account.get('client_email')
        
        logger.info(f"🏗️ Project ID: {project_id}")
        logger.info(f"🔑 Service Account: {client_email}")
        
        return project_id
    except Exception as e:
        logger.error(f"❌ Error reading service account: {e}")
        return None

def check_collections_with_counts():
    """Check all collections and count documents"""
    try:
        logger.info("📊 Checking all Firestore collections with document counts...")
        
        collections_info = {}
        
        # List of expected collections
        expected_collections = [
            'candidates',
            'interviews', 
            'analysis_results',
            'interview_sessions',
            'users'
        ]
        
        for collection_name in expected_collections:
            try:
                collection_ref = db.collection(collection_name)
                docs = list(collection_ref.stream())
                doc_count = len(docs)
                
                collections_info[collection_name] = {
                    'count': doc_count,
                    'docs': []
                }
                
                logger.info(f"📁 {collection_name}: {doc_count} documents")
                
                # Show first 3 document IDs and timestamps
                for i, doc in enumerate(docs[:3]):
                    doc_data = doc.to_dict()
                    timestamp = doc_data.get('created_at') or doc_data.get('timestamp') or 'No timestamp'
                    logger.info(f"  📄 {doc.id} (created: {timestamp})")
                    
                    collections_info[collection_name]['docs'].append({
                        'id': doc.id,
                        'timestamp': timestamp,
                        'data_keys': list(doc_data.keys())
                    })
                
                if doc_count > 3:
                    logger.info(f"  ... and {doc_count - 3} more documents")
                
            except Exception as e:
                logger.error(f"❌ Error checking {collection_name}: {e}")
                collections_info[collection_name] = {'error': str(e)}
        
        return collections_info
        
    except Exception as e:
        logger.error(f"❌ Error checking collections: {e}")
        return {}

def generate_console_urls(project_id):
    """Generate correct Firebase Console URLs"""
    if not project_id:
        logger.error("❌ No project ID available")
        return
    
    logger.info("🔗 CORRECT FIREBASE CONSOLE URLs:")
    logger.info("")
    logger.info(f"🏠 Firebase Project Home:")
    logger.info(f"   https://console.firebase.google.com/project/{project_id}")
    logger.info("")
    logger.info(f"🗄️ Firestore Database (All Collections):")
    logger.info(f"   https://console.firebase.google.com/project/{project_id}/firestore/data")
    logger.info("")
    logger.info(f"🧑‍💼 Candidates Collection:")
    logger.info(f"   https://console.firebase.google.com/project/{project_id}/firestore/data/~2Fcandidates")
    logger.info("")
    logger.info(f"📋 Interviews Collection:")
    logger.info(f"   https://console.firebase.google.com/project/{project_id}/firestore/data/~2Finterviews")
    logger.info("")
    logger.info(f"📊 Analysis Results Collection:")
    logger.info(f"   https://console.firebase.google.com/project/{project_id}/firestore/data/~2Fanalysis_results")
    logger.info("")
    logger.info(f"🎯 Interview Sessions Collection:")
    logger.info(f"   https://console.firebase.google.com/project/{project_id}/firestore/data/~2Finterview_sessions")
    logger.info("")

def check_user_permissions():
    """Check if the user might not have permissions to view data"""
    logger.info("🔐 PERMISSION TROUBLESHOOTING:")
    logger.info("")
    logger.info("If you can't see data in Firebase Console, try:")
    logger.info("1. 🔑 Make sure you're logged into the correct Google account")
    logger.info("2. 👥 Check if you have 'Viewer' or 'Editor' permissions on the project")
    logger.info("3. 🏗️ Verify you're looking at the correct project (insighthire-335a6)")
    logger.info("4. 🔄 Try refreshing the Firebase Console page")
    logger.info("5. 🌐 Try opening in an incognito/private browser window")
    logger.info("")

def test_direct_data_access():
    """Test direct access to specific documents we know exist"""
    try:
        logger.info("🧪 Testing direct access to known documents...")
        
        # Get the most recent candidates
        candidates_ref = db.collection('candidates').order_by('created_at', direction='DESCENDING').limit(3)
        candidates = list(candidates_ref.stream())
        
        logger.info(f"📋 Recent Candidates ({len(candidates)} found):")
        for candidate in candidates:
            data = candidate.to_dict()
            logger.info(f"  👤 {data.get('name', 'No Name')} - {candidate.id}")
            logger.info(f"     Position: {data.get('position', 'N/A')}")
            logger.info(f"     Created: {data.get('created_at', 'N/A')}")
        
        # Get the most recent analysis results
        analysis_ref = db.collection('analysis_results').order_by('timestamp', direction='DESCENDING').limit(3)
        analysis_results = list(analysis_ref.stream())
        
        logger.info(f"📊 Recent Analysis Results ({len(analysis_results)} found):")
        for result in analysis_results:
            data = result.to_dict()
            logger.info(f"  📈 Session: {data.get('session_id', 'N/A')} - {result.id}")
            logger.info(f"     Timestamp: {data.get('timestamp', 'N/A')}")
            overall = data.get('overall', {})
            if overall:
                logger.info(f"     Confidence: {overall.get('confidence_score', 'N/A')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing direct access: {e}")
        return False

if __name__ == '__main__':
    logger.info("🚀 Starting Firebase Console Data Verification...")
    logger.info("")
    
    # Get project info
    project_id = get_project_info()
    logger.info("")
    
    # Check collections
    collections_info = check_collections_with_counts()
    logger.info("")
    
    # Generate correct URLs
    generate_console_urls(project_id)
    logger.info("")
    
    # Test direct access
    test_direct_data_access()
    logger.info("")
    
    # Permission troubleshooting
    check_user_permissions()
    
    logger.info("=" * 60)
    logger.info("🎯 SUMMARY:")
    if collections_info:
        total_docs = sum(info.get('count', 0) for info in collections_info.values() if 'count' in info)
        logger.info(f"📊 Total documents found: {total_docs}")
        
        for collection_name, info in collections_info.items():
            if 'count' in info:
                logger.info(f"  📁 {collection_name}: {info['count']} documents")
    
    logger.info("")
    logger.info("🔗 If you still can't see data, copy and paste this exact URL:")
    logger.info(f"   https://console.firebase.google.com/project/{project_id}/firestore/data")
    logger.info("")
    logger.info("📱 And make sure you're logged into the Google account that has access to this project!")
