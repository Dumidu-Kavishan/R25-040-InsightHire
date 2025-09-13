"""
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
            
            # Create Firestore client (default database)
            db_client = firestore.client(app)
            
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
