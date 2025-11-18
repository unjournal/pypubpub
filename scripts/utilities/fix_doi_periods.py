#!/usr/bin/env python3
"""
Fix DOIs with trailing periods on e2pharmpricing page
"""

import requests
import json
import re
import os
from Crypto.Hash import keccak

COMMUNITY_URL = "https://unjournal.pubpub.org"
COMMUNITY_ID = "d28e8e57-7f59-486b-9395-b548158a27d6"
PUB_SLUG = "e2pharmpricing"

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

def fix_doi_periods(text):
    """Remove trailing periods from DOI URLs"""
    changes = []

    # Pattern to match DOIs with trailing periods
    # Matches doi.org URLs followed by a period and then whitespace/quote/etc
    pattern = r'(https?://doi\.org/[^\s\"\'\)}\]<>]+)\.'

    def replacement(match):
        original = match.group(0)
        fixed = match.group(1)
        # Only count it as a change if the period is actually at the end
        # (not part of a sentence continuation)
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

    print("="*80)
    print("FIXING DOI PERIODS on e2pharmpricing")
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
        print(f"✓ Found: {pub['title']}")
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

    # Find and fix DOI periods
    print("Analyzing for DOI periods...")
    text_str = json.dumps(doc)
    fixed_str, changes = fix_doi_periods(text_str)

    if not changes:
        print("✓ No DOI periods found - may already be fixed!\n")
        return

    print(f"✓ Found {len(changes)} DOIs with trailing periods\n")

    # Show changes
    print("="*80)
    print("FIXES TO BE APPLIED:")
    print("="*80)
    for i, change in enumerate(changes, 1):
        print(f"\n{i}.")
        print(f"  ❌ {change['original']}")
        print(f"  ✅ {change['fixed']}")

    # Apply fix
    print("\n" + "="*80)
    print("APPLYING FIXES...")
    print("="*80)

    try:
        fixed_doc = json.loads(fixed_str)
        update_pub_text(pub_id, fixed_doc, cookies)
        print(f"\n✓ Successfully fixed {len(changes)} DOI periods!")
    except Exception as e:
        print(f"\n✗ Update failed: {e}")
        sys.exit(1)

    print("\n" + "="*80)
    print("SUCCESS!")
    print("="*80)
    print(f"\nView the fixed page:")
    print(f"{COMMUNITY_URL}/pub/{PUB_SLUG}")
    print(f"\nEdit link (to verify changes):")
    print(f"{COMMUNITY_URL}/pub/{PUB_SLUG}/draft")

if __name__ == '__main__':
    main()
