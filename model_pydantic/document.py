from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


DocumentStatus = Literal[
    "pending",
    "processing",
    "completed",
    "failed",
]


class DocumentSystemCreate(BaseModel):
    """
    Internal schema for creating a document record
    after the backend has processed the uploaded file.
    """

    model_config = ConfigDict(extra="forbid")

    user_id: int = Field(..., gt=0)
    original_filename: str = Field(
        ...,
        min_length=1,
        max_length=256,
    )
    storage_path: str = Field(
        ...,
        min_length=1,
    )
    mime_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )
    file_size: int = Field(..., ge=0)
    file_hash: str = Field(
        ...,
        min_length=64,
        max_length=64,
        pattern=r"^[0-9a-fA-F]{64}$",
    )
    source_type: str = Field(
        ...,
        min_length=1,
    )
    source_reference: str | None = None


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_filename: str
    mime_type: str
    file_size: int
    source_type: str
    source_reference: str | None
    status: str
    error_message: str | None
    extraction_method: str | None
    created_at: datetime