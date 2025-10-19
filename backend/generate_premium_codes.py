#!/usr/bin/env python3
"""
Premium Code Generator Script for InsightHire
This script generates test premium codes for development and testing purposes.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database import DatabaseManager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_test_premium_codes(count=5):
    """Generate test premium codes"""
    try:
        db_manager = DatabaseManager()
        
        print(f"🎯 Generating {count} test premium codes...")
        print("=" * 50)
        
        generated_codes = []
        
        for i in range(count):
            premium_code = db_manager.create_premium_code({
                'test_mode': True,
                'generated_by': 'test_script',
                'amount': 99.99,
                'currency': 'USD'
            })
            
            if premium_code:
                generated_codes.append(premium_code)
                print(f"✅ Generated: {premium_code}")
            else:
                print(f"❌ Failed to generate code #{i+1}")
        
        print("=" * 50)
        print(f"🎉 Successfully generated {len(generated_codes)} premium codes!")
        print("\n📋 Generated Codes:")
        for i, code in enumerate(generated_codes, 1):
            print(f"   {i}. {code}")
        
        print("\n💡 You can now use these codes to test the premium access system.")
        print("   Copy any code and paste it in the premium code entry form.")
        
        return generated_codes
        
    except Exception as e:
        logger.error(f"Error generating premium codes: {e}")
        print(f"❌ Error: {e}")
        return []

def validate_premium_code(code):
    """Validate a specific premium code"""
    try:
        db_manager = DatabaseManager()
        result = db_manager.validate_premium_code(code)
        
        print(f"🔍 Validating code: {code}")
        print(f"   Valid: {result['valid']}")
        print(f"   Message: {result['message']}")
        
        return result['valid']
        
    except Exception as e:
        logger.error(f"Error validating premium code: {e}")
        print(f"❌ Error: {e}")
        return False

def list_premium_codes():
    """List all premium codes in the database"""
    try:
        db_manager = DatabaseManager()
        codes = db_manager.get_premium_codes(limit=20)
        
        print(f"📋 Found {len(codes)} premium codes:")
        print("=" * 50)
        
        for code_data in codes:
            code = code_data.get('premium_code', code_data.get('id', 'Unknown'))
            status = code_data.get('status', 'unknown')
            is_used = code_data.get('is_used', False)
            created_at = code_data.get('created_at', 'Unknown')
            
            print(f"Code: {code}")
            print(f"  Status: {status}")
            print(f"  Used: {is_used}")
            print(f"  Created: {created_at}")
            print("-" * 30)
        
    except Exception as e:
        logger.error(f"Error listing premium codes: {e}")
        print(f"❌ Error: {e}")

def main():
    """Main function"""
    print("🚀 InsightHire Premium Code Generator")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'generate':
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            generate_test_premium_codes(count)
        elif command == 'validate':
            if len(sys.argv) > 2:
                code = sys.argv[2]
                validate_premium_code(code)
            else:
                print("❌ Please provide a premium code to validate")
        elif command == 'list':
            list_premium_codes()
        else:
            print("❌ Unknown command. Available commands:")
            print("   generate [count] - Generate test premium codes")
            print("   validate <code>   - Validate a specific premium code")
            print("   list             - List all premium codes")
    else:
        # Default: generate 5 test codes
        generate_test_premium_codes(5)

if __name__ == '__main__':
    main()
