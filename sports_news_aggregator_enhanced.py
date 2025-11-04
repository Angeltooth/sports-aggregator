#!/usr/bin/env python3
"""
Enhanced Sports News Aggregator - With Full Text Extraction
Fetches latest sports news from RSS feeds and publishes to WordPress with complete content
"""

import json
import hashlib
import re
import base64
import requests
from datetime import datetime, timedelta
import feedparser
import sys
import os
from bs4 import BeautifulSoup

class SportsNewsAggregator:
    def __init__(self, config_file='config.json', feeds_file='basic_rss_feeds.json'):
        """Initialize the enhanced sports news aggregator"""
        self.config = self.load_config(config_file)
        self.feeds = self.load_feeds(feeds_file)
        self.published_posts_file = 'published_posts.json'
        self.published_posts = self.load_published_posts()
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {config_file} not found")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error reading config file: {e}")
            sys.exit(1)
    
    def load_feeds(self, feeds_file):
        """Load RSS feeds configuration"""
        try:
            with open(feeds_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {feeds_file} not found")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error reading feeds file: {e}")
            sys.exit(1)
    
    def load_published_posts(self):
        """Load list of already published posts"""
        try:
            with open(self.published_posts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_published_posts(self):
        """Save list of published posts"""
        with open(self.published_posts_file, 'w', encoding='utf-8') as f:
            json.dump(self.published_posts, f, indent=2)
    
    def get_content_hash(self, title, link):
        """Generate unique hash for content deduplication"""
        content = f"{title}{link}".encode('utf-8')
        return hashlib.md5(content).hexdigest()
    
    def is_already_published(self, title, link):
        """Check if content has already been published"""
        content_hash = self.get_content_hash(title, link)
        return content_hash in self.published_posts
    
    def mark_as_published(self, title, link):
        """Mark content as published"""
        content_hash = self.get_content_hash(title, link)
        self.published_posts[content_hash] = {
            'title': title,
            'link': link,
            'published_at': datetime.now().isoformat()
        }
        self.save_published_posts()
    
    def fetch_full_article_content(self, url):
        """Fetch and extract full article content from the source URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Try to find article content
            content_selectors = [
                'article', 
                '.article-content', 
                '.story-body', 
                '.post-content',
                '.entry-content',
                '[role="main"]',
                'main',
                '.content'
            ]
            
            content = ""
            for selector in content_selectors:
                article_element = soup.select_one(selector)
                if article_element:
                    content = article_element.get_text(strip=True)
                    break
            
            # If no specific article element found, get main content
            if not content:
                # Remove common non-content elements
                for element in soup.find_all(['nav', 'header', 'footer', 'aside', 'script', 'style', 'form']):
                    element.decompose()
                content = soup.get_text(strip=True)
            
            # Clean up the content
            content = re.sub(r'\n\s*\n', '\n\n', content)  # Normalize line breaks
            content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
            content = content.strip()
            
            # Limit content length (WordPress has limits)
            if len(content) > 3000:
                content = content[:3000] + "..."
            
            return content
            
        except Exception as e:
            print(f"    Warning: Could not fetch full content: {e}")
            return ""
    
    def extract_image_from_rss(self, entry):
        """Extract image URL from RSS entry"""
        try:
            # Try different methods to find images
            
            # Method 1: Media enclosure
            if hasattr(entry, 'enclosures') and entry.enclosures:
                for enclosure in entry.enclosures:
                    if hasattr(enclosure, 'type') and 'image' in enclosure.type.lower():
                        return enclosure.href
            
            # Method 2: Media content
            if hasattr(entry, 'media_content') and entry.media_content:
                for media in entry.media_content:
                    if 'image' in media.get('type', '').lower():
                        return media.get('url', '')
            
            # Method 3: Media thumbnail
            if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                return entry.media_thumbnail[0].get('url', '')
            
            # Method 4: Content with images (parse HTML)
            content = ""
            if hasattr(entry, 'description'):
                content = entry.description
            elif hasattr(entry, 'content'):
                content = entry.content[0] if entry.content else ""
            elif hasattr(entry, 'summary'):
                content = entry.summary
            
            if content:
                # Use regex to find image URLs
                img_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
                matches = re.findall(img_pattern, content)
                if matches:
                    return matches[0]  # Return first image found
            
            return ""
            
        except Exception as e:
            print(f"    Warning: Could not extract image: {e}")
            return ""
    
    def clean_html_content(self, content):
        """Clean HTML content and convert to plain text"""
        if not content:
            return ""
        
        # Remove HTML tags
        clean = re.compile('<.*?>')
        text = re.sub(clean, '', content)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def fetch_rss_feeds(self):
        """Fetch articles from all RSS feeds with enhanced extraction"""
        articles = []
        
        print(f"Fetching RSS feeds from {len(self.feeds)} sources...")
        
        for feed_config in self.feeds:
            print(f"Processing feed: {feed_config['name']}")
            
            try:
                feed = feedparser.parse(feed_config['url'])
                
                if feed.bozo:
                    print(f"Warning: Feed {feed_config['name']} has parsing issues")
                
                articles_added = 0
                for entry in feed.entries:
                    if hasattr(entry, 'title') and hasattr(entry, 'link'):
                        title = entry.title.strip()
                        link = entry.link.strip()
                        
                        # Check for duplicates
                        if not self.is_already_published(title, link):
                            
                            # Get full article content
                            full_content = self.fetch_full_article_content(link)
                            
                            # If no full content from scraping, use RSS description
                            if not full_content:
                                description = ""
                                if hasattr(entry, 'description'):
                                    description = entry.description
                                elif hasattr(entry, 'summary'):
                                    description = entry.summary
                                
                                full_content = self.clean_html_content(description)
                            
                            # Extract image
                            image_url = self.extract_image_from_rss(entry)
                            
                            # Get publication date
                            pub_date = None
                            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                                pub_date = datetime(*entry.published_parsed[:6])
                            
                            article = {
                                'title': title,
                                'link': link,
                                'description': full_content,
                                'source': feed_config['name'],
                                'pub_date': pub_date.isoformat() if pub_date else datetime.now().isoformat(),
                                'image_url': image_url
                            }
                            
                            articles.append(article)
                            articles_added += 1
                            print(f"  Added: {title[:50]}...")
                        else:
                            print(f"  Skipped (duplicate): {title[:50]}...")
                            
                print(f"  Total articles added from {feed_config['name']}: {articles_added}")
                            
            except Exception as e:
                print(f"Error processing feed {feed_config['name']}: {e}")
                continue
        
        print(f"Total new articles found: {len(articles)}")
        return articles
    
    def post_to_wordpress(self, articles):
        """Post articles to WordPress with enhanced content"""
        if not articles:
            print("No new articles to post.")
            return
        
        wordpress_config = self.config.get('wordpress', {})
        api_url = wordpress_config.get('api_url')
        username = wordpress_config.get('username')
        application_password = wordpress_config.get('application_password')
        
        if not all([api_url, username, application_password]):
            print("Error: Missing WordPress configuration")
            return
        
        # Prepare authentication
        credentials = f"{username}:{application_password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json'
        }
        
        # Get categories
        categories_config = self.config.get('categories', {})
        sports_category_id = categories_config.get('sports', 1)  # Default to category ID 1
        
        posted_count = 0
        
        for article in articles:
            try:
                # Prepare post data with enhanced content
                image_html = ""
                if article.get('image_url'):
                    image_html = f'<p><img src="{article["image_url"]}" alt="{article["title"]}" style="max-width: 100%; height: auto;" /></p>'
                
                post_data = {
                    'title': article['title'],
                    'content': f"""
                    {image_html}
                    <p><strong>Source:</strong> {article['source']}</p>
                    <p>{article['description']}</p>
                    <p><a href="{article['link']}" target="_blank">Read original article</a></p>
                    <p><em>Published: {article['pub_date']}</em></p>
                    """,
                    'status': 'publish',
                    'categories': [sports_category_id],
                    'format': 'standard'
                }
                
                # Post to WordPress
                response = requests.post(
                    f"{api_url}/wp-json/wp/v2/posts",
                    headers=headers,
                    json=post_data,
                    timeout=30
                )
                
                if response.status_code == 201:
                    print(f"✓ Posted: {article['title'][:50]}...")
                    self.mark_as_published(article['title'], article['link'])
                    posted_count += 1
                    
                    # Add a small delay to avoid rate limiting
                    import time
                    time.sleep(2)
                    
                elif response.status_code == 401:
                    print(f"✗ Authentication failed for: {article['title'][:50]}...")
                    break  # Stop if authentication fails
                    
                else:
                    print(f"✗ Failed to post {article['title'][:50]}... (Status: {response.status_code})")
                    if response.status_code == 400:
                        print(f"  Response: {response.text}")
                    
            except Exception as e:
                print(f"✗ Error posting {article['title'][:50]}...: {e}")
                continue
        
        print(f"\nSummary: {posted_count} articles posted to WordPress")
    
    def run(self):
        """Main execution method"""
        print("=" * 60)
        print("Enhanced Sports News Aggregator")
        print("=" * 60)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Fetch articles from RSS feeds
        articles = self.fetch_rss_feeds()
        
        if articles:
            print(f"\nPosting {len(articles)} articles to WordPress...")
            self.post_to_wordpress(articles)
        else:
            print("\nNo new articles to process.")
        
        print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

def main():
    """Main entry point"""
    try:
        aggregator = SportsNewsAggregator()
        aggregator.run()
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
