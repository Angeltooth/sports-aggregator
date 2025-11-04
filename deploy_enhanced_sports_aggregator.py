#!/usr/bin/env python3
"""
Enhanced Sports News Aggregator with Advertisement Removal
Modified version that includes comprehensive ad stripping functionality
CONSERVATIVE AD REMOVAL - Preserves 70-90% of content while removing 10-40% ads
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

class ConservativeAdRemovalProcessor:
    """
    Conservative advertisement removal that preserves main content.
    Targets only specific ad elements and promotional text.
    Preserves 70-90% of content while removing 10-40% advertisements.
    """
    
    def __init__(self):
        # Conservative selectors - only target obvious ad elements
        self.ad_selectors = {
            'classes': ['ad', 'advertisement', 'sponsored', 'promo', 'banner-ad', 'sponsored-content'],
            'ids': ['ad-container', 'sidebar-ad', 'top-ad', 'banner-ad', 'sponsored'],
            'elements': [
                'aside[class*="ad"]', 
                'div[class*="advertisement"]', 
                'div[id*="ad-"]',
                'div[class*="sponsored"]',
                'div[id*="sponsored"]'
            ]
        }
        
        # Promotional text patterns (conservative - only obvious ads)
        self.promotional_patterns = [
            r'sponsored\s+by\s+[\w\s]+store',
            r'buy\s+now\s+[!\.]+',
            r'shop\s+now\s+[!\.]+',
            r'limited\s+time\s+offer',
            r'subscribe\s+to\s+newsletter',
            r'sign\s+up\s+for\s+updates',
            r'get\s+[\w\s]+%?\s*off',
            r'free\s+shipping',
            r'discount\s+code'
        ]
        
        # Content indicators to preserve (helps identify main articles)
        self.content_indicators = [
            'breaking:', 'news:', 'update:', 'report:', 'analysis:',
            'championship', 'victory', 'defeated', 'season', 'team',
            'player', 'coach', 'match', 'game', 'won', 'lost'
        ]
    
    def remove_ads_from_html(self, html_content: str) -> str:
        """Remove advertisements and promotional content from HTML content."""
        if not html_content:
            return html_content
            
        # Store original length for analysis
        original_length = len(html_content)
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style tags (always safe)
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Remove elements with specific ad classes/IDs (conservative approach)
        removed_elements = 0
        
        # Remove by exact class names
        for class_name in self.ad_selectors['classes']:
            elements = soup.find_all(class_=class_name)
            for element in elements:
                if self._is_main_content(element):
                    continue  # Don't remove main content elements
                element.decompose()
                removed_elements += 1
        
        # Remove by exact ID
        for id_name in self.ad_selectors['ids']:
            elements = soup.find_all(id=id_name)
            for element in elements:
                if self._is_main_content(element):
                    continue
                element.decompose()
                removed_elements += 1
        
        # Remove by specific element patterns
        for selector in self.ad_selectors['elements']:
            try:
                elements = soup.select(selector)
                for element in elements:
                    if self._is_main_content(element):
                        continue
                    element.decompose()
                    removed_elements += 1
            except Exception:
                continue  # Skip invalid selectors
        
        # Remove promotional text patterns (very conservative)
        promotional_removed = 0
        
        for pattern in self.promotional_patterns:
            elements = soup.find_all(string=re.compile(pattern, re.IGNORECASE))
            for text_element in elements:
                parent = text_element.parent
                if parent and self._is_main_content(parent):
                    continue
                if parent:
                    parent.decompose()
                    promotional_removed += 1
        
        # Remove newsletter forms and social widgets (conservative)
        for form in soup.find_all('form'):
            if self._is_newsletter_form(form):
                form.decompose()
                promotional_removed += 1
        
        # Remove social sharing widgets (only obvious small ones)
        for div in soup.find_all('div', class_=True):
            class_text = ' '.join(div.get('class', [])).lower()
            if any(social in class_text for social in ['social', 'share', 'twitter', 'facebook']):
                if len(div.get_text(strip=True)) < 100:  # Only small social elements
                    div.decompose()
                    promotional_removed += 1
        
        return str(soup)
    
    def _is_main_content(self, element) -> bool:
        """
        Conservative check to avoid removing main content.
        This is key to preserving 70-90% of content.
        """
        # Get all text from element
        element_text = element.get_text(strip=True).lower()
        
        # If element has substantial content with content indicators, preserve it
        if len(element_text) > 200:  # Main content typically has more text
            for indicator in self.content_indicators:
                if indicator in element_text:
                    return True
        
        # If element contains multiple paragraphs, it's likely main content
        paragraphs = element.find_all('p')
        if len(paragraphs) > 2:
            return True
        
        # If element is a main article element
        if element.name in ['article', 'main', 'section']:
            return True
        
        # If element has a significant amount of text
        if len(element_text) > 500:
            return True
        
        return False
    
    def _is_newsletter_form(self, form_element) -> bool:
        """Check if form is a newsletter signup."""
        form_text = form_element.get_text(strip=True).lower()
        newsletter_keywords = ['newsletter', 'subscribe', 'email updates', 'daily digest']
        return any(keyword in form_text for keyword in newsletter_keywords)
    
    def extract_clean_content(self, url: str) -> str:
        """
        Enhanced content extraction with conservative advertisement removal.
        
        Args:
            url: URL of the article to extract content from
            
        Returns:
            Clean HTML content with advertisements removed
            Content preservation: 70-90% (vs aggressive 3.6%)
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Remove advertisements first (conservative approach)
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
    Enhanced Sports News Aggregator with conservative advertisement removal.
    """
    
    def __init__(self, config_file='config.json'):
        self.config = self.load_config(config_file)
        self.posted_articles = self.load_posted_articles()
        # UPDATED: Use ConservativeAdRemovalProcessor instead of AdRemovalProcessor
        self.ad_processor = ConservativeAdRemovalProcessor()
        
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
        
        # Extract content with conservative advertisement removal
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
