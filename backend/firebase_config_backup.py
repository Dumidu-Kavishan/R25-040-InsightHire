"""
Firebase Configuration for InsightHire
"""
import firebase_admin
from firebase_admin import credentials, firestore, auth, db as realtime_db
import json
import os

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        # Check if Firebase is already initialized
        app = firebase_admin.get_app()
        print("Firebase already initialized")
        return firestore.client(), realtime_db
    except ValueError:
        # Initialize Firebase if not already done
        try:
            # Load credentials from the serviceAccountKey.json file
            cred_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'serviceAccountKey.json')
            
            # Try backend directory first
            if not os.path.exists(cred_path):
                cred_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
            
            print(f"🔑 Loading credentials from: {cred_path}")
            cred = credentials.Certificate(cred_path)
            
            # Initialize Firebase with Realtime Database URL
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://insighthire-335a6-default-rtdb.asia-southeast1.firebasedatabase.app'  # Correct regional URL
            })
            print("✅ Firebase initialized successfully")
            
            # Return Firestore client and Realtime DB module for creating references
            return firestore.client(), realtime_db
        except Exception as e:
            print(f"❌ Error initializing Firebase: {e}")
            raise e

# Initialize Firebase when this module is imported
try:
    db, rtdb = initialize_firebase()
    print("✅ Firebase configuration loaded successfully")
except Exception as e:
    print(f"❌ Failed to load Firebase configuration: {e}")
    db, rtdb = None, None
