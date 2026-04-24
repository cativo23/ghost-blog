#!/usr/bin/env python3
"""Upload profile picture and update user profile."""
import os
import jwt
import requests
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

# Upload image
token = get_auth_token()
headers = {'Authorization': f'Ghost {token}'}

profile_pic = Path.home() / "profile-pic.jpg"
with open(profile_pic, 'rb') as f:
    files = {'file': ('profile-pic.jpg', f, 'image/jpeg')}
    response = requests.post(f'{GHOST_URL}/ghost/api/admin/images/upload/', headers=headers, files=files)

if response.status_code in [200, 201]:
    image_url = response.json()['images'][0]['url']
    print(f"✓ Image uploaded: {image_url}")

    # Get current user
    response = requests.get(f'{GHOST_URL}/ghost/api/admin/users/me/', headers=headers)
    user = response.json()['users'][0]

    # Update user with profile image
    user_data = {
        'users': [{
            'profile_image': image_url
        }]
    }

    response = requests.put(f'{GHOST_URL}/ghost/api/admin/users/{user["id"]}/', headers=headers, json=user_data)

    if response.status_code == 200:
        print("✓ Profile picture updated")
    else:
        print(f"✗ Failed to update profile: {response.status_code}")
        print(response.text)
else:
    print(f"✗ Upload failed: {response.status_code}")
    print(response.text)
