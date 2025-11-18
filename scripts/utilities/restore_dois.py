#!/usr/bin/env python3
"""
FIX THE CORRUPTED DOIs - add back the period after '10'
"""

import requests
import json
import re
from Crypto.Hash import keccak

COMMUNITY_URL = "https://unjournal.pubpub.org"
PUB_SLUG = "e2pharmpricing"
EMAIL = "daaronr@gmail.com"
PASSWORD = "321Cont_v"

def login(email, password):
    k = keccak.new(digest_bits=512)
    k.update(password.encode())
    response = requests.post(
        url=f'{COMMUNITY_URL}/api/login',
        headers={"accept": "application/json", "content-type": "application/json"},
        data=json.dumps({'email': email, 'password': k.hexdigest()}),
    )
    return response.cookies

def get_pub(slug, cookies):
    response = requests.get(f'{COMMUNITY_URL}/api/pubs/{slug}', cookies=cookies)
    return response.json()

def get_pub_text(pub_id, cookies):
    response = requests.get(f'{COMMUNITY_URL}/api/pubs/{pub_id}/text', cookies=cookies)
    return response.json()

def update_pub_text(pub_id, doc, cookies):
    response = requests.put(
        f'{COMMUNITY_URL}/api/pubs/{pub_id}/text',
        headers={"accept": "application/json", "content-type": "application/json"},
        cookies=cookies,
        json={"doc": doc, "method": "replace"}
    )
    if response.status_code < 200 or response.status_code >= 300:
        raise Exception(f'Failed: {response.status_code} {response.text}')
    return response.json()

def restore_dois(text):
    """Fix corrupted DOIs by adding back the period after '10'"""
    changes = []

    # Pattern to match broken DOIs: doi.org/10XXXX (missing period after 10)
    pattern = r'(https?://doi\.org/)10(\d{3,})'

    def replacement(match):
        original = match.group(0)
        fixed = match.group(1) + "10." + match.group(2)
        changes.append({'broken': original, 'fixed': fixed})
        return fixed

    fixed_text = re.sub(pattern, replacement, text)

    # Also remove trailing periods and backslashes from DOIs
    pattern2 = r'(https?://doi\.org/10\.\d+/[^\s\"\'\)}\]<>]+)[.\\\s]+'

    def cleanup(match):
        return match.group(1)

    fixed_text = re.sub(pattern2, cleanup, fixed_text)

    return fixed_text, changes

print("="*80)
print("RESTORING CORRUPTED DOIs")
print("="*80)

cookies = login(EMAIL, PASSWORD)
pub = get_pub(PUB_SLUG, cookies)
doc = get_pub_text(pub['id'], cookies)

print(f"\nPub: {pub['title'][:60]}")
print(f"ID: {pub['id']}\n")

text_str = json.dumps(doc)
fixed_str, changes = restore_dois(text_str)

print(f"Found {len(changes)} corrupted DOIs to fix\n")

if changes:
    print("Fixes:")
    for i, change in enumerate(changes[:10], 1):
        print(f"{i}. {change['broken']} → {change['fixed']}")

    if len(changes) > 10:
        print(f"... and {len(changes) - 10} more")

    print("\n" + "="*80)
    print("APPLYING RESTORATION...")
    print("="*80)

    fixed_doc = json.loads(fixed_str)
    update_pub_text(pub['id'], fixed_doc, cookies)

    print(f"\n✓ Successfully restored {len(changes)} DOIs!")
    print(f"\nView restored page: {COMMUNITY_URL}/pub/{PUB_SLUG}")
else:
    print("No corrupted DOIs found - may already be fixed!")
