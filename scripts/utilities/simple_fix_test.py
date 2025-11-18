#!/usr/bin/env python3
"""
Simple standalone script to fix trailing backslashes
Doesn't use pypubpub imports to avoid version issues
"""

import requests
import json
import re
import os
from Crypto.Hash import keccak

# Config
COMMUNITY_URL = "https://unjournal.pubpub.org"
COMMUNITY_ID = "d28e8e57-7f59-486b-9395-b548158a27d6"
PUB_SLUG = "e2fundraisingcharitablegivingreiley"

def login(email, password):
    """Login to PubPub"""
    k = keccak.new(digest_bits=512)
    k.update(password.encode())

    response = requests.post(
        url=f'{COMMUNITY_URL}/api/login',
        headers={
            "accept": "application/json",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "pragma": "no-cache"
        },
        data=json.dumps({
            'email': email,
            'password': k.hexdigest(),
        }),
    )

    if response.status_code != 200:
        raise Exception(f'Login failed: {response.status_code}')

    return response.cookies

def get_pub(slug, cookies):
    """Get pub by slug"""
    response = requests.get(
        f'{COMMUNITY_URL}/api/pubs/{slug}',
        headers={"accept": "application/json"},
        cookies=cookies
    )
    if response.status_code != 200:
        raise Exception(f'Failed to get pub: {response.status_code}')
    return response.json()

def get_pub_text(pub_id, cookies):
    """Get pub text content"""
    response = requests.get(
        f'{COMMUNITY_URL}/api/pubs/{pub_id}/text',
        headers={"accept": "application/json"},
        cookies=cookies
    )
    if response.status_code != 200:
        raise Exception(f'Failed to get text: {response.status_code}')
    return response.json()

def update_pub_text(pub_id, doc, cookies):
    """Update pub text"""
    response = requests.put(
        f'{COMMUNITY_URL}/api/pubs/{pub_id}/text',
        headers={
            "accept": "application/json",
            "content-type": "application/json",
        },
        cookies=cookies,
        json={
            "doc": doc,
            "method": "replace"
        }
    )
    if response.status_code < 200 or response.status_code >= 300:
        raise Exception(f'Failed to update: {response.status_code} {response.text}')
    return response.json()

def fix_backslashes(text):
    """Remove trailing backslashes from URLs"""
    changes = []
    pattern = r'(https?://[^\s\"\'\)}\]<>]+)\\+'

    def replacement(match):
        original = match.group(0)
        fixed = match.group(1)
        changes.append({'original': original, 'fixed': fixed})
        return fixed

    fixed_text = re.sub(pattern, replacement, text)
    return fixed_text, changes

def main():
    import sys

    # Get credentials
    email = os.environ.get('UNJOURNAL_EMAIL')
    password = os.environ.get('UNJOURNAL_PASSWORD')

    if not email or not password:
        print("Error: Set UNJOURNAL_EMAIL and UNJOURNAL_PASSWORD environment variables")
        sys.exit(1)

    dry_run = '--execute' not in sys.argv

    print("="*80)
    print(f"{'DRY RUN' if dry_run else 'EXECUTING'}: Fix Trailing Backslashes")
    print("="*80)
    print(f"\nTarget: {PUB_SLUG}")
    print(f"URL: {COMMUNITY_URL}/pub/{PUB_SLUG}\n")

    # Login
    print("Logging in...")
    try:
        cookies = login(email, password)
        print("✓ Logged in\n")
    except Exception as e:
        print(f"✗ Login failed: {e}")
        sys.exit(1)

    # Get pub
    print("Fetching pub...")
    try:
        pub = get_pub(PUB_SLUG, cookies)
        pub_id = pub['id']
        print(f"✓ Found: {pub['title'][:60]}")
        print(f"  ID: {pub_id}\n")
    except Exception as e:
        print(f"✗ Failed: {e}")
        sys.exit(1)

    # Get text
    print("Fetching pub content...")
    try:
        doc = get_pub_text(pub_id, cookies)
        print("✓ Content fetched\n")
    except Exception as e:
        print(f"✗ Failed: {e}")
        sys.exit(1)

    # Find and fix backslashes
    print("Analyzing for trailing backslashes...")
    text_str = json.dumps(doc)
    fixed_str, changes = fix_backslashes(text_str)

    if not changes:
        print("✓ No trailing backslashes found!\n")
        print("This page may have already been fixed, or never had the issue.")
        return

    print(f"✓ Found {len(changes)} URLs with trailing backslashes\n")

    # Show changes
    print("="*80)
    print("BROKEN URLS FOUND:")
    print("="*80)
    for i, change in enumerate(changes, 1):
        print(f"\n{i}.")
        print(f"  ❌ {change['original']}")
        print(f"  ✅ {change['fixed']}")

    if dry_run:
        print("\n" + "="*80)
        print("DRY RUN - No changes made")
        print("="*80)
        print("\nTo apply fixes, run with: --execute")
        return

    # Apply fix
    print("\n" + "="*80)
    print("APPLYING FIXES...")
    print("="*80)

    try:
        fixed_doc = json.loads(fixed_str)
        update_pub_text(pub_id, fixed_doc, cookies)
        print(f"\n✓ Successfully fixed {len(changes)} URLs!")
    except Exception as e:
        print(f"\n✗ Update failed: {e}")
        sys.exit(1)

    print("\n" + "="*80)
    print("SUCCESS!")
    print("="*80)
    print(f"\nView the fixed page:")
    print(f"{COMMUNITY_URL}/pub/{PUB_SLUG}")

if __name__ == '__main__':
    main()
