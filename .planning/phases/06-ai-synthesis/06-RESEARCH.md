# Phase 15: AI Synthesis - Research

**Researched:** 2026-01-19
**Domain:** Claude API integration, prompt engineering for team response synthesis
**Confidence:** HIGH

## Summary

This phase integrates Claude API to synthesize team responses into actionable insights. The existing architecture uses FastAPI with async support, and the anthropic SDK 0.76.0 is already installed. The synthesis must produce three outputs: high-level themes (2-4 sentences), attributed statements linking insights to participant names, and a gap diagnosis (Direction, Alignment, or Commitment).

The primary technical decision is whether to use FastAPI's built-in `BackgroundTasks` or a dedicated task queue like Celery. Given the constraints (single facilitator, max 25 team members, infrequent synthesis calls), `BackgroundTasks` is sufficient and simpler. Claude API calls typically complete within 10-30 seconds for this workload, well within acceptable limits.

**Primary recommendation:** Use AsyncAnthropic client with FastAPI BackgroundTasks for synthesis. Store synthesis results directly in the existing Session model fields (synthesis_themes, synthesis_statements, synthesis_gap_type). Poll for completion using the existing participant status endpoint pattern.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| anthropic | 0.76.0 | Claude API client | Official Anthropic SDK, already in requirements.txt |
| FastAPI BackgroundTasks | built-in | Async background processing | Simple, sufficient for single-user scenario |
| Pydantic | via pydantic-settings | Response schema validation | Already in stack, type-safe parsing |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| AsyncAnthropic | in anthropic | Async API calls | Non-blocking synthesis within FastAPI |
| json | stdlib | Parse/serialize bullets | Already used in participant.py |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| BackgroundTasks | Celery | Celery adds Redis/RabbitMQ dependency; overkill for single facilitator |
| BackgroundTasks | asyncio.create_task | Doesn't survive request lifecycle properly |
| Sync Anthropic | Blocking call | Blocks event loop; unacceptable for production |

**Installation:**
No additional packages needed - anthropic 0.76.0 already in requirements.txt.

## Architecture Patterns

### Recommended Project Structure
```
the55/app/
├── services/
│   ├── __init__.py
│   └── synthesis.py       # Claude API integration, prompt logic
├── routers/
│   ├── sessions.py        # Add synthesis trigger endpoint
│   └── participant.py     # Add synthesis view endpoint
├── templates/
│   └── participant/
│       └── synthesis.html # Synthesis display view
```

### Pattern 1: Async Claude API Integration
**What:** Use AsyncAnthropic client for non-blocking API calls within FastAPI
**When to use:** All Claude API calls in this project
**Example:**
```python
# Source: https://github.com/anthropics/anthropic-sdk-python/blob/main/README.md
from anthropic import AsyncAnthropic

client = AsyncAnthropic()  # Uses ANTHROPIC_API_KEY env var

async def generate_synthesis(responses: list[dict], strategy_statement: str) -> dict:
    """Generate synthesis from team responses."""
    message = await client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": build_synthesis_prompt(responses, strategy_statement)
        }]
    )
    return parse_synthesis_response(message.content[0].text)
```

### Pattern 2: Background Task for Long-Running Synthesis
**What:** Use FastAPI BackgroundTasks to avoid blocking HTTP response
**When to use:** When facilitator triggers synthesis after closing capture
**Example:**
```python
# Source: https://fastapi.tiangolo.com/tutorial/background-tasks/
from fastapi import BackgroundTasks

@router.post("/{session_id}/synthesize")
async def trigger_synthesis(
    session_id: int,
    background_tasks: BackgroundTasks,
    auth: AuthDep,
    db: DbDep
):
    """Start synthesis generation in background."""
    session = get_session_or_404(session_id, db)

    # Validate state: must be CLOSED
    if session.state != SessionState.CLOSED:
        raise HTTPException(400, "Session must be closed before synthesis")

    # Add background task (use def, not async def, to avoid timeout issues)
    background_tasks.add_task(
        run_synthesis_task,  # def function, not async
        session_id=session_id
    )

    return {"status": "synthesis_started", "session_id": session_id}
```

