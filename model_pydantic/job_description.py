from datetime import datetime
from typing import Literal, Any

from pydantic import BaseModel, ConfigDict, Field


JobDescriptionStatus = Literal["pending", "extracted", "error"]


class JobDescriptionCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=256,
    )
    company: str | None = Field(
        default=None,
        max_length=256,
    )
    raw_text: str = Field(
        ...,
        min_length=1,
    )


class JobDescriptionUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=256,
    )
    company: str | None = Field(
        default=None,
        max_length=256,
    )
    raw_text: str | None = Field(
        default=None,
        min_length=1,
    )
    parsed_requirements: dict[str, Any] | None = None
    skills: dict[str, Any] | None = None


class JobDescriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company: str | None
    raw_text: str | None
    parsed_requirements: dict[str, Any] | None
    skills: dict[str, Any] | None
    analysis_status: JobDescriptionStatus
    created_at: datetime


class JobDescriptionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company: str | None
    analysis_status: JobDescriptionStatus
    created_at: datetime