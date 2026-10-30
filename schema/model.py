from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
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
    )
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

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
    match_results: Mapped[list[MatchResult]] = relationship(
        back_populates="user"
    )


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False
    )
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    headline: Mapped[str | None] = mapped_column(String, nullable=True)
    links: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    user: Mapped[User] = relationship(back_populates="profile")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    storage_path: Mapped[str] = mapped_column(String, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    source_type: Mapped[str] = mapped_column(String, nullable=False)
    source_reference: Mapped[str | None] = mapped_column(
        String, nullable=True
    )
    status: Mapped[str] = mapped_column(
        String, default="pending", nullable=False
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    extraction_method: Mapped[str | None] = mapped_column(
        String, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "file_hash",
            name="uq_documents_user_file_hash",
        ),
        CheckConstraint(
            "file_size >= 0",
            name="ck_documents_file_size_nonnegative",
        ),
        UniqueConstraint(
            "user_id",
            "id",
            name="uq_documents_user_id_id",
        ),
    )

    user: Mapped[User] = relationship(back_populates="documents")
    evidence_items: Mapped[list[EvidenceItem]] = relationship(
        back_populates="document",
        foreign_keys="EvidenceItem.document_id",
    )


class EvidenceItem(Base):
    __tablename__ = "evidence_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    document_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )
    evidence_type: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    organization: Mapped[str | None] = mapped_column(String, nullable=True)
    role: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    highlights: Mapped[str | None] = mapped_column(Text, nullable=True)
    skills: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_current: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    attributes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    embeddings: Mapped[list[float] | None] = mapped_column(
        JSON, nullable=True
    )
    embedding_model: Mapped[str | None] = mapped_column(
        String, nullable=True
    )
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
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id", "document_id"],
            ["documents.user_id", "documents.id"],
            name="fk_evidence_items_document_owner",
        ),
        CheckConstraint(
            "confidence_score IS NULL OR "
            "(confidence_score >= 0 AND confidence_score <= 1)",
            name="ck_evidence_items_confidence_score_range",
        ),
        CheckConstraint(
            "end_date IS NULL OR start_date IS NULL OR end_date >= start_date",
            name="ck_evidence_items_date_range",
        ),
    )

    user: Mapped[User] = relationship(back_populates="evidence_items")
    document: Mapped[Document] = relationship(
        back_populates="evidence_items",
        foreign_keys=[document_id],
        primaryjoin="and_(EvidenceItem.document_id == Document.id, "
        "EvidenceItem.user_id == Document.user_id)",
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
    )
    skills: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    analysis_status: Mapped[str] = mapped_column(
        String, default="pending", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "id",
            name="uq_job_descriptions_user_id_id",
        ),
    )

    user: Mapped[User] = relationship(back_populates="job_descriptions")
    resumes: Mapped[list[Resume]] = relationship(
        back_populates="job_description",
        foreign_keys="Resume.job_description_id",
    )
    match_results: Mapped[list[MatchResult]] = relationship(
        back_populates="job_description",
        foreign_keys="MatchResult.job_description_id",
    )


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    job_description_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )
    label: Mapped[str] = mapped_column(String, nullable=False)
    template: Mapped[str | None] = mapped_column(String, nullable=True)
    content: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # Keep this as Text if your API stores serialized text.
    version: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False
    )
    file_path: Mapped[str | None] = mapped_column(String, nullable=True)
    used_evidence_items: Mapped[list[int] | None] = mapped_column(
        JSON, nullable=True
    )
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
        ForeignKeyConstraint(
            ["user_id", "job_description_id"],
            ["job_descriptions.user_id", "job_descriptions.id"],
            name="fk_resumes_job_description_owner",
        ),
        UniqueConstraint(
            "user_id",
            "job_description_id",
            "version",
            name="uq_resumes_user_job_version",
        ),
        CheckConstraint(
            "version >= 1",
            name="ck_resumes_version_positive",
        ),
    )

    user: Mapped[User] = relationship(back_populates="resumes")
    job_description: Mapped[JobDescription] = relationship(
        back_populates="resumes",
        foreign_keys=[job_description_id],
        primaryjoin="and_(Resume.job_description_id == "
        "JobDescription.id, Resume.user_id == JobDescription.user_id)",
    )


class MatchResult(Base):
    __tablename__ = "match_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    document_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )
    job_description_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )
    matching_score: Mapped[float] = mapped_column(
        Float, nullable=False
    )
    matching_skills: Mapped[list] = mapped_column(
        JSON, nullable=False, default=list
    )
    missing_skills: Mapped[list | None] = mapped_column(
        JSON, nullable=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id", "document_id"],
            ["documents.user_id", "documents.id"],
            name="fk_match_results_document_owner",
        ),
        ForeignKeyConstraint(
            ["user_id", "job_description_id"],
            ["job_descriptions.user_id", "job_descriptions.id"],
            name="fk_match_results_job_owner",
        ),
        CheckConstraint(
            "matching_score >= 0 AND matching_score <= 100",
            name="ck_match_results_score_range",
        ),
    )

    user: Mapped[User] = relationship(back_populates="match_results")
    document: Mapped[Document] = relationship(
        foreign_keys=[document_id],
        primaryjoin="and_(MatchResult.document_id == Document.id, "
        "MatchResult.user_id == Document.user_id)",
    )
    job_description: Mapped[JobDescription] = relationship(
        back_populates="match_results",
        foreign_keys=[job_description_id],
        primaryjoin="and_(MatchResult.job_description_id == "
        "JobDescription.id, MatchResult.user_id == JobDescription.user_id)",
    )
