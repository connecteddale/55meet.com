"""
The 55 App - Synthesis Service

Claude API integration for generating insights from team responses.
Uses AsyncAnthropic client with sync wrapper for BackgroundTasks compatibility.
"""

import json
import asyncio
from typing import List

from anthropic import AsyncAnthropic

from datetime import datetime

from app.db.database import SessionLocal
from app.db.models import Session, Response, SessionState
from app.schemas import SynthesisOutput


# Module-level client (uses ANTHROPIC_API_KEY env var)
client = AsyncAnthropic()


def build_synthesis_prompt(
    responses: List[dict],
    strategy_statement: str
) -> str:
    """
    Build prompt for team response synthesis.

    Args:
        responses: List of dicts with keys: name, image_id, bullets
        strategy_statement: The team's 3AM test strategy statement

    Returns:
        Complete prompt for Claude synthesis
    """
    responses_text = "\n\n".join([
        f"**{r['name']}** (Image: {r['image_id']}):\n" +
        "\n".join(f"- {b}" for b in r['bullets'])
        for r in responses
    ])

    # JSON schema for structured output instruction
    json_schema = SynthesisOutput.model_json_schema()

    return f"""You are analyzing responses from a leadership team's monthly alignment diagnostic.

## Context
The team's strategy statement (the "3AM test" - what someone should know at 3AM):
"{strategy_statement}"

## Team Responses
Each team member selected an image representing their current state and provided bullet points explaining their choice:

{responses_text}

## Your Task
Synthesize these responses into four parts:

1. **Themes** (2-4 sentences): High-level summary of what the team is experiencing. Focus on patterns across responses.

2. **Attributed Statements**: Specific insights with attribution. Format each as a statement followed by the names of team members whose responses support it.

3. **Gap Diagnosis**: Identify the primary gap type from exactly one of these three options:
   - **Direction**: Team lacks shared understanding of goals or priorities
   - **Alignment**: Team's work is disconnected or uncoordinated
   - **Commitment**: Individual interests override collective success

4. **Gap Reasoning** (2-3 sentences): Explain WHY you diagnosed this specific gap type. Reference specific evidence from the responses that led to this conclusion. This should clearly justify the diagnosis.

5. **Suggested Recalibrations**: Provide exactly 3 specific, actionable recalibration actions the team could take to address the diagnosed gap. Each should be concrete and achievable within 30 days. Format as action items the team can commit to.

## Output Format
Respond ONLY with valid JSON matching this schema:
```json
{json.dumps(json_schema, indent=2)}
```

IMPORTANT:
- gap_type MUST be exactly one of: "Direction", "Alignment", or "Commitment"
- gap_reasoning MUST explain WHY this gap type was chosen based on evidence
- statements array should contain 3-6 attributed insights
- Each statement.participants array should contain 1-3 team member names
- suggested_recalibrations MUST contain exactly 3 actionable items"""


async def _generate_and_store_synthesis(session_id: int) -> None:
    """
    Generate synthesis from Claude and store results in database.

    This is the async implementation called by the sync wrapper.
    Creates its own database session to avoid lifecycle issues.
    """
    db = SessionLocal()
    try:
        session = db.query(Session).filter(Session.id == session_id).first()
        if not session:
            return

        responses = db.query(Response).filter(
            Response.session_id == session_id
        ).all()

        # Minimum 3 responses required for meaningful synthesis
        if len(responses) < 3:
            session.synthesis_themes = "Insufficient responses for synthesis (minimum 3 required)."
            session.synthesis_statements = "[]"
            session.synthesis_gap_type = None
            db.commit()
            return

        # Build response data for prompt
        response_data = [{
            "name": r.member.name,
            "image_id": r.image_id,
            "bullets": json.loads(r.bullets)
        } for r in responses]

        # Get strategy statement (may be None)
        strategy_statement = session.team.strategy_statement or ""

        # Build prompt and call Claude
        prompt = build_synthesis_prompt(response_data, strategy_statement)

        message = await client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Parse response and validate with Pydantic
        response_text = message.content[0].text

        # Handle potential markdown code block wrapping
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            # Remove first line (```json) and last line (```)
            response_text = "\n".join(lines[1:-1])

        result_data = json.loads(response_text)
        result = SynthesisOutput(**result_data)

        # Store validated results
        session.synthesis_themes = result.themes
        session.synthesis_statements = json.dumps(
            [s.model_dump() for s in result.statements]
        )
        session.synthesis_gap_type = result.gap_type
        session.synthesis_gap_reasoning = result.gap_reasoning
        session.suggested_recalibrations = json.dumps(result.suggested_recalibrations)

        # Auto-reveal: transition CLOSED -> REVEALED after successful synthesis
        if session.state == SessionState.CLOSED:
            session.state = SessionState.REVEALED
            session.revealed_at = datetime.utcnow()

        db.commit()

    except Exception as e:
        # Log error but don't crash - store fallback message
        print(f"Synthesis error for session {session_id}: {e}")
        try:
            session.synthesis_themes = "Synthesis generation failed. Please try again."
            session.synthesis_statements = "[]"
            session.synthesis_gap_type = None
            db.commit()
        except Exception:
            # If we can't even save the error state, just log
            print(f"Failed to save error state for session {session_id}")
    finally:
        db.close()


def run_synthesis_task(session_id: int) -> None:
    """
    Background task entry point for synthesis generation.

    This is a sync function that creates its own event loop,
    avoiding worker timeout issues with Gunicorn/Uvicorn.

    Args:
        session_id: Database ID of the session to synthesize
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_generate_and_store_synthesis(session_id))
    finally:
        loop.close()
