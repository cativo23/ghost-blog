# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2026-04-23

### Fixed
- Deploy workflow now correctly copies `compose.prod.yml` to server
- Deploy workflow creates `.env` file with database password from GitHub secrets
- Deploy workflow properly executes `docker compose up -d` instead of just restarting Ghost

## [1.0.0] - 2026-04-23

### Added
- Custom Ghost theme "cativo-terminal" with Tokyo Night Storm palette
- Terminal aesthetic design with monospace fonts and developer-focused UI
- Hybrid homepage layout with hero featured post and terminal-style feed
- Sidebar table of contents for blog posts with active section highlighting
- Terminal grep-style search functionality
- Dark/light theme toggle with system preference detection
- Giscus comments integration for blog posts
- Pagination support for post listings
- Reading progress bar for blog posts
- Mobile-responsive design with hamburger menu
- Docker Compose setup for development and production environments
- Traefik reverse proxy integration for production deployment
- GitHub Actions workflows for automated releases and deployments
- Migration script for 16 Nuxt Content posts to Ghost JSON format
- Tag assignment and categorization for migrated posts
- Custom About page with developer profile

### Fixed
- Mobile layout issues with sidebar visibility
- Mobile menu overlay z-index stacking
- Content overflow on mobile screens
- Post grid responsiveness on small devices
- MySQL root password environment variable configuration

### Infrastructure
- Production deployment at `/home/cativo23/deploy/ghost-blog-deploy`
- Automated release workflow triggered by PR merge from `release/*` branches
- Automated deployment workflow triggered by GitHub Release publication
- Docker-based Ghost 5 setup with MySQL 8 database
- Traefik integration with external `space-server_web` network
