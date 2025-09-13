#!/usr/bin/env python3
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
