#!/usr/bin/env python3
"""
Add all prize-winning evaluations to the commended evaluations collection
"""

import sys
import os
from pypubpub import Pubshelper_v6

# Get credentials from environment variables
email = os.environ.get('UNJOURNAL_EMAIL')
password = os.environ.get('UNJOURNAL_PASSWORD')

if not email or not password:
    print("ERROR: Please set UNJOURNAL_EMAIL and UNJOURNAL_PASSWORD environment variables")
    sys.exit(1)

# Use Unjournal defaults
community_url = os.environ.get('UNJOURNAL_URL', "https://unjournal.pubpub.org")
community_id = os.environ.get('UNJOURNAL_COMMUNITY_ID', "d28e8e57-7f59-486b-9395-b548158a27d6")

print(f"Using credentials: {email}, URL: {community_url}")

def get_collection_id_by_slug(pubhelper, slug):
    """Get collection ID by slug"""
    try:
        response = pubhelper.authed_request(f'collections/{slug}', 'GET')
        return response.get('id')
    except Exception as e:
        print(f"Error getting collection {slug}: {e}")
        return None

def get_pubs_in_collection(pubhelper, collection_id, collection_name):
    """Get all pubs in a collection"""
    print(f"\nFetching pubs from '{collection_name}' collection...")

    all_pubs = []
    offset = 0
    limit = 200

    while True:
        response = pubhelper.get_many_pubs(
            collection_ids=[collection_id],
            limit=limit,
            offset=offset,
            isReleased=None
        )

        pub_ids = response.get('pubIds', [])
        pubs_by_id = response.get('pubsById', {})

        if not pub_ids:
            break

        batch_pubs = [pubs_by_id[pub_id] for pub_id in pub_ids if pub_id in pubs_by_id]
        all_pubs.extend(batch_pubs)

        if response.get('loadedAllPubs', False) or len(pub_ids) < limit:
            break

        offset += limit

    print(f"  Total: {len(all_pubs)} pubs")
    return all_pubs

def add_pub_to_collection(pubhelper, pub_id, collection_id, community_id):
    """Add a pub to a collection"""
    try:
        response = pubhelper.authed_request(
            'collectionPubs',
            'POST',
            {
                "pubId": pub_id,
                "collectionId": collection_id,
                "communityId": community_id,
                "rank": "h"  # Default rank
            }
        )
        # Check if response looks like HTML (error page)
        if isinstance(response, str) and '<html' in response.lower():
            return False, "Received HTML error page instead of JSON response"
        return True, response
    except Exception as e:
        error_msg = str(e)
        # Truncate very long error messages
        if len(error_msg) > 500:
            error_msg = error_msg[:500] + "... [truncated]"
        return False, error_msg

def main():
    print("="*80)
    print("ADDING PRIZE-WINNING EVALUATIONS TO COMMENDED EVALUATIONS")
    print("="*80)

    # Initialize and login
    pubhelper = Pubshelper_v6(
        community_url=community_url,
        community_id=community_id,
        email=email,
        password=password
    )

    print("\nLogging in...")
    pubhelper.login()
    print("✓ Logged in successfully")

    # Get collection IDs
    print("\nGetting collection IDs...")
    prize_winning_slug = "prize-winning-evaluations"
    commended_slug = "commended-evaluations"

    prize_winning_id = get_collection_id_by_slug(pubhelper, prize_winning_slug)
    commended_id = get_collection_id_by_slug(pubhelper, commended_slug)

    if not prize_winning_id or not commended_id:
        print("ERROR: Could not find collections")
        sys.exit(1)

    print(f"✓ Prize-winning evaluations ID: {prize_winning_id}")
    print(f"✓ Commended evaluations ID: {commended_id}")

    # Get pubs from both collections
    prize_winning_pubs = get_pubs_in_collection(pubhelper, prize_winning_id, "prize-winning evaluations")
    commended_pubs = get_pubs_in_collection(pubhelper, commended_id, "commended evaluations")

    # Find missing pubs
    prize_winning_ids = {pub['id'] for pub in prize_winning_pubs}
    commended_ids = {pub['id'] for pub in commended_pubs}
    missing_ids = prize_winning_ids - commended_ids

    print("\n" + "="*80)
    print(f"Found {len(missing_ids)} prize-winning evaluations NOT in commended collection")
    print("="*80)

    if not missing_ids:
        print("\n✓ All prize-winning evaluations are already in commended collection!")
        pubhelper.logout()
        return 0

    # Test mode or full mode
    test_mode = os.environ.get('TEST_MODE', '').lower() == 'yes'

    if test_mode:
        print("\n*** TEST MODE: Will only add ONE pub to test the API ***")
    else:
        print("\nThis will add the following pubs to the commended evaluations collection:")
        for pub in prize_winning_pubs:
            if pub['id'] in missing_ids:
                print(f"  - {pub.get('title', 'No title')}")

    confirm = os.environ.get('AUTO_CONFIRM', '').lower()
    if confirm != 'yes' and not test_mode:
        print("\nTo proceed, set AUTO_CONFIRM=yes environment variable")
        print("Example: AUTO_CONFIRM=yes python add_to_collection.py")
        print("Or set TEST_MODE=yes to test with just one pub")
        pubhelper.logout()
        return 1

    # Add pubs to collection
    print("\n" + "="*80)
    print("ADDING PUBS TO COLLECTION")
    print("="*80)

    success_count = 0
    error_count = 0

    pubs_to_add = [pub for pub in prize_winning_pubs if pub['id'] in missing_ids]

    # In test mode, only add one pub
    if test_mode:
        pubs_to_add = pubs_to_add[:1]
        print(f"\nTest mode: Adding only 1 pub out of {len(missing_ids)} total")

    for i, pub in enumerate(pubs_to_add, 1):
        title = pub.get('title', 'No title')
        slug = pub.get('slug', 'No slug')

        print(f"\n[{i}/{len(pubs_to_add)}] Adding: {title}")
        print(f"  Slug: {slug}")
        print(f"  Pub ID: {pub['id']}")
        print(f"  Collection ID: {commended_id}")

        success, result = add_pub_to_collection(pubhelper, pub['id'], commended_id, community_id)

        if success:
            print(f"  ✓ Successfully added")
            print(f"  Response: {result}")
            success_count += 1
        else:
            print(f"  ✗ Failed: {result}")
            error_count += 1

        # In test mode, show detailed result and exit
        if test_mode:
            break

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Successfully added: {success_count}")
    print(f"Failed: {error_count}")
    print(f"Total processed: {len(missing_ids)}")

    # Logout
    print("\nLogging out...")
    pubhelper.logout()
    print("✓ Done")

    return 0 if error_count == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
