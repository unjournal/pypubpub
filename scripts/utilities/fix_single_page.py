#!/usr/bin/env python3
"""
Test fix on e2fundraisingcharitablegivingreiley page
Set credentials via environment: UNJOURNAL_EMAIL and UNJOURNAL_PASSWORD
Or pass as arguments: --email your@email.com --password yourpass
"""

import json
import re
import os
import sys
import argparse
from pypubpub import Pubshelper_v6

PUB_SLUG = "e2fundraisingcharitablegivingreiley"
COMMUNITY_URL = "https://unjournal.pubpub.org"
COMMUNITY_ID = "d28e8e57-7f59-486b-9395-b548158a27d6"

def fix_trailing_backslashes_in_text(text):
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--email', help='Unjournal email')
    parser.add_argument('--password', help='Unjournal password')
    parser.add_argument('--execute', action='store_true', help='Actually apply changes')
    args = parser.parse_args()

    # Get credentials
    email = args.email or os.environ.get('UNJOURNAL_EMAIL')
    password = args.password or os.environ.get('UNJOURNAL_PASSWORD')

    if not email or not password:
        print("Error: Credentials not provided")
        print("Set environment variables: UNJOURNAL_EMAIL and UNJOURNAL_PASSWORD")
        print("Or use: --email YOUR_EMAIL --password YOUR_PASSWORD")
        sys.exit(1)

    print("="*80)
    print(f"{'DRY RUN' if not args.execute else 'EXECUTING FIX'}: Single Page Test")
    print("="*80)
    print(f"\nTarget: {PUB_SLUG}")
    print(f"URL: {COMMUNITY_URL}/pub/{PUB_SLUG}\n")

    # Connect
    print("Connecting to PubPub...")
    pubhelper = Pubshelper_v6(
        community_url=COMMUNITY_URL,
        community_id=COMMUNITY_ID,
        email=email,
        password=password
    )

    try:
        pubhelper.login()
        print("✓ Logged in\n")
    except Exception as e:
        print(f"✗ Login failed: {e}")
        sys.exit(1)

    # Get pub
    print("Fetching publication...")
    try:
        pub = pubhelper.getPubByIdorSlug(PUB_SLUG)
        pub_id = pub['id']
        print(f"✓ Pub ID: {pub_id}\n")
    except Exception as e:
        print(f"✗ Failed: {e}")
        sys.exit(1)

    # Get content
    print("Fetching content...")
    try:
        pub_text_doc = pubhelper.get_pub_text(pub_id)
        print("✓ Content fetched\n")
    except Exception as e:
        print(f"✗ Failed: {e}")
        sys.exit(1)

    # Find issues
    print("Analyzing URLs...")
    text_str = json.dumps(pub_text_doc)
    fixed_text_str, changes = fix_trailing_backslashes_in_text(text_str)

    if not changes:
        print("✓ No trailing backslashes found!")
        return

    print(f"✓ Found {len(changes)} URLs with trailing backslashes\n")

    # Show changes
    print("="*80)
    print("URLS TO BE FIXED:")
    print("="*80)
    for i, change in enumerate(changes, 1):
        print(f"\n{i}.")
        print(f"  ❌ {change['original']}")
        print(f"  ✅ {change['fixed']}")

    if not args.execute:
        print("\n" + "="*80)
        print("DRY RUN - No changes made")
        print("="*80)
        print(f"\nTo apply these fixes, run with: --execute")
        return

    # Execute fix
    print("\n" + "="*80)
    print("APPLYING FIXES...")
    print("="*80)

    try:
        fixed_doc = json.loads(fixed_text_str)
        pubhelper.replace_pub_text(
            pubId=pub_id,
            doc=fixed_doc,
            attributes=None,
            replace_method="replace"
        )
        print(f"\n✓ Successfully fixed {len(changes)} URLs!")
    except Exception as e:
        print(f"\n✗ Failed to update: {e}")
        sys.exit(1)

    print("\n" + "="*80)
    print("SUCCESS!")
    print("="*80)
    print(f"\nFixed page: {COMMUNITY_URL}/pub/{PUB_SLUG}")
    print("\nVerify the changes by visiting the page.")

if __name__ == '__main__':
    main()
