---
phase: 15-ai-synthesis
plan: 01
subsystem: ai-integration
tags: [claude, anthropic, synthesis, background-tasks, pydantic]
dependency-graph:
  requires: [14-image-browser]
  provides: [synthesis-service, synthesis-schemas]
  affects: [15-02-synthesis-router, 15-03-synthesis-display]
tech-stack:
  added: []
  patterns: [async-claude-client, sync-background-task-wrapper, pydantic-structured-output]
key-files:
  created:
    - the55/app/services/synthesis.py
  modified:
    - the55/app/schemas/__init__.py
decisions:
  - id: use-standard-messages-api
    choice: "Standard messages API with JSON prompt instruction"
    why: "Avoids beta structured outputs API complexity; sufficient for this use case"
metrics:
  duration: 4m
  completed: 2026-01-19
---

# Phase 15 Plan 01: Synthesis Service Summary

Claude API integration service that transforms team responses into structured insights using AsyncAnthropic client with sync wrapper pattern for BackgroundTasks compatibility.

## Outcome

Created synthesis service layer with:
- Pydantic schemas for validated synthesis output (themes, attributed statements, gap diagnosis)
- AsyncAnthropic client integration with proper event loop handling
- Background task wrapper that avoids Gunicorn worker timeout issues

## Tasks Completed

| # | Task | Commit | Key Files |
|---|------|--------|-----------|
| 1 | Create Pydantic schemas for synthesis output | a9963e3 | app/schemas/__init__.py |
| 2 | Create synthesis service with Claude integration | 229295a | app/services/synthesis.py |

## Decisions Made

**Standard messages API vs beta structured outputs:**
- Chose standard messages API with JSON instruction in prompt
- Beta structured outputs require specific beta flag and transform_schema
- Standard approach simpler, sufficient for this use case
- Pydantic validation catches any malformed responses

**Sync wrapper pattern for BackgroundTasks:**
- Background tasks use `def` (sync) function, not `async def`
- Creates new event loop inside the function
- Prevents WORKER TIMEOUT issues with Gunicorn/Uvicorn
- Pattern from FastAPI community best practices

## Technical Details

**SynthesisOutput schema:**
- `themes: str` - 2-4 sentence summary
- `statements: List[AttributedStatement]` - Insights with participant names
- `gap_type: Literal["Direction", "Alignment", "Commitment"]` - Constrained enum
- `gap_reasoning: str` - 1-2 sentence explanation

**Synthesis service flow:**
1. `run_synthesis_task(session_id)` - sync entry point for BackgroundTasks
2. Creates new event loop, runs async function
3. `_generate_and_store_synthesis()` - async implementation
4. Creates fresh DB session (avoids lifecycle issues)
5. Fetches responses, validates minimum 3
6. Builds prompt with `build_synthesis_prompt()`
7. Calls Claude via AsyncAnthropic
8. Validates response with Pydantic
9. Stores results in session model
10. Error handling stores fallback message

**Error handling:**
- Minimum 3 responses required (else stores fallback message)
- Claude API errors caught and stored as "failed" message
- DB session always closed in finally block

## Deviations from Plan

None - plan executed exactly as written.

## Files Changed

**Created:**
- `the55/app/services/synthesis.py` - 180 lines
  - Module-level AsyncAnthropic client
  - build_synthesis_prompt() function
  - _generate_and_store_synthesis() async function
  - run_synthesis_task() sync wrapper

**Modified:**
- `the55/app/schemas/__init__.py` - Added 22 lines
  - AttributedStatement model
  - SynthesisOutput model with Literal gap_type

## Verification

All verification criteria passed:
- Both schemas import without error
- Synthesis service imports without error
- build_synthesis_prompt returns string with all required sections (Direction, Alignment, Commitment, strategy statement)
- run_synthesis_task is synchronous function (not async)
- SynthesisOutput validates gap_type as one of ["Direction", "Alignment", "Commitment"]
- Invalid gap_type correctly rejected by Pydantic

## Next Phase Readiness

Ready for 15-02 (Synthesis Router):
- SynthesisOutput schema available for response typing
- run_synthesis_task ready for BackgroundTasks.add_task()
- Service handles all error cases gracefully

Dependencies for next plan:
- Need ANTHROPIC_API_KEY environment variable set for production
- Session model already has synthesis_themes, synthesis_statements, synthesis_gap_type columns
