#!/usr/bin/env python3
"""
Test both Firestore and Realtime Database connections
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebase_config import db, rtdb
from datetime import datetime

def test_firestore():
    """Test Firestore connection"""
    try:
        print("🔍 Testing Firestore...")
        
        # Test write
        test_doc = {
            'test': True,
            'timestamp': datetime.now().isoformat(),
            'message': 'Firestore connection test'
        }
        
        doc_ref = db.collection('test_collection').add(test_doc)
        doc_id = doc_ref[1].id
        print(f"✅ Firestore write successful: {doc_id}")
        
        # Test read
        doc = db.collection('test_collection').document(doc_id).get()
        if doc.exists:
            print(f"✅ Firestore read successful: {doc.to_dict()}")
        
        # Clean up
        db.collection('test_collection').document(doc_id).delete()
        print("🧹 Firestore test data cleaned up")
        return True
        
    except Exception as e:
        print(f"❌ Firestore test failed: {e}")
        return False

def test_realtime_db():
    """Test Realtime Database connection"""
    try:
        print("🔍 Testing Realtime Database...")
        
        # Test write
        test_ref = rtdb.reference('test_connection')
        test_data = {
            'test': True,
            'timestamp': datetime.now().isoformat(),
            'message': 'Realtime DB connection test'
        }
        
        test_ref.set(test_data)
        print("✅ Realtime DB write successful")
        
        # Test read
        data = test_ref.get()
        print(f"✅ Realtime DB read successful: {data}")
        
        # Clean up
        test_ref.delete()
        print("🧹 Realtime DB test data cleaned up")
        return True
        
    except Exception as e:
        print(f"❌ Realtime DB test failed: {e}")
        print(f"Error type: {type(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Firebase connections...\n")
    
    firestore_ok = test_firestore()
    print()
    
    rtdb_ok = test_realtime_db()
    print()
    
    if firestore_ok and rtdb_ok:
        print("🎉 Both Firebase services are working!")
    elif firestore_ok:
        print("✅ Firestore working, ❌ Realtime DB needs fixing")
    elif rtdb_ok:
        print("✅ Realtime DB working, ❌ Firestore needs fixing") 
    else:
        print("💥 Both services need fixing")
