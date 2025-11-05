#!/usr/bin/env python3
"""
Conservative Ad Removal System
This version is much more selective to preserve main content
"""

from bs4 import BeautifulSoup
import re

class ConservativeAdRemovalProcessor:
    """
    Conservative advertisement removal system that preserves main content.
    """
    
    def __init__(self):
        # Very specific ad selectors only - no broad matches
        self.ad_selectors = [
            # Exact ad classes and IDs
            '.ad', '.ads', '.ad-banner', '.ad-container', '.advertisement',
            '.sponsored', '.sponsored-post', '.promo', '.promotion',
            '#ad', '#ads', '#advertisement', '#sponsored',
            # Newsletter forms
            '.newsletter-signup', '.newsletter-form', '.subscribe-form',
            # Social sharing widgets
            '.social-share', '.social-sharing', '.share-buttons'
        ]
        
        # Very specific ad text patterns (not broad keywords)
        self.ad_patterns = [
            r'sponsored\s+by\s+\w+',
            r'buy\s+now\s+\w+',
            r'shop\s+now',
            r'sign\s+up\s+now',
            r'subscribe\s+to\s+our\s+newsletter',
            r'special\s+offer\s+limited\s+time',
            r'while\s+supplies\s+last',
            r'click\s+here\s+to\s+\w+'
        ]
    
    def remove_ads_from_html(self, html_content: str) -> str:
        """Remove only specific advertisement elements, preserve main content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Step 1: Remove exact ad elements by CSS selector
        for selector in self.ad_selectors:
            elements = soup.select(selector)
            for element in elements:
                # Only remove if it's clearly an ad element
                if self._is_specific_ad_element(element):
                    element.decompose()
        
        # Step 2: Remove elements with specific ad text patterns
        for pattern in self.ad_patterns:
            # Find text that matches ad patterns
            text_elements = soup.find_all(text=re.compile(pattern, re.IGNORECASE))
            for text_element in text_elements:
                parent = text_element.parent
                if parent and self._is_specific_ad_element(parent):
                    parent.decompose()
        
        return str(soup)
    
    def _is_specific_ad_element(self, element) -> bool:
        """Check if element is specifically an ad element, not just contains ad keywords."""
        element_text = element.get_text(strip=True).lower()
        
        # Check if element has specific ad patterns
        for pattern in self.ad_patterns:
            if re.search(pattern, element_text, re.IGNORECASE):
                return True
        
        # Check for very specific ad indicators
        ad_indicators = [
            'sponsored by', 'buy now', 'shop now', 'sign up now',
            'subscribe to our newsletter', 'special offer', 'limited time'
        ]
        
        for indicator in ad_indicators:
            if indicator in element_text:
                return True
        
        # Only remove if element has explicit ad class/ID and contains promotional text
        if element.get('class') or element.get('id'):
            classes = ' '.join(element.get('class', [])).lower()
            element_id = element.get('id', '').lower()
            
            ad_terms = ['ad', 'advertisement', 'sponsored', 'promo']
            has_ad_class = any(term in classes for term in ad_terms)
            has_ad_id = any(term in element_id for term in ad_terms)
            
            if has_ad_class or has_ad_id:
                # Only remove if it also contains promotional language
                promo_words = ['buy', 'shop', 'subscribe', 'sign up', 'offer', 'deal', 'discount']
                if any(word in element_text for word in promo_words):
                    return True
        
        return False

def test_conservative_ad_removal():
    """Test the conservative ad removal system."""
    
    # Sample HTML with ads and main content
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
    </body>
    </html>
    """
    
    print("🧪 Testing Conservative Advertisement Removal")
    print("=" * 50)
    
    # Create processor
    processor = ConservativeAdRemovalProcessor()
    
    # Show original content
    print("📄 ORIGINAL CONTENT:")
    print("-" * 30)
    soup = BeautifulSoup(test_html, 'html.parser')
    original_text = soup.get_text()[:500] + "..."
    print(original_text)
    original_length = len(soup.get_text())
    print(f"Original length: {original_length} characters")
    
    print("\n🧹 REMOVING ADVERTISEMENTS...")
    print("-" * 30)
    
    # Remove ads
    cleaned_content = processor.remove_ads_from_html(test_html)
    
    # Show cleaned content
    print("✨ CLEANED CONTENT:")
    print("-" * 30)
    cleaned_soup = BeautifulSoup(cleaned_content, 'html.parser')
    cleaned_text = cleaned_soup.get_text()[:500] + "..."
    print(cleaned_text)
    cleaned_length = len(cleaned_soup.get_text())
    print(f"Cleaned length: {cleaned_length} characters")
    
    # Calculate improvement
    reduction = ((original_length - cleaned_length) / original_length) * 100
    
    print(f"\n📊 RESULTS:")
    print("-" * 30)
    print(f"Original content: {original_length} characters")
    print(f"Cleaned content: {cleaned_length} characters")
    print(f"Ad removal: {reduction:.1f}% reduction")
    print(f"Content preserved: {((cleaned_length/original_length)*100):.1f}%")
    
    # Show what was removed
    print(f"\n🗑️  ADVERTISEMENTS REMOVED:")
    print("-" * 30)
    
    # Check specific ad content that should be removed
    ad_content_removed = []
    if "SPONSORED BY SPORTS GEAR STORE" not in cleaned_text:
        ad_content_removed.append("SPONSORED BY SPORTS GEAR STORE")
    if "Buy now! 50% off" not in cleaned_text:
        ad_content_removed.append("Buy now! 50% off")
    if "Shop Now" not in cleaned_text:
        ad_content_removed.append("Shop Now")
    if "Follow us on Twitter!" not in cleaned_text:
        ad_content_removed.append("Social sharing widget")
    if "Subscribe to our newsletter" not in cleaned_text:
        ad_content_removed.append("Newsletter signup")
    
    for content in ad_content_removed:
        print(f"✅ Removed: '{content}'")
    
    print(f"\n🎯 CONTENT PRESERVED:")
    print("-" * 30)
    
    # Check main content that should be preserved
    main_content_preserved = []
    content_to_check = [
        "Breaking: Local Team Wins Championship",
        "The local football team has won",
        "Coach Johnson praised his players",
        "The team's success has inspired"
    ]
    
    for content in content_to_check:
        if content in cleaned_text:
            main_content_preserved.append(content)
            print(f"✅ Preserved: '{content[:30]}...'")
    
    print(f"\n📈 TEST SUMMARY:")
    print("-" * 30)
    print(f"Ad content removed: {len(ad_content_removed)}")
    print(f"Main content preserved: {len(main_content_preserved)}/{len(content_to_check)}")
    print(f"Content preservation: {((len(main_content_preserved)/len(content_to_check))*100):.0f}%")
    
    # Good results should show:
    # - 10-30% ad removal (not 90%+)
    # - 90-100% content preservation 
    # - Main article text intact
    if 10 <= reduction <= 40 and len(main_content_preserved) >= 3:
        print(f"\n✅ Conservative ad removal working correctly!")
        print("Ads removed while preserving main content.")
    else:
        print(f"\n⚠️  Ad removal may need adjustment")
        print(f"Current: {reduction:.1f}% reduction, {len(main_content_preserved)}/{len(content_to_check)} content preserved")

if __name__ == "__main__":
    test_conservative_ad_removal()