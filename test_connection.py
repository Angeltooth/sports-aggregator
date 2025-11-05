#!/usr/bin/env python3
"""
Quick WordPress Connection Test
Tests if the fixed configuration works correctly.
"""

import json
import requests
from urllib.parse import urljoin

def test_wordpress_connection():
    """Test WordPress connection with the corrected config."""
    
    # Load the config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    print("🔧 Testing WordPress Connection...")
    print("=" * 50)
    
    # Extract WordPress settings
    wp_url = config['wordpress']['url']
    username = config['wordpress']['username']
    app_password = config['wordpress']['app_password']
    category_id = config['wordpress']['category_id']
    
    print(f"WordPress URL: {wp_url}")
    print(f"Username: {username}")
    print(f"Category ID: {category_id}")
    print(f"App Password: {'✅ Set' if app_password != 'jwbt F5tn NL8I cl0e stTG iKQM' else '⚠️  Using provided password'}")
    
    # Test WordPress API
    api_url = f"{wp_url}/wp-json/wp/v2"
    headers = {
        'Authorization': f"Basic {username}:{app_password}"
    }
    
    print(f"\n🧪 Testing API Connection...")
    
    try:
        # Test categories endpoint
        response = requests.get(f"{api_url}/categories", headers=headers, timeout=10)
        
        if response.status_code == 200:
            categories = response.json()
            print("✅ WordPress API connection successful!")
            print(f"📋 Found {len(categories)} categories")
            
            # Check if our category exists
            found_category = None
            for cat in categories:
                if cat['id'] == category_id:
                    found_category = cat
                    break
            
            if found_category:
                print(f"✅ Target category exists: {found_category['name']} (ID: {category_id})")
                return True
            else:
                print(f"❌ Category ID {category_id} not found")
                print("Available categories:")
                for cat in categories[:10]:
                    print(f"  - {cat['name']} (ID: {cat['id']})")
                return False
                
        elif response.status_code == 401:
            print("❌ Authentication failed!")
            print("Please check:")
            print("  - Username is correct")
            print("  - Password is correct")
            print("  - Application password was generated properly")
            return False
        elif response.status_code == 404:
            print("❌ WordPress REST API not found!")
            print("Please check:")
            print("  - WordPress URL is correct")
            print("  - WordPress is accessible")
            print("  - REST API is enabled")
            return False
        else:
            print(f"❌ API returned status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        print("Please check:")
        print("  - Internet connection")
        print("  - WordPress URL is accessible")
        return False

if __name__ == "__main__":
    test_wordpress_connection()
