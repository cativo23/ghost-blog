# Ghost Blog — blog.cativo.dev

Self-hosted Ghost blog with a custom terminal-themed Handlebars theme ("cativo-terminal").

## Stack

- Ghost 5 (Alpine)
- MySQL 8
- Docker Compose
- Traefik v3.6 (reverse proxy, production)

## Development

```bash
cp .env.example .env
# Edit .env with dev values
docker compose up -d
```

Ghost will be available at `http://localhost:2368`.
Ghost Admin at `http://localhost:2368/ghost`.

The theme is volume-mounted — changes to `theme/` are picked up automatically.

## Production

```bash
docker compose -f compose.prod.yml up -d
```

Traefik routes `blog.cativo.dev` to the Ghost container.

## Theme

The custom theme "cativo-terminal" lives in `theme/`.

### Features

- Tokyo Night Storm palette (dark/light mode)
- Terminal aesthetic (window chrome, prompts, monospace fonts)
- Hybrid homepage: hero featured post + terminal-style feed
- Sidebar table of contents with active section highlighting
- Reading progress bar
- Giscus comments integration
- Blog series navigation (badge + collapsible index)
- Terminal grep-style search

### Blog Series

Posts can be grouped into series using Ghost internal tags:

1. Create an internal tag in Ghost Admin with the naming convention `#series: Series Name` (e.g., `#series: Nova ID`)
2. Assign the tag to all posts in the series
3. Posts are ordered by `published_at` date — oldest = position 1

The theme renders:
- **Post page**: series badge above the title (`Nova ID • 3/8`) and a collapsible series index at the bottom
- **Feed/hero card**: small series badge

### Building the theme zip

```bash
cd theme && zip -r ../cativo-terminal.zip . -x "node_modules/*"
```

## Migration Scripts

Utility scripts in `migration/` for managing Ghost content via the Admin API.

### Setup

```bash
cd migration
python3 -m venv .venv
.venv/bin/pip install pyjwt requests
```

### Usage

All scripts require the `GHOST_ADMIN_API_KEY` environment variable:

```bash
export GHOST_ADMIN_API_KEY="your-key-id:your-key-secret"
```

You can find your Admin API key in Ghost Admin → Settings → Integrations.

| Script | Description |
|---|---|
| `assign_tags.py` | Assign tags to posts in bulk |
| `assign_series_tags.py` | Create internal series tags and assign to posts |
| `fix_tags.py` | Fix/update tag assignments |
| `import_and_update.py` | Import posts from Nuxt Content export |
| `import_posts_individually.py` | Import posts one by one via API |
| `publish_ghost_migration_post.py` | Publish the migration announcement post |
| `upload_theme.py` | Upload and activate theme via API |
| `upload_profile_pic.py` | Upload profile picture |
| `update_profile_image.py` | Update author profile image |
| `create_about_page.py` | Create the about page |
| `update_about_page.py` | Update the about page content |
