#!/usr/bin/env python3
"""
Quick scan for ChatGPT links and formatting issues (without testing each link)
"""

import requests
import re
import json
from typing import Set

COMMUNITY_URL = "https://unjournal.pubpub.org"
COMMUNITY_ID = "d28e8e57-7f59-486b-9395-b548158a27d6"

def get_all_pubs():
    """Fetch all published pubs"""
    response = requests.post(
        f'{COMMUNITY_URL}/api/pubs/many',
        headers={"accept": "application/json", "content-type": "application/json"},
        json={
            'alreadyFetchedPubIds': [],
            'pubOptions': {'getCollections': True},
            'query': {
                'communityId': COMMUNITY_ID,
                'limit': 500,
                'offset': 0,
                'isReleased': True,
                'ordering': {'field': 'updatedDate', 'direction': 'DESC'},
            },
        },
    )
    return response.json() if response.status_code == 200 else None

def get_pub_text(pub_id: str) -> str:
    """Fetch pub text"""
    try:
        response = requests.get(
            f'{COMMUNITY_URL}/api/pubs/{pub_id}/text',
            headers={"accept": "application/json"},
        )
        if response.status_code == 200:
            return json.dumps(response.json())
        return ""
    except Exception as e:
        return ""

def extract_links(text: str) -> Set[str]:
    """Extract all URLs"""
    url_pattern = r'https?://[^\s\"\'\)}\]<>]+'
    return set(re.findall(url_pattern, text))

def main():
    print("Quick scan for ChatGPT links and formatting issues...")
    pubs_data = get_all_pubs()

    if not pubs_data:
        print("Failed to fetch pubs.")
        return

    pub_ids = pubs_data.get('pubIds', [])
    pubs_by_id = pubs_data.get('pubsById', {})
    print(f"Scanning {len(pub_ids)} pubs...\n")

    chatgpt_links_found = []
    trailing_backslash_issues = []
    other_issues = []

    for i, pub_id in enumerate(pub_ids, 1):
        pub = pubs_by_id.get(pub_id, {})
        slug = pub.get('slug', 'unknown')
        title = pub.get('title', 'Untitled')

        if i % 20 == 0:
            print(f"Progress: {i}/{len(pub_ids)}")

        text = get_pub_text(pub_id)
        links = extract_links(text)

        for link in links:
            # ChatGPT links
            if 'chat.openai.com' in link or 'chatgpt.com' in link:
                chatgpt_links_found.append({
                    'pub_title': title,
                    'pub_slug': slug,
                    'pub_url': f"{COMMUNITY_URL}/pub/{slug}",
                    'chatgpt_url': link
                })

            # Trailing backslash
            if link.endswith('\\'):
                trailing_backslash_issues.append({
                    'pub_title': title,
                    'pub_slug': slug,
                    'pub_url': f"{COMMUNITY_URL}/pub/{slug}",
                    'broken_url': link,
                    'fixed_url': link.rstrip('\\')
                })

            # Other suspicious patterns
            if link.endswith('/draft?access='):
                other_issues.append({
                    'pub_title': title,
                    'pub_slug': slug,
                    'pub_url': f"{COMMUNITY_URL}/pub/{slug}",
                    'issue': 'Draft link with access token exposed',
                    'url': link
                })

    # Results
    print("\n" + "="*80)
    print("QUICK SCAN RESULTS")
    print("="*80)

    # ChatGPT links
    if chatgpt_links_found:
        print(f"\n🤖 FOUND {len(chatgpt_links_found)} ChatGPT LINKS:\n")
        for link in chatgpt_links_found:
            print(f"  📄 {link['pub_title']}")
            print(f"     Pub: {link['pub_url']}")
            print(f"     ChatGPT: {link['chatgpt_url']}")
            print()
    else:
        print("\n✅ No ChatGPT links found")

    # Trailing backslashes
    if trailing_backslash_issues:
        # Group by pub
        by_pub = {}
        for issue in trailing_backslash_issues:
            slug = issue['pub_slug']
            if slug not in by_pub:
                by_pub[slug] = {
                    'title': issue['pub_title'],
                    'url': issue['pub_url'],
                    'issues': []
                }
            by_pub[slug]['issues'].append({
                'broken': issue['broken_url'],
                'fixed': issue['fixed_url']
            })

        print(f"\n❌ FOUND {len(trailing_backslash_issues)} TRAILING BACKSLASH ISSUES")
        print(f"   Affecting {len(by_pub)} publications:\n")

        for slug, data in list(by_pub.items())[:10]:  # Show first 10
            print(f"  📄 {data['title'][:70]}")
            print(f"     Edit: {data['url']}/draft")
            print(f"     {len(data['issues'])} broken links")
            print()

        if len(by_pub) > 10:
            print(f"  ... and {len(by_pub) - 10} more pubs with issues")
    else:
        print("\n✅ No trailing backslash issues")

    # Other issues
    if other_issues:
        print(f"\n⚠️  OTHER ISSUES ({len(other_issues)}):\n")
        for issue in other_issues[:5]:
            print(f"  📄 {issue['pub_title'][:70]}")
            print(f"     {issue['issue']}")
            print(f"     {issue['url']}")
            print()
    else:
        print("\n✅ No other issues found")

    # Save results
    results = {
        'chatgpt_links': chatgpt_links_found,
        'trailing_backslash_issues': trailing_backslash_issues,
        'other_issues': other_issues
    }

    with open('quick_scan_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n📝 Results saved to quick_scan_results.json")

if __name__ == '__main__':
    main()
