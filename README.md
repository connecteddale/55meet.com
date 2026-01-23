# 55meet.com (The 55)

Leadership alignment diagnostics tool.

## Overview

- **Domains**: 55meet.com, 55.connecteddale.com
- **Type**: FastAPI application
- **Port**: 8055
- **Service**: the55

## Purpose

"The 55" is a team alignment diagnostic tool that helps leadership teams:
1. Surface individual perspectives on strategy
2. Identify alignment and gaps
3. Facilitate meaningful conversations
4. Track evolution over time

## How It Works

1. **Setup**: Create a team and add members
2. **Session**: Start a monthly session
3. **Respond**: Members select images and provide bullets
4. **Reveal**: Show all responses together
5. **Synthesize**: AI generates themes and identifies gaps
6. **Recalibrate**: Take action on misalignments

## Directory Structure

```
/var/www/sites/55meet.com/
├── app/
│   ├── main.py            # FastAPI application entry
│   ├── config.py          # Configuration
│   ├── dependencies.py    # Dependency injection
│   ├── routers/           # API route modules
│   │   ├── teams.py
│   │   ├── sessions.py
│   │   ├── members.py
│   │   └── responses.py
│   ├── schemas/           # Pydantic models
│   ├── services/          # Business logic
│   └── db/                # Database models
├── templates/             # Jinja2 HTML templates
├── static/                # CSS, JS, images
│   ├── css/
│   ├── js/
│   └── images/
├── db/
│   └── the55.db           # SQLite database
├── logs/
│   ├── access.log
│   ├── error.log
│   ├── nginx_access.log
│   └── nginx_error.log
├── scripts/               # Utility scripts
├── venv/                  # Python virtual environment
├── requirements.txt
└── .env                   # Environment variables
```

## Database Schema

### teams
Leadership teams using the system.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| company_name | VARCHAR | Company/organization |
| team_name | VARCHAR | Team name |
| code | VARCHAR | Unique access code |
| strategy_statement | TEXT | Team's strategy statement |
| image_prompt | TEXT | AI prompt for image generation |
| bullet_prompt | TEXT | AI prompt for bullet themes |

### members
Team members.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| team_id | INTEGER | Foreign key to teams |
| name | VARCHAR | Member name |

### sessions
Monthly diagnostic sessions.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| team_id | INTEGER | Foreign key to teams |
| month | VARCHAR | "YYYY-MM" format |
| state | VARCHAR | 'active', 'revealed', 'closed' |
| synthesis_themes | TEXT | AI-generated themes |
| synthesis_statements | TEXT | Key alignment statements |
| synthesis_gap_type | VARCHAR | Type of gap identified |
| synthesis_gap_reasoning | TEXT | Explanation of gap |
| suggested_recalibrations | TEXT | Recommended actions |
| facilitator_notes | TEXT | Notes from session |
| recalibration_action | TEXT | Chosen action |
| recalibration_completed | BOOLEAN | Action completed |

### responses
Individual member responses.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| session_id | INTEGER | Foreign key to sessions |
| member_id | INTEGER | Foreign key to members |
| image_id | VARCHAR | Selected image identifier |
| bullets | TEXT | Member's bullet points |

## Key Endpoints

### Public Pages
- `/` - Landing page
- `/health` - Health check endpoint
- `/team/{code}` - Team dashboard
- `/session/{code}` - Current session
- `/respond/{code}/{member_id}` - Member response form

### API Routes
- `POST /api/teams` - Create team
- `GET /api/teams/{code}` - Get team info
- `POST /api/sessions` - Create session
- `POST /api/responses` - Submit response
- `POST /api/sessions/{id}/reveal` - Reveal responses
- `POST /api/sessions/{id}/synthesize` - Generate AI synthesis
- `POST /api/sessions/{id}/close` - Close session

### Facilitator
- `/facilitator/{code}` - Facilitator view
- `/synthesis/{session_id}` - Synthesis results

## Configuration

### Environment Variables (.env)

```bash
OPENAI_API_KEY=...       # For AI synthesis
SECRET_KEY=...           # Session security
DATABASE_URL=...         # SQLite path
```

### Nginx Config

`/etc/nginx/sites-available/55.connecteddale.com`

### Systemd Service

`/etc/systemd/system/the55.service`

## Common Tasks

### Restart Application

```bash
sudo systemctl restart the55
```

### View Logs

```bash
# Application logs
tail -f /var/www/sites/55meet.com/logs/error.log

# Nginx logs
tail -f /var/www/sites/55meet.com/logs/nginx_access.log
```

### Database Access

```bash
sqlite3 /var/www/sites/55meet.com/db/the55.db

# Useful queries
SELECT id, company_name, team_name, code FROM teams;
SELECT id, team_id, month, state FROM sessions ORDER BY created_at DESC LIMIT 10;
SELECT m.name, r.image_id FROM responses r JOIN members m ON r.member_id = m.id WHERE r.session_id = X;
```

### Create New Team (via API)

```bash
curl -X POST https://55meet.com/api/teams \
  -H "Content-Type: application/json" \
  -d '{"company_name": "Acme Corp", "team_name": "Executive Team", "code": "ACME123"}'
```

### Check Health

```bash
curl https://55meet.com/health
# Returns: {"status": "healthy"}
```

## Session States

```
active → revealed → closed
```

- **active**: Members can submit/update responses
- **revealed**: All responses visible, synthesis available
- **closed**: Session archived, cannot modify

## Troubleshooting

### Session stuck in wrong state

```sql
-- Check current state
SELECT id, month, state FROM sessions WHERE team_id = X ORDER BY created_at DESC;

-- Update if needed (use carefully)
UPDATE sessions SET state = 'active' WHERE id = Y;
```

### AI synthesis not working

1. Check OpenAI API key in `.env`
2. Check logs for API errors:
   ```bash
   grep -i openai /var/www/sites/55meet.com/logs/error.log
   ```

### Member can't access response form

1. Verify member exists:
   ```sql
   SELECT * FROM members WHERE team_id = X;
   ```
2. Verify session is active:
   ```sql
   SELECT state FROM sessions WHERE team_id = X ORDER BY created_at DESC LIMIT 1;
   ```

### 502 Bad Gateway

```bash
sudo systemctl status the55
sudo systemctl restart the55
journalctl -u the55 -n 50
```

## Architecture Notes

- FastAPI with async support
- Jinja2 templates for server-rendered HTML
- SQLAlchemy ORM for database
- OpenAI API for synthesis features
- Uvicorn as ASGI server (via Gunicorn)
