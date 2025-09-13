#!/usr/bin/env python3
"""
Debug Firebase database configuration and find where data is actually stored
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

import firebase_admin
from firebase_admin import credentials, firestore
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def check_firebase_app_config():
    """Check the current Firebase app configuration"""
    try:
        # Get current app
        app = firebase_admin.get_app()
        
        logger.info("🔍 Current Firebase App Configuration:")
        logger.info(f"   App name: {app.name}")
        logger.info(f"   Project ID: {app.project_id}")
        
        # Get Firestore client
        db = firestore.client(app)
        
        logger.info(f"   Database ID: {db._database_id}")
        logger.info(f"   Database path: {db._database_string}")
        
        return app, db
        
    except Exception as e:
        logger.error(f"❌ Error checking app config: {e}")
        return None, None

def check_service_account_details():
    """Check service account configuration"""
    try:
        with open('serviceAccountKey.json', 'r') as f:
            service_account = json.load(f)
        
        logger.info("🔑 Service Account Details:")
        logger.info(f"   Project ID: {service_account.get('project_id')}")
        logger.info(f"   Client Email: {service_account.get('client_email')}")
        logger.info(f"   Auth URI: {service_account.get('auth_uri')}")
        logger.info(f"   Token URI: {service_account.get('token_uri')}")
        
        return service_account
        
    except Exception as e:
        logger.error(f"❌ Error reading service account: {e}")
        return None

def test_multiple_database_instances():
    """Test different database instances"""
    try:
        logger.info("🧪 Testing different database instances...")
        
        # Test default database
        logger.info("\n1. Testing (default) database:")
        db_default = firestore.client()
        collections_default = list(db_default.collections())
        logger.info(f"   Collections in (default): {[c.id for c in collections_default]}")
        
        # Test if there are other database instances
        # Note: We can't easily list all databases, but we can try common patterns
        
        return collections_default
        
    except Exception as e:
        logger.error(f"❌ Error testing databases: {e}")
        return []

def verify_data_with_different_clients():
    """Try different ways to access Firestore"""
    try:
        logger.info("🔍 Trying different Firestore client configurations...")
        
        # Method 1: Direct client
        logger.info("\n📊 Method 1: Direct firestore.client()")
        db1 = firestore.client()
        try:
            collections1 = list(db1.collections())
            logger.info(f"   Found collections: {[c.id for c in collections1]}")
            
            if collections1:
                # Check first collection
                first_collection = collections1[0]
                docs = list(first_collection.limit(1).stream())
                logger.info(f"   Sample doc from {first_collection.id}: {len(docs)} documents")
        except Exception as e:
            logger.error(f"   Error with method 1: {e}")
        
        # Method 2: Using current app
        logger.info("\n📊 Method 2: Using current app")
        try:
            app = firebase_admin.get_app()
            db2 = firestore.client(app)
            collections2 = list(db2.collections())
            logger.info(f"   Found collections: {[c.id for c in collections2]}")
        except Exception as e:
            logger.error(f"   Error with method 2: {e}")
        
        # Method 3: Force reinitialize
        logger.info("\n📊 Method 3: Fresh initialization")
        try:
            # Delete existing app
            try:
                firebase_admin.delete_app(firebase_admin.get_app())
                logger.info("   Deleted existing app")
            except:
                pass
            
            # Reinitialize
            cred = credentials.Certificate('serviceAccountKey.json')
            app3 = firebase_admin.initialize_app(cred, name='test_app')
            db3 = firestore.client(app3)
            collections3 = list(db3.collections())
            logger.info(f"   Found collections: {[c.id for c in collections3]}")
            
            # Clean up
            firebase_admin.delete_app(app3)
            
        except Exception as e:
            logger.error(f"   Error with method 3: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verifying data: {e}")
        return False

def generate_console_urls_with_debug():
    """Generate URLs with debug info"""
    try:
        with open('serviceAccountKey.json', 'r') as f:
            service_account = json.load(f)
        
        project_id = service_account.get('project_id')
        
        logger.info("🔗 DEBUG: Console URLs to try:")
        logger.info(f"\n1. Main project: https://console.firebase.google.com/project/{project_id}")
        logger.info(f"2. Firestore data: https://console.firebase.google.com/project/{project_id}/firestore/data")
        logger.info(f"3. All databases: https://console.firebase.google.com/project/{project_id}/firestore/databases")
        logger.info(f"4. Project settings: https://console.firebase.google.com/project/{project_id}/settings/general")
        
        logger.info("\n🔍 Things to check in console:")
        logger.info("   1. Are you logged into the right Google account?")
        logger.info("   2. Do you see the project name 'InsightHire' in the top bar?")
        logger.info("   3. In Firestore > Database, do you see any database dropdown options?")
        logger.info("   4. Try clicking 'Query builder' to see if data shows up there")
        
    except Exception as e:
        logger.error(f"❌ Error generating URLs: {e}")

if __name__ == '__main__':
    logger.info("🚀 Starting Firebase database configuration debug...")
    logger.info("=" * 60)
    
    # Check service account
    service_account = check_service_account_details()
    logger.info("=" * 60)
    
    # Check current app config
    app, db = check_firebase_app_config()
    logger.info("=" * 60)
    
    # Test different database instances
    collections = test_multiple_database_instances()
    logger.info("=" * 60)
    
    # Try different client methods
    verify_data_with_different_clients()
    logger.info("=" * 60)
    
    # Generate debug URLs
    generate_console_urls_with_debug()
    logger.info("=" * 60)
    
    if not collections:
        logger.error("🚨 NO COLLECTIONS FOUND!")
        logger.error("This suggests either:")
        logger.error("   1. Data is in a different database instance")
        logger.error("   2. Service account doesn't have proper permissions")
        logger.error("   3. We're connecting to the wrong project")
        logger.error("   4. The database instance in console is different from code")
    else:
        logger.info("✅ Collections found! The issue is likely in the console view.")
