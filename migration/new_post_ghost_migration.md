---
title: "Moving to Ghost: Why I Ditched Nuxt Content for a Real Blog"
slug: moving-to-ghost-why-i-ditched-nuxt-content
tags: ["ghost", "self-hosting", "blogging", "infrastructure", "migration"]
created_at: 2026-04-23T06:30:00.000Z
updated_at: 2026-04-23T06:30:00.000Z
---

# Moving to Ghost: Why I Ditched Nuxt Content for a Real Blog

My blog lived in my portfolio repo. Markdown files in `content/blog/`, rendered by Nuxt Content. It worked. Until it didn't.

## The Problem With Nuxt Content

**It's not a blog. It's a content renderer.**

Every time I wanted to write, I had to:
1. Open VS Code
2. Create a markdown file
3. Write frontmatter by hand
4. Commit and push
5. Wait for Vercel to rebuild the entire portfolio

Want to fix a typo? Full rebuild. Want to schedule a post? Write a script. Want comments? Integrate a third-party service. Want RSS? Build it yourself.

I wasn't blogging. I was maintaining a static site generator.

## Why Ghost

**Because it's a blog platform, not a framework.**

- **Admin UI**: Write in a browser. Edit published posts. No git commits for typos.
- **Scheduling**: Built-in. Write now, publish later.
- **API**: First-class. My portfolio can fetch latest posts without rebuilding.
- **Themes**: Handlebars templates. Full control, no framework overhead.
- **Self-hosted**: My server, my data, my rules.

Ghost does one thing: blogging. It does it well.

## Why Self-Hosted

**Because I already run the infrastructure.**

I have a server. It runs Docker. It has Traefik. Adding Ghost was:
- One `compose.prod.yml` file
- MySQL 5.7 container (because my CPU is old)
- Traefik labels for SSL
- Done

No monthly fees. No vendor lock-in. No "your plan doesn't include X" bullshit.

## The Migration

**17 posts. 42 tags. One Python script.**

```python
# Parse Nuxt Content markdown
frontmatter, body = parse_frontmatter(content)

# Convert to Ghost JSON
mobiledoc = {
    "version": "0.3.1",
    "cards": [["markdown", {"markdown": body}]],
    "sections": [[10, 0]]
}

# Export
export = {
    'db': [{
        'data': {
            'posts': posts,
            'tags': tags,
            'posts_tags': relationships
        }
    }]
}
```

Import via Ghost Admin API. Fix tags. Done.

## The Custom Theme

**Because default themes are boring.**

I built "cativo-terminal" with:
- Tokyo Night Storm palette
- Monospace fonts (Geist Mono)
- Terminal aesthetic (window chrome, cursor, prompt)
- Hybrid homepage (hero + feed)
- Sidebar TOC for posts
- Terminal grep-style search
- Dark/light mode

It looks like my GitHub profile README. Because consistency matters.

## The Infrastructure

**Docker Compose + Traefik + GitHub Actions.**

```yaml
services:
  ghost:
    image: ghost:5-alpine
    environment:
      database__client: mysql
      database__connection__host: db
      url: https://blog.cativo.dev
    depends_on:
      db:
        condition: service_healthy

  db:
    image: mysql:5.7
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 3s
      retries: 10
```

GitHub Actions for releases:
- Merge `release/*` to master → create GitHub Release
- Release published → deploy to production
- Theme zipped and uploaded as release asset

GitFlow workflow. Automated deploys. No manual steps.

## What I Learned

**Nuxt Content is great for documentation. Not for blogging.**

If you're building a blog:
- Use a blog platform (Ghost, WordPress, whatever)
- Don't build your own unless that's the project
- Self-hosting is easier than you think

If you're building documentation:
- Nuxt Content is perfect
- Keep it in the repo
- Version it with the code

## The Result

**blog.cativo.dev**

- 17 posts migrated
- Custom theme deployed
- Admin UI for writing
- API for portfolio integration
- RSS feed (built-in)
- Comments (Giscus)
- Search (terminal grep style)

I can write in a browser. Edit published posts. Schedule content. No rebuilds. No commits.

That's what a blog should be.

---

**Stack**: Ghost 5, MySQL 5.7, Docker, Traefik, GitHub Actions  
**Theme**: Custom Handlebars (Tokyo Night Storm)  
**Hosting**: Self-hosted on my server  
**Domain**: blog.cativo.dev

The code is on GitHub: [cativo23/ghost-blog](https://github.com/cativo23/ghost-blog)
