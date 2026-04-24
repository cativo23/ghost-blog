"""Upload and activate Ghost theme via Admin API."""
import os
import jwt
import requests
from datetime import datetime

GHOST_URL = "http://localhost:2368"
ADMIN_API_KEY = os.environ.get("GHOST_ADMIN_API_KEY")
if not ADMIN_API_KEY:
    print("ERROR: Set GHOST_ADMIN_API_KEY environment variable")
    exit(1)
THEME_ZIP = "/home/cativo23/projects/personal/ghost-blog/cativo-terminal.zip"

key_id, key_secret = ADMIN_API_KEY.split(':')
iat = int(datetime.now().timestamp())
header = {'alg': 'HS256', 'typ': 'JWT', 'kid': key_id}
payload = {'iat': iat, 'exp': iat + 300, 'aud': '/admin/'}
token = jwt.encode(payload, bytes.fromhex(key_secret), algorithm='HS256', headers=header)

headers = {'Authorization': f'Ghost {token}'}

print("Uploading theme...")
with open(THEME_ZIP, 'rb') as f:
    resp = requests.post(
        f'{GHOST_URL}/ghost/api/admin/themes/upload/',
        headers=headers,
        files={'file': ('cativo-terminal.zip', f, 'application/zip')}
    )

if resp.status_code == 200:
    theme = resp.json()['themes'][0]
    print(f"  Uploaded: {theme['name']} (active: {theme.get('active', False)})")

    if not theme.get('active'):
        print("Activating theme...")
        resp = requests.put(
            f'{GHOST_URL}/ghost/api/admin/themes/{theme["name"]}/activate/',
            headers={'Authorization': f'Ghost {token}', 'Content-Type': 'application/json'}
        )
        if resp.status_code == 200:
            print(f"  Activated!")
        else:
            print(f"  Activation failed: {resp.status_code} - {resp.text}")
else:
    print(f"  Upload failed: {resp.status_code}")
    print(f"  {resp.text[:500]}")

print("\nDone!")
