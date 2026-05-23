# ReadLater

A bookmark manager for saving URLs to articles and websites you want to read later. Built with FastAPI, SQLAlchemy, and Three.js.

## Features

- Save URLs with auto-fetched title, description, and favicon
- Tag bookmarks and filter by tag
- Mark as read or archive
- Full-text search across titles, descriptions, and URLs
- 3D force-directed graph view — nodes are bookmarks, edges connect bookmarks that share tags

## Stack

- **Backend**: FastAPI, SQLAlchemy 2.0 (async), aiosqlite
- **Scraping**: httpx + BeautifulSoup
- **Frontend**: Vanilla JS ES modules, no build step
- **Graph**: Three.js with custom force-directed layout

## Getting started

```bash
cd readlater
uv sync
uv run uvicorn app.main:app --reload
```

Open http://localhost:8000. The database is created automatically on first run.

## Graph view

The graph view requires Three.js. Download `three.module.min.js` and `OrbitControls.js` from the [Three.js r165 release](https://github.com/mrdoob/three.js/releases/tag/r165) and place them in `static/js/vendor/`.

## API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/bookmarks` | Save a URL |
| `GET` | `/api/bookmarks` | List bookmarks (`?q=&tags=&is_read=&sort=&limit=&offset=`) |
| `GET` | `/api/bookmarks/{id}` | Get a bookmark |
| `PATCH` | `/api/bookmarks/{id}` | Update fields or tags |
| `DELETE` | `/api/bookmarks/{id}` | Delete a bookmark |
| `GET` | `/api/tags` | List all tags with counts |
| `POST` | `/api/tags` | Create a tag |
| `DELETE` | `/api/tags/{id}` | Delete a tag |
| `GET` | `/api/search?q=` | Full-text search |
| `GET` | `/api/bookmarks/graph` | Graph data (nodes + edges) |

Interactive docs at http://localhost:8000/docs.

## Running tests

```bash
cd readlater
uv sync --extra dev
uv run pytest
```
