"""Create internal series tag and assign to Nova ID posts via Ghost Admin API."""
import os
import jwt
import requests
from datetime import datetime

GHOST_URL = "http://localhost:2368"
ADMIN_API_KEY = os.environ.get("GHOST_ADMIN_API_KEY")
if not ADMIN_API_KEY:
    print("ERROR: Set GHOST_ADMIN_API_KEY environment variable")
    exit(1)

key_id, key_secret = ADMIN_API_KEY.split(':')

iat = int(datetime.now().timestamp())
header = {'alg': 'HS256', 'typ': 'JWT', 'kid': key_id}
payload = {'iat': iat, 'exp': iat + 300, 'aud': '/admin/'}
token = jwt.encode(payload, bytes.fromhex(key_secret), algorithm='HS256', headers=header)

headers = {
    'Authorization': f'Ghost {token}',
    'Content-Type': 'application/json'
}

NOVA_ID_SLUGS = [
    "nova-id-day-1-why-traditional-security-is-bullshit",
    "nova-id-day-2-3-docker-compose-hell",
    "nova-id-day-4-5-when-a-general-gets-a-403",
    "nova-id-day-6-8-fighting-vues-reactivity-system",
    "nova-id-day-9-15-seven-days-of-everything-breaking",
    "nova-id-day-16-is-this-thing-production-ready-no",
    "nova-id-day-17-tearing-the-frontend-apart",
    "nova-id-day-18-proving-zero-trust-actually-works",
]

SERIES_TAG_NAME = "#series: Nova ID"

# Step 1: Create the internal series tag
print("Creating internal tag...")
tag_data = {'tags': [{'name': SERIES_TAG_NAME}]}
resp = requests.post(f'{GHOST_URL}/ghost/api/admin/tags/', headers=headers, json=tag_data)

if resp.status_code == 201:
    series_tag = resp.json()['tags'][0]
    print(f"  Created: {series_tag['name']} (slug: {series_tag['slug']}, id: {series_tag['id']})")
elif resp.status_code == 422:
    print("  Tag may already exist, fetching...")
    resp = requests.get(f'{GHOST_URL}/ghost/api/admin/tags/?limit=all&filter=visibility:internal', headers=headers)
    tags = resp.json()['tags']
    series_tag = next((t for t in tags if 'series' in t['slug'] and 'nova' in t['slug']), None)
    if not series_tag:
        resp = requests.get(f'{GHOST_URL}/ghost/api/admin/tags/?limit=all', headers=headers)
        tags = resp.json()['tags']
        series_tag = next((t for t in tags if 'series' in t.get('slug', '')), None)
    if series_tag:
        print(f"  Found existing: {series_tag['name']} (slug: {series_tag['slug']})")
    else:
        print("  ERROR: Could not find or create series tag")
        exit(1)
else:
    print(f"  ERROR: {resp.status_code} - {resp.text}")
    exit(1)

# Step 2: Fetch all posts
print("\nFetching posts...")
resp = requests.get(f'{GHOST_URL}/ghost/api/admin/posts/?limit=all&include=tags', headers=headers)
posts = resp.json()['posts']
print(f"  Found {len(posts)} posts")

# Step 3: Add series tag to Nova ID posts (keeping existing tags)
print("\nAssigning series tag to Nova ID posts...")
for post in posts:
    if post['slug'] in NOVA_ID_SLUGS:
        existing_tags = [{'id': t['id'], 'name': t['name']} for t in post.get('tags', [])]

        already_has = any(t['id'] == series_tag['id'] for t in existing_tags)
        if already_has:
            print(f"  ~ {post['slug']} already has series tag, skipping")
            continue

        existing_tags.append({'id': series_tag['id']})

        post_data = {
            'posts': [{
                'id': post['id'],
                'updated_at': post['updated_at'],
                'tags': existing_tags
            }]
        }

        resp = requests.put(
            f'{GHOST_URL}/ghost/api/admin/posts/{post["id"]}/',
            headers=headers,
            json=post_data
        )
        if resp.status_code == 200:
            print(f"  + {post['slug']}")
        else:
            print(f"  x {post['slug']}: {resp.status_code} - {resp.text}")

print("\nDone!")
