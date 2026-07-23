#!/usr/bin/env python3
"""Update the Payment Service case study post with the revised opening."""
import os
import jwt
import requests
import json
import re
from datetime import datetime
from pathlib import Path

GHOST_URL = "https://blog.cativo.dev"
SLUG = "payment-service-one-interface-many-processors"
ADMIN_API_KEY = os.environ.get("GHOST_ADMIN_API_KEY")
if not ADMIN_API_KEY:
    print("ERROR: Set GHOST_ADMIN_API_KEY environment variable")
    exit(1)

def get_auth_token():
    key_id, key_secret = ADMIN_API_KEY.split(':')
    iat = int(datetime.now().timestamp())
    header = {'alg': 'HS256', 'typ': 'JWT', 'kid': key_id}
    payload = {'iat': iat, 'exp': iat + 300, 'aud': '/admin/'}
    return jwt.encode(payload, bytes.fromhex(key_secret), algorithm='HS256', headers=header)

def headers():
    return {
        'Authorization': f'Ghost {get_auth_token()}',
        'Content-Type': 'application/json'
    }

# Fetch current post to get id + updated_at (required for Ghost's optimistic lock)
resp = requests.get(f'{GHOST_URL}/ghost/api/admin/posts/slug/{SLUG}/', headers=headers())
if resp.status_code != 200:
    print(f"✗ Failed to fetch post: {resp.status_code}")
    print(resp.text)
    exit(1)

post = resp.json()['posts'][0]
post_id = post['id']
current_updated_at = post['updated_at']

# Read the revised markdown
post_file = Path(__file__).parent / "new_post_payment_service.md"
content = post_file.read_text()
match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
_, body = match.groups()

mobiledoc = {
    "version": "0.3.1",
    "atoms": [],
    "cards": [["markdown", {"markdown": body}]],
    "markups": [],
    "sections": [[10, 0]]
}

update_data = {
    'posts': [{
        'mobiledoc': json.dumps(mobiledoc),
        'updated_at': current_updated_at
    }]
}

resp = requests.put(f'{GHOST_URL}/ghost/api/admin/posts/{post_id}/', headers=headers(), json=update_data)

if resp.status_code in [200, 201]:
    updated = resp.json()['posts'][0]
    print(f"✓ Updated: {updated['title']}")
    print(f"  URL: {updated['url']}")
else:
    print(f"✗ Failed: {resp.status_code}")
    print(resp.text)
