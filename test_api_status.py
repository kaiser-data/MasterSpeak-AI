#!/usr/bin/env python3
"""
Simple test to check API status and endpoints
"""

import requests
import json
import sys

# API base URL
API_BASE = "https://masterspeakai-production.up.railway.app/api/v1"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        print(f"🔍 Health Check: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Health response: {response.json()}")
            return True
        else:
            print(f"❌ Health failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_analysis_text_endpoint():
    """Test text analysis endpoint without user_id"""
    try:
        # Test the main analysis endpoint
        data = {
            'text': 'Hello world test analysis',
            'prompt_type': 'default'
        }
        
        response = requests.post(
            f"{API_BASE}/analysis/text", 
            data=data,
            timeout=30
        )
        
        print(f"🔍 Analysis Text: {response.status_code}")
        
        if response.status_code == 422:
            print(f"❌ Still getting 422 validation error: {response.json()}")
            return False
        elif response.status_code in [200, 201]:
            print(f"✅ Analysis successful: {response.json()}")
            return True
        else:
            print(f"⚠️ Analysis returned {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Analysis test failed: {e}")
        return False

def test_simple_text_endpoint():
    """Test simple text endpoint"""
    try:
        data = {
            'text': 'Hello world test',
            'prompt_type': 'default'
        }
        
        response = requests.post(
            f"{API_BASE}/analysis/simple-text", 
            data=data,
            timeout=10
        )
        
        print(f"🔍 Simple Text: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Simple text successful: {response.json()}")
            return True
        else:
            print(f"❌ Simple text failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Simple text test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing MasterSpeak AI API...")
    print("=" * 50)
    
    health_ok = test_health()
    analysis_ok = test_analysis_text_endpoint() 
    simple_ok = test_simple_text_endpoint()
    
    print("=" * 50)
    print("📊 Test Results:")
    print(f"  Health: {'✅' if health_ok else '❌'}")
    print(f"  Analysis: {'✅' if analysis_ok else '❌'}")
    print(f"  Simple: {'✅' if simple_ok else '❌'}")
    
    if analysis_ok and simple_ok:
        print("🎉 API is working correctly!")
        sys.exit(0)
    else:
        print("❌ API has issues that need attention")
        sys.exit(1)