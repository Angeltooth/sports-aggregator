import feedparser
import requests
import json
import time
import hashlib
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import os
from io import BytesIO
from PIL import Image

class SportsNewsAggregator:
    def __init__(self):
        """Initialize the aggregator with configuration"""
        self.posted_articles = set()
        self.config_file = 'config.json'
        self.load_config()
        self.load_posted_articles()
        self.auth = (self.wordpress['username'], self.wordpress['password'])
    
    def load_config(self):
        """Load configuration from config.json"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.wordpress = config['wordpress']
                self.rss_feeds = config['rss_feeds']
        except Exception as e:
            print(f"Error loading config: {e}")
            self.wordpress = {}
            self.rss_feeds = {}
    
    def load_posted_articles(self):
        """Load already posted articles from posted_articles.json"""
        try:
            if os.path.exists('posted_articles.json'):
                with open('posted_articles.json', 'r') as f:
                    self.posted_articles = set(json.load(f))
        except Exception as e:
            print(f"Error loading posted articles: {e}")
            self.posted_articles = set()
    
    def save_posted_articles(self):
        """Save posted articles to posted_articles.json"""
        try:
            with open('posted_articles.json', 'w') as f:
                json.dump(list(self.posted_articles), f)
        except Exception as e:
            print(f"Error saving posted articles: {e}")
    
    def fetch_rss_feeds(self):
        """Fetch articles from all RSS feeds"""
        new_articles = []
        
        print(f"Fetching from {len(self.rss_feeds)} feeds...")
        print("-" * 60)
        
        for source_name, feed_url in self.rss_feeds.items():
            try:
                print(f"Fetching from {source_name}...")
                feed = feedparser.parse(feed_url)
                
                if feed.bozo:
                    print(f"  ⚠️ Feed parsing issues for {source_name}")
                
                if not feed.entries:
                    print(f"  ❌ No entries found for {source_name}")
                    continue
                
                # Process only the first 10 articles per feed
                for entry in feed.entries[:10]:
                    article_data = {
                        'title': entry.get('title', '').strip(),
                        'link': entry.get('link', ''),
                        'summary': entry.get('summary', '').strip(),
                        'published': entry.get('published', ''),
                        'source': source_name,
                        'image_url': self.extract_image_url(entry)
                    }
                    
                    # Skip if we already posted this article
                    if article_data['link'] in self.posted_articles:
                        print(f"  ⏭️ Already posted: {article_data['title'][:50]}...")
                        continue
                    
                    # Extract full content
                    print(f"  📄 Processing: {article_data['title'][:50]}...")
                    article_data['content'] = self.extract_article_content(
                        article_data['link'], 
                        source_name
                    )
                    
                    if article_data['content']:
                        new_articles.append(article_data)
                        print(f"  ✅ Added: {article_data['title'][:50]}...")
                    else:
                        print(f"  ❌ Failed to extract content: {article_data['title'][:50]}...")
                
                print(f"  📊 Found {len(new_articles)} new articles from {source_name}")
                
            except Exception as e:
                print(f"  ❌ Error fetching {source_name}: {e}")
        
        return new_articles
    
    def extract_image_url(self, entry):
        """Extract image URL from RSS entry"""
        # Try media_content
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
            img = Image.open(BytesIO(image_data))
            
            # Convert RGBA to RGB
            if img.mode in ('RGBA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Resize to max 800px width
            max_width = 800
            if img.width > max_width:
                new_height = int((img.height * max_width) / img.width)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Save with 85% quality
            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            return output.getvalue()
        except Exception as e:
            print(f"Error optimizing image: {e}")
            return image_data
    
    def upload_image_to_wordpress(self, image_url, title):
        """Upload image to WordPress media library"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Download image
            img_response = requests.get(image_url, headers=headers, timeout=10)
            img_response.raise_for_status()
            
            # Optimize image
            optimized_data = self.optimize_image(img_response.content, image_url)
            
            # Prepare upload
            filename = f"{hashlib.md5(image_url.encode()).hexdigest()}.jpg"
            
            files = {
                'file': (filename, optimized_data, 'image/jpeg')
            }
            
            # Upload to WordPress
            upload_url = f"{self.wordpress['api_url']}/wp-json/wp/v2/media"
            
            response = requests.post(
                upload_url,
                files=files,
                auth=self.auth,
                headers={
                    'Content-Disposition': f'attachment; filename={filename}'
                }
            )
            
            if response.status_code == 201:
                return response.json()['id']
            
        except Exception as e:
            print(f"Error uploading image: {e}")
        
        return None
    
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
                return True, response.json().get('link', '')
            else:
                print(f"Error posting to WordPress: {response.status_code} - {response.text}")
                return False, None
                
        except Exception as e:
            print(f"Error posting to WordPress: {e}")
            return False, None
    
    def extract_article_content(self, link, source_name):
        """Extract full article content from the source website"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(link, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()
            
            # Try different selectors for article content
            article_selectors = [
                'article',
                '.article-content',
                '.post-content',
                '.entry-content',
                '.content',
                '.story-body'
            ]
            
            article_content = None
            for selector in article_selectors:
                article_element = soup.select_one(selector)
                if article_element:
                    article_content = article_element
                    break
            
            # If no specific article container found, try main content areas
            if not article_content:
                main_selectors = ['main', '.main', '#main', 'body']
                for selector in main_selectors:
                    main_element = soup.select_one(selector)
                    if main_element:
                        # Remove navigation, ads, etc. and keep substantial content
                        for unwanted in main_element.select('nav, header, footer, aside, .sidebar, .navigation, .ads, .advertisement'):
                            unwanted.decompose()
                        article_content = main_element
                        break
            
            if article_content:
                # Get text content and clean it
                text = article_content.get_text(separator='\n', strip=True)
                
                # Split into paragraphs and filter out short ones
                paragraphs = [p.strip() for p in text.split('\n') if p.strip() and len(p.strip()) > 50]
                
                if paragraphs:
                    # Format content with proper HTML
                    formatted_content = '\n\n'.join([f'<p>{p}</p>' for p in paragraphs[:10]])
                    return formatted_content
            
            print(f"Could not extract content from {source_name}")
            return None
            
        except Exception as e:
            print(f"Error extracting content from {link}: {e}")
            return None
    
    def process_articles(self, articles):
        """Process and post articles to WordPress"""
        total_posts = 0
        
        print(f"\nProcessing {len(articles)} new articles...")
        print("-" * 60)
        
        for i, article in enumerate(articles, 1):
            try:
                print(f"\n[{i}/{len(articles)}] Processing: {article['title'][:50]}...")
                
                # Handle featured image
                featured_image_id = None
                if article.get('image_url'):
                    print("  📷 Uploading featured image...")
                    featured_image_id = self.upload_image_to_wordpress(
                        article['image_url'], 
                        article['title']
                    )
                    if featured_image_id:
                        print("  ✅ Image uploaded successfully")
                    else:
                        print("  ⚠️ Image upload failed, posting without image")
                else:
                    print("  ⚠️ No featured image found")
                
                # Add source link to content
                source_link_html = f'\n\n<p><em>Read the full article at: <a href="{article["link"]}" target="_blank" rel="noopener">{article["source"]}</a></em></p>'
                content_with_source = article['content'] + source_link_html
                
                # Post to WordPress
                print("  📤 Posting to WordPress...")
                success, post_link = self.post_to_wordpress(
                    article['title'], 
                    content_with_source, 
                    featured_image_id
                )
                
                if success:
                    print("  ✅ Posted successfully!")
                    self.posted_articles.add(article['link'])
                    total_posts += 1
                    
                    if post_link:
                        print(f"  🔗 Post URL: {post_link}")
                else:
                    print("  ❌ Failed to post")
                
                # Add delay between posts
                time.sleep(2)
                
            except Exception as e:
                print(f"  ❌ Error processing article: {e}")
        
        return total_posts
    
    def run(self):
        """Run the news aggregation process"""
        print(f"{'='*60}")
        print(f"SPORTS NEWS AGGREGATOR")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # Fetch new articles
        articles = self.fetch_rss_feeds()
        
        if not articles:
            print("\nNo new articles found.")
            return
        
        print(f"\n📊 SUMMARY:")
        print(f"Total new articles: {len(articles)}")
        
        # Process articles
        total_posts = self.process_articles(articles)
        
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
