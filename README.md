# The 55

**Leadership alignment diagnostics - 55 minutes, once a month.**

The 55 is a real-time facilitation tool that helps leadership teams catch alignment problems before they become execution problems. Teams meet monthly to surface how they're *actually* executing their strategy, identify gaps, and commit to one recalibration action.

## The 55 Meeting Flow

1. **Capture (5 min)** - Participants select an image representing their current state and explain why in 1-5 bullet points
2. **Surface (10 min)** - AI synthesizes responses into themes, insights, and diagnoses the gap type
3. **Read (25 min)** - Facilitator leads discussion through the synthesis
4. **Set (15 min)** - Team commits to ONE recalibration action

## Gap Types

The 55 diagnoses one of three gap types:

- **Direction** - Team lacks shared understanding of goals or priorities
- **Alignment** - Team's work is disconnected or uncoordinated
- **Commitment** - Individual interests override collective success

## Quick Start

### Prerequisites

- Python 3.11+
- SQLite 3
- Anthropic API key (for AI synthesis)

### Installation

```bash
# Clone and enter directory
cd the55

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your values (see Configuration below)

# Run development server
uvicorn app.main:app --reload --port 8055
```

Visit http://localhost:8055/health to verify.

## Configuration

Create `.env` file with:

```env
# Required
SECRET_KEY=your-secret-key-min-32-chars
FACILITATOR_PASSWORD_HASH=argon2-hash-of-password
ANTHROPIC_API_KEY=sk-ant-...

# Optional (defaults shown)
DEBUG=false
DATABASE_URL=sqlite:///db/the55.db
IMAGE_LIBRARY_PATH=app/static/images/library/reducedlive
IMAGES_PER_PAGE=42
IMAGE_CACHE_TTL=300
```

### Generating Password Hash

```python
from pwdlib import PasswordHash
hasher = PasswordHash.recommended()
print(hasher.hash("your-password"))
```

## Project Structure

```
the55/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Pydantic settings
│   ├── dependencies.py      # Auth & DB dependencies
│   ├── routers/
│   │   ├── admin.py         # Dashboard routes
│   │   ├── auth.py          # Login/logout
│   │   ├── teams.py         # Team CRUD
│   │   ├── members.py       # Member management
│   │   ├── sessions.py      # Session control & synthesis
│   │   ├── participant.py   # Participant flow (join, respond)
│   │   ├── images.py        # Image browser API
│   │   └── qr.py            # QR code generation
│   ├── services/
│   │   ├── auth.py          # Password verification
│   │   ├── images.py        # Image library with caching
│   │   └── synthesis.py     # Claude API integration
│   ├── db/
│   │   ├── database.py      # SQLAlchemy setup
│   │   └── models.py        # ORM models
│   ├── schemas/
│   │   └── __init__.py      # Pydantic schemas for Claude
│   ├── templates/           # Jinja2 HTML templates
│   └── static/
│       ├── css/main.css     # All styles
│       ├── js/              # Client-side scripts
│       └── images/library/  # 200+ evocative images
├── db/
│   └── the55.db             # SQLite database
├── logs/                    # Access & error logs
├── nginx/                   # nginx config
├── scripts/                 # Utility scripts
├── requirements.txt
├── .env.example
└── README.md
```

## Database Schema

### Teams
- `id`, `company_name`, `team_name`, `code` (unique join code)
- `strategy_statement` - The "3AM test" statement
- `image_prompt`, `bullet_prompt` - Customizable participant prompts

### Members
- `id`, `team_id`, `name`

### Sessions
- `id`, `team_id`, `month` (YYYY-MM format)
- `state` - draft → capturing → closed → revealed
- `synthesis_themes`, `synthesis_statements` (JSON), `synthesis_gap_type`, `synthesis_gap_reasoning`
- `facilitator_notes`, `recalibration_action` with timestamps

### Responses
- `id`, `session_id`, `member_id`
- `image_id` (filename stem), `bullets` (JSON array)

## Session State Machine

```
DRAFT → CAPTURING → CLOSED → REVEALED
          ↑____________|
          (reopen)
```

- **DRAFT**: Session created, not yet started
- **CAPTURING**: Participants can join and submit responses
- **CLOSED**: Capture complete, synthesis can be generated
- **REVEALED**: Synthesis visible to participants (optional)

## Key User Flows

### Facilitator Flow
1. Login at `/admin`
2. Create team with members
3. Start session for a team/month
4. Share QR code or team code with participants
5. Monitor submissions in real-time
6. Close capture when ready
7. Generate AI synthesis
8. Lead discussion, record notes
9. Set recalibration action

### Participant Flow
1. Scan QR or visit `/join` with team code
2. Select name from team roster
3. View strategy statement
4. Browse images, select one
5. Enter 1-5 bullet points explaining choice
6. Submit and wait for reveal

## API Endpoints

### Public
- `GET /` - Landing page
- `GET /join` - Participant entry
- `GET /health` - Health check

### Facilitator (requires auth)
- `GET /admin` - Dashboard
- `GET /admin/sessions/{id}` - Session control
- `POST /admin/sessions/{id}/synthesize` - Trigger AI synthesis
- `GET /admin/sessions/{id}/export/markdown` - Export report

### Participant (no auth)
- `POST /participant/join` - Join session
- `GET /participant/respond/{session_id}` - Image browser
- `POST /participant/submit` - Submit response

## Production Deployment

### Systemd Service

```ini
[Unit]
Description=The 55 - Leadership Alignment Diagnostics
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/the55
Environment="PATH=/var/www/the55/venv/bin"
ExecStart=/var/www/the55/venv/bin/gunicorn app.main:app \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8055 \
    --access-logfile /var/www/the55/logs/access.log \
    --error-logfile /var/www/the55/logs/error.log
Restart=always

[Install]
WantedBy=multi-user.target
```

### nginx Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name 55meet.com;

    location / {
        proxy_pass http://127.0.0.1:8055;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /var/www/the55/app/static/;
        expires 7d;
    }
}
```

## AI Synthesis

The synthesis uses Claude (Sonnet) to analyze team responses and generate:

1. **Themes** - 2-4 sentence summary of what the team is experiencing
2. **Attributed Statements** - Specific insights with participant names
3. **Gap Diagnosis** - Direction, Alignment, or Commitment
4. **Rationale** - Why this gap type was diagnosed

The prompt includes the team's strategy statement and all participant responses (image selection + bullet points).

## Image Library

- 200+ evocative, metaphorical images
- Auto-discovered from `IMAGE_LIBRARY_PATH` directory
- Session-seeded randomization (consistent order per session)
- 5-minute cache TTL for performance
- Web-optimized versions in `/reducedlive/` subdirectory

## Browser Compatibility

Tested on:
- Chrome, Safari, Firefox (desktop)
- iOS Safari, Chrome (mobile)
- Samsung Internet, Chrome (Android)

Targets devices from the last 3-4 years.

## License

Private - ConnectedDale
