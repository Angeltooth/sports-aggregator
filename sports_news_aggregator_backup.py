#!/usr/bin/env python3
"""
Sports News Aggregator for WordPress
Automatically aggregates sports news from RSS feeds and publishes to WordPress
"""

import requests
import json
import feedparser
from datetime import datetime
import os
import base64
import hashlib
import re
from urllib.parse import urlparse
import time

class SportsNewsAggregator:
    def __init__(self, config_file='config.json'):
        self.config = self.load_config(config_file)
        self.published_hashes = self.load_published_hashes()
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"‚ùå Error loading config: {e}")
            return {}
            
    def load_published_hashes(self):
        """Load published article hashes to avoid duplicates"""
        try:
            with open('published_hashes.json', 'r') as f:
                return json.load(f)
        except:
            return {}
            
    def save_published_hashes(self):
        """Save published article hashes"""
        try:
            with open('published_hashes.json', 'w') as f:
                json.dump(self.published_hashes, f)
        except Exception as e:
            print(f"‚ùå Error saving hashes: {e}")
            
    def get_content_hash(self, title, description):
        """Generate hash for duplicate detection"""
        content = f"{title}{description}".encode('utf-8')
        return hashlib.md5(content).hexdigest()
        
    def is_duplicate(self, content_hash):
        """Check if content has already been published"""
        return content_hash in self.published_hashes
        
    def mark_as_published(self, content_hash):
        """Mark content as published"""
        self.published_hashes[content_hash] = datetime.now().isoformat()
        
    def clean_html(self, text):
        """Remove HTML tags from text"""
        if not text:
            return ""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
        
    def extract_images_from_content(self, html_content):
        """Extract image URLs from HTML content"""
        if not html_content:
            return []
            
        # Find image URLs
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
        images = re.findall(img_pattern, html_content)
        
        # Filter for valid image URLs
        valid_images = []
        for img_url in images:
            if img_url.startswith('http') and any(img_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                valid_images.append(img_url)
                
        return valid_images
        
    def publish_to_wordpress(self, article):
        """Publish article to WordPress via REST API"""
        wp_config = self.config.get('wordpress', {})
        api_url = f"{wp_config['api_url']}/wp-json/wp/v2/posts"
        
        # Setup authentication
        username = wp_config.get('username', '')
        password = wp_config.get('application_password', '')
        credentials = f"{username}:{password}"
        auth_header = f"Basic {base64.b64encode(credentials.encode()).decode()}"
        
        headers = {
            'Authorization': auth_header,
            'Content-Type': 'application/json'
        }
        
        # Prepare post data
        post_data = {
            'title': article['title'],
            'content': article['content'],
            'status': 'publish',
            'excerpt': article.get('excerpt', ''),
            'meta': {
                'original_source': article['source'],
                'original_url': article['link']
            }
        }
        
        try:
            print(f"Ì†ΩÌ Publishing to WordPress: {article['title']}")
            response = requests.post(api_url, headers=headers, json=post_data, timeout=30)
            
            if response.status_code == 201:
                print(f"≥§‚úÖ Successfully published: {article['title']}")
                return True
            else:
                print(f"‚ùå Failed to publish: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"‚ùå Error publishing to WordPress: {e}")
            return False
            
    def aggregate_from_rss(self, rss_url, source_name):
        """Fetch and process articles from RSS feed"""
        try:
            print(f"Ì†ΩÌ Fetching RSS: {source_name}")
            feed = feedparser.parse(rss_url)
            
            if hasattr(feed, 'bozo') and feed.bozo:
                print(f"≥°‚ö†Ô∏è  RSS feed has some issues: {feed.bozo_exception}")
                
            articles = []
            
            for entry in feed.entries[:10]:  # Limit to 10 articles per feed
                title = entry.get('title', '').strip()
                description = entry.get('description', '')
                link = entry.get('link', '')
                
                # Skip if no title
                if not title:
                    continue
                    
                # Clean content
                clean_description = self.clean_html(description)
                
                # Create content hash for duplicate detection
                content_hash = self.get_content_hash(title, clean_description)
                
                # Check for duplicates
                if self.is_duplicate(content_hash):
                    print(f"‚è≠Ô∏è  Skipped duplicate: {title}")
                    continue
                    
                # Prepare article content with attribution
                content = f"""
                <p>{clean_description}</p>
                
                <hr>
                <p><strong>Source:</strong> {source_name} | 
                <a href="{link}" target="_blank" rel="noopener">Read Original Article</a></p>
                """
                
                # Generate excerpt
                excerpt = f"Latest {source_name} sports news"[:150]
                
                # Prepare article
                article = {
                    'title': title,
                    'content': content.strip(),
                    'excerpt': excerpt,
                    'source': source_name,
                    'link': link,
                    'content_hash': content_hash
                }
                
                articles.append(article)
                
            return articles
            
        except Exception as e:
            print(f"‚ùå Error fetching RSS {rss_url}: {e}")
            return []
            
    def run(self):
        """Main aggregation and publishing loop"""
        print("Ì†ºÌ Sports News Automation Starting...")
        print(f"øàÌ†ΩÌ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        # Load RSS feeds configuration
        try:
            with open('basic_rss_feeds.json', 'r') as f:
                feeds_config = json.load(f)
        except Exception as e:
            print(f"≥Ö‚ùå Error loading RSS feeds: {e}")
            return
            
        # Validate WordPress configuration
        wp_config = self.config.get('wordpress', {})
        if not all([wp_config.get('api_url'), wp_config.get('username'), wp_config.get('application_password')]):
            print("‚ùå WordPress configuration incomplete. Please check config.json")
            return
            
        all_articles = []
        published_count = 0
        
        # Aggregate from each RSS feed
        for feed_config in feeds_config['rss_feeds']:
            articles = self.aggregate_from_rss(feed_config['url'], feed_config['name'])
            all_articles.extend(articles)
            time.sleep(2)  # Rate limiting between feeds
            
        print(f"\nÌ†ΩÌ Total articles found: {len(all_articles)}")
        
        # Publish to WordPress
        if all_articles:
            print("\n≥äÌ†ΩÌ Starting WordPress publishing...")
            for i, article in enumerate(all_articles, 1):
                print(f"[{i}/{len(all_articles)}] Publishing: {article['title']}")
                
                if self.publish_to_wordpress(article):
                    self.mark_as_published(article['content_hash'])
                    published_count += 1
                    
                # Rate limiting
                time.sleep(3)
        
        # Save published hashes
        self.save_published_hashes()
        
        print("\n" + "=" * 50)
        print(f"≥§‚úÖ Automation completed!")
        print(f"Ì†ΩÌ Published: {published_count} articles")
        print(f"≥äÌ†ΩÌ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        aggregator = SportsNewsAggregator()
        aggregator.run()
    except KeyboardInterrupt:
        print("\nµê‚èπÔ∏è  Automation stopped by user")
    except Exception as e:
        print(f"‚ùå Fatal error: {e}")
