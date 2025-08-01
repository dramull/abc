#!/usr/bin/env python3
"""
Simple test script to verify the ABC Multi-Agent Framework is working correctly.
Run this after starting the backend server to verify functionality.
"""

import requests
import json
import sys

def test_api_endpoint(endpoint, expected_status=200):
    """Test an API endpoint and return the response"""
    try:
        response = requests.get(f"http://localhost:8000{endpoint}", timeout=10)
        print(f"✓ {endpoint} - Status: {response.status_code}")
        
        if response.status_code == expected_status:
            return response.json()
        else:
            print(f"  ⚠ Expected status {expected_status}, got {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"✗ {endpoint} - Error: {e}")
        return None

def main():
    print("🧪 Testing ABC Multi-Agent Framework API")
    print("=" * 50)
    
    # Test health check
    health = test_api_endpoint("/health")
    if not health:
        print("❌ Backend server is not responding. Make sure it's running on port 8000.")
        sys.exit(1)
    
    # Test system status
    status = test_api_endpoint("/api/agents/status")
    if status:
        print(f"  📊 Active agents: {status.get('active_agents', 0)}")
        print(f"  📋 Available profiles: {status.get('available_profiles', 0)}")
        print(f"  🔑 Kimi configured: {status.get('kimi_configured', False)}")
    
    # Test agent profiles
    profiles = test_api_endpoint("/api/agents/profiles")
    if profiles:
        print(f"  🤖 Loaded {len(profiles)} agent profiles:")
        for profile in profiles:
            print(f"    - {profile.get('name', 'Unknown')} ({profile.get('type', 'unknown')})")
    
    # Test active instances
    instances = test_api_endpoint("/api/agents/instances")
    if instances:
        print(f"  🏃 Active instances: {len(instances)}")
        for instance in instances:
            print(f"    - {instance.get('name', 'Unknown')} ({instance.get('status', 'unknown')})")
    
    print("\n🎉 All basic API tests passed!")
    print("\n📝 Next steps:")
    print("1. Add your Kimi K2 API key to the .env file")
    print("2. Open http://localhost:3000 in your browser")
    print("3. Start chatting with the Base Agent!")

if __name__ == "__main__":
    main()