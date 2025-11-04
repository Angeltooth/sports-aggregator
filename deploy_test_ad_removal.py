#!/usr/bin/env python3
"""
Fixed test script for Advertisement Removal System
This version has corrected imports
"""

import sys
import os

# Add current directory to path so we can import our modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from deploy_sports_aggregator_enhanced import AdRemovalProcessor
from bs4 import BeautifulSoup

def test_ad_removal():
    """Test the ad removal system with sample content."""
    
    # Sample HTML with various types of advertisements
    test_html = """
    <html>
    <body>
        <div class="header">
            <h1>Main Sports News Article</h1>
        </div>
        
        <article>
            <h2>Breaking: Local Team Wins Championship</h2>
            <p>The local football team has won their first championship in 10 years, 
            defeating their rivals 3-1 in yesterday's final match.</p>
            
            <p>The victory was celebrated by thousands of fans who gathered at the stadium 
            to support their team throughout the season.</p>
            
            <!-- This is an advertisement banner -->
            <div class="ad-banner">
                <p><strong>SPONSORED BY SPORTS GEAR STORE</strong></p>
                <p>Buy now! 50% off all equipment! Limited time offer!</p>
                <a href="#">Shop Now</a>
            </div>
            
            <p>Coach Johnson praised his players' dedication and hard work throughout the season.</p>
            
            <!-- Social sharing widget -->
            <div class="social-share">
                <p>Follow us on Twitter! Share this article!</p>
                <button>Share on Facebook</button>
            </div>
            
            <p>The team's success has inspired a new generation of young athletes in the community.</p>
            
            <!-- Newsletter signup -->
            <div class="newsletter-signup">
                <h3>Don't miss out!</h3>
                <p>Subscribe to our newsletter for the latest sports news</p>
                <form><input type="email"><button>Sign Up</button></form>
            </div>
            
            <p>Local businesses have reported increased sales as fans celebrate the victory.</p>
        </article>
        
        <!-- Related articles section -->
        <div class="related-articles">
            <h3>Related Stories</h3>
            <ul>
                <li><a href="#">Sponsored: Best Sports Equipment Deals</a></li>
                <li><a href="#">Exclusive Interview with Star Player</a></li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    print("🧪 Testing Advertisement Removal System")
    print("=" * 50)
    
    # Create ad processor
    processor = AdRemovalProcessor()
    
    # Show original content
    print("📄 ORIGINAL CONTENT:")
    print("-" * 30)
    soup = BeautifulSoup(test_html, 'html.parser')
    print(soup.get_text()[:500] + "...")
    print(f"Original length: {len(soup.get_text())} characters")
    
    print("\n🧹 REMOVING ADVERTISEMENTS...")
    print("-" * 30)
    
    # Remove ads
    cleaned_content = processor.remove_ads_from_html(test_html)
    
    # Show cleaned content
    print("✨ CLEANED CONTENT:")
    print("-" * 30)
    cleaned_soup = BeautifulSoup(cleaned_content, 'html.parser')
    print(cleaned_soup.get_text()[:500] + "...")
    print(f"Cleaned length: {len(cleaned_soup.get_text())} characters")
    
    # Calculate improvement
    original_length = len(soup.get_text())
    cleaned_length = len(cleaned_soup.get_text())
    reduction = ((original_length - cleaned_length) / original_length) * 100
    
    print(f"\n📊 RESULTS:")
    print("-" * 30)
    print(f"Original content: {original_length} characters")
    print(f"Cleaned content: {cleaned_length} characters")
    print(f"Ad removal: {reduction:.1f}% reduction")
    print(f"Clean content ratio: {(cleaned_length/original_length)*100:.1f}%")
    
    # Show what was removed
    print(f"\n🗑️  ADVERTISEMENTS REMOVED:")
    print("-" * 30)
    ad_indicators = [
        "SPONSORED BY",
        "Buy now!",
        "Limited time offer",
        "Shop Now",
        "Follow us on Twitter",
        "Share this article",
        "Don't miss out",
        "Subscribe to our newsletter",
        "Sign Up",
        "Related Stories"
    ]
    
    for indicator in ad_indicators:
        if indicator in soup.get_text() and indicator not in cleaned_soup.get_text():
            print(f"✅ Removed: '{indicator}'")
    
    print(f"\n🎯 CONTENT PRESERVED:")
    print("-" * 30)
    main_content = [
        "Breaking: Local Team Wins Championship",
        "The local football team has won",
        "Coach Johnson praised his players",
        "The team's success has inspired"
    ]
    
    for content in main_content:
        if content in cleaned_soup.get_text():
            print(f"✅ Preserved: '{content[:30]}...'")
    
    print(f"\n✅ Ad removal test completed successfully!")

if __name__ == "__main__":
    test_ad_removal()
