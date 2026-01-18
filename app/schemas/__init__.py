# The 55 App - Pydantic schemas package
"""
Pydantic models for API response validation and Claude structured outputs.
"""

from typing import List, Literal
from pydantic import BaseModel, Field


class AttributedStatement(BaseModel):
    """An insight with attribution to supporting team members."""
    statement: str = Field(description="The insight or observation")
    participants: List[str] = Field(description="Names of team members supporting this insight")


class SynthesisOutput(BaseModel):
    """Claude synthesis output schema for team response analysis."""
    themes: str = Field(description="2-4 sentences summarizing team experience")
    statements: List[AttributedStatement] = Field(description="Specific insights with attribution")
    gap_type: Literal["Direction", "Alignment", "Commitment"] = Field(
        description="Primary gap type identified"
    )
    gap_reasoning: str = Field(description="1-2 sentence explanation for gap diagnosis")
