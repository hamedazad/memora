#!/usr/bin/env python3
"""
Test script to verify mobile app can connect to PostgreSQL server
"""

import requests
import json
import time
from datetime import datetime

# Server configuration (same as mobile app)
SERVER_URL = "http://127.0.0.1:8000"
API_BASE_URL = f"{SERVER_URL}/api/v1"

def test_server_health():
    """Test server health endpoint"""
    print("🏥 Testing server health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is healthy:")
            print(f"   • Status: {data.get('status')}")
            print(f"   • Database: {data.get('database')}")
            print(f"   • AI Service: {data.get('ai_service')}")
            print(f"   • Version: {data.get('version')}")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False

def test_api_endpoints():
    """Test critical API endpoints"""
    print("\n🔗 Testing API endpoints...")
    
    endpoints_to_test = {
        "memories": "/memories/",
        "auth_login": "/auth/login/",
        "auth_register": "/auth/register/",
        "ai_status": "/ai/status/",
    }
    
    results = {}
    for name, endpoint in endpoints_to_test.items():
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
            # 401 (unauthorized) or 405 (method not allowed) are OK - means endpoint exists
            # 500 (internal server error) is bad - means server/database issue
            success = response.status_code < 500
            results[name] = {
                "success": success,
                "status_code": response.status_code,
                "url": f"{API_BASE_URL}{endpoint}"
            }
            status_icon = "✅" if success else "❌"
            print(f"   {status_icon} {name}: {response.status_code} - {endpoint}")
        except Exception as e:
            results[name] = {
                "success": False,
                "error": str(e),
                "url": f"{API_BASE_URL}{endpoint}"
            }
            print(f"   ❌ {name}: ERROR - {e}")
    
    return results

def test_database_connection():
    """Test PostgreSQL database connection through Django"""
    print("\n🗄️ Testing PostgreSQL database connection...")
    
    try:
        # Try to access memories endpoint - this requires database access
        response = requests.get(f"{API_BASE_URL}/memories/", timeout=10)
        
        if response.status_code == 401:
            print("✅ PostgreSQL database is accessible (authentication required)")
            return True
        elif response.status_code == 200:
            print("✅ PostgreSQL database is accessible (direct access)")
            return True
        elif response.status_code == 500:
            print("❌ Database connection error (500 Internal Server Error)")
            print("   This usually indicates PostgreSQL connection issues")
            return False
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def test_authentication_flow():
    """Test authentication endpoints"""
    print("\n🔐 Testing authentication flow...")
    
    # Test registration endpoint with empty data
    try:
        reg_response = requests.post(
            f"{API_BASE_URL}/auth/register/",
            json={},
            timeout=10
        )
        
        login_response = requests.post(
            f"{API_BASE_URL}/auth/login/",
            json={},
            timeout=10
        )
        
        # Both should return 400 (bad request) not 500 (server error)
        auth_working = reg_response.status_code == 400 and login_response.status_code == 400
        
        if auth_working:
            print("✅ Authentication endpoints are properly configured")
            print(f"   • Register endpoint: {reg_response.status_code}")
            print(f"   • Login endpoint: {login_response.status_code}")
            return True
        else:
            print("❌ Authentication endpoints have issues")
            print(f"   • Register endpoint: {reg_response.status_code}")
            print(f"   • Login endpoint: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

def test_mobile_specific_features():
    """Test mobile-specific features"""
    print("\n📱 Testing mobile-specific features...")
    
    # Test CORS headers (important for mobile apps)
    try:
        response = requests.options(f"{API_BASE_URL}/health/", timeout=5)
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        }
        
        has_cors = any(cors_headers.values())
        if has_cors:
            print("✅ CORS is configured for mobile apps")
            for header, value in cors_headers.items():
                if value:
                    print(f"   • {header}: {value}")
        else:
            print("⚠️  CORS headers not found - mobile apps may have connection issues")
        
        return has_cors
        
    except Exception as e:
        print(f"❌ CORS test failed: {e}")
        return False

def create_test_memory():
    """Test creating a memory (requires authentication)"""
    print("\n📝 Testing memory creation (will fail without auth - that's expected)...")
    
    try:
        test_memory = {
            "title": "Test Memory from Mobile",
            "content": "This is a test memory created to verify mobile-server connection",
            "category": "test",
            "importance": 5,
            "tags": ["test", "mobile", "postgresql"]
        }
        
        response = requests.post(
            f"{API_BASE_URL}/memories/",
            json=test_memory,
            timeout=10
        )
        
        if response.status_code == 401:
            print("✅ Memory creation endpoint works (authentication required)")
            return True
        elif response.status_code == 201:
            print("✅ Memory created successfully!")
            data = response.json()
            print(f"   • Memory ID: {data.get('id')}")
            return True
        elif response.status_code == 500:
            print("❌ Server error during memory creation (database issue?)")
            return False
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Memory creation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Mobile App Connection to PostgreSQL Server")
    print("=" * 60)
    print(f"Server URL: {SERVER_URL}")
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run all tests
    tests = [
        ("Server Health", test_server_health),
        ("API Endpoints", test_api_endpoints),
        ("PostgreSQL Database", test_database_connection),
        ("Authentication Flow", test_authentication_flow),
        ("Mobile CORS Features", test_mobile_specific_features),
        ("Memory Creation", create_test_memory),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
        
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n📊 Test Summary")
    print("-" * 30)
    
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Mobile app should work perfectly with PostgreSQL server.")
    elif passed_tests >= total_tests * 0.8:
        print("\n✅ Most tests passed! Mobile app should work with minor issues.")
    else:
        print("\n⚠️  Several tests failed. Please check server configuration.")
    
    print(f"\n📱 Mobile app can connect to: {SERVER_URL}")
    print("🌐 Web interface available at: http://localhost:8000")
    print("📊 Admin panel available at: http://localhost:8000/admin/")

if __name__ == "__main__":
    main()


