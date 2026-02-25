# CLAUDE.md — Peppy

## Project Overview

Peppy is a Giphy-clone web application built with **Flask** (Python backend) and **Vanilla JavaScript** (frontend). It allows users to browse trending GIFs, search by keyword/tag, upload images (including bulk upload), manage tags, and browse by category. Image data is stored in-memory with uploaded files persisted via Replit's key-value database.

## Tech Stack

- **Backend**: Python 3.11, Flask 2.3+
- **Frontend**: Vanilla JS, Tailwind CSS (CDN), custom CSS
- **Package Manager**: Poetry (`pyproject.toml` / `poetry.lock`)
- **Image Processing**: Pillow (PIL) + imagehash (perceptual duplicate detection)
- **Storage**: Replit DB (`replit` package) for uploaded image binary data (base64-encoded)
- **Hosting**: Designed for Replit (see `.replit`, `replit.nix`)

## Repository Structure

```
peppy/
├── main.py                  # Flask app entry point — registers blueprints, serves index
├── config.py                # Config class (SECRET_KEY, UPLOAD_FOLDER, MAX_CONTENT_LENGTH, ALLOWED_EXTENSIONS)
├── mock_data.py             # Legacy mock data file (superseded by services/image_service.py)
├── routes/
│   ├── __init__.py
│   ├── search_routes.py     # GET /api/search, /api/trending, /api/untagged
│   ├── upload_routes.py     # POST /api/upload, GET /api/image/<filename>, POST /api/add_tags
│   └── category_routes.py   # GET /api/categories, /api/category/<category>
├── services/
│   ├── __init__.py
│   └── image_service.py     # Core data layer — MOCK_IMAGES list, IMAGE_HASHES, CRUD helpers
├── templates/
│   └── index.html           # Single-page Jinja2 template (Tailwind + custom CSS)
├── static/
│   ├── css/styles.css        # Custom styles (image hover, tags, section backgrounds)
│   ├── js/app.js             # Client-side JS — search, upload, trending, categories, infinite scroll
│   └── uploads/              # Local uploaded files (some test images present)
├── tests/
│   └── __init__.py           # Test package (tests not yet implemented)
├── pyproject.toml            # Poetry project definition and dependencies
├── poetry.lock               # Locked dependency versions
├── .replit                   # Replit run/deploy configuration
└── replit.nix                # Nix system dependencies (zlib, image libs, PostgreSQL client)
```

## Running the Application

```bash
# Install dependencies
poetry install

# Run the development server (listens on 0.0.0.0:5000)
python main.py
```

The app runs on **port 5000** in debug mode when `FLASK_DEBUG=true`.

## API Endpoints

| Method | Path                        | Description                              |
|--------|-----------------------------|------------------------------------------|
| GET    | `/`                         | Serves the main HTML page                |
| GET    | `/api/search?q=&offset=&limit=` | Search images by title or tag        |
| GET    | `/api/trending?limit=`      | Random selection of trending GIFs        |
| GET    | `/api/untagged`             | List images with no tags                 |
| GET    | `/api/categories`           | List all category names                  |
| GET    | `/api/category/<category>`  | Filter images by category tag            |
| POST   | `/api/upload`               | Upload an image (multipart form: `file`, `tags`) |
| GET    | `/api/image/<filename>`     | Serve an uploaded image from Replit DB   |
| POST   | `/api/add_tags`             | Add tags to an image (JSON: `image_id`, `tags`) |

## Architecture & Key Patterns

### Data Storage
- **In-memory**: `MOCK_IMAGES` list in `services/image_service.py` is the single source of truth for image metadata. Data resets on server restart.
- **Replit DB**: Uploaded image binary data is stored as base64 strings keyed by unique filename. Accessed via `from replit import db`.
- **No SQL database** is used. The `replit.nix` includes PostgreSQL but it is not wired up.

### Duplicate Detection
- Uses `imagehash.average_hash` on the first frame of uploaded images.
- Compares against `IMAGE_HASHES` list; a hash distance of <= 5 flags a duplicate.
- Implemented in `services/image_service.py:is_duplicate_image()`.

### Blueprint Organization
Routes are organized into Flask Blueprints registered in `main.py`:
- `search_bp` — search, trending, untagged
- `upload_bp` — file upload, image serving, tag management
- `category_bp` — category listing and filtering

### Frontend
- Single `index.html` template rendered by Flask with Jinja2.
- All interactivity in `static/js/app.js` — vanilla JS with fetch API calls.
- Uses Tailwind CSS via CDN for layout/utility classes, custom CSS in `static/css/styles.css`.
- Features: debounced search, infinite scroll pagination, bulk upload with progress bar, modal for full-size view + tag editing.

## Code Conventions

- **Python**: Standard Flask patterns, type hints on function signatures, docstrings on some routes.
- **JavaScript**: ES6+ (const/let, arrow functions, template literals, Promises). No build step or bundler.
- **File naming**: Snake_case for Python files. Route files named `<domain>_routes.py`.
- **Imports**: Service functions imported directly in route files (e.g., `from services.image_service import ...`).

## Important Caveats

1. **`mock_data.py` vs `services/image_service.py`**: Both files define `MOCK_IMAGES` and similar functions. The routes import from `services/image_service.py` — that is the active module. `mock_data.py` at the project root is legacy/unused by the running app.
2. **Replit dependency**: `upload_routes.py` and `services/image_service.py` import `from replit import db`. This will fail outside a Replit environment unless mocked.
3. **No persistent metadata**: All image metadata (titles, tags, IDs) lives in `MOCK_IMAGES` in-memory and is lost on restart. Only the raw image bytes persist in Replit DB.
4. **No tests**: The `tests/` directory exists but contains no test files beyond `__init__.py`.
5. **Allowed upload types**: png, jpg, jpeg, gif, webp (configured in `config.py`).
6. **Max upload size**: 16 MB (configured in `config.py`).
