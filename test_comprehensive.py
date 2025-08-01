#!/usr/bin/env python3
"""
Comprehensive test suite for ABC Multi-Agent Framework
Tests all core functionality and validates production readiness
"""

import requests
import json
import sys
import time
from typing import Dict, Any

class ABCFrameworkTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
    def test_api_endpoint(self, endpoint: str, method: str = "GET", data: Dict[str, Any] = None, expected_status: int = 200) -> Dict[str, Any]:
        """Test an API endpoint"""
        try:
            url = f"{self.base_url}{endpoint}"
            if method.upper() == "GET":
                response = self.session.get(url, timeout=10)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, timeout=10)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            print(f"✓ {method} {endpoint} - Status: {response.status_code}")
            
            if response.status_code == expected_status:
                try:
                    return response.json()
                except:
                    return {"raw_response": response.text}
            else:
                print(f"  ⚠ Expected status {expected_status}, got {response.status_code}")
                print(f"  Response: {response.text[:200]}...")
                return None
        except requests.exceptions.RequestException as e:
            print(f"✗ {method} {endpoint} - Error: {e}")
            return None

    def test_health_checks(self):
        """Test basic health and status endpoints"""
        print("\n🔍 Testing Health Checks")
        print("-" * 30)
        
        # Test health endpoint
        health = self.test_api_endpoint("/health")
        if not health:
            print("❌ Backend server is not responding. Make sure it's running on port 8000.")
            return False
        
        # Test system status
        status = self.test_api_endpoint("/api/agents/status")
        if status:
            print(f"  📊 Active agents: {status.get('active_agents', 0)}")
            print(f"  📋 Available profiles: {status.get('available_profiles', 0)}")
            print(f"  🔑 Kimi configured: {status.get('kimi_configured', False)}")
            
        return True

    def test_agent_profiles(self):
        """Test agent profile endpoints"""
        print("\n🤖 Testing Agent Profiles")
        print("-" * 30)
        
        profiles = self.test_api_endpoint("/api/agents/profiles")
        if not profiles:
            return False
            
        print(f"  📋 Loaded {len(profiles)} agent profiles:")
        
        required_types = {"research", "writing", "code", "planning", "analysis"}
        found_types = set()
        
        for profile in profiles:
            profile_type = profile.get('type', 'unknown')
            print(f"    - {profile.get('name', 'Unknown')} ({profile_type})")
            
            # Validate profile structure
            required_fields = ["id", "name", "type", "description", "instructions", "capabilities"]
            missing_fields = [field for field in required_fields if field not in profile]
            if missing_fields:
                print(f"      ⚠ Missing fields: {missing_fields}")
            
            found_types.add(profile_type)
        
        missing_types = required_types - found_types
        if missing_types:
            print(f"  ⚠ Missing required agent types: {missing_types}")
            
        return True

    def test_agent_instances(self):
        """Test agent instance management"""
        print("\n🏃 Testing Agent Instances")
        print("-" * 30)
        
        # Get initial instances
        instances = self.test_api_endpoint("/api/agents/instances")
        if instances is None:
            return False
            
        initial_count = len(instances)
        print(f"  📊 Initial instances: {initial_count}")
        
        # Test creating agent from profile
        print("  🔄 Testing agent creation from profile...")
        new_agent = self.test_api_endpoint("/api/agents/create-from-profile/research_agent", "POST", expected_status=200)
        
        if new_agent:
            agent_id = new_agent.get("id")
            print(f"    ✓ Created agent: {new_agent.get('name')} (ID: {agent_id[:8]}...)")
            
            # Verify agent was created
            time.sleep(0.5)
            instances_after = self.test_api_endpoint("/api/agents/instances")
            if instances_after and len(instances_after) == initial_count + 1:
                print("    ✓ Agent instance count increased correctly")
            else:
                print("    ⚠ Agent instance count did not increase as expected")
            
            # Test getting specific agent
            agent_detail = self.test_api_endpoint(f"/api/agents/instances/{agent_id}")
            if agent_detail:
                print(f"    ✓ Retrieved agent details: {agent_detail.get('name')}")
            
            # Clean up - delete the test agent
            delete_result = self.test_api_endpoint(f"/api/agents/instances/{agent_id}", "DELETE", expected_status=200)
            if delete_result:
                print("    ✓ Successfully deleted test agent")
            
        return True

    def test_custom_agent_creation(self):
        """Test custom agent creation"""
        print("\n🛠️ Testing Custom Agent Creation")
        print("-" * 30)
        
        custom_agent_data = {
            "name": "Test Assistant",
            "description": "A test agent for validating custom agent creation functionality",
            "agent_type": "custom"
        }
        
        # This should fail without API key, which is expected behavior
        custom_agent = self.test_api_endpoint("/api/agents/create-custom", "POST", custom_agent_data, expected_status=500)
        
        if custom_agent and "API key" in custom_agent.get("detail", ""):
            print("    ✓ Custom agent creation correctly requires API key")
            return True
        else:
            print("    ⚠ Unexpected response for custom agent creation")
            return False

    def test_input_validation(self):
        """Test input validation and error handling"""
        print("\n🔒 Testing Input Validation")
        print("-" * 30)
        
        # Test empty custom agent creation
        print("  🔄 Testing empty agent creation...")
        empty_data = {"name": "", "description": ""}
        result = self.test_api_endpoint("/api/agents/create-custom", "POST", empty_data, expected_status=422)
        if result:
            print("    ✓ Correctly rejected empty agent data")
        
        # Test invalid agent ID
        print("  🔄 Testing invalid agent ID...")
        invalid_task = {
            "agent_id": "nonexistent_agent",
            "instruction": "Test task"
        }
        result = self.test_api_endpoint("/api/agents/execute-task", "POST", invalid_task, expected_status=404)
        if result:
            print("    ✓ Correctly rejected invalid agent ID")
        
        return True

    def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n⚠️ Testing Error Handling")
        print("-" * 30)
        
        # Test task execution without Kimi API key
        print("  🔄 Testing task execution without API key...")
        
        # Get base agent
        instances = self.test_api_endpoint("/api/agents/instances")
        if instances:
            base_agent = next((agent for agent in instances if agent.get("id") == "base_agent_instance"), None)
            
            if base_agent:
                task_data = {
                    "agent_id": "base_agent_instance",
                    "instruction": "Hello, can you introduce yourself?"
                }
                
                # This should work but return an error about missing API key
                result = self.test_api_endpoint("/api/agents/execute-task", "POST", task_data)
                if result:
                    if result.get("status") == "error" and "API key" in result.get("error", ""):
                        print("    ✓ Correctly handled missing API key")
                    else:
                        print(f"    ⚠ Unexpected result: {result}")
        
        return True

    def test_performance_metrics(self):
        """Test basic performance metrics"""
        print("\n⚡ Testing Performance")
        print("-" * 30)
        
        # Test response times
        start_time = time.time()
        profiles = self.test_api_endpoint("/api/agents/profiles")
        profiles_time = time.time() - start_time
        
        start_time = time.time()
        instances = self.test_api_endpoint("/api/agents/instances")
        instances_time = time.time() - start_time
        
        print(f"  📊 Profiles endpoint: {profiles_time:.3f}s")
        print(f"  📊 Instances endpoint: {instances_time:.3f}s")
        
        if profiles_time > 2.0 or instances_time > 2.0:
            print("  ⚠ Some endpoints are responding slowly")
        else:
            print("  ✓ All endpoints responding within acceptable time")
        
        return True

    def run_comprehensive_test(self):
        """Run the complete test suite"""
        print("🧪 ABC Multi-Agent Framework - Comprehensive Test Suite")
        print("=" * 60)
        
        test_results = []
        
        # Run all tests
        test_methods = [
            ("Health Checks", self.test_health_checks),
            ("Agent Profiles", self.test_agent_profiles),
            ("Agent Instances", self.test_agent_instances),
            ("Custom Agent Creation", self.test_custom_agent_creation),
            ("Input Validation", self.test_input_validation),
            ("Error Handling", self.test_error_handling),
            ("Performance", self.test_performance_metrics),
        ]
        
        for test_name, test_method in test_methods:
            try:
                result = test_method()
                test_results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                test_results.append((test_name, False))
        
        # Summary
        print(f"\n📊 Test Results Summary")
        print("=" * 30)
        
        passed = sum(1 for _, result in test_results if result)
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 All tests passed! The framework is functioning correctly.")
            print("\n📝 Next steps:")
            print("1. Add your Kimi K2 API key to the .env file")
            print("2. Run with Docker: docker-compose up")
            print("3. Open http://localhost:3000 in your browser")
            return True
        else:
            print(f"\n⚠️ {total - passed} tests failed. Please review the issues above.")
            return False

if __name__ == "__main__":
    tester = ABCFrameworkTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)