#!/usr/bin/env python3
"""
Test script to verify the career advisor app is working correctly
"""
import requests
import json
import time

def test_app():
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Career Advisor App...")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Health check passed")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False
    
    # Test 2: Skills analysis
    print("2. Testing skills analysis...")
    try:
        test_data = {
            "skills": "Python, SQL, JavaScript, React, Git",
            "interest": "web"
        }
        response = requests.post(
            f"{base_url}/api/analyze", 
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Skills analysis successful")
            print(f"   📊 Found {len(data.get('bestRoles', []))} matching roles")
            print(f"   🎯 Top role: {data.get('bestRoles', [{}])[0].get('title', 'N/A')}")
            print(f"   📈 Match score: {data.get('bestRoles', [{}])[0].get('score', 'N/A')}%")
            print(f"   🔍 Skill gaps: {len(data.get('skillGaps', []))}")
            print(f"   📚 Learning resources: {len(data.get('learningPlan', []))}")
        else:
            print(f"   ❌ Skills analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Skills analysis failed: {e}")
        return False
    
    print("\n🎉 All tests passed! The app is working correctly.")
    print("\n📝 How to use:")
    print("   1. Open index.html in your browser")
    print("   2. Or visit http://localhost:5000")
    print("   3. Enter your skills and click 'Analyze Skills'")
    print("   4. View your career matches and learning plan")
    
    return True

if __name__ == "__main__":
    test_app()
