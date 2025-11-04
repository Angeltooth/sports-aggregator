#!/usr/bin/env python3
"""
Enhanced Sports News Aggregator with Advertisement Removal
Modified version that includes comprehensive ad stripping functionality
"""

import feedparser
import requests
import json
import hashlib
import time
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import re
from typing import List, Set, Optional, Dict, Any

class AdRemovalProcessor:
    """
    Advanced advertisement removal system for news content.
    """
    
    def __init__(self):
        # CSS selectors for common ad elements
        self.ad_selectors = {
            'banner_ads': [
                '[class*="ad"]', '[id*="ad"]', '[class*="advert"]', '[id*="advert"]',
                '[class*="banner"]', '[class*="sponsored"]', '[id*="sponsored"]',
                '[class*="promo"]', '[id*="promo"]', '[class*="promotion"]'
            ],
            'social_widgets': [
                '[class*="share"]', '[id*="share"]', '[class*="social"]', '[id*="social"]',
                '.social-share', '.social-sharing', '.share-buttons'
            ],
            'newsletter_forms': [
                '[class*="newsletter"]', '[id*="newsletter"]', '[class*="subscribe"]',
                '[class*="signup"]', '[id*="signup"]', '[class*="subscription"]'
            ],
            'related_content': [
                '[class*="related"]', '[id*="related"]', '[class*="more"]', 
                '[class*="suggested"]', '[class*="recommended"]'
            ],
            'comments': [
                '[class*="comment"]', '[id*="comment"]', '[class*="discussion"]'
            ]
        }
        
        # Text patterns for ad content
        self.ad_patterns = [
            r'sponsored\s+by', r'partnered\s+with', r'advertisement', r'ad\s+supported',
            r'buy\s+now', r'shop\s+now', r'learn\s+more', r'click\s+here', r'sign\s+up\s+now',
            r'subscribe\s+to\s+our\s+newsletter', r'get\s+the\s+latest', r'don\'t\s+miss\s+out',
            r'follow\s+us\s+on', r'like\s+and\s+share', r'share\s+this\s+article',
            r'special\s+offer', r'limited\s+time', r'exclusive\s+deal', r'while\s+supplies\s+last',
            r'sale\s+price', r'discount', r'free\s+shipping', r'cheap', r'deal\s+of\s+the\s+day'
        ]
        
        self.ad_keywords = {
            'sponsored', 'advertisement', 'promoted', 'promotion', 'banner',
            'newsletter', 'subscribe', 'signup', 'follow', 'share', 'like',
            'buy now', 'shop now', 'learn more', 'click here', 'free', 
            'discount', 'sale', 'deal', 'limited time', 'exclusive'
        }
    
    def remove_ads_from_html(self, html_content: str) -> str:
        """Remove advertisements and promotional content from HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove ad-related elements by CSS selectors
        for category, selectors in self.ad_selectors.items():
            for selector in selectors:
                elements = soup.select(selector)
                for element in elements:
                    element_text = element.get_text(strip=True).lower()
                    if self._is_ad_element(element, element_text):
                        element.decompose()
        
        # Remove elements by text patterns
        for pattern in self.ad_patterns:
            elements = soup.find_all(text=re.compile(pattern, re.IGNORECASE))
            for text_element in elements:
                parent = text_element.parent
                if parent and self._is_ad_element(parent, text_element.lower()):
                    parent.decompose()
        
        # Remove elements with high ad keyword density
        all_elements = soup.find_all(['div', 'p', 'span', 'section', 'article'])
        for element in all_elements:
            if self._should_remove_by_keywords(element):
                element.decompose()
        
        return str(soup)
    
    def _is_ad_element(self, element, element_text: str) -> bool:
        """Determine if an element is likely an advertisement."""
        for pattern in self.ad_patterns:
            if re.search(pattern, element_text, re.IGNORECASE):
                return True
        
        words = element_text.lower().split()
        ad_keyword_count = sum(1 for word in words if word in self.ad_keywords)
        
        if len(words) > 0:
            ad_keyword_ratio = ad_keyword_count / len(words)
            if ad_keyword_ratio > 0.1:
                return True
        
        return False
    
    def _should_remove_by_keywords(self, element) -> bool:
        """Check if element should be removed based on keyword density."""
        text = element.get_text(strip=True).lower()
        words = text.split()
        
        if len(words) < 3:
            return False
        
        ad_keyword_count = 0
        for keyword in self.ad_keywords:
            ad_keyword_count += text.count(keyword)
        
        if len(words) > 0:
            keyword_density = ad_keyword_count / len(words)
            if keyword_density > 0.15:
                return True
        
        return False
    
    def extract_clean_content(self, url: str) -> str:
        """
        Enhanced content extraction with advertisement removal.
        
        Args:
            url: URL of the article to extract content from
            
        Returns:
            Clean HTML content with advertisements removed
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Remove advertisements first
            cleaned_html = self.remove_ads_from_html(response.text)
            
            # Parse the cleaned HTML
            soup = BeautifulSoup(cleaned_html, 'html.parser')
            
            # Try to identify the main content area
            content_selectors = [
                'article',
                '[role="main"]',
                '.content',
                '.post-content',
                '.entry-content',
                '.article-content',
                'main',
                '.story-body',
                '.article-body',
                '.post-body',
                '#content',
                '.article_text',
                '.story-content'
            ]
            
            main_content = None
            for selector in content_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if not main_content:
                # Fallback: find the largest content block
                content_blocks = soup.find_all(['div', 'article', 'section'])
                if content_blocks:
                    main_content = max(content_blocks, key=lambda x: len(x.get_text(strip=True)))
            
            if not main_content:
                # Final fallback: use body content
                main_content = soup.find('body') or soup
            
            # Clean the main content again (in case new ads were added after initial removal)
            final_content = self.remove_ads_from_html(str(main_content))
            
            return final_content
            
        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return f"<p>Error extracting content from {url}</p>"


