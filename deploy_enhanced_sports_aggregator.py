#!/usr/bin/env python3
"""
Enhanced Sports News Aggregator - ULTIMATE VERSION (UPDATED)
INTEGRATES: Advanced Content Processing + WordPress Professional Formatting

IMPROVEMENTS:
✅ Smart RSS content extraction (faster, more reliable)
✅ Advanced ad removal and content cleaning  
✅ Professional WordPress formatting (FIXES LAYOUT ISSUES)
✅ All existing authentication and safety fixes
✅ Enhanced text processing and formatting
✅ Better fallback handling

MAINTAINS ALL CURRENT WORKING FEATURES:
✅ HTTPBasicAuth authentication
✅ Safe RSS field access
✅ Image optimization and uploading
✅ Duplicate detection
✅ Rate limiting and delays
✅ Ultimate Content Processor
"""

import feedparser
import requests
from requests.auth import HTTPBasicAuth
import json
import hashlib
import time
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import re
from typing import List, Set, Optional, Dict, Any
from datetime import datetime


class UltimateContentProcessor:
    """
    Ultimate content processing with intelligent extraction and formatting
    Combines RSS content extraction with smart fallbacks
    """
    
    def __init__(self):
        # Enhanced ad selectors
        self.ad_selectors = [
            '[class*="ad"]', '[class*="advert"]', '[class*="sponsor"]',
            '[class*="related"]', '[class*="recommend"]', '[class*="sidebar"]',
            '[id*="ad"]', '[id*="advert"]', '[id*="sponsor"]',
            'script', 'style', 'nav', 'header', 'footer', 'aside',
            '[class*="nav"]', '[class*="header"]', '[class*="footer"]',
            '[class*="breadcrumb"]', '[class*="share"]', '[class*="social"]',
            '[class*="comment"]', '[class*="newsletter"]', '[class*="news-letter"]',
            '[class*="related-articles"]', '[class*="recommended"]'
        ]
        
        # Text cleaning patterns
        self.clean_patterns = {
            'whitespace': re.compile(r'\s+'),
            'smart_quotes': re.compile(r'["""]'),
            'dashes': re.compile(r'[–—]'),
            'multiple_newlines': re.compile(r'\n\s*\n\s*\n+')
        }
    
    def process_rss_content(self, rss_entry, source_name):
        """
        Enhanced RSS content processing with smart extraction
        
        Args:
            rss_entry: RSS feed entry object
            source_name: Name of the RSS source
            
        Returns:
            dict: Processed content with title, clean HTML, and metadata
        """
        try:
            # Extract basic info safely
            title = getattr(rss_entry, 'title', '') or ''
            url = getattr(rss_entry, 'link', '') or ''
            description = getattr(rss_entry, 'description', '') or ''
            
            # Try to get full content from RSS fields
            content_html = description
            
            # Check for full content in RSS
            if hasattr(rss_entry, 'content') and rss_entry.content:
                if isinstance(rss_entry.content, list) and len(rss_entry.content) > 0:
                    if isinstance(rss_entry.content[0], dict):
                        content_html = rss_entry.content[0].get('value', content_html)
                    else:
                        content_html = str(rss_entry.content[0])
                elif isinstance(rss_entry.content, str):
                    content_html = rss_entry.content
            
            # Check for custom fields
            if hasattr(rss_entry, 'fullcontent') and rss_entry.fullcontent:
                content_html = str(rss_entry.fullcontent)
            
            # If RSS content is good enough, process and return
            if content_html and len(content_html.strip()) > 100:
                processed_content = self._process_rss_html(content_html, url, title, source_name)
                if processed_content:
                    return processed_content
            
            # Fallback: Extract full article content
            print(f"   🔍 RSS content insufficient, extracting full article...")
            full_article_content = self._extract_full_article(url)
            if full_article_content:
                return {
                    'title': self._clean_title(title),
                    'content': full_article_content,
                    'url': url,
                    'source': source_name,
                    'extracted_at': datetime.now().isoformat()
                }
            
            # Final fallback: Use description with basic cleaning
            if description:
                clean_content = self._clean_text_only(description)
                return {
                    'title': self._clean_title(title) or 'Sports News Update',
                    'content': f'<p>{clean_content}</p>',
                    'url': url,
                    'source': source_name,
                    'extracted_at': datetime.now().isoformat()
                }
            
            return None
            
        except Exception as e:
            print(f"   ❌ Error processing RSS content: {str(e)}")
            return None
    
    def _process_rss_html(self, html_content, url, title, source_name):
        """Process HTML content from RSS"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unwanted elements
            self._remove_unwanted_elements(soup)
            
            # Extract text content
            text_content = soup.get_text(separator='\n\n', strip=True)
            
            if text_content and len(text_content.strip()) > 50:
                # Format as WordPress HTML
                formatted_html = self._format_for_wordpress(text_content, title, url, source_name)
                return {
                    'title': self._clean_title(title),
                    'content': formatted_html,
                    'url': url,
                    'source': source_name,
                    'extracted_at': datetime.now().isoformat()
                }
            
            return None
            
        except Exception as e:
            print(f"   ❌ Error processing RSS HTML: {str(e)}")
            return None
    
    def _extract_full_article(self, url):
        """Extract clean content from full article URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            self._remove_unwanted_elements(soup)
            
            # Try common article selectors
            article_selectors = [
                'article',
                '[role="main"]',
                '.content',
                '.article-content',
                '.post-content',
                '.entry-content',
                '.story-body',
                '.article-body',
                '#content',
                '.main-content',
                '.story-content'
            ]
            
            article_element = None
            for selector in article_selectors:
                article_element = soup.select_one(selector)
                if article_element and len(article_element.get_text(strip=True)) > 200:
                    break
            
            if article_element:
                text_content = article_element.get_text(separator='\n\n', strip=True)
            else:
                # Fallback: extract from body but exclude unwanted elements
                body = soup.find('body')
                if body:
                    # Remove common unwanted elements
                    for unwanted in body.find_all(['nav', 'header', 'footer', 'aside', '.sidebar']):
                        unwanted.decompose()
                    text_content = body.get_text(separator='\n\n', strip=True)
                else:
                    text_content = soup.get_text(separator='\n\n', strip=True)
            
            return text_content if text_content and len(text_content.strip()) > 100 else None
            
        except Exception as e:
            print(f"   ❌ Error extracting full article: {str(e)}")
            return None
    
    def _remove_unwanted_elements(self, soup):
        """Remove ads, navigation, and other unwanted elements"""
        # Remove script and style tags
        for tag in soup.find_all(['script', 'style']):
            tag.decompose()
        
        # Remove ad-related elements
        for selector in self.ad_selectors:
            for element in soup.select(selector):
                element.decompose()
        
        # Remove empty paragraphs and divs
        for element in soup.find_all(['p', 'div', 'span']):
            if element.get_text(strip=True) == '' and not element.find_all(['img', 'video', 'iframe']):
                element.decompose()
    
    def _format_for_wordpress(self, text_content, title, url, source_name):
        """Format clean text content for WordPress"""
        # Split into paragraphs and format
        paragraphs = []
        for paragraph in text_content.split('\n\n'):
            paragraph = paragraph.strip()
            if paragraph and len(paragraph) > 10:
                # Capitalize first letter if needed
                if paragraph and paragraph[0].islower():
                    paragraph = paragraph[0].upper() + paragraph[1:]
                paragraphs.append(f'<p>{paragraph}</p>')
        
        formatted_content = '\n\n'.join(paragraphs)
        
        # Add attribution
        formatted_content += f'\n\n<hr>\n<p><em>Originally published at: <a href="{url}" target="_blank" rel="noopener noreferrer">{source_name}</a></em></p>'
        
        return formatted_content
    
    def _clean_text_only(self, text):
        """Clean text without HTML"""
        # Replace smart quotes
        text = self.clean_patterns['smart_quotes'].sub('"', text)
        
        # Normalize dashes
        text = self.clean_patterns['dashes'].sub('-', text)
        
        # Remove excessive whitespace
        text = self.clean_patterns['whitespace'].sub(' ', text)
        text = self.clean_patterns['multiple_newlines'].sub('\n\n', text)
        
        return text.strip()
    
    def _clean_title(self, title):
        """Clean and format title"""
        if not title:
            return ''
        
        # Remove extra whitespace
        title = self.clean_patterns['whitespace'].sub(' ', title.strip())
        
        # Remove common prefixes/suffixes
        prefixes_to_remove = [
            r'^\s*(News|Update|Report|Breaking)\s*[-:|]\s*',
            r'^\s*Latest\s*[-:|]\s*',
            r'^\s*\[\w+\]\s*'  # Remove [sport] prefixes
        ]
        
        for pattern in prefixes_to_remove:
            title = re.sub(pattern, '', title, flags=re.IGNORECASE)
        
        return title.strip()


