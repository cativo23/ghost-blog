# Blog Series UI Design

**Date:** 2026-04-24  
**Status:** Ready for implementation  
**Mockup:** See `/home/cativo23/projects/personal/portfolio/.superpowers/brainstorm/1190346-1776994981/content/series-ui-mockup.html`

## Context

The blog has several post series (Nova ID, Qwen/Claude setup, etc.) that currently have no visual indication they're part of a series. Posts are only grouped by tags, but there's no way for readers to:

1. See that a post is part of a series
2. Know which post in the series they're reading (1/8, 2/8, etc.)
3. Navigate to other posts in the same series

Additionally, when viewing the blog index, series posts appear consecutively which makes the blog feel repetitive. We want to intercalate non-series posts between series posts.

## Design Decision

**Approved approach:** Badge + collapsible series index

### Post Individual View (`post.hbs`)

1. **Series badge** above the title:
   - Format: `[Series Name] • [Position/Total]` (e.g., "Nova ID • 1/8")
   - Style: Magenta badge matching Tokyo Night theme
   - Only shows if post has series metadata

2. **Series index** at the bottom of post content (before comments):
   - Collapsible panel showing all posts in the series
   - Current post highlighted with "← estás aquí" indicator
   - Numbered list (1., 2., 3., etc.)
   - Links to other posts in series

### Blog Index View (`index.hbs`, `terminal-feed-row.hbs`)

- Small badge on the right side of each card: `[1/8]`, `[2/8]`, etc.
- Only shows for posts that are part of a series

## Ghost Implementation

### Required Custom Fields

Ghost posts need these custom fields (added via Ghost Admin → Settings → Code Injection or via API):

```yaml
series: "nova-id"           # Series slug (nullable)
series_position: 1          # Position in series (number)
series_label: "Nova ID"     # Display name for series
```

### Files to Modify

1. **`theme/post.hbs`**
   - Add series badge before title (line ~20)
   - Add series index partial before comments section (line ~83)

2. **`theme/partials/series-index.hbs`** (NEW FILE)
   - Collapsible series navigation component
   - Query all posts with same `series` value
   - Sort by `series_position`
   - Highlight current post

3. **`theme/partials/post-card.hbs`**
   - Add series badge to card header (conditional)

4. **`theme/partials/terminal-feed-row.hbs`**
   - Add series badge column (conditional)

5. **`theme/assets/css/post.css`**
   - Add styles for `.series-badge`
   - Add styles for `.series-index` component

## Visual Design (Tokyo Night Colors)

```css
/* Series Badge */
.series-badge {
  background: rgba(157, 124, 216, 0.15);
  border: 1px solid rgba(157, 124, 216, 0.3);
  color: #9d7cd8; /* --accent-magenta */
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.875rem;
}

/* Series Index */
.series-index {
  background: #292e42; /* --bg-elevated */
  border: 1px solid #414868; /* --border-primary */
  border-radius: 6px;
  margin-top: 3rem;
}

.series-item.current {
  background: rgba(158, 206, 106, 0.1);
  border-left: 3px solid #9ece6a; /* --accent-green */
}
```

## Ghost Handlebars Queries

To get all posts in a series:

```handlebars
{{#get "posts" filter="data.series:{{series}}" include="data" limit="all"}}
  {{#foreach posts}}
    {{!-- Sort by data.series_position --}}
  {{/foreach}}
{{/get}}
```

**Note:** Ghost's `#get` helper doesn't support sorting by custom fields directly. You'll need to either:
- Sort in JavaScript after fetching
- Use a custom helper
- Rely on posts being created in order

## Implementation Steps

1. **Add custom fields to Ghost posts**
   - Go through Nova ID series (8 posts) and add series metadata
   - Test with one post first

2. **Create `series-index.hbs` partial**
   - Query posts by series
   - Render collapsible list
   - Add toggle functionality (JavaScript)

3. **Modify `post.hbs`**
   - Add series badge conditional
   - Include series-index partial

4. **Modify `post-card.hbs` and `terminal-feed-row.hbs`**
   - Add series badge to cards

5. **Add CSS styles**
   - Series badge styles
   - Series index component styles
   - Hover states and transitions

6. **Test**
   - View a series post → badge and index should appear
   - View a non-series post → no badge or index
   - Click series links → navigation works
   - Mobile responsive check

## Nova ID Series Posts to Tag

These posts need series metadata added:

1. Day 1: Why Traditional Security Is Bullshit (Jan 15)
2. Day 2-3: Docker Compose Hell (Jan 16)
3. Day 4-5: When a General Gets a 403 (Jan 18)
4. Day 6-8: Fighting Vue's Reactivity System (Jan 20)
5. Day 9-15: Seven Days of Everything Breaking (Jan 23)
6. Day 16: Is This Thing Production-Ready? (Jan 30)
7. Day 17: Tearing the Frontend Apart (Jan 31)
8. Day 18: Proving Zero Trust Actually Works (Feb 1)

## Open Questions

- Should the series index be expanded by default or collapsed?
- Should we add "Previous/Next" navigation buttons in addition to the index?
- How to handle series with 10+ posts? (pagination in index?)

## References

- Mockup: `.superpowers/brainstorm/content/series-ui-mockup.html` (open in browser to see design)
- Ghost Custom Fields: https://ghost.org/docs/themes/helpers/get/
- Tokyo Night colors: `theme/assets/css/tokyo-night.css`
