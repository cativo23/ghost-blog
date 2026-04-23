#!/usr/bin/env python3
"""Run migration on all Nuxt Content posts."""
import json
from pathlib import Path
from migrate import parse_frontmatter, convert_post_to_ghost, create_ghost_export


def main():
    """Migrate all posts from Nuxt Content to Ghost format."""
    source_dir = Path.home() / "projects/personal/portfolio/content/blog"
    output_file = Path(__file__).parent / "ghost-export.json"

    posts_data = []

    # Process all markdown files
    for md_file in sorted(source_dir.glob("*.md")):
        if md_file.name.startswith('.'):
            continue

        print(f"Processing: {md_file.name}")
        content = md_file.read_text(encoding='utf-8')

        try:
            frontmatter, body = parse_frontmatter(content)
            slug = md_file.stem
            post = convert_post_to_ghost(frontmatter, body, slug)
            posts_data.append(post)
            print(f"  ✓ Converted: {post['title']}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
            continue

    # Create Ghost export
    export = create_ghost_export(posts_data)

    # Write output
    output_file.write_text(json.dumps(export, indent=2), encoding='utf-8')
    print(f"\n✓ Exported {len(posts_data)} posts to {output_file}")
    print(f"  Total tags: {len(export['db'][0]['data']['tags'])}")


if __name__ == "__main__":
    main()
