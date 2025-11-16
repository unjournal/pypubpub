#!/usr/bin/env python3
"""Script to find and delete pubs with titles starting with 'untitled pub'"""

from pypubpub import Pubshelper_v6
import sys
import os
import getpass

# Try to import from conf_settings, or use environment variables
sys.path.insert(0, 'tests')
try:
    from conf_settings import community_url, community_id, email, password
except ImportError:
    community_url = os.environ.get("COMMUNITY_URL")
    community_id = os.environ.get("COMMUNITY_ID")
    email = os.environ.get("EMAIL")
    password = os.environ.get("PASSWORD") or os.environ.get("PUBPUB_PASSWORD")

# Validate we have credentials
if not password:
    print("ERROR: Password not found. Please set PASSWORD environment variable.")
    sys.exit(1)

def find_untitled_pubs():
    """Find all pubs with titles starting with 'untitled pub'"""
    pubhelper = Pubshelper_v6(
        community_url=community_url,
        community_id=community_id,
        email=email,
        password=password
    )
    pubhelper.login()

    # Get all pubs
    pubs_response = pubhelper.get_many_pubs(limit=500, isReleased=None)

    # Extract pub objects from response
    all_pubs = list(pubs_response.get('pubsById', {}).values())

    # Filter for untitled pubs (case-insensitive)
    untitled_pubs = [
        pub for pub in all_pubs
        if pub.get('title', '').lower().startswith('untitled pub')
    ]

    return pubhelper, untitled_pubs

def delete_one_pub(pubhelper, pub):
    """Delete a single pub"""
    pub_id = pub['id']
    title = pub['title']
    slug = pub.get('slug', 'N/A')

    print(f"Deleting pub:")
    print(f"  ID: {pub_id}")
    print(f"  Title: {title}")
    print(f"  Slug: {slug}")

    result = pubhelper.delete_pub(pub_id)
    return result

if __name__ == "__main__":
    # Find untitled pubs
    pubhelper, untitled_pubs = find_untitled_pubs()

    print(f"Found {len(untitled_pubs)} pubs with titles starting with 'untitled pub'")

    if len(untitled_pubs) == 0:
        print("No untitled pubs to delete.")
    else:
        print("\nAll untitled pubs to delete:")
        for i, pub in enumerate(untitled_pubs):
            print(f"  {i+1}. {pub['title']} (slug: {pub.get('slug', 'N/A')})")

        print("\n" + "="*60)
        print(f"Deleting all {len(untitled_pubs)} pubs...")
        print("="*60 + "\n")

        deleted_count = 0
        failed_count = 0

        for i, pub in enumerate(untitled_pubs):
            print(f"\n[{i+1}/{len(untitled_pubs)}] Deleting: {pub['title']} (slug: {pub.get('slug', 'N/A')})")
            try:
                result = delete_one_pub(pubhelper, pub)
                print(f"  ✓ Successfully deleted")
                deleted_count += 1
            except Exception as e:
                print(f"  ✗ Failed: {e}")
                failed_count += 1

        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Successfully deleted: {deleted_count}")
        print(f"Failed: {failed_count}")
        print(f"Total processed: {len(untitled_pubs)}")
