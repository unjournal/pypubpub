#!/usr/bin/env python3
"""
Scan unjournal.pubpub.org for dead links and ChatGPT threads
"""

import requests
import re
import json
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set
import time

# Unjournal configuration (from README)
COMMUNITY_URL = "https://unjournal.pubpub.org"
COMMUNITY_ID = "d28e8e57-7f59-486b-9395-b548158a27d6"

def get_all_pubs() -> Dict:
    """Fetch all published pubs from Unjournal"""
    # Try to fetch without authentication first (public pubs)
    response = requests.post(
        f'{COMMUNITY_URL}/api/pubs/many',
        headers={
            "accept": "application/json",
            "content-type": "application/json",
        },
        json={
            'alreadyFetchedPubIds': [],
            'pubOptions': {
                'getCollections': True,
            },
            'query': {
                'communityId': COMMUNITY_ID,
                'limit': 500,
                'offset': 0,
                'isReleased': True,  # Only published pubs
                'ordering': {'field': 'updatedDate', 'direction': 'DESC'},
            },
        },
    )

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching pubs: {response.status_code}")
        print(response.text)
        return None

def get_pub_text(pub_id: str) -> str:
    """Fetch the text content of a pub"""
    try:
        response = requests.get(
            f'{COMMUNITY_URL}/api/pubs/{pub_id}/text',
            headers={"accept": "application/json"},
        )
        if response.status_code == 200:
            data = response.json()
            # PubPub stores content in ProseMirror format
            return json.dumps(data)  # Convert to string to search for URLs
        else:
            return ""
    except Exception as e:
        print(f"Error fetching text for pub {pub_id}: {e}")
        return ""

def extract_links(text: str) -> Set[str]:
    """Extract all URLs from text"""
    # Match http/https URLs
    url_pattern = r'https?://[^\s\"\'\)}\]<>]+'
    links = set(re.findall(url_pattern, text))
    return links

def check_link(url: str) -> Dict[str, any]:
    """Check if a link is accessible"""
    result = {
        'url': url,
        'status': None,
        'error': None,
        'is_chatgpt': False,
        'is_dead': False
    }

    # Check if it's a ChatGPT link
    if 'chat.openai.com' in url or 'chatgpt.com' in url:
        result['is_chatgpt'] = True

    try:
        # Use HEAD request first (faster)
        response = requests.head(url, timeout=10, allow_redirects=True)
        result['status'] = response.status_code

        # If HEAD fails, try GET
        if response.status_code >= 400:
            response = requests.get(url, timeout=10, allow_redirects=True)
            result['status'] = response.status_code

        # Consider 404, 403, 500+ as dead links
        if response.status_code >= 400:
            result['is_dead'] = True

    except requests.exceptions.Timeout:
        result['error'] = 'Timeout'
        result['is_dead'] = True
    except requests.exceptions.ConnectionError:
        result['error'] = 'Connection Error'
        result['is_dead'] = True
    except requests.exceptions.RequestException as e:
        result['error'] = str(e)
        result['is_dead'] = True

    return result

