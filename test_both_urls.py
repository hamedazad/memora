#!/usr/bin/env python
"""
Test both localhost and 127.0.0.1 URLs
"""
import requests

def test_both_urls():
    print("🧪 Testing Both Server URLs")
    print("=" * 50)
    
    urls = [
        "http://localhost:8000/api/v1/health",
        "http://127.0.0.1:8000/api/v1/health"
    ]
    
    for url in urls:
        try:
            print(f"\n🔍 Testing: {url}")
            response = requests.get(url, timeout=5)
            print(f"✅ Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response: {data}")
            else:
                print(f"❌ Error response: {response.text}")
        except Exception as e:
            print(f"❌ Failed to connect: {e}")

if __name__ == "__main__":
    test_both_urls()


