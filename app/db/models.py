"""
The 55 App - ORM Models

SQLAlchemy model definitions for teams, members, sessions, and responses.
"""

import enum
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean
)
from sqlalchemy.orm import relationship

from app.db.database import Base


class SessionState(enum.Enum):
    """Session lifecycle states."""
    CAPTURING = "capturing"
    CLOSED = "closed"
    REVEALED = "revealed"


class Team(Base):
    """A team participating in The 55 diagnostics."""
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    team_name = Column(String(255), nullable=False)
    code = Column(String(20), unique=True, nullable=False, index=True)
    strategy_statement = Column(Text, nullable=True)
    # Customizable prompts for participant experience
    image_prompt = Column(Text, nullable=True)  # Shown when selecting image
    bullet_prompt = Column(Text, nullable=True)  # Shown when entering bullet points
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    members = relationship("Member", back_populates="team", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="team", cascade="all, delete-orphan")


class Member(Base):
    """A team member who participates in sessions."""
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    team = relationship("Team", back_populates="members")
    responses = relationship("Response", back_populates="member")


class Session(Base):
    """A monthly diagnostic session for a team."""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    month = Column(String(7), nullable=False)  # Format: "2025-05"
    state = Column(Enum(SessionState), default=SessionState.CAPTURING, nullable=False)
    synthesis_themes = Column(Text, nullable=True)
    synthesis_statements = Column(Text, nullable=True)
    synthesis_gap_type = Column(String(50), nullable=True)
    synthesis_gap_reasoning = Column(Text, nullable=True)
    suggested_recalibrations = Column(Text, nullable=True)  # JSON array of 3 suggestions
    facilitator_notes = Column(Text, nullable=True)
    facilitator_notes_updated_at = Column(DateTime, nullable=True)
    recalibration_action = Column(Text, nullable=True)
    recalibration_action_updated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    revealed_at = Column(DateTime, nullable=True)

    team = relationship("Team", back_populates="sessions")
    responses = relationship("Response", back_populates="session", cascade="all, delete-orphan")


class Response(Base):
    """A participant's response in a session."""
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    image_id = Column(String(255), nullable=False)  # filename stem e.g. "kids-swimming-pool-2026..."
    bullets = Column(Text, nullable=False)  # JSON array of 1-5 strings
    submitted_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    session = relationship("Session", back_populates="responses")
    member = relationship("Member", back_populates="responses")
