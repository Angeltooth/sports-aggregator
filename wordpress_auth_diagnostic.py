#!/usr/bin/env python3
"""
WordPress Authentication Diagnostic Tool
Helps identify issues with WordPress API authentication
"""

import requests
import json
from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin
import sys

def load_config():
    """Load configuration from config.json"""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print("❌ config.json not found!")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in config.json: {e}")
        return None

def test_wordpress_connection(config):
    """Test basic WordPress connection and authentication"""
    print("🔍 Testing WordPress Connection...")
    
    url = config['wordpress']['url']
    username = config['wordpress']['username']
    app_password = config['wordpress']['app_password']
    
    print(f"📍 WordPress URL: {url}")
    print(f"👤 Username: {username}")
    print(f"🔑 Application Password: {app_password[:4]}...{app_password[-4:]}")
    
    # Test basic authentication
    api_url = urljoin(url, 'wp-json/wp/v2/users/me')
    
    try:
        response = requests.get(
            api_url,
            auth=HTTPBasicAuth(username, app_password),
            timeout=10
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Authentication SUCCESSFUL!")
            print(f"👤 User Info:")
            print(f"   - ID: {user_data.get('id')}")
            print(f"   - Username: {user_data.get('username')}")
            print(f"   - Name: {user_data.get('name')}")
            print(f"   - Roles: {user_data.get('roles')}")
            return True, user_data
        elif response.status_code == 401:
            print("❌ Authentication FAILED - 401 Unauthorized")
            print(f"   - This means the username/password is incorrect")
            print(f"   - Or the Application Password is invalid/expired")
            print(f"   - Response: {response.text}")
            return False, None
        else:
            print(f"❌ Unexpected error: {response.status_code}")
            print(f"   - Response: {response.text}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False, None

def test_post_capabilities(config, user_data):
    """Test if user has post creation capabilities"""
    print("\n🔍 Testing Post Creation Capabilities...")
    
    url = config['wordpress']['url']
    username = config['wordpress']['username']
    app_password = config['wordpress']['app_password']
    
    api_url = urljoin(url, 'wp-json/wp/v2/posts')
    
    # Create a test post
    test_post = {
        'title': 'Test Post - Authentication Check',
        'content': 'This is a test post to verify posting permissions.',
        'status': 'draft'  # Use draft to avoid actually publishing
    }
    
    try:
        response = requests.post(
            api_url,
            json=test_post,
            auth=HTTPBasicAuth(username, app_password),
            timeout=10
        )
        
        print(f"📊 Post Creation Status: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Post creation successful!")
            post_data = response.json()
            print(f"   - Post ID: {post_data.get('id')}")
            print(f"   - Post Title: {post_data.get('title', {}).get('rendered', 'N/A')}")
            
            # Clean up - delete the test post
            post_id = post_data.get('id')
            delete_url = f"{api_url}/{post_id}"
            delete_response = requests.delete(delete_url, auth=HTTPBasicAuth(username, app_password))
            
            if delete_response.status_code in [200, 410]:
                print("🧹 Test post cleaned up successfully")
            else:
                print(f"⚠️  Could not clean up test post: {delete_response.status_code}")
                
            return True
        elif response.status_code == 401:
            print("❌ Post creation FAILED - 401 Unauthorized")
            print("   - Authentication works but user lacks posting permissions")
            print(f"   - User roles: {user_data.get('roles', 'Unknown')}")
            print(f"   - Response: {response.text}")
            return False
        else:
            print(f"❌ Post creation error: {response.status_code}")
            print(f"   - Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False

def check_wordpress_permissions(user_data):
    """Check what permissions the user has"""
    print("\n🔍 Checking User Permissions...")
    
    if not user_data:
        print("❌ No user data available")
        return
    
    roles = user_data.get('roles', [])
    capabilities = user_data.get('capabilities', {})
    
    print(f"👤 User Roles: {roles}")
    
    # Check for important capabilities
    important_caps = [
        'edit_posts',
        'publish_posts', 
        'edit_published_posts',
        'delete_posts',
        'edit_others_posts'
    ]
    
    print("\n🎯 Key Capabilities:")
    for cap in important_caps:
        has_cap = capabilities.get(cap, False)
        status = "✅" if has_cap else "❌"
        print(f"   {status} {cap}: {has_cap}")

def provide_recommendations():
    """Provide recommendations based on common issues"""
    print("\n💡 TROUBLESHOOTING RECOMMENDATIONS:")
    print("\n1. 🔑 Application Password Issues:")
    print("   - Go to https://sportsalertnews.com/wp-admin/profile.php")
    print("   - Scroll to 'Application Passwords' section")
    print("   - Delete the existing password and create a new one")
    print("   - Use the EXACT password from the interface (including spaces)")
    print("   - Copy it immediately - it won't be shown again")
    
    print("\n2. 👤 User Permission Issues:")
    print("   - Go to https://sportsalertnews.com/wp-admin/users.php")
    print("   - Click on 'Sports News Aggregator' user")
    print("   - Check the role is 'Administrator' or 'Editor'")
    print("   - If not, change the role to 'Administrator'")
    
    print("\n3. 🛡️ Security Plugins:")
    print("   - Some security plugins block REST API requests")
    print("   - Temporarily disable security plugins to test")
    print("   - Check if IP restrictions are blocking the request")
    
    print("\n4. 🔍 Common Issues:")
    print("   - Extra spaces in Application Password")
    print("   - Application Password expired")
    print("   - User account is disabled")
    print("   - Two-factor authentication enabled (disable for API)")

def main():
    """Main diagnostic function"""
    print("🚀 WordPress Authentication Diagnostic Tool")
    print("=" * 50)
    
    config = load_config()
    if not config:
        sys.exit(1)
    
    # Test authentication
    auth_success, user_data = test_wordpress_connection(config)
    
    if not auth_success:
        print("\n❌ AUTHENTICATION FAILED")
        provide_recommendations()
        return False
    
    # Check permissions
    check_wordpress_permissions(user_data)
    
    # Test posting capabilities
    post_success = test_post_capabilities(config, user_data)
    
    if post_success:
        print("\n✅ ALL TESTS PASSED!")
        print("   Your WordPress setup is working correctly.")
        print("   You can now run your Sports News Aggregator.")
    else:
        print("\n⚠️  AUTHENTICATION WORKS BUT POSTING FAILED")
        provide_recommendations()
    
    return auth_success and post_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