### Pattern 3: Synchronous Background Task Wrapper
**What:** Wrap async Claude call in sync function for BackgroundTasks
**When to use:** Prevents WORKER TIMEOUT with Gunicorn/Uvicorn
**Example:**
```python
# Source: https://github.com/fastapi/fastapi/discussions/5956
import asyncio

def run_synthesis_task(session_id: int):
    """Sync wrapper for background task - avoids event loop issues."""
    # Create new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(generate_and_store_synthesis(session_id))
    finally:
        loop.close()

async def generate_and_store_synthesis(session_id: int):
    """Async function that does the actual work."""
    # Get database session
    db = SessionLocal()
    try:
        session = db.query(Session).filter(Session.id == session_id).first()
        if not session:
            return

        # Get responses
        responses = db.query(Response).filter(
            Response.session_id == session_id
        ).all()

        # Call Claude
        result = await generate_synthesis(
            responses=[{
                "name": r.member.name,
                "image_number": r.image_number,
                "bullets": json.loads(r.bullets)
            } for r in responses],
            strategy_statement=session.team.strategy_statement
        )

        # Store results
        session.synthesis_themes = result["themes"]
        session.synthesis_statements = json.dumps(result["statements"])
        session.synthesis_gap_type = result["gap_type"]
        db.commit()
    finally:
        db.close()
```

### Pattern 4: Structured JSON Output with Pydantic
**What:** Use Claude's structured output for guaranteed schema compliance
**When to use:** For synthesis response parsing
**Example:**
```python
# Source: https://platform.claude.com/docs/en/build-with-claude/structured-outputs
from pydantic import BaseModel
from typing import List

class AttributedStatement(BaseModel):
    statement: str
    participants: List[str]  # Names of contributing participants

class SynthesisOutput(BaseModel):
    themes: str  # 2-4 sentences of high-level themes
    statements: List[AttributedStatement]  # Statements with attribution
    gap_type: str  # "Direction", "Alignment", or "Commitment"
    gap_reasoning: str  # Brief explanation of gap diagnosis

# With beta structured outputs (recommended for production reliability)
from anthropic import transform_schema

response = await client.beta.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=2048,
    betas=["structured-outputs-2025-11-13"],
    messages=[{"role": "user", "content": prompt}],
    output_format={
        "type": "json_schema",
        "schema": transform_schema(SynthesisOutput)
    }
)
```

### Anti-Patterns to Avoid
- **Blocking sync Claude calls in async endpoints:** Blocks entire event loop, degrades all requests
- **Using async def for BackgroundTasks with external API:** Can cause WORKER TIMEOUT with Gunicorn
- **Storing raw Claude response without validation:** May contain unexpected format
- **Triggering synthesis before CLOSED state:** Responses may still be changing
- **Not handling Claude API errors gracefully:** Leaves session in broken state

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Async HTTP client | Custom requests wrapper | anthropic SDK | Type-safe, handles retries, streaming |
| JSON schema validation | Manual parsing | Pydantic models | Automatic validation, clear error messages |
| Background task orchestration | Custom thread management | FastAPI BackgroundTasks | Handles lifecycle, cleanup properly |
| Response parsing | String manipulation | Structured outputs beta | Guaranteed schema compliance |

**Key insight:** The anthropic SDK handles retries, rate limiting, and connection management. Using raw httpx/requests loses these benefits.

## Common Pitfalls

### Pitfall 1: Blocking the Event Loop
**What goes wrong:** Using sync Anthropic client or `time.sleep` in async context freezes all requests
**Why it happens:** Python's asyncio requires all long operations to yield control
**How to avoid:** Use AsyncAnthropic client, or wrap sync code in threadpool via `def` background task
**Warning signs:** Requests hang, timeouts across unrelated endpoints

### Pitfall 2: Worker Timeout with Async BackgroundTasks
**What goes wrong:** Gunicorn kills worker before Claude API responds
**Why it happens:** `async def` background tasks run in the same event loop; if Gunicorn times out the worker, task dies
**How to avoid:** Use `def` (sync) function for background task, create new event loop inside
**Warning signs:** "[CRITICAL] WORKER TIMEOUT" in logs, synthesis never completes

