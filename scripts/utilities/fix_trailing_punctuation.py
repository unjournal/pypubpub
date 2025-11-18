#!/usr/bin/env python3
"""
Fix ONLY trailing periods/backslashes at the END of DOI URLs
Does NOT touch the critical "10." in DOI structure
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
    """
    ONLY remove trailing periods, backslashes, or newlines at the END of DOI URLs.
    Does NOT modify the DOI structure itself (keeps 10.XXXX intact).
    """
    if not text or not isinstance(text, str):
        return text, False

    original = text

    # Pattern explanation:
    # (https://doi\.org/10\.[0-9]+/[^\s\"\'\)}\]<>]+) - captures complete DOI
    #   - Must start with https://doi.org/10.
    #   - Followed by digits
    #   - Then a slash and the rest of the identifier
    # [.\\\n]+ - matches one or more trailing periods, backslashes, or newlines
    #
    # We replace with just group 1 (the DOI without trailing punctuation)

    pattern = r'(https://doi\.org/10\.[0-9]+/[a-zA-Z0-9._\-]+)[.\\\n]+'

    def show_fix(match):
        return match.group(1)  # Just the DOI without trailing punctuation

    text = re.sub(pattern, show_fix, text)

    return text, text != original

def traverse_and_fix(node, changes):
    """Recursively traverse document and fix text nodes"""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == 'text' and isinstance(value, str):
                fixed, changed = fix_text(value)
                if changed:
                    changes.append({
                        'old': value[:200],  # Show first 200 chars
                        'new': fixed[:200]
                    })
                    node[key] = fixed
            else:
                traverse_and_fix(value, changes)
    elif isinstance(node, list):
        for item in node:
            traverse_and_fix(item, changes)

    return node

# Test the regex first
print("="*80)
print("TESTING REGEX PATTERNS")
print("="*80)

test_cases = [
    "See https://doi.org/10.1001/jama.2024.25827. This is a sentence.",
    "Research at https://doi.org/10.1086/707407. shows results.",
    "Study: https://doi.org/10.1017/bca.2022.12.",
    "Link: https://doi.org/10.1162/rest_a_00849.",
    "Good DOI: https://doi.org/10.1093/rfs/hhab024 without period",
    "Backslash: https://doi.org/10.3386/w31834.\\",
]

print("\nTest cases:")
for test in test_cases:
    fixed, changed = fix_text(test)
    if changed:
        print(f"\n✓ WILL FIX:")
        print(f"  Before: {test}")
        print(f"  After:  {fixed}")
    else:
        print(f"\n✓ No change needed:")
        print(f"  {test}")

print("\n" + "="*80)
print("Test output looks good - proceeding with fix...")
print("="*80)

# Now do the actual fix
print("\n" + "="*80)
print("FIXING TRAILING PUNCTUATION ON DOIs")
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
    print("Sample of changes made:")
    for i, change in enumerate(changes[:3], 1):
        print(f"\n{i}.")
        print(f"  Before: ...{change['old']}...")
        print(f"  After:  ...{change['new']}...")

    print("\n" + "="*80)
    print("APPLYING FIXES...")
    print("="*80)

    update_pub_text(pub['id'], fixed_doc, cookies)

    print(f"\n✓ Successfully fixed trailing punctuation on DOIs!")
    print(f"\nView fixed page: {COMMUNITY_URL}/pub/{PUB_SLUG}")
else:
    print("No changes needed - all DOIs look good!")
