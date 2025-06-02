#!/usr/bin/env python3
"""Check different GitHub repo possibilities"""

import urllib.request
import json

repos_to_try = [
    "Czeiszperger/themeparkwaits.release",
    "Czeiszperger/themeparkwaits",
    "Czeiszperger/ThemeParkWaits",
    "Czeiszperger/ThemeParkAPI"
]

for repo in repos_to_try:
    url = f"https://api.github.com/repos/{repo}"
    print(f"\nTrying: {url}")
    
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'OTA-Updater/1.0')
        
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f"  ✓ Found! Full name: {data.get('full_name')}")
            print(f"  Private: {data.get('private', 'Unknown')}")
            print(f"  Default branch: {data.get('default_branch', 'Unknown')}")
            
            # Try releases endpoint
            releases_url = f"{url}/releases"
            req2 = urllib.request.Request(releases_url)
            req2.add_header('User-Agent', 'OTA-Updater/1.0')
            
            try:
                with urllib.request.urlopen(req2) as resp2:
                    releases = json.loads(resp2.read().decode('utf-8'))
                    print(f"  Releases: {len(releases)} found")
            except Exception as e:
                print(f"  Releases error: {e}")
                
    except urllib.error.HTTPError as e:
        print(f"  ✗ HTTP Error {e.code}: {e.reason}")
    except Exception as e:
        print(f"  ✗ Error: {e}")