def validate_rss_entry(entry):
    """
    Validate RSS entry and return safe field access (EXISTING - KEEP UNCHANGED)
    """
    safe_entry = {
        'title': entry.get('title', 'No title available'),
        'link': entry.get('link') or entry.get('id', ''),
        'content': '',
        'summary': entry.get('summary', ''),
        'published': entry.get('published', ''),
        'author': entry.get('author', ''),
        'tags': []
    }
    
    if entry.get('content'):
        if isinstance(entry['content'], list) and len(entry['content']) > 0:
            if isinstance(entry['content'][0], dict):
                safe_entry['content'] = entry['content'][0].get('value', '')
            else:
                safe_entry['content'] = str(entry['content'][0])
        elif isinstance(entry['content'], str):
            safe_entry['content'] = entry['content']
    
    if entry.get('tags'):
        safe_entry['tags'] = [tag.get('term', '') for tag in entry['tags'] if hasattr(tag, 'term')]
    
    return safe_entry


def safe_extract_image_url(article):
    """
    Safely extract featured image URL from RSS article (EXISTING - KEEP UNCHANGED)
    """
    try:
        safe_article = validate_rss_entry(article)
        
        if safe_article['content']:
            soup = BeautifulSoup(safe_article['content'], 'html.parser')
            img = soup.find('img')
            if img and img.get('src'):
                return img.get('src')
        
        if hasattr(article, 'media_content') and article.media_content:
            return article.media_content[0]['url']
        
        if hasattr(article, 'media_thumbnail') and article.media_thumbnail:
            return article.media_thumbnail[0]['url']
        
        if hasattr(article, 'links') and article.links:
            for link in article.links:
                if hasattr(link, 'type') and link.type and 'image' in link.type:
                    if hasattr(link, 'href'):
                        return link.href
        
        return None
        
    except Exception as e:
        print(f"Error extracting image URL: {str(e)}")
        return None


