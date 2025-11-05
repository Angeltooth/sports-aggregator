#!/usr/bin/env python3
"""
File Version Checker
Helps identify which version of deploy_enhanced_sports_aggregator.py is being run
"""

import os
import hashlib
from datetime import datetime

def check_file_version(file_path):
    """Check file version and details"""
    if not os.path.exists(file_path):
        return f"❌ File not found: {file_path}"
    
    # Get file stats
    stat = os.stat(file_path)
    file_size = stat.st_size
    modified_time = datetime.fromtimestamp(stat.st_mtime)
    
    # Calculate file hash
    with open(file_path, 'rb') as f:
        file_content = f.read()
        file_hash = hashlib.md5(file_content).hexdigest()
    
    # Check for authentication fix
    has_auth_fix = b'HTTPBasicAuth' in file_content
    has_import_auth = b'from requests.auth import HTTPBasicAuth' in file_content
    
    return {
        'path': file_path,
        'size': file_size,
        'modified': modified_time,
        'hash': file_hash,
        'has_auth_fix': has_auth_fix,
        'has_import_auth': has_import_auth
    }

def compare_files(file1, file2):
    """Compare two files"""
    try:
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            hash1 = hashlib.md5(f1.read()).hexdigest()
            hash2 = hashlib.md5(f2.read()).hexdigest()
        return hash1 == hash2, hash1, hash2
    except Exception as e:
        return False, None, None

def main():
    print("🔍 FILE VERSION CHECKER")
    print("=" * 40)
    
    # Check workspace version
    workspace_version = check_file_version('/workspace/user_input_files/deploy_enhanced_sports_aggregator.py')
    current_version = check_file_version('./deploy_enhanced_sports_aggregator.py')
    
    print(f"\n📁 Workspace version:")
    print(f"   - Path: {workspace_version.get('path', 'N/A')}")
    print(f"   - Size: {workspace_version.get('size', 'N/A')} bytes")
    print(f"   - Modified: {workspace_version.get('modified', 'N/A')}")
    print(f"   - Hash: {workspace_version.get('hash', 'N/A')}")
    print(f"   - Has HTTPBasicAuth: {'✅' if workspace_version.get('has_auth_fix') else '❌'}")
    print(f"   - Has Auth Import: {'✅' if workspace_version.get('has_import_auth') else '❌'}")
    
    print(f"\n📁 Current directory version:")
    print(f"   - Path: {current_version.get('path', 'N/A')}")
    print(f"   - Size: {current_version.get('size', 'N/A')} bytes")
    print(f"   - Modified: {current_version.get('modified', 'N/A')}")
    print(f"   - Hash: {current_version.get('hash', 'N/A')}")
    print(f"   - Has HTTPBasicAuth: {'✅' if current_version.get('has_auth_fix') else '❌'}")
    print(f"   - Has Auth Import: {'✅' if current_version.get('has_import_auth') else '❌'}")
    
    # Compare files
    if 'hash' in workspace_version and 'hash' in current_version:
        same_file, hash1, hash2 = compare_files(
            '/workspace/user_input_files/deploy_enhanced_sports_aggregator.py',
            './deploy_enhanced_sports_aggregator.py'
        )
        
        print(f"\n🔄 File Comparison:")
        print(f"   - Files are identical: {'✅ YES' if same_file else '❌ NO'}")
        print(f"   - Workspace hash: {hash1}")
        print(f"   - Current hash: {hash2}")
        
        if not same_file:
            print(f"\n🚨 ISSUE FOUND:")
            print(f"   You are running a DIFFERENT version of the file!")
            print(f"   Copy the workspace version to your current directory:")
            print(f"   cp /workspace/user_input_files/deploy_enhanced_sports_aggregator.py ./")
    
    print(f"\n💡 Recommendations:")
    if workspace_version.get('has_auth_fix') and not current_version.get('has_auth_fix'):
        print(f"   - Copy the fixed version: cp /workspace/user_input_files/deploy_enhanced_sports_aggregator.py ./")
        print(f"   - Then run: python test_main_script_exact.py")
    elif workspace_version.get('has_auth_fix') and current_version.get('has_auth_fix'):
        print(f"   - Both files have the auth fix ✅")
        print(f"   - Run: python test_main_script_exact.py to test")
    else:
        print(f"   - Workspace version may not have the fix")
        print(f"   - Check the fix in: /workspace/AUTHENTICATION_FIX_SUMMARY.md")

if __name__ == "__main__":
    main()
