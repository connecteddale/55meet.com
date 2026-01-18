# The 55 App

Leadership alignment diagnostics - 55 minutes, once a month.

## Overview

The 55 is a real-time facilitation tool that helps leadership teams catch alignment problems before they become execution problems.

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy and configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

3. Run development server:
   ```bash
   uvicorn app.main:app --reload --port 8055
   ```

4. Visit http://localhost:8055/health to verify.

## Project Structure

```
the55/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Pydantic settings
│   ├── dependencies.py      # Shared dependencies
│   ├── routers/             # Route handlers
│   ├── services/            # Business logic
│   ├── db/                  # Database models
│   ├── schemas/             # Pydantic schemas
│   ├── templates/           # Jinja2 templates
│   └── static/              # CSS, JS, images
├── db/                      # SQLite database
├── logs/                    # Application logs
├── requirements.txt
├── .env.example
└── README.md
```

## Production Deployment

```bash
gunicorn app.main:app \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8055
```

## License

Private - ConnectedDale
