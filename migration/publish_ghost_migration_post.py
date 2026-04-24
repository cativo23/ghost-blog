#!/usr/bin/env python3
"""Publish the Ghost migration post."""
import os
import jwt
import requests
import json
from datetime import datetime
from pathlib import Path

GHOST_URL = "https://blog.cativo.dev"
ADMIN_API_KEY = os.environ.get("GHOST_ADMIN_API_KEY")
if not ADMIN_API_KEY:
    print("ERROR: Set GHOST_ADMIN_API_KEY environment variable")
    exit(1)

def get_auth_token():
    """Generate JWT token for Ghost Admin API."""
    key_id, key_secret = ADMIN_API_KEY.split(':')
    iat = int(datetime.now().timestamp())
    header = {'alg': 'HS256', 'typ': 'JWT', 'kid': key_id}
    payload = {'iat': iat, 'exp': iat + 300, 'aud': '/admin/'}
    return jwt.encode(payload, bytes.fromhex(key_secret), algorithm='HS256', headers=header)

def get_or_create_tags(tag_names):
    """Get or create tags, return list of tag objects."""
    token = get_auth_token()
    headers = {
        'Authorization': f'Ghost {token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(f'{GHOST_URL}/ghost/api/admin/tags/?limit=all', headers=headers)
    existing_tags = {tag['name']: tag['id'] for tag in response.json()['tags']}

    tag_objects = []
    for tag_name in tag_names:
        if tag_name in existing_tags:
            tag_objects.append({'id': existing_tags[tag_name]})
        else:
            tag_data = {'tags': [{'name': tag_name, 'slug': tag_name.lower().replace(' ', '-')}]}
            response = requests.post(f'{GHOST_URL}/ghost/api/admin/tags/', headers=headers, json=tag_data)
            if response.status_code in [200, 201]:
                tag_objects.append({'id': response.json()['tags'][0]['id']})
                print(f"  Created tag: {tag_name}")

    return tag_objects

# Read the markdown post
post_file = Path(__file__).parent / "new_post_ghost_migration.md"
content = post_file.read_text()

# Extract frontmatter and body
import re
match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
frontmatter_text, body = match.groups()

# Parse frontmatter
frontmatter = {}
for line in frontmatter_text.split('\n'):
    if ':' in line:
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip().strip('"')
        if value.startswith('['):
            value = [v.strip().strip('"') for v in value.strip('[]').split(',')]
        frontmatter[key] = value

# Get or create tags
tags = get_or_create_tags(frontmatter['tags'])

# Create mobiledoc
mobiledoc = {
    "version": "0.3.1",
    "atoms": [],
    "cards": [["markdown", {"markdown": body}]],
    "markups": [],
    "sections": [[10, 0]]
}

# Publish post
token = get_auth_token()
headers = {
    'Authorization': f'Ghost {token}',
    'Content-Type': 'application/json'
}

post_data = {
    'posts': [{
        'title': frontmatter['title'],
        'slug': frontmatter['slug'],
        'mobiledoc': json.dumps(mobiledoc),
        'status': 'published',
        'tags': tags,
        'featured': True
    }]
}

response = requests.post(f'{GHOST_URL}/ghost/api/admin/posts/', headers=headers, json=post_data)

if response.status_code in [200, 201]:
    post = response.json()['posts'][0]
    print(f"✓ Published: {post['title']}")
    print(f"  URL: {post['url']}")
else:
    print(f"✗ Failed: {response.status_code}")
    print(response.text)