### Pitfall 3: Database Session Lifecycle
**What goes wrong:** SQLAlchemy session expires before background task uses it
**Why it happens:** Background tasks run after request completes; the request's DB session is closed
**How to avoid:** Create new database session inside the background task
**Warning signs:** DetachedInstanceError, lazy loading failures

### Pitfall 4: Gap Type Hallucination
**What goes wrong:** Claude invents gap types beyond Direction/Alignment/Commitment
**Why it happens:** Without constraints, Claude may create custom categories
**How to avoid:** Use enum in structured output schema; validate before storing
**Warning signs:** Unexpected gap_type values in database

### Pitfall 5: Empty or Insufficient Responses
**What goes wrong:** Synthesis fails with 0-2 team responses
**Why it happens:** Not enough data for meaningful synthesis
**How to avoid:** Require minimum 3 responses before allowing synthesis; provide fallback message
**Warning signs:** Generic/placeholder synthesis text, error responses from Claude

## Code Examples

Verified patterns from official sources:

### Claude API Call with AsyncAnthropic
```python
# Source: https://github.com/anthropics/anthropic-sdk-python/blob/main/README.md
from anthropic import AsyncAnthropic

client = AsyncAnthropic()

async def call_claude(prompt: str) -> str:
    message = await client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text
```

### Synthesis Prompt Structure
```python
# Based on prompt engineering best practices from Anthropic docs
def build_synthesis_prompt(
    responses: list[dict],
    strategy_statement: str
) -> str:
    """Build prompt for team response synthesis."""

    responses_text = "\n\n".join([
        f"**{r['name']}** (Image #{r['image_number']}):\n" +
        "\n".join(f"- {b}" for b in r['bullets'])
        for r in responses
    ])

    return f"""You are analyzing responses from a leadership team's monthly alignment diagnostic.

## Context
The team's strategy statement (the "3AM test" - what someone should know at 3AM):
"{strategy_statement}"

## Team Responses
Each team member selected an image representing their current state and provided bullet points explaining their choice:

{responses_text}

## Your Task
Synthesize these responses into three parts:

1. **Themes** (2-4 sentences): High-level summary of what the team is experiencing. Focus on patterns across responses.

2. **Attributed Statements**: Specific insights with attribution. Format each as a statement followed by the names of team members whose responses support it. Example: "Concern about competing priorities (Dale, Peter)"

3. **Gap Diagnosis**: Identify the primary gap type from exactly one of these three options:
   - **Direction**: Team lacks shared understanding of goals or priorities
   - **Alignment**: Team's work is disconnected or uncoordinated
   - **Commitment**: Individual interests override collective success

Provide your reasoning for the gap diagnosis in 1-2 sentences.

Respond in the exact JSON format specified."""
```

### Structured Output Schema
```python
# Source: https://platform.claude.com/docs/en/build-with-claude/structured-outputs
from pydantic import BaseModel, Field
from typing import List, Literal

class AttributedStatement(BaseModel):
    statement: str = Field(description="The insight or observation")
    participants: List[str] = Field(description="Names of team members supporting this insight")

class SynthesisOutput(BaseModel):
    themes: str = Field(description="2-4 sentences summarizing team experience")
    statements: List[AttributedStatement] = Field(description="Specific insights with attribution")
    gap_type: Literal["Direction", "Alignment", "Commitment"] = Field(
        description="Primary gap type identified"
    )
    gap_reasoning: str = Field(description="1-2 sentence explanation for gap diagnosis")
```

