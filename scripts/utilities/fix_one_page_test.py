#!/usr/bin/env python3
"""
Test fix on a single page - prompts for credentials
"""

import json
import re
import getpass
from pypubpub import Pubshelper_v6

# Target publication
PUB_SLUG = "e2fundraisingcharitablegivingreiley"
PUB_TITLE = 'Evaluation 2 of "Does online fundraising increase charitable giving?"'

# Unjournal settings
COMMUNITY_URL = "https://unjournal.pubpub.org"
COMMUNITY_ID = "d28e8e57-7f59-486b-9395-b548158a27d6"

def fix_trailing_backslashes_in_text(text):
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
    print("="*80)
    print("TEST FIX: Single Page")
    print("="*80)
    print(f"\nTarget: {PUB_TITLE}")
    print(f"URL: {COMMUNITY_URL}/pub/{PUB_SLUG}")
    print()

    # Get credentials
    print("Enter your Unjournal PubPub credentials:")
    email = input("Email: ").strip()
    password = getpass.getpass("Password: ")

    print("\n" + "="*80)
    print("STEP 1: DRY RUN (Preview Changes)")
    print("="*80)

    # Initialize
    print("\nConnecting to PubPub...")
    pubhelper = Pubshelper_v6(
        community_url=COMMUNITY_URL,
        community_id=COMMUNITY_ID,
        email=email,
        password=password
    )

    try:
        pubhelper.login()
        print("✓ Logged in successfully")
    except Exception as e:
        print(f"✗ Login failed: {e}")
        return

    # Get pub ID
    print(f"\nFetching publication '{PUB_SLUG}'...")
    try:
        pub = pubhelper.getPubByIdorSlug(PUB_SLUG)
        pub_id = pub['id']
        print(f"✓ Found pub ID: {pub_id}")
    except Exception as e:
        print(f"✗ Failed to fetch pub: {e}")
        return

    # Get current text
    print("\nFetching pub content...")
    try:
        pub_text_doc = pubhelper.get_pub_text(pub_id)
        print(f"✓ Fetched content")
    except Exception as e:
        print(f"✗ Failed to fetch content: {e}")
        return

    # Find issues
    print("\nSearching for trailing backslashes...")
    text_str = json.dumps(pub_text_doc)
    fixed_text_str, changes = fix_trailing_backslashes_in_text(text_str)

    if not changes:
        print("✓ No trailing backslashes found (already fixed or none present)")
        return

    print(f"✓ Found {len(changes)} URLs with trailing backslashes\n")

    # Show changes
    print("="*80)
    print("CHANGES THAT WOULD BE MADE:")
    print("="*80)
    for i, change in enumerate(changes, 1):
        print(f"\n{i}. Broken URL:")
        print(f"   ❌ {change['original']}")
        print(f"   ✅ {change['fixed']}")

    # Ask to proceed
    print("\n" + "="*80)
    print("STEP 2: EXECUTE FIX")
    print("="*80)
    proceed = input(f"\nDo you want to fix these {len(changes)} URLs? (yes/no): ").strip().lower()

    if proceed != 'yes':
        print("Aborted. No changes made.")
        return

    # Apply fix
    print("\nApplying fix...")
    try:
        fixed_doc = json.loads(fixed_text_str)
        pubhelper.replace_pub_text(
            pubId=pub_id,
            doc=fixed_doc,
            attributes=None,
            replace_method="replace"
        )
        print(f"✓ Successfully fixed {len(changes)} URLs!")
    except Exception as e:
        print(f"✗ Failed to update pub: {e}")
        return

    # Summary
    print("\n" + "="*80)
    print("SUCCESS!")
    print("="*80)
    print(f"\nFixed {len(changes)} broken URLs in:")
    print(f"{COMMUNITY_URL}/pub/{PUB_SLUG}")
    print("\nYou can verify the fixes by visiting the page and checking the links.")
    print()

if __name__ == '__main__':
    main()
