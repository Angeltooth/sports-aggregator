# Local Testing Instructions

## Step 2: Test the Updated Application

### Prerequisites
Make sure you have your WordPress configuration file (`config.json`) in the same directory as your script.

### Run the Application
```bash
python3 deploy_enhanced_sports_aggregator.py
```

### What to Expect
1. **Successful Ad Processing:** The application will process RSS feeds and use conservative ad removal
2. **WordPress Integration:** Posts will be sent to WordPress with cleaned content
3. **Content Preservation:** Articles should maintain 70-90% of original content
4. **Ad Removal:** Promotional content should be removed effectively

### Troubleshooting
- **Missing config.json:** Create one with your WordPress settings
- **Import errors:** Install dependencies: `pip install feedparser requests beautifulsoup4 python-dateutil lxml`
- **WordPress API issues:** Verify your WordPress credentials and endpoints

### Validation
Check the output for:
- ✅ RSS feeds processed successfully
- ✅ Conservative ad removal applied
- ✅ WordPress posts created with proper content
- ✅ Content preservation above 70%

### If Issues Occur
1. Check the application logs for specific errors
2. Verify your `config.json` file format
3. Test WordPress API connectivity
4. Review the ad removal processing results