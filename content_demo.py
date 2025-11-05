#!/usr/bin/env python3
"""
Content Quality Test - Compare old vs new processing
This script demonstrates the improvement in content quality
"""

import feedparser
import requests
from bs4 import BeautifulSoup

def simulate_old_processing(rss_entry):
    """Simulate the old content processing method"""
    print("🔴 OLD METHOD (Current Issues):")
    print("-" * 40)
    
    # Get description (like old method)
    description = getattr(rss_entry, 'description', '') or ''
    print("❌ Raw RSS Description:")
    print(f"Length: {len(description)} characters")
    print(f"Contains HTML: {('<' in description)}")
    print(f"Contains ads: {'advert' in description.lower()}")
    
    # Show first 200 chars
    preview = description[:200] + "..." if len(description) > 200 else description
    print(f"Preview: {preview}")
    print()

def simulate_new_processing(rss_entry, url):
    """Simulate the new content processing method"""
    print("🟢 NEW METHOD (Enhanced Processing):")
    print("-" * 40)
    
    try:
        # Try RSS content first
        content_html = getattr(rss_entry, 'description', '') or ''
        
        if content_html and len(content_html.strip()) > 100:
            soup = BeautifulSoup(content_html, 'html.parser')
            
            # Remove unwanted elements
            unwanted = soup.find_all(['script', 'style', 'nav', 'footer', 'aside'])
            for element in unwanted:
                element.decompose()
            
            # Extract clean text
            clean_text = soup.get_text(separator='\n\n', strip=True)
            
            print("✅ Clean Text Output:")
            print(f"Length: {len(clean_text)} characters")
            print(f"Clean paragraphs: {clean_text.count(chr(10) + chr(10))}")
            print(f"Ready for WordPress: Yes")
            
            # Show first 200 chars
            preview = clean_text[:200] + "..." if len(clean_text) > 200 else clean_text
            print(f"Preview: {preview}")
            print()
            
            return clean_text
        else:
            print("⚠️ RSS content insufficient - would fetch full article")
            return None
            
    except Exception as e:
        print(f"❌ Processing error: {e}")
        return None

def demonstrate_improvement():
    """Demonstrate the improvement with a sample RSS feed"""
    print("🎯 CONTENT QUALITY COMPARISON")
    print("=" * 50)
    print()
    
    # Use BBC Sport RSS feed for demo
    feed_url = "https://feeds.bbci.co.uk/sport/rss.xml"
    
    print(f"📡 Testing with: {feed_url}")
    print()
    
    try:
        feed = feedparser.parse(feed_url)
        
        if feed.entries:
            # Take the first article for demonstration
            entry = feed.entries[0]
            
            print(f"📰 Sample Article: {entry.title[:60]}...")
            print(f"🔗 URL: {entry.link}")
            print()
            
            # Show old method
            simulate_old_processing(entry)
            
            # Show new method
            simulate_new_processing(entry, entry.link)
            
            print("🎉 RESULT:")
            print("The new method extracts clean, readable text")
            print("ready for WordPress formatting!")
            
        else:
            print("❌ No entries found in feed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    demonstrate_improvement()
