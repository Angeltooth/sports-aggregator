#!/usr/bin/env python3
"""
Simple test to debug feeds loading issue
"""
import json

print("Testing feeds file loading...")

# Test 1: Try to load the current feeds file
try:
    with open('basic_rss_feeds.json', 'r', encoding='utf-8') as f:
        feeds = json.load(f)
    print(f"✓ Loaded {len(feeds)} feeds successfully")
    print("Sample feed structure:", feeds[0] if feeds else "No feeds found")
except Exception as e:
    print(f"✗ Error loading basic_rss_feeds.json: {e}")

# Test 2: Try to load test feeds
try:
    with open('test_feeds.json', 'r', encoding='utf-8') as f:
        feeds = json.load(f)
    print(f"✓ Loaded test feeds successfully: {len(feeds)} feeds")
except Exception as e:
    print(f"✗ Error loading test_feeds.json: {e}")

# Test 3: Check if feeds is a list
try:
    with open('test_feeds.json', 'r', encoding='utf-8') as f:
        feeds = json.load(f)
    if isinstance(feeds, list):
        print("✓ Feeds is a list")
        if feeds:
            print(f"  First feed: {feeds[0]}")
            print(f"  Feed type: {type(feeds[0])}")
    else:
        print(f"✗ Feeds is not a list, it's: {type(feeds)}")
except Exception as e:
    print(f"✗ Error in type check: {e}")
