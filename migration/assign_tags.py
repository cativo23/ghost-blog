"""Assign tags to Ghost posts via Admin API."""
import os
import jwt
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path

# Ghost Admin API configuration
GHOST_URL = "http://localhost:2368"
ADMIN_API_KEY = os.environ.get("GHOST_ADMIN_API_KEY")
if not ADMIN_API_KEY:
    print("ERROR: Set GHOST_ADMIN_API_KEY environment variable")
    exit(1)

# Extract key ID and secret
key_id, key_secret = ADMIN_API_KEY.split(':')

# Generate JWT token
iat = int(datetime.now().timestamp())
header = {'alg': 'HS256', 'typ': 'JWT', 'kid': key_id}
payload = {
    'iat': iat,
    'exp': iat + 300,  # 5 minutes
    'aud': '/admin/'
}
token = jwt.encode(payload, bytes.fromhex(key_secret), algorithm='HS256', headers=header)

# Headers for API requests
headers = {
    'Authorization': f'Ghost {token}',
    'Content-Type': 'application/json'
}

# Tags mapping from markdown files
posts_tags = {
    "fuck-tutorials-what-building-real-backends-actually-looks-like": ["backend", "career", "learning", "software-development"],
    "free-claude-code-routing-the-cli-through-qwens-free-tier": ["ai", "claude-code", "qwen", "open-source", "linux"],
    "killing-my-own-project-why-i-archived-qwen-claude-setup": ["ai", "docker", "infrastructure", "tooling", "open-source"],
    "my-server-was-a-security-dumpster-fire": ["traefik", "docker", "security", "infrastructure", "self-hosting"],
    "nova-id-day-1-why-traditional-security-is-bullshit": ["zero-trust", "ory", "identity", "architecture", "nova-id"],
    "nova-id-day-16-is-this-thing-production-ready-no": ["retrospective", "roadmap", "zero-trust", "nova-id"],
    "nova-id-day-17-tearing-the-frontend-apart": ["architecture", "zero-trust", "refactoring", "vue", "nova-id"],
    "nova-id-day-18-proving-zero-trust-actually-works": ["nestjs", "zero-trust", "ory", "api", "nova-id"],
    "nova-id-day-2-3-docker-compose-hell": ["docker", "ory", "infrastructure", "nova-id", "debugging"],
    "nova-id-day-4-5-when-a-general-gets-a-403": ["rbac", "keto", "permissions", "zero-trust", "nova-id"],
    "nova-id-day-6-8-fighting-vues-reactivity-system": ["vue", "frontend", "kratos", "nova-id", "debugging"],
    "nova-id-day-9-15-seven-days-of-everything-breaking": ["debugging", "zero-trust", "ory", "nova-id", "lessons-learned"],
    "one-partition-to-rule-them-all": ["arch-linux", "sysadmin", "claude-code", "nvme", "partitions"],
    "qwen-was-having-an-identity-crisis": ["ai", "middleware", "debugging", "qwen", "claude-code"],
    "self-hosting-email-30-commits-of-pain": ["docker", "email", "self-hosting", "traefik", "roundcube"],
    "they-nerfed-the-free-tier": ["cli", "qwen", "ai", "open-source", "quotas"],
    "three-boots-at-1am": ["arch-linux", "sysadmin", "claude-code", "nvme"]
}

# Fetch all posts
response = requests.get(f'{GHOST_URL}/ghost/api/admin/posts/?limit=all', headers=headers)
posts = response.json()['posts']

print(f"Found {len(posts)} posts in Ghost")

# Fetch or create tags
all_tags = set()
for tag_list in posts_tags.values():
    all_tags.update(tag_list)

print(f"Need to create/fetch {len(all_tags)} unique tags")

# Get existing tags
response = requests.get(f'{GHOST_URL}/ghost/api/admin/tags/?limit=all', headers=headers)
existing_tags = {tag['name']: tag['id'] for tag in response.json()['tags']}

# Create missing tags
for tag_name in all_tags:
    if tag_name not in existing_tags:
        tag_data = {'tags': [{'name': tag_name}]}
        response = requests.post(f'{GHOST_URL}/ghost/api/admin/tags/', headers=headers, json=tag_data)
        if response.status_code == 201:
            tag_id = response.json()['tags'][0]['id']
            existing_tags[tag_name] = tag_id
            print(f"Created tag: {tag_name}")

# Update posts with tags
for post in posts:
    slug = post['slug']
    if slug in posts_tags:
        tag_names = posts_tags[slug]
        tags = [{'id': existing_tags[name]} for name in tag_names if name in existing_tags]

        post_data = {
            'posts': [{
                'id': post['id'],
                'updated_at': post['updated_at'],
                'tags': tags
            }]
        }

        response = requests.put(f'{GHOST_URL}/ghost/api/admin/posts/{post["id"]}/', headers=headers, json=post_data)
        if response.status_code == 200:
            print(f"✓ Updated {slug} with {len(tags)} tags")
        else:
            print(f"✗ Failed to update {slug}: {response.text}")

print("\nDone!")
