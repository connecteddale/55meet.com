---
phase: 10-foundation
plan: 02
subsystem: database
tags: [sqlalchemy, sqlite, orm, wal-mode]
dependency-graph:
  requires: [10-01]
  provides: [database-engine, orm-models, session-dependency, wal-mode]
  affects: [10-03, 10-04, 10-05]
tech-stack:
  added: [sqlalchemy-2.0.36]
  patterns: [session-per-request, declarative-base, orm-relationships]
key-files:
  created: [the55/app/db/database.py, the55/app/db/models.py]
  modified: [the55/app/db/__init__.py, the55/app/dependencies.py, the55/app/main.py, the55/requirements.txt]
decisions:
  - {id: d10-02-01, choice: "SQLAlchemy ORM", reason: "Plan specified SQLAlchemy for type-safe models with relationships", impact: "All database access through SQLAlchemy Session"}
metrics:
  duration: 2m
  completed: 2026-01-18
---

# Phase 10 Plan 02: Database Models Summary

SQLite database layer with SQLAlchemy ORM models for teams, members, sessions, and responses. WAL mode enabled for concurrent access.

## What Was Built

### Database Engine (database.py)

```python
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine(
    "sqlite:///db/the55.db",
    connect_args={"check_same_thread": False}
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA busy_timeout=5000")
    cursor.close()
```

Key features:
- WAL mode for concurrent reads/writes
- busy_timeout=5000ms for lock contention
- check_same_thread=False for FastAPI compatibility

### ORM Models (models.py)

| Model | Purpose | Key Fields |
|-------|---------|------------|
| Team | Group participating in diagnostics | company_name, team_name, code (unique), strategy_statement |
| Member | Individual in a team | name, team_id (FK) |
| Session | Monthly diagnostic instance | team_id (FK), month ("YYYY-MM"), state (enum), synthesis_* fields |
| Response | Participant submission | session_id (FK), member_id (FK), image_number (1-55), bullets (JSON) |

### Session State Machine

```
DRAFT -> CAPTURING -> CLOSED -> REVEALED
```

```python
class SessionState(enum.Enum):
    DRAFT = "draft"
    CAPTURING = "capturing"
    CLOSED = "closed"
    REVEALED = "revealed"
```

### Dependencies (dependencies.py)

```python
from app.db.database import get_db
DbDep = Annotated[Session, Depends(get_db)]
```

Usage in routes:
```python
@router.get("/teams")
def list_teams(db: DbDep):
    return db.query(Team).all()
```

## Database Schema

```sql
CREATE TABLE teams (
    id INTEGER PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    team_name VARCHAR(255) NOT NULL,
    code VARCHAR(20) NOT NULL UNIQUE,
    strategy_statement TEXT,
    created_at DATETIME,
    updated_at DATETIME
);

CREATE TABLE members (
    id INTEGER PRIMARY KEY,
    team_id INTEGER NOT NULL REFERENCES teams(id),
    name VARCHAR(255) NOT NULL,
    created_at DATETIME
);

CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    team_id INTEGER NOT NULL REFERENCES teams(id),
    month VARCHAR(7) NOT NULL,
    state VARCHAR(9) NOT NULL,
    synthesis_themes TEXT,
    synthesis_statements TEXT,
    synthesis_gap_type VARCHAR(50),
    facilitator_notes TEXT,
    recalibration_action TEXT,
    recalibration_completed BOOLEAN,
    created_at DATETIME,
    closed_at DATETIME,
    revealed_at DATETIME
);

CREATE TABLE responses (
    id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES sessions(id),
    member_id INTEGER NOT NULL REFERENCES members(id),
    image_number INTEGER NOT NULL,
    bullets TEXT NOT NULL,
    submitted_at DATETIME,
    updated_at DATETIME
);
```

## Commits

| Hash | Type | Description |
|------|------|-------------|
| 31d88cc | feat | Create database engine and session management |
| b681df5 | feat | Create ORM models |
| 3d66e62 | feat | Initialize database on startup |

## Decisions Made

| ID | Decision | Rationale |
|----|----------|-----------|
| d10-02-01 | SQLAlchemy ORM | Plan specified SQLAlchemy for type-safe models with cascade relationships |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added SQLAlchemy to requirements.txt**
- **Found during:** Task 1
- **Issue:** SQLAlchemy not in requirements.txt, `ModuleNotFoundError`
- **Fix:** Added `sqlalchemy==2.0.36` to requirements.txt and installed
- **Files modified:** requirements.txt
- **Commit:** 31d88cc

## Verification Results

- [x] database.py creates engine with WAL mode pragma
- [x] models.py defines Team, Member, Session, Response
- [x] SessionState enum has all four states (DRAFT, CAPTURING, CLOSED, REVEALED)
- [x] Tables created in SQLite database
- [x] WAL mode confirmed active (`PRAGMA journal_mode` returns `wal`)
- [x] dependencies.py exports DbDep

## Database File

```
/var/www/the55/db/the55.db (40KB)
/var/www/the55/db/the55.db-wal (WAL file)
```

## Next Phase Readiness

Ready for Plan 10-03 (Base templates). Database layer provides:
- All models for team, member, session, response entities
- Session-per-request pattern via DbDep dependency
- State machine enum for session lifecycle
- WAL mode for concurrent participant access during capture
