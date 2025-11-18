#!/usr/bin/env python3
"""
Properly restore corrupted DOIs by traversing the document structure
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

def fix_text(text):
    """Fix DOIs in a text string"""
    if not text or not isinstance(text, str):
        return text, False

    changed = False
    original = text

    # Fix ALL broken DOIs: add period after 10 (more comprehensive pattern)
    # Matches both doi.org/10XXXX and doi.org/10.XXXX patterns
    text = re.sub(r'https://doi\.org/10([0-9])', r'https://doi.org/10.\g<1>', text)

    # Remove trailing periods, backslashes, and newlines from DOIs
    text = re.sub(r'(https://doi\.org/10\.[0-9]+/[^\s\"\'\)}\]<>\\]+)[\\.\\n]+', r'\g<1>', text)

    return text, text != original

def traverse_and_fix(node, changes):
    """Recursively traverse document and fix text nodes"""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == 'text' and isinstance(value, str):
                fixed, changed = fix_text(value)
                if changed:
                    changes.append({'old': value, 'new': fixed})
                    node[key] = fixed
            else:
                traverse_and_fix(value, changes)
    elif isinstance(node, list):
        for item in node:
            traverse_and_fix(item, changes)

    return node

print("="*80)
print("RESTORING CORRUPTED DOIs (Proper Method)")
print("="*80)

cookies = login(EMAIL, PASSWORD)
pub = get_pub(PUB_SLUG, cookies)
doc = get_pub_text(pub['id'], cookies)

print(f"\nPub: {pub['title'][:60]}")
print(f"ID: {pub['id']}\n")

changes = []
fixed_doc = traverse_and_fix(doc, changes)

print(f"Made {len(changes)} text modifications\n")

if changes:
    print("Sample fixes:")
    for i, change in enumerate(changes[:5], 1):
        # Show just the DOI parts
        old_dois = re.findall(r'https?://doi\.org/10\d+', change['old'])
        new_dois = re.findall(r'https?://doi\.org/10\.\d+', change['new'])
        if old_dois and new_dois:
            print(f"{i}. Fixed DOI: {old_dois[0]} → {new_dois[0]}")

    print("\n" + "="*80)
    print("APPLYING RESTORATION...")
    print("="*80)

    update_pub_text(pub['id'], fixed_doc, cookies)

    print(f"\n✓ Successfully restored DOIs!")
    print(f"\nView restored page: {COMMUNITY_URL}/pub/{PUB_SLUG}")
else:
    print("No changes needed!")
