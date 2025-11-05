#!/usr/bin/env python3
"""
Final Test: WordPress posting capability
This tests if articles can actually be posted to WordPress.
"""

import json
import requests
import hashlib
import time

def test_wordpress_posting():
    """Test posting a sample article to WordPress."""
    
    # Load the config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    print("🚀 Testing WordPress Posting...")
    print("=" * 50)
    
    # Extract WordPress settings
    wp_url = config['wordpress']['url']
    username = config['wordpress']['username']
    app_password = config['wordpress']['app_password']
    category_id = config['wordpress']['category_id']
    
    print(f"WordPress URL: {wp_url}")
    print(f"Username: {username}")
    print(f"Category ID: {category_id}")
    
    # Create test article data
    test_article = {
        'title': 'Test Article - Sports News Aggregator',
        'content': '''
        <p>This is a test article from the <strong>Sports News Aggregator</strong> system.</p>
        
        <h2>Test Content</h2>
        <p>The system should be able to:</p>
        <ul>
        <li>Extract content from RSS feeds</li>
        <li>Remove advertisements conservatively</li>
        <li>Post to WordPress successfully</li>
        <li>Handle images and media</li>
        </ul>
        
        <p><em>This is a test post to verify the integration is working correctly.</em></p>
        
        <p><strong>Read the full article at: <a href="https://example.com" target="_blank" rel="noopener noreferrer">Test Source</a></strong></p>
        ''',
        'status': 'draft',  # Use draft to avoid cluttering live site
        'categories': [category_id]
    }
    
    # Test posting
    api_url = f"{wp_url}/wp-json/wp/v2/posts"
    headers = {
        'Authorization': f"Basic {username}:{app_password}",
        'Content-Type': 'application/json'
    }
    
    print(f"\n📝 Attempting to post test article...")
    
    try:
        response = requests.post(api_url, headers=headers, json=test_article, timeout=30)
        
        if response.status_code == 201:
            post_data = response.json()
            post_id = post_data.get('id')
            post_link = post_data.get('link')
            
            print("✅ SUCCESS! Test article posted successfully!")
            print(f"📄 Post ID: {post_id}")
            print(f"🔗 Post Link: {post_link}")
            print(f"📂 Category ID: {category_id}")
            print(f"📅 Status: {post_data.get('status', 'unknown')}")
            
            # Clean up test post
            print(f"\n🧹 Cleaning up test post...")
            delete_response = requests.delete(
                f"{api_url}/{post_id}?force=true", 
                headers=headers, 
                timeout=10
            )
            
            if delete_response.status_code == 200:
                print("✅ Test post automatically deleted")
                print("\n🎉 CONFIGURATION IS PERFECT!")
                print("✅ You can now run: python deploy_enhanced_sports_aggregator.py")
            else:
                print("⚠️  Test post created but could not be automatically deleted")
                print(f"   You can delete it manually from WordPress admin (ID: {post_id})")
            
            return True
            
        else:
            print(f"❌ Failed to post article: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error details: {error_data}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Posting error: {str(e)}")
        return False

if __name__ == "__main__":
    test_wordpress_posting()