### Complete Synthesis Service
```python
# Recommended implementation pattern
import json
import asyncio
from anthropic import AsyncAnthropic, transform_schema

from app.db.database import SessionLocal
from app.db.models import Session, Response

client = AsyncAnthropic()

def run_synthesis_task(session_id: int):
    """Background task entry point (sync wrapper)."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_generate_and_store_synthesis(session_id))
    finally:
        loop.close()

async def _generate_and_store_synthesis(session_id: int):
    """Generate synthesis and store results."""
    db = SessionLocal()
    try:
        session = db.query(Session).filter(Session.id == session_id).first()
        if not session:
            return

        responses = db.query(Response).filter(
            Response.session_id == session_id
        ).all()

        if len(responses) < 3:
            # Not enough responses for meaningful synthesis
            session.synthesis_themes = "Insufficient responses for synthesis (minimum 3 required)."
            session.synthesis_statements = "[]"
            session.synthesis_gap_type = None
            db.commit()
            return

        # Build response data
        response_data = [{
            "name": r.member.name,
            "image_number": r.image_number,
            "bullets": json.loads(r.bullets)
        } for r in responses]

        # Call Claude with structured output
        prompt = build_synthesis_prompt(response_data, session.team.strategy_statement or "")

        message = await client.beta.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2048,
            betas=["structured-outputs-2025-11-13"],
            messages=[{"role": "user", "content": prompt}],
            output_format={
                "type": "json_schema",
                "schema": transform_schema(SynthesisOutput)
            }
        )

        result = json.loads(message.content[0].text)

        # Store results
        session.synthesis_themes = result["themes"]
        session.synthesis_statements = json.dumps(result["statements"])
        session.synthesis_gap_type = result["gap_type"]
        db.commit()

    except Exception as e:
        # Log error but don't crash
        print(f"Synthesis error for session {session_id}: {e}")
        session.synthesis_themes = f"Synthesis generation failed. Please try again."
        session.synthesis_statements = "[]"
        session.synthesis_gap_type = None
        db.commit()
    finally:
        db.close()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| JSON mode prompting | Structured outputs beta | Nov 2025 | Guaranteed schema compliance |
| Sync API calls | AsyncAnthropic | Always available | Non-blocking for FastAPI |
| Manual retries | SDK built-in | Always available | Automatic retry with backoff |

**Deprecated/outdated:**
- `anthropic.HUMAN_PROMPT` / `anthropic.AI_PROMPT`: Use messages API instead (since 2023)
- `client.completion()`: Use `client.messages.create()` (since 2024)

## Open Questions

Things that couldn't be fully resolved:

1. **Optimal model selection**
   - What we know: claude-sonnet-4-5-20250929 is current, fast, cost-effective
   - What's unclear: Whether Haiku would be sufficient for this synthesis task
   - Recommendation: Start with Sonnet; test with Haiku if cost becomes concern

2. **Synthesis quality validation**
   - What we know: Structured outputs guarantee schema compliance
   - What's unclear: How to validate synthesis quality/accuracy
   - Recommendation: Plan for facilitator to have edit capability in Phase 16 (noted in EXT-05)

3. **Rate limiting behavior**
   - What we know: SDK handles rate limits with retries
   - What's unclear: Exact retry behavior with 0.76.0 version
   - Recommendation: Add timeout and error handling; monitor in production

## Sources

### Primary (HIGH confidence)
- [Anthropic Python SDK README](https://github.com/anthropics/anthropic-sdk-python/blob/main/README.md) - Async client usage, streaming patterns
- [Anthropic Structured Outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) - JSON schema output format, Pydantic integration
- [Anthropic Streaming Messages](https://platform.claude.com/docs/en/api/messages-streaming) - Event types, stream handling
- [FastAPI BackgroundTasks](https://fastapi.tiangolo.com/tutorial/background-tasks/) - Task patterns, limitations

### Secondary (MEDIUM confidence)
- [CCL DAC Framework](https://www.ccl.org/articles/leading-effectively-articles/make-leadership-happen-with-dac-framework/) - Direction/Alignment/Commitment gap definitions
- [Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-4-best-practices) - Synthesis prompt structure

### Tertiary (LOW confidence)
- [FastAPI GitHub Discussion #5956](https://github.com/fastapi/fastapi/discussions/5956) - Worker timeout solutions (community knowledge)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - anthropic SDK documented, already installed
- Architecture: HIGH - FastAPI patterns well-established, verified against official docs
- Pitfalls: MEDIUM - Worker timeout issue from community discussions, needs validation

**Research date:** 2026-01-19
**Valid until:** 30 days (stable domain, SDK version locked)
