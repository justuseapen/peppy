# CLAUDE.md — Peppy

## Project Overview

Peppy is a Giphy-clone web application built with **Flask** (Python) and **Vanilla JavaScript**. It provides image/GIF search, browsing by category, trending GIFs, image uploading with duplicate detection, and tag management. The app uses in-memory mock data (no external database for image metadata) and Replit's key-value database (`replit.db`) for storing uploaded file binary data.

## Tech Stack

- **Backend:** Python 3.9+, Flask 2.3
- **Frontend:** Vanilla JavaScript, Tailwind CSS (loaded via CDN), custom CSS
- **Image Processing:** Pillow (PIL), imagehash (perceptual hashing for duplicate detection)
- **Storage:** Replit DB for uploaded file data (base64-encoded), in-memory lists for image metadata
- **Package Management:** Poetry (`pyproject.toml` / `poetry.lock`)
- **Deployment Target:** Replit (configured via `.replit` and `replit.nix`)

## Project Structure

```
peppy/
├── main.py                  # Flask app entry point — registers blueprints, serves index
├── config.py                # Config class (SECRET_KEY, upload limits, allowed extensions)
├── mock_data.py             # Extended mock image dataset with hash utilities (older copy)
├── routes/
│   ├── __init__.py
│   ├── search_routes.py     # GET /api/search, /api/trending, /api/untagged
│   ├── upload_routes.py     # POST /api/upload, GET /api/image/<filename>, POST /api/add_tags
│   └── category_routes.py   # GET /api/categories, /api/category/<category>
├── services/
│   ├── __init__.py
│   └── image_service.py     # Core logic: MOCK_IMAGES list, IMAGE_HASHES, duplicate detection,
│                            #   add_uploaded_image(), add_tags_to_image(), is_duplicate_image()
├── static/
│   ├── css/styles.css       # Custom styles (image hover, tags, sections, bulk upload)
│   ├── js/app.js            # Client-side SPA logic (search, trending, categories, upload, modals)
│   └── uploads/             # (Unused — uploads go to Replit DB instead)
├── templates/
│   └── index.html           # Single-page Jinja2 template with Tailwind CSS
├── tests/
│   └── __init__.py          # Test package (currently empty — no tests written)
├── pyproject.toml           # Poetry project config & dependencies
├── poetry.lock              # Locked dependency versions
├── replit.nix               # Nix dependencies (image libs, PostgreSQL client)
└── .replit                  # Replit workflow config (runs `python main.py` on port 5000)
```

## How to Run

```bash
# Install dependencies
poetry install

# Run the development server
python main.py
```

The app starts on `http://0.0.0.0:5000`. Debug mode is controlled by the `FLASK_DEBUG` environment variable.

## Architecture & Key Patterns

### Flask Blueprints

The app uses three Flask blueprints registered in `main.py`:

| Blueprint       | Prefix | File                        | Purpose                              |
|-----------------|--------|-----------------------------|--------------------------------------|
| `search_bp`     | —      | `routes/search_routes.py`   | Search, trending, untagged endpoints |
| `upload_bp`     | —      | `routes/upload_routes.py`   | File upload, image serving, tagging  |
| `category_bp`   | —      | `routes/category_routes.py` | Category listing and filtering       |

### API Endpoints

| Method | Endpoint                    | Description                                    |
|--------|-----------------------------|------------------------------------------------|
| GET    | `/`                         | Serves the main HTML page                      |
| GET    | `/api/search?q=&offset=&limit=` | Search images by title or tags (paginated) |
| GET    | `/api/trending?limit=`      | Random selection of mock images                |
| GET    | `/api/untagged`             | Images with empty tags list                    |
| GET    | `/api/categories`           | Returns category name list                     |
| GET    | `/api/category/<name>`      | Filter images by category tag (paginated)      |
| POST   | `/api/upload`               | Upload image file (multipart form, optional tags) |
| GET    | `/api/image/<filename>`     | Serve uploaded image from Replit DB             |
| POST   | `/api/add_tags`             | Add tags to an image (JSON body: image_id, tags) |

### Data Model

Images are plain dictionaries stored in the `MOCK_IMAGES` list (`services/image_service.py`):

```python
{
    "id": "1",
    "title": "Happy Cat",
    "tags": ["cat", "happy", "cute"],
    "images": {
        "fixed_height": {"url": "https://...200.gif"},
        "original": {"url": "https://...giphy.gif"}
    }
}
```

There is no persistent database for metadata — `MOCK_IMAGES` is an in-memory list that resets on server restart. Uploaded file binary data is stored in Replit DB via base64 encoding.

### Duplicate Detection

Uses `imagehash` (perceptual average hashing) to detect duplicate uploads. A hash difference threshold of `<= 5` is considered a duplicate. Hashes are stored in the `IMAGE_HASHES` list in `services/image_service.py`.

### Frontend Architecture

- Single HTML page (`templates/index.html`) with Jinja2 templating for category buttons
- All interactivity handled in `static/js/app.js` (vanilla JS, no framework)
- Debounced search input with infinite scroll pagination
- Sections: Trending GIFs, Categories, Untagged Assets, Search Results
- Modal for full-size image viewing and inline tag editing
- Bulk upload with progress bar
- Tailwind CSS via CDN + custom styles in `static/css/styles.css`

## Development Conventions

### Code Style

- Python: Standard Flask patterns with type hints on route return types
- JavaScript: ES6+ (const/let, arrow functions, template literals, Promises)
- No linter or formatter is configured; follow existing code style
- Docstrings used on some route functions (Google style)

### Adding a New API Endpoint

1. Create or edit a route file in `routes/`
2. Define a Flask Blueprint (or add to an existing one)
3. Register the blueprint in `main.py` if new
4. Add corresponding fetch calls in `static/js/app.js`

### Adding New Mock Data

Edit `services/image_service.py` — add entries to the `MOCK_IMAGES` list following the existing dictionary structure. Note: `mock_data.py` at the root is an older copy and is **not** imported by the application.

### File Uploads

Uploaded files are stored as base64 in Replit DB (not on the filesystem). The `static/uploads/` directory exists but is unused. Allowed file types: PNG, JPG, JPEG, GIF, WebP. Max upload size: 16 MB.

## Important Notes

- **No tests exist yet.** The `tests/` directory contains only an empty `__init__.py`. When adding tests, use Flask's test client (`app.test_client()`).
- **`mock_data.py` (root) vs `services/image_service.py`:** The root `mock_data.py` is a stale duplicate. The app imports from `services/image_service.py` — always edit that file.
- **Replit DB dependency:** `upload_routes.py` and `image_service.py` import `from replit import db`. This only works in a Replit environment. For local development outside Replit, this would need to be mocked or replaced.
- **No authentication or authorization** is implemented on any endpoint.
- **In-memory state:** All image metadata (`MOCK_IMAGES`, `IMAGE_HASHES`) lives in memory and is lost on restart. Only uploaded file binaries persist in Replit DB.
- The `Pasted-*.txt` files in the root are development reference notes, not part of the application.
