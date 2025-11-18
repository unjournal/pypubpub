#!/usr/bin/env python3
"""
Fix trailing backslashes in URLs within PubPub content
This script reads the link_scan_results.json and generates fixes
"""

import json
import re
import sys

def load_scan_results(filename='link_scan_results.json'):
    """Load the scan results"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filename} not found. Run scan_links.py first.")
        sys.exit(1)

def generate_fix_instructions(results):
    """Generate human-readable fix instructions"""
    trailing_backslash_links = results.get('trailing_backslash_links', [])

    if not trailing_backslash_links:
        print("No trailing backslash issues found!")
        return

    # Group by pub
    pubs_to_fix = {}
    for link in trailing_backslash_links:
        pub_slug = link['pub_slug']
        if pub_slug not in pubs_to_fix:
            pubs_to_fix[pub_slug] = {
                'title': link['pub_title'],
                'url': link['pub_url'],
                'fixes': []
            }
        pubs_to_fix[pub_slug]['fixes'].append({
            'broken': link['url'],
            'fixed': link['fixed_url']
        })

    print(f"\n{'='*80}")
    print(f"FIXING {len(trailing_backslash_links)} TRAILING BACKSLASH ISSUES")
    print(f"Affecting {len(pubs_to_fix)} publications")
    print(f"{'='*80}\n")

    print("INSTRUCTIONS:")
    print("1. Open each pub in edit mode")
    print("2. Use Find & Replace (Ctrl+F or Cmd+F)")
    print("3. Replace the broken URLs with the fixed versions")
    print("4. Save and publish\n")

    for i, (slug, data) in enumerate(pubs_to_fix.items(), 1):
        print(f"\n{i}. {data['title']}")
        print(f"   Edit URL: {data['url']}/draft")
        print(f"   Issues: {len(data['fixes'])} broken links")
        print("\n   Find and replace:")

        for fix in data['fixes']:
            print(f"   Find:    {fix['broken']}")
            print(f"   Replace: {fix['fixed']}")
            print()

    # Generate a summary file
    summary_file = 'fix_instructions.txt'
    with open(summary_file, 'w') as f:
        f.write("TRAILING BACKSLASH FIX INSTRUCTIONS\n")
        f.write("="*80 + "\n\n")
        f.write(f"Total issues: {len(trailing_backslash_links)}\n")
        f.write(f"Publications affected: {len(pubs_to_fix)}\n\n")

        for i, (slug, data) in enumerate(pubs_to_fix.items(), 1):
            f.write(f"\n{i}. {data['title']}\n")
            f.write(f"   Edit URL: {data['url']}/draft\n")
            f.write(f"   Issues: {len(data['fixes'])}\n\n")

            for fix in data['fixes']:
                f.write(f"   Find:    {fix['broken']}\n")
                f.write(f"   Replace: {fix['fixed']}\n\n")

    print(f"\n📝 Detailed instructions saved to {summary_file}")

def main():
    results = load_scan_results()
    generate_fix_instructions(results)

    # Summary statistics
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    summary = results.get('summary', {})
    print(f"Pubs scanned: {results.get('total_pubs_scanned', 0)}")
    print(f"Trailing backslash issues: {summary.get('trailing_backslash_issues', 0)}")
    print(f"Other dead links: {summary.get('real_dead_links', 0)}")
    print(f"ChatGPT links: {summary.get('chatgpt_links', 0)}")

if __name__ == '__main__':
    main()
