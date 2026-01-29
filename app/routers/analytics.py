"""
The 55 App - Analytics Router

Admin endpoints for conversion funnel metrics.
Privacy-first: No PII, just aggregate counts.
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.db.models import ConversionEvent, EventType

router = APIRouter(prefix="/admin/analytics", tags=["analytics"])


@router.get("/funnel")
def get_conversion_funnel(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to query"),
    db: Session = Depends(get_db)
):
    """
    Query conversion funnel metrics for last N days.

    Returns counts for each funnel stage and conversion rates between stages.
    Funnel: demo_click -> demo_completion -> email_click
    """
    start_date = datetime.utcnow() - timedelta(days=days)

    # Query event counts grouped by type
    results = db.query(
        ConversionEvent.event_type,
        func.count(ConversionEvent.id).label('count')
    ).filter(
        ConversionEvent.created_at >= start_date
    ).group_by(
        ConversionEvent.event_type
    ).all()

    # Build funnel dict
    funnel = {event_type.value: count for event_type, count in results}

    # Get counts with defaults
    demo_clicks = funnel.get('demo_click', 0)
    completions = funnel.get('demo_completion', 0)
    email_clicks = funnel.get('email_click', 0)

    # Calculate conversion rates
    demo_to_completion = round(completions / demo_clicks * 100, 1) if demo_clicks > 0 else 0
    completion_to_inquiry = round(email_clicks / completions * 100, 1) if completions > 0 else 0
    overall = round(email_clicks / demo_clicks * 100, 1) if demo_clicks > 0 else 0

    return {
        "period_days": days,
        "start_date": start_date.isoformat(),
        "end_date": datetime.utcnow().isoformat(),
        "funnel": {
            "demo_click": demo_clicks,
            "demo_completion": completions,
            "email_click": email_clicks
        },
        "rates": {
            "demo_to_completion_pct": demo_to_completion,
            "completion_to_inquiry_pct": completion_to_inquiry,
            "overall_conversion_pct": overall
        }
    }


@router.get("/events/recent")
def get_recent_events(
    limit: int = Query(default=20, ge=1, le=100, description="Number of events to return"),
    db: Session = Depends(get_db)
):
    """
    Get most recent conversion events for debugging/monitoring.

    Returns raw event data (no PII - just event types and timestamps).
    """
    events = db.query(ConversionEvent).order_by(
        ConversionEvent.created_at.desc()
    ).limit(limit).all()

    return {
        "count": len(events),
        "events": [
            {
                "id": e.id,
                "event_type": e.event_type.value,
                "event_data": e.event_data,
                "created_at": e.created_at.isoformat()
            }
            for e in events
        ]
    }
