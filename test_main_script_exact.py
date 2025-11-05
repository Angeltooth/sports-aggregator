#!/usr/bin/env python3
"""
Exact Replica of Main Script WordPress Functions
Tests exactly the same authentication and posting methods as deploy_enhanced_sports_aggregator.py
"""

import json
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup

class WordPressPostTester:
    def __init__(self):
        self.config = self.load_config()
        
    def load_config(self):
        """Load configuration from config.json"""
        with open('config.json', 'r') as f:
            return json.load(f)
    
    def test_wordpress_posting(self):
        """Test the EXACT same functions as main script"""
        print("🔍 Testing EXACT WordPress posting methods...")
        
        # Test exactly what main script does
        title = "Test Post - Authentication Check"
        content = "<p>This is a test post using the exact same method as the main script.</p>"
        
        success = self.post_to_wordpress_exact(title, content)
        return success
    
    def post_to_wordpress_exact(self, title, content):
        """EXACT copy of main script's post_to_wordpress method"""
        try:
            print("📝 Attempting to post...")
            
            # Use EXACT same method as main script
            wordpress_url = f"{self.config['wordpress']['url']}/wp-json/wp/v2/posts"
            
            post_data = {
                'title': title,
                'content': content,
                'status': 'publish',
                'categories': [self.config['wordpress']['category_id']]
            }
            
            # EXACT same authentication as main script
            username = self.config['wordpress']['username']
            app_password = self.config['wordpress']['app_password']
            auth = HTTPBasicAuth(username, app_password)
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            print(f"🔑 Using credentials:")
            print(f"   - URL: {wordpress_url}")
            print(f"   - Username: {username}")
            print(f"   - Password: {app_password[:4]}...{app_password[-4:]}")
            print(f"   - Category ID: {self.config['wordpress']['category_id']}")
            
            response = requests.post(
                wordpress_url, 
                headers=headers, 
                json=post_data, 
                auth=auth
            )
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 201:
                print("✅ SUCCESS! Posting works perfectly!")
                post_data = response.json()
                print(f"   - Post ID: {post_data.get('id')}")
                print(f"   - Post URL: {post_data.get('link', 'N/A')}")
                
                # Clean up - delete the test post
                self.delete_test_post(post_data.get('id'))
                return True
            else:
                print(f"❌ FAILED with status: {response.status_code}")
                print(f"   - Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception occurred: {str(e)}")
            return False
    
    def delete_test_post(self, post_id):
        """Delete the test post"""
        try:
            delete_url = f"{self.config['wordpress']['url']}/wp-json/wp/v2/posts/{post_id}"
            username = self.config['wordpress']['username']
            app_password = self.config['wordpress']['app_password']
            auth = HTTPBasicAuth(username, app_password)
            
            response = requests.delete(delete_url, auth=auth)
            
            if response.status_code in [200, 410]:
                print(f"🧹 Test post {post_id} deleted successfully")
            else:
                print(f"⚠️  Could not delete test post {post_id}: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️  Error deleting test post: {str(e)}")

def main():
    """Main test function"""
    print("🧪 EXACT MAIN SCRIPT REPLICA TEST")
    print("=" * 50)
    
    tester = WordPressPostTester()
    
    print("\n📋 Configuration Check:")
    config = tester.config
    print(f"   - URL: {config['wordpress']['url']}")
    print(f"   - Username: {config['wordpress']['username']}")
    print(f"   - Password: {config['wordpress']['app_password'][:4]}...{config['wordpress']['app_password'][-4:]}")
    print(f"   - Category ID: {config['wordpress']['category_id']}")
    
    success = tester.test_wordpress_posting()
    
    if success:
        print("\n🎉 EXACT METHOD TEST PASSED!")
        print("   Your main script should work perfectly.")
        print("   Check if you're running the correct updated file!")
    else:
        print("\n❌ EXACT METHOD TEST FAILED!")
        print("   There's an issue with the posting method itself.")
        print("   The problem is not with file versions.")
    
    return success

if __name__ == "__main__":
    main()
