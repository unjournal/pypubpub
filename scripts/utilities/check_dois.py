#!/usr/bin/env python3
"""
Check what DOIs are actually in the e2pharmpricing page
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

cookies = login(EMAIL, PASSWORD)
pub = get_pub(PUB_SLUG, cookies)
doc = get_pub_text(pub['id'], cookies)

# Find all DOI URLs in the content
text_str = json.dumps(doc)
dois = re.findall(r'https://doi\.org/[^\s\"\'\)}\]<>]+', text_str)

print(f"Found {len(dois)} DOI URLs in the content:\n")
unique_dois = list(set(dois))[:20]
for i, doi in enumerate(unique_dois, 1):
    print(f"{i}. {doi}")

# Check for suspiciously short DOIs
broken_dois = [d for d in dois if d == "https://doi.org/10"]
if broken_dois:
    print(f"\n⚠️  WARNING: Found {len(broken_dois)} broken DOIs that are just 'https://doi.org/10'")
    print("The content may have been corrupted by the previous fix attempt.")
