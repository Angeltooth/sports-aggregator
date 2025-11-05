#!/usr/bin/env python3
"""
Quick test script for the Ultimate Sports Aggregator
Tests basic functionality and content processing improvements
"""

import sys
import os

def test_imports():
    """Test if all required imports work"""
    print("🔍 Testing imports...")
    try:
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
        from datetime import datetime
        print("   ✅ All imports successful")
        return True
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False

def test_aggregator_initialization():
    """Test if aggregator initializes properly"""
    print("\n🔍 Testing aggregator initialization...")
    try:
        from deploy_enhanced_sports_aggregator import UltimateSportsAggregator
        
        aggregator = UltimateSportsAggregator()
        print(f"   ✅ Aggregator initialized successfully")
        print(f"   ✅ Config loaded: {bool(aggregator.config)}")
        print(f"   ✅ Content processor active: {bool(aggregator.content_processor)}")
        return True
    except Exception as e:
        print(f"   ❌ Initialization error: {e}")
        return False

def test_config_file():
    """Test if config file exists and is valid"""
    print("\n🔍 Testing config file...")
    config_file = 'config.json'
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            has_rss_feeds = 'rss_feeds' in config
            has_wordpress = 'wordpress' in config
            
            print(f"   ✅ Config file exists: {config_file}")
            print(f"   ✅ RSS feeds configured: {has_rss_feeds}")
            print(f"   ✅ WordPress configured: {has_wordpress}")
            
            if has_rss_feeds:
                feed_count = len(config['rss_feeds'])
                print(f"   📡 RSS feeds count: {feed_count}")
                for name, url in list(config['rss_feeds'].items())[:3]:  # Show first 3
                    print(f"      - {name}: {url}")
            
            return True
        except Exception as e:
            print(f"   ❌ Config error: {e}")
            return False
    else:
        print(f"   ❌ Config file not found: {config_file}")
        return False

def test_wordpress_credentials():
    """Test if WordPress credentials are present"""
    print("\n🔍 Testing WordPress credentials...")
    try:
        from deploy_enhanced_sports_aggregator import UltimateSportsAggregator
        
        aggregator = UltimateSportsAggregator()
        if aggregator.config and 'wordpress' in aggregator.config:
            wp_config = aggregator.config['wordpress']
            
            has_url = 'url' in wp_config
            has_username = 'username' in wp_config
            has_password = 'app_password' in wp_config
            has_category = 'category_id' in wp_config
            
            print(f"   ✅ WordPress URL: {has_url}")
            print(f"   ✅ Username: {has_username}")
            print(f"   ✅ App password: {has_password}")
            print(f"   ✅ Category ID: {has_category}")
            
            if has_url:
                print(f"   🌐 WordPress URL: {wp_config['url']}")
            
            return has_url and has_username and has_password and has_category
        else:
            print("   ❌ WordPress config not found")
            return False
    except Exception as e:
        print(f"   ❌ WordPress test error: {e}")
        return False

def test_database_file():
    """Test posted articles database"""
    print("\n🔍 Testing database file...")
    db_file = 'posted_articles.json'
    
    if os.path.exists(db_file):
        try:
            with open(db_file, 'r') as f:
                articles = json.load(f)
            print(f"   ✅ Database exists: {db_file}")
            print(f"   📊 Posted articles: {len(articles)}")
            return True
        except Exception as e:
            print(f"   ❌ Database error: {e}")
            return False
    else:
        print(f"   ⚠️  Database not found (will be created): {db_file}")
        return True

def test_virtual_environment():
    """Test if we're in the correct virtual environment"""
    print("\n🔍 Testing virtual environment...")
    import sys
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("   ✅ Virtual environment detected")
        python_path = sys.executable
        print(f"   🐍 Python path: {python_path}")
    else:
        print("   ⚠️  Not in virtual environment")
    
    return True

def main():
    """Run all tests"""
    print("🚀 ULTIMATE SPORTS AGGREGATOR - COMPREHENSIVE TEST")
    print("="*60)
    
    tests = [
        test_imports,
        test_aggregator_initialization,
        test_config_file,
        test_wordpress_credentials,
        test_database_file,
        test_virtual_environment
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "="*60)
    print(f"📊 TEST SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Ready to run!")
        print("\n🚀 To test the aggregator:")
        print("   python deploy_enhanced_sports_aggregator.py")
        print("\n💡 For a quick test with just one feed:")
        print("   python deploy_enhanced_sports_aggregator.py config_test.json")
    else:
        print("❌ Some tests failed - please check the errors above")
        return False
    
    return True

if __name__ == "__main__":
    main()
