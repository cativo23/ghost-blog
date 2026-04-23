"""Migrate Nuxt Content posts to Ghost JSON format."""
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any


def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """Parse YAML frontmatter and body from markdown content."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
    if not match:
        raise ValueError("No frontmatter found")

    frontmatter_text, body = match.groups()
    frontmatter = {}

    # Simple YAML parser for our specific format
    current_key = None
    for line in frontmatter_text.split('\n'):
        if ':' in line and not line.startswith(' '):
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            # Handle quoted strings
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]

            # Handle arrays
            if value.startswith('['):
                value = value.strip('[]')
                value = [v.strip().strip('"') for v in value.split(',')]

            frontmatter[key] = value
            current_key = key

    return frontmatter, body


def convert_post_to_ghost(frontmatter: Dict[str, Any], body: str, slug: str) -> Dict[str, Any]:
    """Convert a single post to Ghost format."""
    # Convert ISO timestamp to milliseconds since epoch
    created_at = frontmatter.get('created_at', '')
    updated_at = frontmatter.get('updated_at', created_at)

    created_ms = int(datetime.fromisoformat(created_at.replace('Z', '+00:00')).timestamp() * 1000)
    updated_ms = int(datetime.fromisoformat(updated_at.replace('Z', '+00:00')).timestamp() * 1000)

    # Create mobiledoc structure for markdown content
    mobiledoc = {
        "version": "0.3.1",
        "atoms": [],
        "cards": [["markdown", {"markdown": body}]],
        "markups": [],
        "sections": [[10, 0]]
    }

    # Ghost post structure
    post = {
        'title': frontmatter.get('title', ''),
        'slug': slug,
        'mobiledoc': json.dumps(mobiledoc),
        'status': 'published',
        'created_at': created_ms,
        'published_at': created_ms,
        'updated_at': updated_ms,
        'feature_image': None,
        'tags': frontmatter.get('tags', [])
    }

    return post


def create_ghost_export(posts_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create complete Ghost export JSON structure."""
    # Extract unique tags
    all_tags = set()
    for post in posts_data:
        all_tags.update(post.get('tags', []))

    # Create tag objects
    tags = [{'name': tag, 'slug': tag.lower().replace(' ', '-')} for tag in sorted(all_tags)]

    # Create posts_tags relationships
    posts_tags = []
    tag_map = {tag['name']: idx for idx, tag in enumerate(tags)}

    for post_idx, post in enumerate(posts_data):
        for tag_name in post.get('tags', []):
            posts_tags.append({
                'post_id': post_idx,
                'tag_id': tag_map[tag_name]
            })

    # Remove tags from posts (they're in relationships now)
    clean_posts = []
    for post in posts_data:
        clean_post = {k: v for k, v in post.items() if k != 'tags'}
        clean_posts.append(clean_post)

    # Ghost export structure
    export = {
        'db': [{
            'meta': {
                'exported_on': int(datetime.now().timestamp() * 1000),
                'version': '5.0.0'
            },
            'data': {
                'posts': clean_posts,
                'tags': tags,
                'posts_tags': posts_tags
            }
        }]
    }

    return export
