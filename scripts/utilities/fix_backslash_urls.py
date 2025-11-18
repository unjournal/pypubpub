#!/usr/bin/env python3
"""
Systematically fix trailing backslashes in URLs across all affected pubs
"""

import json
import re
import sys
import time
from datetime import datetime
from pypubpub import Pubshelper_v6

# Load configuration
try:
    from tests.conf_settings import email, password, community_id, community_url
except ImportError:
    print("Error: Configuration not found.")
    print("Please create tests/conf_settings.py with your credentials")
    print("Use tests/conf_settings_template.py as a guide")
    sys.exit(1)

def load_scan_results(filename='quick_scan_results.json'):
    """Load the quick scan results"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        print("Run: python quick_scan_chatgpt.py first")
        sys.exit(1)

def fix_trailing_backslashes_in_text(text):
    """
    Remove trailing backslashes from URLs in text
    Returns: (fixed_text, changes_made)
    """
    changes = []

    # Pattern to match URLs with trailing backslashes
    # Matches http(s)://... followed by backslash
    pattern = r'(https?://[^\s\"\'\)}\]<>]+)\\+'

    def replacement(match):
        original = match.group(0)
        fixed = match.group(1)  # Without the backslash
        changes.append({'original': original, 'fixed': fixed})
        return fixed

    fixed_text = re.sub(pattern, replacement, text)

    return fixed_text, changes

def fix_pub(pubhelper, pub_id, pub_slug, pub_title, dry_run=True):
    """
    Fix trailing backslashes in a single pub
    Returns: dict with status and changes
    """
    result = {
        'pub_id': pub_id,
        'pub_slug': pub_slug,
        'pub_title': pub_title,
        'success': False,
        'changes': [],
        'error': None,
        'dry_run': dry_run
    }

    try:
        # Get current pub text
        print(f"  Fetching pub text for {pub_slug}...")
        pub_text_doc = pubhelper.get_pub_text(pub_id)

        if not pub_text_doc:
            result['error'] = "Failed to fetch pub text"
            return result

        # Convert to JSON string to search for URLs
        text_str = json.dumps(pub_text_doc)

        # Fix trailing backslashes
        fixed_text_str, changes = fix_trailing_backslashes_in_text(text_str)

        if not changes:
            result['success'] = True
            result['changes'] = []
            print(f"  ✓ No trailing backslashes found (may have been fixed already)")
            return result

        result['changes'] = changes
        print(f"  Found {len(changes)} URLs to fix")

        if dry_run:
            print(f"  [DRY RUN] Would fix {len(changes)} URLs")
            result['success'] = True
            return result

        # Parse the fixed text back to JSON
        fixed_doc = json.loads(fixed_text_str)

        # Update the pub
        print(f"  Updating pub...")
        pubhelper.replace_pub_text(
            pubId=pub_id,
            doc=fixed_doc,
            attributes=None,
            replace_method="replace"
        )

        result['success'] = True
        print(f"  ✓ Successfully fixed {len(changes)} URLs")

        # Sleep to avoid rate limiting
        time.sleep(1)

    except Exception as e:
        result['error'] = str(e)
        print(f"  ✗ Error: {e}")

    return result

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Fix trailing backslashes in PubPub URLs')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Dry run mode (default: True)')
    parser.add_argument('--execute', action='store_true',
                        help='Actually execute the fixes (overrides --dry-run)')
    parser.add_argument('--limit', type=int, default=None,
                        help='Limit number of pubs to fix (for testing)')
    parser.add_argument('--pub-slug', type=str, default=None,
                        help='Fix only a specific pub by slug')

    args = parser.parse_args()

    # Determine if this is a dry run
    dry_run = not args.execute

    if dry_run:
        print("\n" + "="*80)
        print("DRY RUN MODE - No changes will be made")
        print("To execute fixes, run with: --execute")
        print("="*80 + "\n")
    else:
        print("\n" + "="*80)
        print("EXECUTE MODE - Changes WILL be made to PubPub")
        print("="*80 + "\n")

        response = input("Are you sure you want to proceed? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            sys.exit(0)

    # Load scan results
    print("Loading scan results...")
    results = load_scan_results()
    trailing_backslash_issues = results.get('trailing_backslash_issues', [])

    if not trailing_backslash_issues:
        print("No trailing backslash issues found!")
        return

    # Group by pub
    pubs_to_fix = {}
    for issue in trailing_backslash_issues:
        pub_slug = issue['pub_slug']
        if pub_slug not in pubs_to_fix:
            pubs_to_fix[pub_slug] = {
                'title': issue['pub_title'],
                'url': issue['pub_url'],
                'issues': []
            }
        pubs_to_fix[pub_slug]['issues'].append({
            'broken': issue['broken_url'],
            'fixed': issue['fixed_url']
        })

    # Filter by slug if specified
    if args.pub_slug:
        if args.pub_slug not in pubs_to_fix:
            print(f"Error: Pub slug '{args.pub_slug}' not found in results")
            sys.exit(1)
        pubs_to_fix = {args.pub_slug: pubs_to_fix[args.pub_slug]}

    # Apply limit if specified
    if args.limit:
        pubs_to_fix = dict(list(pubs_to_fix.items())[:args.limit])

    print(f"\nFound {len(pubs_to_fix)} publications to fix")
    print(f"Total issues: {len(trailing_backslash_issues)}")

    # Initialize PubPub helper
    print("\nConnecting to PubPub...")
    pubhelper = Pubshelper_v6(
        community_url=community_url,
        community_id=community_id,
        email=email,
        password=password
    )

    try:
        pubhelper.login()
        print("✓ Logged in successfully\n")
    except Exception as e:
        print(f"✗ Login failed: {e}")
        sys.exit(1)

    # Process each pub
    all_results = []
    success_count = 0
    error_count = 0

    print("="*80)
    print("PROCESSING PUBLICATIONS")
    print("="*80 + "\n")

    for i, (slug, data) in enumerate(pubs_to_fix.items(), 1):
        print(f"[{i}/{len(pubs_to_fix)}] {data['title'][:70]}")
        print(f"  Slug: {slug}")
        print(f"  Expected issues: {len(data['issues'])}")

        # Get pub ID from slug
        try:
            pub_response = pubhelper.getPubByIdorSlug(slug)
            pub_id = pub_response['id']
        except Exception as e:
            print(f"  ✗ Error getting pub ID: {e}")
            error_count += 1
            continue

        # Fix the pub
        result = fix_pub(
            pubhelper=pubhelper,
            pub_id=pub_id,
            pub_slug=slug,
            pub_title=data['title'],
            dry_run=dry_run
        )

        all_results.append(result)

        if result['success']:
            success_count += 1
        else:
            error_count += 1

        print()  # Blank line between pubs

    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total pubs processed: {len(all_results)}")
    print(f"Successful: {success_count}")
    print(f"Errors: {error_count}")

    if dry_run:
        print("\n⚠️  This was a DRY RUN - no changes were made")
        print("To execute fixes, run with: --execute")
    else:
        print("\n✓ Changes have been applied to PubPub")

    # Save detailed results
    output_file = f"fix_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'dry_run': dry_run,
            'summary': {
                'total_processed': len(all_results),
                'successful': success_count,
                'errors': error_count
            },
            'results': all_results
        }, f, indent=2)

    print(f"\n📝 Detailed results saved to {output_file}")

    # Show some example changes
    if all_results and all_results[0].get('changes'):
        print("\nExample changes made:")
        for change in all_results[0]['changes'][:3]:
            print(f"  ❌ {change['original']}")
            print(f"  ✅ {change['fixed']}")
            print()

if __name__ == '__main__':
    main()
