#!/usr/bin/env python3
"""
Quick WordPress Auth Test
Simple script to test if authentication is working
"""

import json
import requests
from requests.auth import HTTPBasicAuth

def quick_test():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        url = config['wordpress']['url']
        username = config['wordpress']['username']
        password = config['wordpress']['app_password']
        
        # Test basic auth
        response = requests.get(
            f"{url}/wp-json/wp/v2/users/me",
            auth=HTTPBasicAuth(username, password),
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Authentication: WORKING")
            return True
        elif response.status_code == 401:
            print("❌ Authentication: FAILED")
            print("   → Regenerate Application Password")
            return False
        else:
            print(f"❌ Authentication: ERROR ({response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Quick Auth Test...")
    success = quick_test()
    
    if success:
        print("\n🎉 Now test posting: python test_wordpress_posting.py")
    else:
        print("\n🔧 Fix authentication first, then test again")