class WordPressContentFormatter:
    """Professional WordPress content formatter to fix layout issues"""
    
    def __init__(self):
        self.max_paragraphs = 12
        self.min_paragraph_length = 30
        
    def format_content(self, content_html, title, url, source_name):
        """
        Format content professionally for WordPress display
        
        Args:
            content_html: Raw HTML content from processor
            title: Article title
            url: Source URL
            source_name: Source name
        
        Returns:
            Clean, professional HTML for WordPress
        """
        try:
            # If it's already clean HTML with paragraphs, process further
            if '<p>' in content_html:
                return self._enhance_existing_html(content_html, url, source_name)
            else:
                # Convert raw text to proper HTML
                return self._convert_text_to_html(content_html, url, source_name)
                
        except Exception as e:
            print(f"Error in WordPress formatting: {e}")
            return f"<p>Content from {source_name}</p><p><em>Read more: <a href='{url}' target='_blank' rel='noopener'>Original Article</a></em></p>"
    
    def _enhance_existing_html(self, html_content, url, source_name):
        """Enhance existing HTML to remove layout issues"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove empty paragraphs
            for p in soup.find_all('p'):
                text = p.get_text(strip=True)
                if not text or len(text) < 5:
                    p.decompose()
                else:
                    # Clean paragraph text
                    clean_text = self._clean_paragraph_text(text)
                    if clean_text:
                        p.string = clean_text
                    else:
                        p.decompose()
            
            # Get remaining paragraphs
            paragraphs = soup.find_all('p')
            
            # Limit and format paragraphs
            final_paragraphs = []
            for p in paragraphs[:self.max_paragraphs]:
                text = p.get_text(strip=True)
                if text and len(text) >= self.min_paragraph_length:
                    final_paragraphs.append(f"<p>{text}</p>")
            
            # Create final content
            content_html = '\n\n'.join(final_paragraphs)
            
            # Add clean source attribution
            content_html += f'\n\n<p><strong>Source:</strong> <a href="{url}" target="_blank" rel="noopener noreferrer">{source_name}</a></p>'
            
            return content_html
            
        except Exception as e:
            print(f"Error enhancing HTML: {e}")
            return f"<p>Content from {source_name}</p><p><em>Read more: <a href='{url}' target='_blank' rel='noopener'>Original Article</a></em></p>"
    
    def _convert_text_to_html(self, text_content, url, source_name):
        """Convert raw text to professional HTML"""
        try:
            # Split into paragraphs by double newlines or sentence patterns
            paragraphs = []
            
            # Clean the text
            text_content = self._clean_paragraph_text(text_content)
            
            # Split by double newlines first
            parts = text_content.split('\n\n')
            
            for part in parts:
                part = part.strip()
                if part and len(part) >= self.min_paragraph_length:
                    # Further split very long paragraphs
                    if len(part) > 500:
                        sentences = re.split(r'(?<=[.!?])\s+', part)
                        current_para = ""
                        
                        for sentence in sentences:
                            if len(current_para + sentence) < 400:
                                current_para += sentence + " "
                            else:
                                if current_para.strip():
                                    paragraphs.append(current_para.strip())
                                current_para = sentence + " "
                        
                        if current_para.strip():
                            paragraphs.append(current_para.strip())
                    else:
                        paragraphs.append(part)
            
            # Limit paragraphs
            limited_paragraphs = paragraphs[:self.max_paragraphs]
            
            # Format as HTML
            html_paragraphs = [f"<p>{para}</p>" for para in limited_paragraphs]
            content_html = '\n\n'.join(html_paragraphs)
            
            # Add source attribution
            content_html += f'\n\n<p><strong>Source:</strong> <a href="{url}" target="_blank" rel="noopener noreferrer">{source_name}</a></p>'
            
            return content_html
            
        except Exception as e:
            print(f"Error converting text to HTML: {e}")
            return f"<p>Content from {source_name}</p><p><em>Read more: <a href='{url}' target='_blank' rel='noopener'>Original Article</a></em></p>"
    
    def _clean_paragraph_text(self, text):
        """Clean paragraph text for WordPress"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix HTML entities
        text = text.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        
        # Remove any HTML tags (defensive)
        text = re.sub(r'<[^>]+>', '', text)
        
        # Clean special characters
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        text = text.replace('–', '-').replace('—', ' - ')
        
        # Remove promotional text
        promotional_patterns = [
            r'subscribe.*newsletter',
            r'sign.*up.*updates', 
            r'limited.*time.*offer',
            r'discount.*code',
            r'shop.*now',
            r'buy.*now',
            r'limited.*edition',
            r'while.*supplies.*last'
        ]
        
        for pattern in promotional_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return ""  # Skip promotional content
        
        return text.strip()


