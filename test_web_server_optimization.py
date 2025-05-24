#!/usr/bin/env python3
"""
Test script to verify web server optimization is working correctly
"""

import re

def check_file_for_page_concatenation(filepath):
    """Check if generate_main_page uses list building instead of string concatenation"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find the generate_main_page method
    method_match = re.search(r'def generate_main_page\(self.*?\):(.*?)(?=\n    def|\Z)', content, re.DOTALL)
    if not method_match:
        return False, "Could not find generate_main_page method"
    
    method_content = method_match.group(1)
    
    # Check for page_parts initialization
    if 'page_parts = []' not in method_content:
        return False, "Missing page_parts = [] initialization"
    
    # Check for usage of page_parts.append or page_parts.extend
    if 'page_parts.append' not in method_content and 'page_parts.extend' not in method_content:
        return False, "Not using page_parts.append() or page_parts.extend()"
    
    # Check for return statement with join
    if "''.join(page_parts)" not in method_content:
        return False, "Not returning ''.join(page_parts)"
    
    # Check for any remaining page += statements
    if 'page +=' in method_content:
        return False, "Still contains page += statements"
    
    return True, "Optimization applied correctly"

# Test both files
files_to_check = [
    'src/network/web_server.py',
    'src/network/dev_web_server.py'
]

print("Checking web server optimization...")
print("-" * 50)

all_good = True
for filepath in files_to_check:
    success, message = check_file_for_page_concatenation(filepath)
    status = "✓" if success else "✗"
    print(f"{status} {filepath}: {message}")
    if not success:
        all_good = False

print("-" * 50)
if all_good:
    print("✓ All web server files are properly optimized!")
else:
    print("✗ Some files still need optimization.")

# Also check for any uninitialized 'page' variable usage
print("\nChecking for uninitialized 'page' variable...")
for filepath in files_to_check:
    with open(filepath, 'r') as f:
        content = f.read()
    
    method_match = re.search(r'def generate_main_page\(self.*?\):(.*?)(?=\n    def|\Z)', content, re.DOTALL)
    if method_match:
        method_content = method_match.group(1)
        # Look for 'page' usage without initialization
        if 'page =' in method_content and 'page = ' not in method_content and 'page =' in method_content:
            print(f"✗ {filepath}: Potential uninitialized 'page' variable")
        else:
            print(f"✓ {filepath}: No uninitialized 'page' variable issues")