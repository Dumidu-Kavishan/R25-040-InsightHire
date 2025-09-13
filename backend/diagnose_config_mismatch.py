#!/usr/bin/env python3
"""
Find configuration mismatch and fix database connection
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def analyze_service_account_config():
    """Analyze service account configuration"""
    try:
        logger.info("🔍 ANALYZING SERVICE ACCOUNT CONFIGURATION...")
        
        with open('serviceAccountKey.json', 'r') as f:
            service_account = json.load(f)
        
        logger.info(f"📋 Service Account Details:")
        logger.info(f"   Project ID: {service_account.get('project_id')}")
        logger.info(f"   Client Email: {service_account.get('client_email')}")
        logger.info(f"   Private Key ID: {service_account.get('private_key_id', 'N/A')[:20]}...")
        logger.info(f"   Auth Provider: {service_account.get('auth_provider_x509_cert_url')}")
        
        return service_account
    except Exception as e:
        logger.error(f"❌ Error reading service account: {e}")
        return None

def check_firebase_config_file():
    """Check current Firebase configuration"""
    try:
        logger.info("🔍 CHECKING FIREBASE_CONFIG.PY...")
        
        with open('firebase_config.py', 'r') as f:
            config_content = f.read()
        
        logger.info("📋 Current firebase_config.py content:")
        logger.info("=" * 50)
        logger.info(config_content)
        logger.info("=" * 50)
        
        return config_content
    except Exception as e:
        logger.error(f"❌ Error reading firebase_config.py: {e}")
        return None

def get_required_configuration_info():
    """Get information needed to fix the configuration"""
    logger.info("🎯 TO FIX THIS ISSUE, I NEED YOU TO PROVIDE:")
    logger.info("=" * 60)
    logger.info("")
    logger.info("1. 🌐 GO TO FIREBASE CONSOLE:")
    logger.info("   https://console.firebase.google.com/project/insighthire-335a6/settings/general")
    logger.info("")
    logger.info("2. 📋 COPY THE PROJECT CONFIGURATION:")
    logger.info("   - Scroll down to 'Your apps' section")
    logger.info("   - If you see a web app, click the config icon (</>) ")
    logger.info("   - Copy the firebaseConfig object")
    logger.info("   - If no web app exists, click 'Add app' > Web app")
    logger.info("")
    logger.info("3. 🗄️ CHECK DATABASE SETTINGS:")
    logger.info("   - Go to: https://console.firebase.google.com/project/insighthire-335a6/firestore/databases")
    logger.info("   - Take a screenshot of all database instances")
    logger.info("   - Note the database ID and region for each")
    logger.info("")
    logger.info("4. 🔑 SERVICE ACCOUNT PERMISSIONS:")
    logger.info("   - Go to: https://console.cloud.google.com/iam-admin/iam?project=insighthire-335a6")
    logger.info("   - Find your service account email")
    logger.info("   - Check what roles it has")
    logger.info("")
    logger.info("5. 📊 PROVIDE ME THIS INFO:")
    logger.info("   a) The firebaseConfig object (from step 2)")
    logger.info("   b) Screenshot of database instances (from step 3)")
    logger.info("   c) List of service account roles (from step 4)")
    logger.info("")

def create_test_with_explicit_database():
    """Create a test to verify which database we're actually using"""
    try:
        logger.info("🧪 TESTING CURRENT DATABASE CONNECTION...")
        
        # Import with current config
        from firebase_config import db
        
        # Create a unique test document
        test_doc = {
            'test_timestamp': '2025-09-08T13:30:00Z',
            'test_message': 'CONFIGURATION TEST - Check console now!',
            'configuration_debug': True,
            'database_target': 'This should appear in the correct database'
        }
        
        # Add to a new collection for easy identification
        result = db.collection('CONFIGURATION_TEST').add(test_doc)
        doc_id = result[1].id
        
        logger.info(f"✅ Test document created in collection 'CONFIGURATION_TEST'")
        logger.info(f"   Document ID: {doc_id}")
        logger.info("")
        logger.info("🔍 NOW CHECK YOUR FIREBASE CONSOLE:")
        logger.info("   1. Refresh the console page")
        logger.info("   2. Look for 'CONFIGURATION_TEST' collection")
        logger.info("   3. If you see it - our backend is working but using wrong DB")
        logger.info("   4. If you don't see it - there's a deeper config issue")
        logger.info("")
        logger.info("🔗 Direct link to check:")
        logger.info("   https://console.firebase.google.com/project/insighthire-335a6/firestore/data/~2FCONFIGURATION_TEST")
        
        return doc_id
        
    except Exception as e:
        logger.error(f"❌ Error creating test document: {e}")
        return None

def generate_fix_options():
    """Generate different options to fix the configuration"""
    logger.info("🔧 POSSIBLE FIXES:")
    logger.info("=" * 50)
    logger.info("")
    logger.info("OPTION 1: Update Database URL")
    logger.info("   - If your data should go to the console database")
    logger.info("   - We'll update firebase_config.py with correct database ID")
    logger.info("")
    logger.info("OPTION 2: Create New Database Instance")
    logger.info("   - Create a new database in console that matches our config")
    logger.info("   - Import existing data to new database")
    logger.info("")
    logger.info("OPTION 3: Update Console View")
    logger.info("   - Find where our data is actually stored")
    logger.info("   - Update console to point to correct database")
    logger.info("")
    logger.info("OPTION 4: Service Account Fix")
    logger.info("   - Update service account permissions")
    logger.info("   - Generate new service account key")
    logger.info("")

if __name__ == '__main__':
    logger.info("🚀 CONFIGURATION DIAGNOSIS STARTING...")
    logger.info("=" * 60)
    
    # Check service account
    service_account = analyze_service_account_config()
    logger.info("")
    
    # Check firebase config
    config_content = check_firebase_config_file()
    logger.info("")
    
    # Create test document
    test_doc_id = create_test_with_explicit_database()
    logger.info("")
    
    # Get required info
    get_required_configuration_info()
    logger.info("")
    
    # Generate fix options
    generate_fix_options()
    
    logger.info("=" * 60)
    logger.info("🎯 NEXT STEPS:")
    logger.info("1. Follow the instructions above to get configuration info")
    logger.info("2. Check if you see the 'CONFIGURATION_TEST' collection in console")
    logger.info("3. Provide me the requested information")
    logger.info("4. I'll create the exact fix for your configuration")
    logger.info("=" * 60)
