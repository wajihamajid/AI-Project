from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ResumeStatus = Literal[
    "pending",
    "processing",
    "completed",
    "failed",
]


class ResumeCreate(BaseModel):
    job_description_id: int = Field(
        ...,
        gt=0,
        description="The job description targeted by this resume",
    )
    label: str = Field(
        ...,
        min_length=1,
        max_length=256,
    )
    template: str | None = None


class ResumeUpdate(BaseModel):
    label: str | None = Field(
        default=None,
        min_length=1,
        max_length=256,
    )
    template: str | None = None
    content: str | None = None


class ResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_description_id: int
    label: str
    template: str | None
    content: str | None
    version: int
    used_evidence_items: list[int] | None
    status: ResumeStatus
    model_used: str | None
    created_at: datetime
    updated_at: datetime


class ResumeSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_description_id: int
    label: str
    template: str | None
    version: int
    status: ResumeStatus
    created_at: datetime
    updated_at: datetime