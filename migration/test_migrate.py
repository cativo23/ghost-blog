"""Tests for Nuxt Content to Ghost migration script."""
import json
import pytest
from pathlib import Path
from migrate import parse_frontmatter, convert_post_to_ghost, create_ghost_export


def test_parse_frontmatter():
    """Test parsing Nuxt Content frontmatter."""
    content = """---
title: "Test Post"
created_at: 2026-02-08T16:18:00Z
updated_at: 2026-02-08T16:18:00Z
image: "/img/blog/test.jpg"
author: "Carlos Cativo"
description: "Test description"
tags: ["cli", "python"]
---

Post content here."""

    frontmatter, body = parse_frontmatter(content)

    assert frontmatter['title'] == "Test Post"
    assert frontmatter['created_at'] == "2026-02-08T16:18:00Z"
    assert frontmatter['tags'] == ["cli", "python"]
    assert body.strip() == "Post content here."


def test_convert_post_to_ghost():
    """Test converting a single post to Ghost format."""
    frontmatter = {
        'title': "Test Post",
        'created_at': "2026-02-08T16:18:00Z",
        'updated_at': "2026-02-08T16:18:00Z",
        'image': "/img/blog/test.jpg",
        'description': "Test description",
        'tags': ["cli", "python"]
    }
    body = "Post content"
    slug = "test-post"

    post = convert_post_to_ghost(frontmatter, body, slug)

    assert post['title'] == "Test Post"
    assert post['slug'] == "test-post"
    assert post['status'] == "published"
    assert post['feature_image'] is None
    assert 'created_at' in post
    assert 'published_at' in post
    assert 'mobiledoc' in post


def test_create_ghost_export():
    """Test creating complete Ghost export JSON."""
    posts_data = [
        {
            'title': "Post 1",
            'slug': "post-1",
            'mobiledoc': '{"version":"0.3.1"}',
            'status': "published",
            'created_at': 1707408000000,
            'published_at': 1707408000000,
            'updated_at': 1707408000000,
            'tags': ["cli", "python"]
        }
    ]

    export = create_ghost_export(posts_data)

    assert 'db' in export
    assert 'data' in export['db'][0]
    assert 'posts' in export['db'][0]['data']
    assert 'tags' in export['db'][0]['data']
    assert 'posts_tags' in export['db'][0]['data']
    assert len(export['db'][0]['data']['posts']) == 1
