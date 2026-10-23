import pytest

from pydantic import ValidationError

from model_pydantic.user import UserCreate, UserLogin, UserResponse
from model_pydantic.user_profile import (
    UserProfileCreate,
    UserProfileUpdate,
)
from model_pydantic.job_description import (
    JobDescriptionCreate,
    JobDescriptionUpdate,
)
from model_pydantic.resumes import ResumeCreate, ResumeUpdate
from model_pydantic.evidence_items import (
    EvidenceItemCreate,
    EvidenceItemUpdate,
)
from model_pydantic.document import DocumentSystemCreate


# --------------------------------------------------
# USER SCHEMAS
# --------------------------------------------------

def test_user_create_accepts_valid_data():
    user = UserCreate(
        email="test@example.com",
        password="SecurePassword123",
    )

    assert user.email == "test@example.com"
    assert user.password == "SecurePassword123"


def test_user_create_rejects_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(
            email="not-an-email",
            password="SecurePassword123",
        )


def test_user_create_rejects_short_password():
    with pytest.raises(ValidationError):
        UserCreate(
            email="test@example.com",
            password="short",
        )


def test_user_login_requires_password():
    with pytest.raises(ValidationError):
        UserLogin(email="test@example.com")


def test_user_response_does_not_expose_password_hash():
    # The response schema should not declare a password_hash field.
    assert "password_hash" not in UserResponse.model_fields


# --------------------------------------------------
# USER PROFILE SCHEMAS
# --------------------------------------------------

def test_profile_create_accepts_valid_data():
    profile = UserProfileCreate(
        full_name="Test User",
        location="Pakistan",
        links={
            "github": "https://github.com/example",
            "linkedin": "https://linkedin.com/in/example",
        },
    )

    assert profile.full_name == "Test User"
    assert profile.location == "Pakistan"
    assert profile.links["github"].startswith("https://")


def test_profile_create_rejects_missing_full_name():
    with pytest.raises(ValidationError):
        UserProfileCreate()


def test_profile_create_allows_optional_fields_to_be_omitted():
    profile = UserProfileCreate(full_name="Test User")

    assert profile.phone is None
    assert profile.location is None
    assert profile.headline is None
    assert profile.links is None


def test_profile_update_can_contain_only_one_field():
    update = UserProfileUpdate(location="Wah Cantt")

    assert update.model_dump(exclude_unset=True) == {
        "location": "Wah Cantt"
    }


# --------------------------------------------------
# JOB DESCRIPTION SCHEMAS
# --------------------------------------------------

def test_job_description_create_accepts_valid_data():
    job = JobDescriptionCreate(
        title="Backend Developer",
        company="Example Company",
        raw_text="Python, FastAPI, PostgreSQL, and REST APIs.",
    )

    assert job.title == "Backend Developer"
    assert job.company == "Example Company"


def test_job_description_create_rejects_empty_title():
    with pytest.raises(ValidationError):
        JobDescriptionCreate(
            title="",
            raw_text="Some job description",
        )


def test_job_description_update_accepts_partial_data():
    update = JobDescriptionUpdate(title="Python Developer")

    assert update.model_dump(exclude_unset=True) == {
        "title": "Python Developer"
    }


# --------------------------------------------------
# RESUME SCHEMAS
# --------------------------------------------------

def test_resume_create_accepts_valid_data():
    resume = ResumeCreate(
        job_description_id=1,
        label="Backend Developer Resume",
        template="modern",
    )

    assert resume.job_description_id == 1
    assert resume.label == "Backend Developer Resume"


def test_resume_create_rejects_nonpositive_job_id():
    with pytest.raises(ValidationError):
        ResumeCreate(
            job_description_id=0,
            label="My Resume",
        )


def test_resume_update_accepts_partial_data():
    update = ResumeUpdate(label="Updated Resume")

    assert update.model_dump(exclude_unset=True) == {
        "label": "Updated Resume"
    }


# --------------------------------------------------
# EVIDENCE ITEM SCHEMAS
# --------------------------------------------------

def test_evidence_create_accepts_valid_data():
    evidence = EvidenceItemCreate(
        document_id=1,
        evidence_type="project",
        title="Weather-Based Crop Advisory System",
        organization="University Project",
        skills={"Python": "intermediate", "SQL": "intermediate"},
    )

    assert evidence.document_id == 1
    assert evidence.title == "Weather-Based Crop Advisory System"
    assert "Python" in evidence.skills


def test_evidence_create_rejects_missing_required_fields():
    with pytest.raises(ValidationError):
        EvidenceItemCreate()


def test_evidence_update_accepts_partial_data():
    update = EvidenceItemUpdate(
        title="Updated Project Title"
    )

    assert update.model_dump(exclude_unset=True) == {
        "title": "Updated Project Title"
    }


# --------------------------------------------------
# DOCUMENT SCHEMAS
# --------------------------------------------------

def test_document_system_create_accepts_valid_data():
    document = DocumentSystemCreate(
        user_id=1,
        original_filename="resume.pdf",
        storage_path="uploads/user_1/resume.pdf",
        mime_type="application/pdf",
        file_size=1024,
        file_hash="a" * 64,
        source_type="upload",
    )

    assert document.user_id == 1
    assert document.file_size == 1024
    assert len(document.file_hash) == 64


def test_document_system_create_rejects_invalid_hash():
    with pytest.raises(ValidationError):
        DocumentSystemCreate(
            user_id=1,
            original_filename="resume.pdf",
            storage_path="uploads/resume.pdf",
            mime_type="application/pdf",
            file_size=1024,
            file_hash="invalid",
            source_type="upload",
        )


def test_document_system_create_rejects_negative_file_size():
    with pytest.raises(ValidationError):
        DocumentSystemCreate(
            user_id=1,
            original_filename="resume.pdf",
            storage_path="uploads/resume.pdf",
            mime_type="application/pdf",
            file_size=-1,
            file_hash="a" * 64,
            source_type="upload",
        )