def get_optimized_image_quality(source_name):
    """
    Get optimal image quality settings based on source
    Returns quality settings for different news sources
    """
    # Higher quality for BBC Sport and professional sports outlets
    if 'bbc' in source_name.lower():
        return {
            'quality': 95,  # Much higher quality for BBC
            'optimize': False,  # Disable optimization for BBC
            'max_width': 1400,  # Allow larger images for BBC
            'progressive': True  # Progressive JPEG
        }
    elif any(source in source_name.lower() for source in ['sky', 'guardian', 'yahoo']):
        return {
            'quality': 92,  # High quality for premium sources
            'optimize': False,
            'max_width': 1300,
            'progressive': True
        }
    else:
        # Standard quality for other sources
        return {
            'quality': 88,  # Still higher than current 85
            'optimize': True,
            'max_width': 1200,
            'progressive': False
        }


def format_wordpress_content_professional(content_html, title, url, source_name):
    """
    Professional WordPress content formatting
    
    Args:
        content_html: Raw content from ultimate processor
        title: Article title
        url: Source URL
        source_name: Source name
    
    Returns:
        Clean, professional HTML for WordPress
    """
    formatter = WordPressContentFormatter()
    return formatter.format_content(content_html, title, url, source_name)


class UltimateSportsAggregator:
    def __init__(self, config_file='config.json'):
        """Initialize the Ultimate Sports News Aggregator."""
        self.config = self.load_config(config_file)
        self.content_processor = UltimateContentProcessor()  # Ultimate processor
        self.posted_articles = self.load_posted_articles()
    
    def load_config(self, config_file):
        """Load configuration from JSON file (EXISTING - KEEP UNCHANGED)."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Config file {config_file} not found!")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {config_file}: {e}")
            return {}
    
    def load_posted_articles(self):
        """Load list of previously posted articles (EXISTING - KEEP UNCHANGED)."""
        try:
            with open('posted_articles.json', 'r') as f:
                return set(json.load(f))
        except FileNotFoundError:
            return set()
    
    def save_posted_articles(self):
        """Save list of posted articles (EXISTING - KEEP UNCHANGED)."""
        with open('posted_articles.json', 'w') as f:
            json.dump(list(self.posted_articles), f)
    
    def get_article_hash(self, title, url):
        """Generate a unique hash for an article (EXISTING - KEEP UNCHANGED)."""
        content = f"{title}{url}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def optimize_image(self, image_url, source_name="Unknown"):
        """Download and optimize image with improved quality settings for WordPress."""
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            image = Image.open(BytesIO(response.content))
            
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                image = background
            
            # Get quality settings based on source
            quality_settings = get_optimized_image_quality(source_name)
            max_width = quality_settings['max_width']
            
            # Resize only if needed
            if image.width > max_width:
                ratio = max_width / image.width
                new_height = int(image.height * ratio)
                image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            output = BytesIO()
            
            # Save with improved settings
            save_kwargs = {
                'format': 'JPEG',
                'quality': quality_settings['quality'],
                'optimize': quality_settings['optimize']
            }
            
            # Add progressive setting if available
            if quality_settings.get('progressive'):
                save_kwargs['progressive'] = True
                
            image.save(output, **save_kwargs)
            output.seek(0)
            
            print(f"   🖼️  Optimized image: {max_width}px width, Q{quality_settings['quality']}")
            return output.getvalue()
            
        except Exception as e:
            print(f"Error optimizing image: {str(e)}")
            return None
    
    def upload_image_to_wordpress(self, image_url, title, source_name="Unknown"):
        """Upload optimized image to WordPress (FIXED VERSION)."""
        if not image_url:
            return None
        
        optimized_image = self.optimize_image(image_url, source_name)
        if not optimized_image:
            return None
        
        try:
            media_url = f"{self.config['wordpress']['url']}/wp-json/wp/v2/media"
            
            username = self.config['wordpress']['username']
            app_password = self.config['wordpress']['app_password']
            auth = HTTPBasicAuth(username, app_password)
            
            # Fixed headers - WordPress needs Content-Type for images
            headers = {
                'Content-Type': 'image/jpeg',  # Added proper content type
                'Content-Disposition': f'attachment; filename="{title[:30].replace("/", "_").replace(":", "_")}.jpg"'
            }
            
            response = requests.post(
                media_url, 
                headers=headers, 
                data=optimized_image,
                auth=auth
            )
            
            if response.status_code == 400:
                print(f"Image upload attempt failed (400). Trying alternative method...")
                # Alternative method using multipart form data
                files = {
                    'file': (f"{title[:30].replace('/', '_').replace(':', '_')}.jpg", 
                            optimized_image, 'image/jpeg')
                }
                data = {'title': title[:50]}
                
                response = requests.post(
                    media_url,
                    files=files,
                    data=data,
                    auth=auth
                )
            
            response.raise_for_status()
            return response.json()['id']
            
        except Exception as e:
            print(f"Error uploading image: {str(e)}")
            return None
    
    def post_to_wordpress(self, title, content, source_name, image_url=None):
        """Post article to WordPress (EXISTING - KEEP UNCHANGED)."""
        try:
            wordpress_url = f"{self.config['wordpress']['url']}/wp-json/wp/v2/posts"
            
            # Upload image if available
            featured_media_id = None
            if image_url:
                featured_media_id = self.upload_image_to_wordpress(image_url, title, source_name)
            
            post_data = {
                'title': title,
                'content': content,  # Now clean HTML from content processor + formatter
                'status': 'publish',
                'categories': [self.config['wordpress']['category_id']],
                'featured_media': featured_media_id
            }
            
            username = self.config['wordpress']['username']
            app_password = self.config['wordpress']['app_password']
            auth = HTTPBasicAuth(username, app_password)
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                wordpress_url, 
                headers=headers, 
                json=post_data, 
                auth=auth
            )
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            print(f"Error posting to WordPress: {str(e)}")
            return False
    
    def process_article(self, article, source_name, feed_url):
        """Process a single article with enhanced content extraction and professional formatting."""
        try:
            # Use safe article field access
            safe_article = validate_rss_entry(article)
            
            # Check if URL exists
            if not safe_article['link']:
                print(f"   ⏭️  Skipping article with no valid URL from {source_name}")
                return False
            
            # Check if article was already posted
            article_hash = self.get_article_hash(safe_article['title'], safe_article['link'])
            if article_hash in self.posted_articles:
                print(f"   ⏭️  Article already posted: {safe_article['title'][:50]}...")
                return False
            
            print(f"   🔄 Processing: {safe_article['title'][:50]}...")
            
            # NEW: Use ultimate content processor
            processed_content = self.content_processor.process_rss_content(article, source_name)
            
            if not processed_content:
                print(f"   ❌ Failed to extract content from {safe_article['title'][:50]}...")
                return False
            
            print(f"   ✨ Applying professional WordPress formatting...")
            
            # NEW: Apply professional WordPress formatting
            final_content = format_wordpress_content_professional(
                processed_content['content'],
                processed_content['title'],
                processed_content['url'],
                source_name
            )
            
            # Extract featured image
            image_url = safe_extract_image_url(article)
            
            # Post to WordPress
            print(f"   📤 Posting to WordPress...")
            success = self.post_to_wordpress(
                processed_content['title'], 
                final_content,  # Use professionally formatted content
                source_name, 
                image_url
            )
            
            if success:
                print(f"   ✅ Successfully posted: {processed_content['title'][:50]}...")
                self.posted_articles.add(article_hash)
                return True
            else:
                print(f"   ❌ Failed to post: {processed_content['title'][:50]}...")
                return False
                
        except Exception as e:
            print(f"   ❌ Error processing article: {str(e)}")
            return False
    
    def process_rss_feed(self, source_name, feed_url):
        """Process RSS feed and post articles to WordPress (EXISTING - KEEP UNCHANGED)."""
        try:
            print(f"\n📡 Processing {source_name}...")
            feed = feedparser.parse(feed_url)
            
            if not feed.entries:
                print(f"   ⚠️  No entries found in {source_name}")
                return 0
            
            processed_articles = 0
            max_articles = self.config.get('settings', {}).get('articles_per_feed', 10)
            
            for entry in feed.entries[:max_articles]:
                if self.process_article(entry, source_name, feed_url):
                    processed_articles += 1
                    # Add delay between posts
                    delay = self.config.get('settings', {}).get('delay_between_posts', 2)
                    time.sleep(delay)
                
                # Check if we've reached daily limits
                if processed_articles >= max_articles:
                    break
            
            print(f"   ✅ Processed {processed_articles} articles from {source_name}")
            return processed_articles
            
        except Exception as e:
            print(f"   ❌ Error processing {source_name}: {str(e)}")
            return 0
    
    def run(self):
        """Main execution method with enhanced processing."""
        print("🚀 Ultimate Sports News Aggregator Starting...")
        print("📰 Using Advanced Content Processing + Professional WordPress Formatting...")
        print(f"🕐 Processing time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if not self.config:
            print("❌ No configuration loaded. Exiting.")
            return
        
        total_processed = 0
        total_feeds = len(self.config['rss_feeds'])
        
        for source_name, feed_url in self.config['rss_feeds'].items():
            try:
                processed = self.process_rss_feed(source_name, feed_url)
                total_processed += processed
                
                # Add delay between feeds
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error processing {source_name}: {str(e)}")
                continue
        
        # Save posted articles
        self.save_posted_articles()
        
        print(f"\n🏁 Ultimate Aggregation Complete!")
        print(f"📊 Summary:")
        print(f"   📡 Total feeds processed: {total_feeds}")
        print(f"   📰 Total articles posted: {total_processed}")
        print(f"   🗃️  Database updated: posted_articles.json")
        print(f"   ✨ Enhanced content processing active")
        print(f"   🎯 Professional WordPress formatting active")


def main():
    """Main entry point."""
    try:
        aggregator = UltimateSportsAggregator()
        aggregator.run()
    except KeyboardInterrupt:
        print("\n🛑 Process interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
