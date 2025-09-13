#!/usr/bin/env python3
"""
Test script for Job Role Management API endpoints
"""
import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_USER_ID = "test-user-123"

def test_job_role_endpoints():
    """Test all job role management endpoints"""
    
    print("🧪 Testing Job Role Management API Endpoints")
    print("=" * 50)
    
    # Test data
    test_job_role = {
        "name": "Software Engineer",
        "description": "Full-stack software engineer with focus on web development",
        "confidence_levels": {
            "voice_confidence": 20,
            "hand_confidence": 30,
            "eye_confidence": 50
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": TEST_USER_ID
    }
    
    try:
        # Test 1: Create Job Role
        print("1. Testing CREATE job role...")
        response = requests.post(
            f"{BASE_URL}/job-roles",
            headers=headers,
            json=test_job_role
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                job_role_id = data['job_role']['id']
                print(f"✅ Job role created successfully: {job_role_id}")
            else:
                print(f"❌ Failed to create job role: {data.get('message')}")
                return False
        else:
            print(f"❌ Create request failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        # Test 2: Get All Job Roles
        print("\n2. Testing GET all job roles...")
        response = requests.get(f"{BASE_URL}/job-roles", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                job_roles = data.get('job_roles', [])
                print(f"✅ Retrieved {len(job_roles)} job roles")
            else:
                print(f"❌ Failed to get job roles: {data.get('message')}")
        else:
            print(f"❌ Get request failed with status: {response.status_code}")
        
        # Test 3: Get Specific Job Role
        print(f"\n3. Testing GET specific job role ({job_role_id})...")
        response = requests.get(f"{BASE_URL}/job-roles/{job_role_id}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                job_role = data['job_role']
                print(f"✅ Retrieved job role: {job_role['name']}")
            else:
                print(f"❌ Failed to get job role: {data.get('message')}")
        else:
            print(f"❌ Get specific request failed with status: {response.status_code}")
        
        # Test 4: Update Job Role
        print(f"\n4. Testing UPDATE job role ({job_role_id})...")
        update_data = {
            "name": "Senior Software Engineer",
            "description": "Updated description for senior role",
            "confidence_levels": {
                "voice_confidence": 25,
                "hand_confidence": 25,
                "eye_confidence": 50
            }
        }
        
        response = requests.put(
            f"{BASE_URL}/job-roles/{job_role_id}",
            headers=headers,
            json=update_data
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print(f"✅ Job role updated successfully")
            else:
                print(f"❌ Failed to update job role: {data.get('message')}")
        else:
            print(f"❌ Update request failed with status: {response.status_code}")
        
        # Test 5: Delete Job Role
        print(f"\n5. Testing DELETE job role ({job_role_id})...")
        response = requests.delete(f"{BASE_URL}/job-roles/{job_role_id}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print(f"✅ Job role deleted successfully")
            else:
                print(f"❌ Failed to delete job role: {data.get('message')}")
        else:
            print(f"❌ Delete request failed with status: {response.status_code}")
        
        print("\n🎉 Job Role API tests completed!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the backend server is running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_confidence_validation():
    """Test confidence level validation"""
    
    print("\n🧪 Testing Confidence Level Validation")
    print("=" * 50)
    
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": TEST_USER_ID
    }
    
    # Test invalid confidence levels (total > 100)
    invalid_job_role = {
        "name": "Test Role",
        "description": "Test role with invalid confidence levels",
        "confidence_levels": {
            "voice_confidence": 50,
            "hand_confidence": 50,
            "eye_confidence": 50  # Total = 150%
        }
    }
    
    print("1. Testing invalid confidence levels (total > 100%)...")
    response = requests.post(
        f"{BASE_URL}/job-roles",
        headers=headers,
        json=invalid_job_role
    )
    
    if response.status_code == 400:
        data = response.json()
        if "exceed 100%" in data.get('message', ''):
            print("✅ Validation correctly rejected total > 100%")
        else:
            print(f"❌ Unexpected validation message: {data.get('message')}")
    else:
        print(f"❌ Expected 400 status code, got: {response.status_code}")
    
    # Test auto-calculation of eye confidence
    auto_calc_job_role = {
        "name": "Auto Calc Role",
        "description": "Test role with auto-calculated eye confidence",
        "confidence_levels": {
            "voice_confidence": 30,
            "hand_confidence": 40,
            "eye_confidence": 0  # Should be auto-calculated to 30
        }
    }
    
    print("\n2. Testing auto-calculation of eye confidence...")
    response = requests.post(
        f"{BASE_URL}/job-roles",
        headers=headers,
        json=auto_calc_job_role
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'success':
            job_role = data['job_role']
            eye_confidence = job_role['confidence_levels']['eye_confidence']
            if eye_confidence == 30:
                print("✅ Eye confidence auto-calculated correctly to 30%")
                # Clean up
                job_role_id = job_role['id']
                requests.delete(f"{BASE_URL}/job-roles/{job_role_id}", headers=headers)
            else:
                print(f"❌ Expected eye confidence 30%, got: {eye_confidence}%")
        else:
            print(f"❌ Failed to create job role: {data.get('message')}")
    else:
        print(f"❌ Create request failed with status: {response.status_code}")

if __name__ == "__main__":
    print("🚀 Starting Job Role Management API Tests")
    print("=" * 60)
    
    # Test basic CRUD operations
    success = test_job_role_endpoints()
    
    if success:
        # Test validation
        test_confidence_validation()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests completed successfully!")
    else:
        print("❌ Some tests failed. Check the output above.")
        sys.exit(1)
