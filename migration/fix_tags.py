#!/usr/bin/env python3
"""Fix tags for imported posts."""
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

def fix_tags():
    """Fix tags for all imported posts."""
    export_file = Path(__file__).parent / "ghost-export.json"

    with open(export_file, 'r') as f:
        export_data = json.load(f)

    posts_data = export_data['db'][0]['data']['posts']
    tags_data = export_data['db'][0]['data']['tags']
    posts_tags = export_data['db'][0]['data']['posts_tags']

    # Create slug to tags mapping from export
    slug_to_tags = {}
    for idx, post in enumerate(posts_data):
        tag_names = [
            tags_data[pt['tag_id']]['name']
            for pt in posts_tags
            if pt['post_id'] == idx
        ]
        slug_to_tags[post['slug']] = tag_names

    # Get all tag names and create them
    all_tag_names = set()
    for tags in slug_to_tags.values():
        all_tag_names.update(tags)

    print(f"Creating {len(all_tag_names)} tags...")
    tag_map = get_or_create_tags(all_tag_names)

    # Get all posts from Ghost
    token = get_auth_token()
    headers = {
        'Authorization': f'Ghost {token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(f'{GHOST_URL}/ghost/api/admin/posts/?limit=all&include=tags', headers=headers)
    ghost_posts = response.json()['posts']

    # Update each post with correct tags
    print(f"\nUpdating tags for {len(ghost_posts)} posts...")
    for post in ghost_posts:
        slug = post['slug']

        # Skip the default "Coming soon" post
        if slug not in slug_to_tags:
            continue

        correct_tag_names = slug_to_tags[slug]
        correct_tag_ids = [tag_map[name] for name in correct_tag_names]

        # Update post with correct tags
        post_data = {
            'posts': [{
                'updated_at': post['updated_at'],
                'tags': [{'id': tag_id} for tag_id in correct_tag_ids]
            }]
        }

        response = requests.put(
            f'{GHOST_URL}/ghost/api/admin/posts/{post["id"]}/',
            headers=headers,
            json=post_data
        )

        if response.status_code == 200:
            print(f"  ✓ {post['title'][:50]}: {correct_tag_names}")
        else:
            print(f"  ✗ {post['title'][:50]}: {response.status_code}")

if __name__ == "__main__":
    fix_tags()
    print("\n✓ Done!")
