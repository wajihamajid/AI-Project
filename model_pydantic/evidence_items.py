from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


EvidenceStatus = Literal[
    "pending",
    "extracted",
    "rejected",
    "error",
]


class EvidenceItemCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: int = Field(..., gt=0)
    evidence_type: str = Field(
        ...,
        min_length=1,
        max_length=128,
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=256,
    )
    organization: str | None = Field(
        default=None,
        max_length=256,
    )
    role: str | None = Field(
        default=None,
        max_length=256,
    )
    description: str | None = Field(
        default=None,
        max_length=10000,
    )
    highlights: str | None = Field(
        default=None,
        max_length=10000,
    )
    skills: dict[str, Any] | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool = False
    location: str | None = None
    attributes: dict[str, Any] | None = None


class EvidenceItemUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=256,
    )
    organization: str | None = Field(
        default=None,
        max_length=256,
    )
    role: str | None = Field(
        default=None,
        max_length=256,
    )
    description: str | None = Field(
        default=None,
        max_length=10000,
    )
    highlights: str | None = Field(
        default=None,
        max_length=10000,
    )
    skills: dict[str, Any] | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool | None = None
    location: str | None = None
    attributes: dict[str, Any] | None = None


class EvidenceItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int
    evidence_type: str
    title: str
    organization: str | None
    role: str | None
    description: str | None
    highlights: str | None
    skills: dict[str, Any] | None
    start_date: date | None
    end_date: date | None
    is_current: bool
    location: str | None
    attributes: dict[str, Any] | None
    confidence_score: float | None
    status: EvidenceStatus
    error_message: str | None
    created_at: datetime
    updated_at: datetime