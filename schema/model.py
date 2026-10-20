from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(
        String(320), unique=True, nullable=False
    )  # Unique email identifies each account.
    password_hash: Mapped[str] = mapped_column(
        String, nullable=False
    )  # Store a password hash, never a plaintext password.
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )  # New accounts are active by default.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )  # The database records when the account was created.

    # A user has at most one profile.
    profile: Mapped[UserProfile | None] = relationship(
        back_populates="user"
    )
    documents: Mapped[list[Document]] = relationship(
        back_populates="user"
    )
    evidence_items: Mapped[list[EvidenceItem]] = relationship(
        back_populates="user"
    )
    resumes: Mapped[list[Resume]] = relationship(
        back_populates="user"
    )
    job_descriptions: Mapped[list[JobDescription]] = relationship(
        back_populates="user"
    )


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False
    )  # UNIQUE enforces one profile per user at database level.
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    headline: Mapped[str | None] = mapped_column(String, nullable=True)
    links: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # Stores structured links such as LinkedIn and GitHub.

    user: Mapped[User] = relationship(back_populates="profile")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )  # Index helps retrieve a user's documents efficiently.
    original_filename: Mapped[str] = mapped_column(
        String, nullable=False
    )  # Preserve the uploaded filename without its typo.
    storage_path: Mapped[str] = mapped_column(
        String, nullable=False
    )  # Store a controlled storage key or path, not arbitrary user input.
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_hash: Mapped[str] = mapped_column(
        String(64), nullable=False
    )  # SHA-256 hashes are 64 hexadecimal characters.
    source_type: Mapped[str] = mapped_column(
        String, nullable=False
    )  # Identifies where the document originated.
    source_reference: Mapped[str | None] = mapped_column(
        String, nullable=True
    )
    status: Mapped[str] = mapped_column(
        String, default="pending", nullable=False
    )  # Tracks the document processing lifecycle.
    error_message: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    extraction_method: Mapped[str | None] = mapped_column(
        String, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        # Prevents the same user from uploading identical content twice.
        UniqueConstraint(
            "user_id", "file_hash", name="uq_documents_user_file_hash"
        ),
        CheckConstraint(
            "file_size >= 0", name="ck_documents_file_size_nonnegative"
        ),
    )

    user: Mapped[User] = relationship(back_populates="documents")
    evidence_items: Mapped[list[EvidenceItem]] = relationship(
        back_populates="document"
    )


class EvidenceItem(Base):
    __tablename__ = "evidence_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id"), nullable=False, index=True
    )  # Links extracted evidence to its source document.
    evidence_type: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    organization: Mapped[str | None] = mapped_column(String, nullable=True)
    role: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    highlights: Mapped[str | None] = mapped_column(Text, nullable=True)
    skills: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # Stores structured skills extracted by the AI.
    start_date: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )  # Employment and education dates usually do not need times.
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_current: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    attributes: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # Stores additional structured evidence attributes.
    confidence_score: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )  # Allows fractional scores such as 0.87.
    embeddings: Mapped[list[float] | None] = mapped_column(
        JSON, nullable=True
    )  # JSON is acceptable for a prototype; consider pgvector later.
    embedding_model: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(
        String, default="pending", nullable=False
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )  # onupdate refreshes this value when SQLAlchemy updates the row.

    user: Mapped[User] = relationship(back_populates="evidence_items")
    document: Mapped[Document] = relationship(
        back_populates="evidence_items"
    )


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    job_description_id: Mapped[int] = mapped_column(
        ForeignKey("job_descriptions.id"), nullable=False, index=True
    )  # Identifies the job description this resume targets.
    label: Mapped[str] = mapped_column(String, nullable=False)
    template: Mapped[str | None] = mapped_column(String, nullable=True)
    content: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # Stores generated resume content.
    version: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False
    )  # Every saved resume starts at version 1.
    file_path: Mapped[str | None] = mapped_column(String, nullable=True)
    used_evidence_items: Mapped[list[int] | None] = mapped_column(
        JSON, nullable=True
    )  # Stores the IDs of evidence items used during generation.
    status: Mapped[str] = mapped_column(
        String, default="pending", nullable=False
    )
    model_used: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        # Prevent duplicate version numbers for the same user and job.
        UniqueConstraint(
            "user_id",
            "job_description_id",
            "version",
            name="uq_resumes_user_job_version",
        ),
        CheckConstraint(
            "version >= 1", name="ck_resumes_version_positive"
        ),
    )

    user: Mapped[User] = relationship(back_populates="resumes")
    job_description: Mapped[JobDescription] = relationship(
        back_populates="resumes"
    )


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    company: Mapped[str | None] = mapped_column(String, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_requirements: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # Structured AI output is easier to query than serialized text.
    skills: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # Stores extracted job skills and related metadata.
    analysis_status: Mapped[str] = mapped_column(
        String, default="pending", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped[User] = relationship(back_populates="job_descriptions")
    resumes: Mapped[list[Resume]] = relationship(
        back_populates="job_description"
    )
