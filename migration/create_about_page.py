"""Create About page via Ghost Admin API."""
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

# Create About page
page_data = {
    'pages': [{
        'title': 'About',
        'slug': 'about',
        'mobiledoc': '{"version":"0.3.1","atoms":[],"cards":[["markdown",{"markdown":"# About\\n\\nFull Stack Developer focused on backend systems, infrastructure, and developer tooling.\\n\\n## What I Do\\n\\n- Backend development (NestJS, Go, Python)\\n- Infrastructure & DevOps (Docker, Traefik, self-hosting)\\n- Zero-trust architecture & identity systems\\n- Developer experience & tooling\\n\\n## Current Focus\\n\\nBuilding robust backend systems and exploring self-hosted infrastructure. Documenting what I learn along the way.\\n\\n## Connect\\n\\n- GitHub: [@cativo23](https://github.com/cativo23)\\n- LinkedIn: [cativo23](https://linkedin.com/in/cativo23)\\n- Portfolio: [cativo.dev](https://cativo.dev)"}]],"markups":[],"sections":[[10,0]]}',
        'status': 'published'
    }]
}

response = requests.post(f'{GHOST_URL}/ghost/api/admin/pages/', headers=headers, json=page_data)
if response.status_code == 201:
    print("✓ About page created")
else:
    print(f"✗ Failed: {response.text}")
