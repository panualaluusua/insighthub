#!/usr/bin/env python3
"""
Manual test script for enhanced feedback API functionality
Tests the new features added in refactoring phase
"""
import requests
import json
from uuid import uuid4

# Note: This assumes the FastAPI server is running
BASE_URL = "http://localhost:8000"

def test_enhanced_response():
    """Test that response includes enhanced fields"""
    print("🧪 Testing enhanced response fields...")
    
    payload = {
        "content_id": str(uuid4()),
        "user_id": str(uuid4()),
        "feedback_type": "NOT_RELEVANT"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/feedback", json=payload)
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    # Check enhanced fields
    required_fields = ["feedback_id", "timestamp", "status", "message"]
    for field in required_fields:
        if field in data:
            print(f"✅ {field}: present")
        else:
            print(f"❌ {field}: missing")
    
    print()

def test_uuid_validation():
    """Test UUID validation error handling"""
    print("🧪 Testing UUID validation...")
    
    payload = {
        "content_id": "not-a-uuid",
        "user_id": str(uuid4()),
        "feedback_type": "NOT_RELEVANT"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/feedback", json=payload)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        print("✅ UUID validation working")
        print(f"Error: {response.json()}")
    else:
        print("❌ UUID validation not working")
        
    print()

def test_missing_fields():
    """Test missing fields validation"""
    print("🧪 Testing missing fields validation...")
    
    payload = {
        "content_id": str(uuid4()),
        # Missing user_id and feedback_type
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/feedback", json=payload)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 422:
        print("✅ Missing fields validation working")
        print(f"Error: {response.json()}")
    else:
        print("❌ Missing fields validation not working")
        
    print()

def test_health_endpoint():
    """Test health endpoint"""
    print("🧪 Testing health endpoint...")
    
    response = requests.get(f"{BASE_URL}/health")
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if data.get("status") == "healthy" and data.get("service") == "feedback-api":
        print("✅ Health endpoint working")
    else:
        print("❌ Health endpoint not working correctly")
        
    print()

def main():
    """Run all manual tests"""
    print("🚀 Running manual tests for enhanced feedback API")
    print("=" * 50)
    
    try:
        test_enhanced_response()
        test_uuid_validation() 
        test_missing_fields()
        test_health_endpoint()
        
        print("✅ All manual tests completed!")
        print("\n📝 To run this test:")
        print("1. Start the FastAPI server: uvicorn src.api.feedback:app --reload")
        print("2. Run this script: python manual_test_enhanced.py")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Please start FastAPI server first:")
        print("   uvicorn src.api.feedback:app --reload")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    main() 