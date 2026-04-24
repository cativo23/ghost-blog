#!/usr/bin/env python3
"""Import posts and update About page via Ghost Admin API."""
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

def import_posts():
    """Import posts from ghost-export.json."""
    token = get_auth_token()
    headers = {
        'Authorization': f'Ghost {token}',
    }

    export_file = Path(__file__).parent / "ghost-export.json"

    with open(export_file, 'rb') as f:
        files = {'importfile': ('ghost-export.json', f, 'application/json')}
        response = requests.post(
            f'{GHOST_URL}/ghost/api/admin/db/',
            headers=headers,
            files=files
        )

    if response.status_code in [200, 201]:
        print("✓ Posts imported successfully")
        return True
    else:
        print(f"✗ Import failed: {response.status_code}")
        print(response.text)
        return False

def update_about_page():
    """Update About page content."""
    token = get_auth_token()
    headers = {
        'Authorization': f'Ghost {token}',
        'Content-Type': 'application/json'
    }

    # Get the About page
    response = requests.get(f'{GHOST_URL}/ghost/api/admin/pages/slug/about/', headers=headers)
    if response.status_code != 200:
        print(f"✗ Failed to get About page: {response.status_code}")
        return False

    page = response.json()['pages'][0]

    # Update with better content
    page_data = {
        'pages': [{
            'updated_at': page['updated_at'],
            'mobiledoc': '{"version":"0.3.1","atoms":[],"cards":[["markdown",{"markdown":"# $ whoami\\n\\nFull Stack Developer. Backend-focused. Infrastructure enthusiast. Self-hosting advocate.\\n\\nI build systems that don\'t suck, document what breaks, and occasionally yell at Docker.\\n\\n## What I Actually Do\\n\\n**Backend:** NestJS, Go, Python. The stuff that makes APIs work and databases not explode.\\n\\n**Infrastructure:** Docker, Traefik, self-hosted everything. If it can run on my server, it will.\\n\\n**Security:** Zero-trust architecture, Ory stack, the kind of auth flows that make you question your life choices at 2am.\\n\\n**Tooling:** Developer experience matters. If I have to do something twice, I automate it.\\n\\n## Current Obsessions\\n\\n- Building robust backend systems that handle real-world chaos\\n- Self-hosting infrastructure (because why pay for cloud when you can pay for therapy instead)\\n- Writing about what I learn, what breaks, and why it was probably my fault\\n\\n## The Blog\\n\\nThis is where I document the journey. No tutorials. No \\"10 steps to become a senior developer.\\" Just real projects, real problems, and real solutions (or real failures, depending on the day).\\n\\nIf you\'re here for polished content, you\'re in the wrong place. If you\'re here to see how things actually get built, welcome.\\n\\n## Find Me\\n\\n- **GitHub:** [@cativo23](https://github.com/cativo23) — where the code lives\\n- **LinkedIn:** [cativo23](https://linkedin.com/in/cativo23) — the professional version\\n- **Portfolio:** [cativo.dev](https://cativo.dev) — the showcase\\n\\n---\\n\\n*Built with Ghost, Docker, and an unreasonable amount of coffee.*"}]],"markups":[],"sections":[[10,0]]}'
        }]
    }

    response = requests.put(
        f'{GHOST_URL}/ghost/api/admin/pages/{page["id"]}/',
        headers=headers,
        json=page_data
    )

    if response.status_code == 200:
        print("✓ About page updated")
        return True
    else:
        print(f"✗ Failed to update About page: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    print("Importing posts...")
    import_posts()

    print("\nUpdating About page...")
    update_about_page()

    print("\n✓ Done!")
