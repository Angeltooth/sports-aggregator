#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sports News Aggregator with Improved Text Formatting
Fetches sports news from multiple RSS feeds and posts to WordPress
"""

import json
import requests
import feedparser
import hashlib
from datetime import datetime
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import time
import re

class SportsNewsAggregator:
    def __init__(self, config_file='config.json'):
        """Initialize the aggregator with configuration"""
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.wordpress = self.config['wordpress']
        self.auth = HTTPBasicAuth(
            self.wordpress['username'],
            self.wordpress['application_password']
        )
        self.posted_articles = set()
        self.load_posted_articles()
    
    def load_posted_articles(self):
        """Load previously posted article hashes"""
        try:
            with open('posted_articles.json', 'r') as f:
                data = json.load(f)
                self.posted_articles = set(data.get('articles', []))
        except FileNotFoundError:
            self.posted_articles = set()
    
    def save_posted_articles(self):
        """Save posted article hashes"""
        with open('posted_articles.json', 'w') as f:
            json.dump({'articles': list(self.posted_articles)}, f)
    
    def get_article_hash(self, title, link):
        """Generate unique hash for article"""
        content = f"{title}|{link}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def format_content_improved(self, text):
        """
        Format text content with proper paragraphs and HTML structure
        """
        if not text or len(text.strip()) < 20:
            return '<p>Content not available.</p>'
        
        # Clean the text
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Split on sentence endings
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Group into paragraphs (2-3 sentences each)
        paragraphs = []
        current_para = []
        
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                current_para.append(sentence)
                
                # Create paragraph when we have 2-3 sentences or at end
                if len(current_para) >= 2 or i == len(sentences) - 1:
                    if current_para:
                        para_text = ' '.join(current_para)
                        if len(para_text.strip()) > 20:  # Skip very short paragraphs
                            paragraphs.append(para_text)
                        current_para = []
        
        # Format as HTML paragraphs
        if paragraphs:
            formatted = []
            for i, para in enumerate(paragraphs):
                if i == 0:  # Make first paragraph bold
                    formatted.append(f'<p><strong>{para}</strong></p>')
                else:
                    formatted.append(f'<p>{para}</p>')
            return '\n'.join(formatted)
        
        return f'<p>{text}</p>'
    
    def extract_article_content(self, url, source_name):
        """Extract full article content from URL with improved formatting"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple selectors to find main content
            content_selectors = [
                'article',
                '.article-body',
                '.story-body',
                '.entry-content',
                '.post-content',
                'div[itemprop="articleBody"]',
                '.content',
                'main'
            ]
            
            content_element = None
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    break
            
            if content_element:
                # Get text and format it properly
                raw_text = content_element.get_text().strip()
                formatted_content = self.format_content_improved(raw_text)
                
                # Add source attribution
                formatted_content += f'\n\n<p><em>Source: {source_name}</em></p>'
                
                return formatted_content
            
            return '<p>Unable to extract full article content.</p>'
            
        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
            return '<p>Content extraction failed.</p>'
    
    def extract_image_url(self, entry):
        """Extract image URL from feed entry"""
        # Try media:content
        if hasattr(entry, 'media_content') and entry.media_content:
            return entry.media_content[0].get('url')
        
        # Try media:thumbnail
        if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
            return entry.media_thumbnail[0].get('url')
        
        # Try enclosures
        if hasattr(entry, 'enclosures') and entry.enclosures:
            for enclosure in entry.enclosures:
                if 'image' in enclosure.get('type', ''):
                    return enclosure.get('href')
        
        return None
    
    def optimize_image(self, image_data, image_url):
    """Optimize image by resizing and compressing"""
        try:
            from io import BytesIO
            from PIL import Image
            
            # Open image from bytes
            img = Image.open(BytesIO(image_data))
            
            # Convert to RGB if necessary (handles RGBA, etc.)
            if img.mode in ('RGBA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Resize to max 800px width (maintain aspect ratio)
            max_width = 800
            if img.width > max_width:
                new_height = int((img.height * max_width) / img.width)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Save optimized image to bytes
            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            return output.getvalue()
            
        except Exception as e:
            print(f"Error optimizing image: {e}")
            return image_data
    
    def post_to_wordpress(self, title, content, featured_image_id=None):
        """Post article to WordPress"""
        try:
            post_data = {
                'title': title,
                'content': content,
                'status': 'publish',
                'categories': [self.wordpress.get('category_id', 1)]
            }
            
            if featured_image_id:
                post_data['featured_media'] = featured_image_id
            
            response = requests.post(
                f"{self.wordpress['api_url']}/wp-json/wp/v2/posts",
                json=post_data,
                auth=self.auth
            )
            
            if response.status_code == 201:
                return True, response.json()['link']
            else:
                print(f"Error posting: {response.status_code} - {response.text}")
                return False, None
                
        except Exception as e:
            print(f"Error posting to WordPress: {e}")
            return False, None
    
    def process_feed(self, feed_url, source_name):
        """Process a single RSS feed"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Processing: {source_name}")
        
        try:
            feed = feedparser.parse(feed_url)
            new_posts = 0
            
            for entry in feed.entries[:10]:  # Process up to 10 latest entries
                title = entry.get('title', 'No Title')
                link = entry.get('link', '')
                
                # Check if already posted
                article_hash = self.get_article_hash(title, link)
                if article_hash in self.posted_articles:
                    continue
                
                # Extract full content with improved formatting
                content = self.extract_article_content(link, source_name)
                
                # Try to get featured image
                image_url = self.extract_image_url(entry)
                featured_image_id = None
                
                if image_url:
                    featured_image_id = self.upload_image_to_wordpress(image_url, title)
                
                # Add source link to content
                source_link_html = f'\n\n<p><em>Read the full article at: <a href="{link}" target="_blank" rel="noopener">{source_name}</a></em></p>'
                content_with_source = content + source_link_html

                # Post to WordPress
                success, post_link = self.post_to_wordpress(title, content_with_source, featured_image_id)
                
                if success:
                    self.posted_articles.add(article_hash)
                    new_posts += 1
                    print(f"  ✅ Posted: {title[:60]}...")
                    if post_link:
                        print(f"     Link: {post_link}")
                else:
                    print(f"  ❌ Failed: {title[:60]}...")
                
                # Rate limiting
                time.sleep(2)
            
            print(f"[{source_name}] New posts: {new_posts}")
            return new_posts
            
        except Exception as e:
            print(f"Error processing {source_name}: {e}")
            return 0
    
    def run(self):
        """Run the aggregator for all feeds"""
        print(f"\n{'='*60}")
        print(f"Sports News Aggregator - Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        total_posts = 0
        
        for feed in self.config['feeds']:
            posts = self.process_feed(feed['url'], feed['name'])
            total_posts += posts
        
        # Save posted articles
        self.save_posted_articles()
        
        print(f"\n{'='*60}")
        print(f"Aggregation Complete!")
        print(f"Total new posts: {total_posts}")
        print(f"Total tracked articles: {len(self.posted_articles)}")
        print(f"{'='*60}\n")

if __name__ == '__main__':
    aggregator = SportsNewsAggregator()
    aggregator.run()
