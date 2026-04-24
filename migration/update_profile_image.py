#!/usr/bin/env python3
"""Update user profile image to use uploaded file."""
import os
import jwt
import requests
from datetime import datetime

GHOST_URL = "https://blog.cativo.dev"
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

token = get_auth_token()
headers = {'Authorization': f'Ghost {token}', 'Content-Type': 'application/json'}

# Get current user
response = requests.get(f'{GHOST_URL}/ghost/api/admin/users/me/', headers=headers)
if response.status_code != 200:
    print(f"✗ Failed to get user: {response.status_code}")
    print(response.text)
    exit(1)

data = response.json()
if 'users' not in data:
    print(f"✗ Unexpected response: {data}")
    exit(1)

user = data['users'][0]

# Update with profile image
user_data = {
    'users': [{
        'profile_image': f'{GHOST_URL}/content/images/profile-pic.jpg'
    }]
}

response = requests.put(f'{GHOST_URL}/ghost/api/admin/users/{user["id"]}/', headers=headers, json=user_data)

if response.status_code == 200:
    print("✓ Profile picture updated")
else:
    print(f"✗ Failed: {response.status_code}")
    print(response.text)
