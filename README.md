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

The custom theme "cativo-terminal" lives in `theme/`. To build a zip for upload:

```bash
cd theme && zip -r ../cativo-terminal.zip . -x "node_modules/*"
```
