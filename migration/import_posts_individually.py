#!/usr/bin/env python3
"""Import posts individually via Ghost Admin API."""
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
    """Get or create tags, return mapping of name to id."""
    token = get_auth_token()
    headers = {
        'Authorization': f'Ghost {token}',
        'Content-Type': 'application/json'
    }

    # Get existing tags
    response = requests.get(f'{GHOST_URL}/ghost/api/admin/tags/?limit=all', headers=headers)
    existing_tags = {tag['name']: tag['id'] for tag in response.json()['tags']}

    tag_map = {}
    for tag_name in tag_names:
        if tag_name in existing_tags:
            tag_map[tag_name] = existing_tags[tag_name]
        else:
            # Create new tag
            tag_data = {
                'tags': [{
                    'name': tag_name,
                    'slug': tag_name.lower().replace(' ', '-')
                }]
            }
            response = requests.post(
                f'{GHOST_URL}/ghost/api/admin/tags/',
                headers=headers,
                json=tag_data
            )
            if response.status_code in [200, 201]:
                tag_map[tag_name] = response.json()['tags'][0]['id']
                print(f"  Created tag: {tag_name}")

    return tag_map

def import_posts():
    """Import posts from ghost-export.json individually."""
    export_file = Path(__file__).parent / "ghost-export.json"

    with open(export_file, 'r') as f:
        export_data = json.load(f)

    posts = export_data['db'][0]['data']['posts']
    tags_data = export_data['db'][0]['data']['tags']
    posts_tags = export_data['db'][0]['data']['posts_tags']

    # Create tag name to id mapping from export
    tag_names = [tag['name'] for tag in tags_data]
    print(f"Creating {len(tag_names)} tags...")
    tag_map = get_or_create_tags(tag_names)

    # Create posts
    token = get_auth_token()
    headers = {
        'Authorization': f'Ghost {token}',
        'Content-Type': 'application/json'
    }

    print(f"\nImporting {len(posts)} posts...")
    for idx, post in enumerate(posts):
        # Get tags for this post
        post_tag_ids = [
            tag_map[tags_data[pt['tag_id']]['name']]
            for pt in posts_tags
            if pt['post_id'] == idx
        ]

        # Convert millisecond timestamps to ISO 8601 strings
        created_at = datetime.fromtimestamp(post['created_at'] / 1000).isoformat() + 'Z'
        published_at = datetime.fromtimestamp(post['published_at'] / 1000).isoformat() + 'Z'
        updated_at = datetime.fromtimestamp(post['updated_at'] / 1000).isoformat() + 'Z'

        post_data = {
            'posts': [{
                'title': post['title'],
                'slug': post['slug'],
                'mobiledoc': post['mobiledoc'],
                'status': 'published',
                'created_at': created_at,
                'published_at': published_at,
                'updated_at': updated_at,
                'tags': [{'id': tag_id} for tag_id in post_tag_ids]
            }]
        }

        response = requests.post(
            f'{GHOST_URL}/ghost/api/admin/posts/',
            headers=headers,
            json=post_data
        )

        if response.status_code in [200, 201]:
            print(f"  ✓ {post['title']}")
        else:
            print(f"  ✗ {post['title']}: {response.status_code}")
            print(f"    {response.text}")

if __name__ == "__main__":
    import_posts()
    print("\n✓ Done!")