def main():
    print("Fetching all published pubs from unjournal.pubpub.org...")
    pubs_data = get_all_pubs()

    if not pubs_data:
        print("Failed to fetch pubs. Exiting.")
        return

    pub_ids = pubs_data.get('pubIds', [])
    pubs_by_id = pubs_data.get('pubsById', {})

    print(f"Found {len(pub_ids)} published pubs")

    all_links = {}
    dead_links = []
    chatgpt_links = []

    # Categorized issues
    trailing_backslash_links = []
    real_dead_links = []

    for i, pub_id in enumerate(pub_ids):  # Scan ALL pubs
        pub = pubs_by_id.get(pub_id, {})
        slug = pub.get('slug', 'unknown')
        title = pub.get('title', 'Untitled')

        print(f"\n[{i+1}/{len(pub_ids)}] Scanning: {title[:80]}")

        # Get pub text
        text = get_pub_text(pub_id)

        # Extract links
        links = extract_links(text)

        if links:
            print(f"  Found {len(links)} links")
            all_links[pub_id] = {
                'title': title,
                'slug': slug,
                'links': []
            }

            # Check each link
            for link in links:
                # Check for trailing backslash issue first
                if link.endswith('\\'):
                    trailing_backslash_links.append({
                        'pub_title': title,
                        'pub_slug': slug,
                        'pub_url': f"{COMMUNITY_URL}/pub/{slug}",
                        'url': link,
                        'fixed_url': link.rstrip('\\')
                    })

                result = check_link(link)
                all_links[pub_id]['links'].append(result)

                # Filter out false positives
                is_false_positive = (
                    (result['status'] == 403 and 'doi.org' in link) or  # DOI anti-bot
                    (result['status'] == 403 and any(domain in link for domain in
                        ['tandfonline.com', 'pubsonline.informs.org', 'dl.acm.org'])) or  # Academic paywalls
                    (result['status'] == 429)  # Rate limiting
                )

                if result['is_dead'] and not is_false_positive:
                    real_dead_links.append({
                        'pub_title': title,
                        'pub_slug': slug,
                        'pub_url': f"{COMMUNITY_URL}/pub/{slug}",
                        **result
                    })

                if result['is_chatgpt']:
                    chatgpt_links.append({
                        'pub_title': title,
                        'pub_slug': slug,
                        'pub_url': f"{COMMUNITY_URL}/pub/{slug}",
                        **result
                    })

                # Be nice to servers
                time.sleep(0.3)

    # Print summary
    print("\n" + "="*80)
    print("SCAN COMPLETE")
    print("="*80)
    print(f"Scanned {len(pub_ids)} published pubs")

    # Trailing backslash issues (formatting bug)
    if trailing_backslash_links:
        print(f"\n❌ CRITICAL: Found {len(trailing_backslash_links)} URLs with TRAILING BACKSLASH:")
        print("These are broken links caused by formatting issues in the content.")
        unique_pubs = {}
        for link in trailing_backslash_links:
            pub_slug = link['pub_slug']
            if pub_slug not in unique_pubs:
                unique_pubs[pub_slug] = {
                    'title': link['pub_title'],
                    'url': link['pub_url'],
                    'bad_links': []
                }
            unique_pubs[pub_slug]['bad_links'].append({
                'broken': link['url'],
                'should_be': link['fixed_url']
            })

        for slug, data in unique_pubs.items():
            print(f"\n  📄 {data['title'][:80]}")
            print(f"     {data['url']}")
            for bl in data['bad_links'][:3]:  # Show first 3
                print(f"     ❌ {bl['broken']}")
                print(f"     ✅ {bl['should_be']}")
            if len(data['bad_links']) > 3:
                print(f"     ... and {len(data['bad_links']) - 3} more")
    else:
        print("\n✅ No trailing backslash issues found!")

    # Real dead links (excluding false positives)
    if real_dead_links:
        print(f"\n⚠️  Found {len(real_dead_links)} POTENTIALLY DEAD LINKS (excluding academic paywalls/anti-bot):")
        for link in real_dead_links[:10]:  # Show first 10
            print(f"\n  Pub: {link['pub_title'][:80]}")
            print(f"  Pub URL: {link['pub_url']}")
            print(f"  Dead Link: {link['url']}")
            print(f"  Status: {link['status']} {link['error'] or ''}")
        if len(real_dead_links) > 10:
            print(f"\n  ... and {len(real_dead_links) - 10} more")
    else:
        print("\n✅ No confirmed dead links found!")

    # ChatGPT links
    if chatgpt_links:
        print(f"\n🤖 Found {len(chatgpt_links)} ChatGPT LINKS:")
        for link in chatgpt_links:
            print(f"\n  Pub: {link['pub_title'][:80]}")
            print(f"  Pub URL: {link['pub_url']}")
            print(f"  ChatGPT Link: {link['url']}")
            print(f"  Accessible: {'No' if link['is_dead'] else 'Yes'}")
            if link['is_dead']:
                print(f"  ⚠️  This ChatGPT link is NOT accessible!")
    else:
        print("\n✅ No ChatGPT links found!")

    # Save results to JSON
    results = {
        'scan_date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_pubs_scanned': len(pub_ids),
        'summary': {
            'trailing_backslash_issues': len(trailing_backslash_links),
            'real_dead_links': len(real_dead_links),
            'chatgpt_links': len(chatgpt_links),
        },
        'trailing_backslash_links': trailing_backslash_links,
        'real_dead_links': real_dead_links,
        'chatgpt_links': chatgpt_links,
        'all_links': all_links
    }

    with open('link_scan_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n📝 Full results saved to link_scan_results.json")

if __name__ == '__main__':
    main()
