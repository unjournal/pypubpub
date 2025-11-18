#!/usr/bin/env python3
"""
Test ChatGPT links for accessibility
"""

import json
import requests
import time

def load_results():
    with open('quick_scan_results.json', 'r') as f:
        return json.load(f)

def test_chatgpt_link(url):
    """Test if a ChatGPT link is accessible"""
    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        return {
            'url': url,
            'status': response.status_code,
            'accessible': response.status_code == 200,
            'error': None
        }
    except requests.exceptions.Timeout:
        return {'url': url, 'status': None, 'accessible': False, 'error': 'Timeout'}
    except requests.exceptions.ConnectionError:
        return {'url': url, 'status': None, 'accessible': False, 'error': 'Connection Error'}
    except Exception as e:
        return {'url': url, 'status': None, 'accessible': False, 'error': str(e)}

def main():
    results = load_results()
    chatgpt_links = results.get('chatgpt_links', [])

    # Filter to only real ChatGPT links (not just utm_source)
    real_chatgpt = []
    false_positives = []

    for link in chatgpt_links:
        url = link['chatgpt_url']
        if 'chatgpt.com' in url or 'chat.openai.com' in url:
            # Check if it's really a ChatGPT link or just has utm_source
            if 'utm_source=chatgpt.com' in url and not url.startswith('https://chatgpt.com'):
                false_positives.append(link)
            else:
                real_chatgpt.append(link)
        else:
            false_positives.append(link)

    print(f"Found {len(real_chatgpt)} real ChatGPT links")
    print(f"Found {len(false_positives)} false positives (utm_source tags)\n")

    print("Testing real ChatGPT links for accessibility...\n")

    results_by_pub = {}
    for link in real_chatgpt:
        url = link['chatgpt_url']
        pub_slug = link['pub_slug']

        print(f"Testing: {url}")
        test_result = test_chatgpt_link(url)

        if pub_slug not in results_by_pub:
            results_by_pub[pub_slug] = {
                'pub_title': link['pub_title'],
                'pub_url': link['pub_url'],
                'chatgpt_links': []
            }

        results_by_pub[pub_slug]['chatgpt_links'].append(test_result)
        time.sleep(0.5)

    # Summary
    print("\n" + "="*80)
    print("CHATGPT LINK ACCESSIBILITY RESULTS")
    print("="*80)

    total_accessible = 0
    total_not_accessible = 0

    for slug, data in results_by_pub.items():
        print(f"\n📄 {data['pub_title']}")
        print(f"   {data['pub_url']}")

        for link in data['chatgpt_links']:
            if link['accessible']:
                print(f"   ✅ Accessible: {link['url']}")
                total_accessible += 1
            else:
                print(f"   ❌ NOT accessible: {link['url']}")
                print(f"      Status: {link['status']}, Error: {link['error']}")
                total_not_accessible += 1

    print(f"\n{'='*80}")
    print(f"Summary:")
    print(f"  Real ChatGPT links: {len(real_chatgpt)}")
    print(f"  Accessible: {total_accessible}")
    print(f"  NOT accessible: {total_not_accessible}")
    print(f"  False positives (utm_source): {len(false_positives)}")

    # Save detailed results
    output = {
        'real_chatgpt_links': results_by_pub,
        'false_positives': false_positives,
        'summary': {
            'total_real': len(real_chatgpt),
            'accessible': total_accessible,
            'not_accessible': total_not_accessible,
            'false_positives': len(false_positives)
        }
    }

    with open('chatgpt_accessibility_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n📝 Detailed results saved to chatgpt_accessibility_results.json")

if __name__ == '__main__':
    main()
