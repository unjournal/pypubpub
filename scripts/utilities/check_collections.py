#!/usr/bin/env python3
"""
Check if all papers in 'prize-winning evaluations' collection are also in 'commended evaluations' collection
"""

import sys
import os
import getpass
from pypubpub import Pubshelper_v6

# Get credentials from environment variables
email = os.environ.get('UNJOURNAL_EMAIL')
password = os.environ.get('UNJOURNAL_PASSWORD')

if not email or not password:
    print("ERROR: Please set UNJOURNAL_EMAIL and UNJOURNAL_PASSWORD environment variables")
    print("\nExample:")
    print("  export UNJOURNAL_EMAIL='your@email.com'")
    print("  export UNJOURNAL_PASSWORD='yourpassword'")
    print("  python check_collections.py")
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
    print(f"\nFetching pubs from '{collection_name}' collection (ID: {collection_id})...")

    all_pubs = []
    all_pub_ids = []
    offset = 0
    limit = 200

    while True:
        response = pubhelper.get_many_pubs(
            collection_ids=[collection_id],
            limit=limit,
            offset=offset,
            isReleased=None  # Get both published and unpublished
        )

        # The API returns pubIds (array) and pubsById (object)
        pub_ids = response.get('pubIds', [])
        pubs_by_id = response.get('pubsById', {})

        print(f"  Fetched {len(pub_ids)} pub IDs in this batch")

        if not pub_ids:
            break

        # Convert to list of pub objects
        batch_pubs = [pubs_by_id[pub_id] for pub_id in pub_ids if pub_id in pubs_by_id]
        all_pubs.extend(batch_pubs)
        all_pub_ids.extend(pub_ids)

        print(f"  Running total: {len(all_pubs)} pubs")

        # Check if we've loaded all pubs
        if response.get('loadedAllPubs', False) or len(pub_ids) < limit:
            break

        offset += limit

    return all_pubs

def main():
    # Initialize PubPub helper
    print("="*80)
    print("CHECKING PRIZE-WINNING EVALUATIONS IN COMMENDED EVALUATIONS")
    print("="*80)

    pubhelper = Pubshelper_v6(
        community_url=community_url,
        community_id=community_id,
        email=email,
        password=password
    )

    # Login
    print("\nLogging in...")
    pubhelper.login()
    print("✓ Logged in successfully")

    # Get collection IDs
    print("\nGetting collection IDs...")
    prize_winning_slug = "prize-winning-evaluations"
    commended_slug = "commended-evaluations"

    prize_winning_id = get_collection_id_by_slug(pubhelper, prize_winning_slug)
    commended_id = get_collection_id_by_slug(pubhelper, commended_slug)

    if not prize_winning_id:
        print(f"ERROR: Could not find collection '{prize_winning_slug}'")
        sys.exit(1)
    if not commended_id:
        print(f"ERROR: Could not find collection '{commended_slug}'")
        sys.exit(1)

    print(f"✓ Prize-winning evaluations ID: {prize_winning_id}")
    print(f"✓ Commended evaluations ID: {commended_id}")

    # Get pubs from both collections
    prize_winning_pubs = get_pubs_in_collection(pubhelper, prize_winning_id, "prize-winning evaluations")
    commended_pubs = get_pubs_in_collection(pubhelper, commended_id, "commended evaluations")

    # Extract pub IDs
    prize_winning_ids = {pub['id'] for pub in prize_winning_pubs}
    commended_ids = {pub['id'] for pub in commended_pubs}

    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    print(f"\nTotal prize-winning evaluations: {len(prize_winning_ids)}")
    print(f"Total commended evaluations: {len(commended_ids)}")

    # Check if all prize-winning are in commended
    missing_from_commended = prize_winning_ids - commended_ids

    if not missing_from_commended:
        print("\n✓ SUCCESS: All prize-winning evaluations are in the commended evaluations collection!")
    else:
        print(f"\n✗ ISSUE: {len(missing_from_commended)} prize-winning evaluation(s) NOT in commended evaluations:")
        print("\nMissing pubs:")
        for pub in prize_winning_pubs:
            if pub['id'] in missing_from_commended:
                title = pub.get('title', 'No title')
                slug = pub.get('slug', 'No slug')
                print(f"  - {title}")
                print(f"    Slug: {slug}")
                print(f"    ID: {pub['id']}")
                print(f"    URL: {community_url}/{slug}")
                print()

    # Also check the reverse - which commended are NOT prize-winning
    commended_not_prize = commended_ids - prize_winning_ids
    if commended_not_prize:
        print(f"\nNote: {len(commended_not_prize)} commended evaluation(s) are NOT prize-winning:")
        for pub in commended_pubs:
            if pub['id'] in commended_not_prize:
                title = pub.get('title', 'No title')
                slug = pub.get('slug', 'No slug')
                print(f"  - {title} ({slug})")

    # Logout
    print("\nLogging out...")
    pubhelper.logout()
    print("✓ Done")

    return 0 if not missing_from_commended else 1

if __name__ == '__main__':
    sys.exit(main())