class SportsNewsAggregator:
    """
    Enhanced Sports News Aggregator with advertisement removal.
    """
    
    def __init__(self, config_file='config.json'):
        self.config = self.load_config(config_file)
        self.posted_articles = self.load_posted_articles()
        self.ad_processor = AdRemovalProcessor()
        
    def load_config(self, config_file):
        """Load configuration from JSON file."""
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_posted_articles(self):
        """Load list of already posted articles."""
        try:
            with open('posted_articles.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_posted_articles(self):
        """Save list of posted articles."""
        with open('posted_articles.json', 'w', encoding='utf-8') as f:
            json.dump(self.posted_articles, f, indent=2)
    
    def get_article_hash(self, title, link):
        """Generate unique hash for article."""
        content = f"{title}-{link}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def fetch_rss_feeds(self):
        """Fetch and process RSS feeds from all sources."""
        print("Starting RSS feed processing...")
        
        total_articles = 0
        processed_articles = 0
        for source_name, feed_url in self.config['rss_feeds'].items():
            try:
                print(f"Processing {source_name}...")
                feed = feedparser.parse(feed_url)
                
                if feed.bozo:
                    print(f"Warning: {source_name} feed parsing issues")
                
                articles = feed.entries[:10]  # Get first 10 articles
                total_articles += len(articles)
                
                for article in articles:
                    try:
                        if self.process_article(article, source_name, feed_url):
                            processed_articles += 1
                            time.sleep(2)  # Rate limiting
                    except Exception as e:
                        print(f"Error processing article from {source_name}: {str(e)}")
                        continue
                
            except Exception as e:
                print(f"Error processing {source_name}: {str(e)}")
                continue
        
        print(f"Processed {processed_articles}/{total_articles} articles")
        return processed_articles
    
    def process_article(self, article, source_name, feed_url):
        """Process a single article and post to WordPress."""
        # Check if article was already posted
        article_hash = self.get_article_hash(article.title, article.link)
        if article_hash in self.posted_articles:
            print(f"Article already posted: {article.title[:50]}...")
            return False
        
        # Extract content with advertisement removal
        print(f"Extracting clean content from: {article.title[:50]}...")
        content_html = self.ad_processor.extract_clean_content(article.link)
        
        # Clean up HTML and ensure it's suitable for WordPress
        soup = BeautifulSoup(content_html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Add source attribution
        source_link = f'<p><strong>Read the full article at: <a href="{article.link}" target="_blank" rel="noopener noreferrer">{source_name}</a></strong></p>'
        content_html = str(soup) + source_link
        
        # Extract featured image
        image_url = self.extract_image_url(article)
        
        # Post to WordPress
        if self.post_to_wordpress(article.title, content_html, source_name, image_url):
            # Track posted article
            self.posted_articles.append(article_hash)
            self.save_posted_articles()
            print(f"Successfully posted: {article.title[:50]}...")
            return True
        
        return False
    
    def extract_image_url(self, article):
        """Extract featured image URL from article."""
        # Try to extract from content
        if hasattr(article, 'content') and article.content:
            soup = BeautifulSoup(article.content[0].value, 'html.parser')
            img = soup.find('img')
            if img and img.get('src'):
                return img.get('src')
        
        # Try media_content
        if hasattr(article, 'media_content') and article.media_content:
            return article.media_content[0]['url']
        
        # Try media_thumbnail
        if hasattr(article, 'media_thumbnail') and article.media_thumbnail:
            return article.media_thumbnail[0]['url']
        
        # Try links
        for link in article.links:
            if link.type and 'image' in link.type:
                return link.href
        
        return None
    
    def optimize_image(self, image_url):
        """Optimize image for web usage."""
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            img = Image.open(BytesIO(response.content))
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Resize if larger than 800px width
            max_width = 800
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Save optimized image
            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            return output
            
        except Exception as e:
            print(f"Error optimizing image {image_url}: {str(e)}")
            return None
    
    def upload_image_to_wordpress(self, image_url, title):
        """Upload optimized image to WordPress and return media ID."""
        if not image_url:
            return None
        
        optimized_image = self.optimize_image(image_url)
        if not optimized_image:
            return None
        
        try:
            media_url = f"{self.config['wordpress']['url']}/wp-json/wp/v2/media"
            
            headers = {
                'Authorization': f"Basic {self.config['wordpress']['app_password']}",
                'Content-Disposition': f'attachment; filename="{title[:50]}.jpg"'
            }
            
            response = requests.post(media_url, headers=headers, data=optimized_image)
            response.raise_for_status()
            
            return response.json()['id']
            
        except Exception as e:
            print(f"Error uploading image: {str(e)}")
            return None
    
    def post_to_wordpress(self, title, content, source_name, image_url=None):
        """Post article to WordPress."""
        try:
            wordpress_url = f"{self.config['wordpress']['url']}/wp-json/wp/v2/posts"
            
            # Upload image if available
            featured_media_id = None
            if image_url:
                featured_media_id = self.upload_image_to_wordpress(image_url, title)
            
            post_data = {
                'title': title,
                'content': content,
                'status': 'publish',
                'categories': [self.config['wordpress']['category_id']],
                'featured_media': featured_media_id
            }
            
            headers = {
                'Authorization': f"Basic {self.config['wordpress']['app_password']}",
                'Content-Type': 'application/json'
            }
            
            response = requests.post(wordpress_url, headers=headers, json=post_data)
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            print(f"Error posting to WordPress: {str(e)}")
            return False


def main():
    """Main execution function."""
    aggregator = SportsNewsAggregator()
    aggregator.fetch_rss_feeds()


if __name__ == "__main__":
    main()
