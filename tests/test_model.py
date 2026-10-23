import pytest

from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from schema.model import (
    User,
    UserProfile,
    Document,
    EvidenceItem,
    JobDescription,
    Resume,
)


def create_user(db_session, email="test@example.com"):
    user = User(
        email=email,
        password_hash="test-hash-not-a-real-password",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


def create_document(db_session, user):
    document = Document(
        user_id=user.id,
        original_filename="resume.pdf",
        storage_path=f"uploads/{user.id}/resume.pdf",
        mime_type="application/pdf",
        file_size=1024,
        file_hash="a" * 64,
        source_type="upload",
    )

    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    return document


def create_job_description(db_session, user):
    job = JobDescription(
        user_id=user.id,
        title="Backend Developer",
        company="Example Company",
        raw_text="Python, FastAPI, PostgreSQL",
    )

    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    return job


# --------------------------------------------------
# TABLE CREATION AND METADATA
# --------------------------------------------------

def test_all_expected_tables_exist(db_session):
    inspector = inspect(db_session.bind)
    tables = set(inspector.get_table_names())

    expected_tables = {
        "users",
        "user_profiles",
        "documents",
        "evidence_items",
        "job_descriptions",
        "resumes",
    }

    assert expected_tables.issubset(tables)


# --------------------------------------------------
# USER MODEL
# --------------------------------------------------

def test_user_can_be_inserted_and_retrieved(db_session):
    user = create_user(db_session)

    retrieved_user = db_session.get(User, user.id)

    assert retrieved_user is not None
    assert retrieved_user.email == "test@example.com"
    assert retrieved_user.is_active is True
    assert retrieved_user.created_at is not None


def test_duplicate_user_email_is_rejected(db_session):
    create_user(db_session, "duplicate@example.com")

    duplicate = User(
        email="duplicate@example.com",
        password_hash="another-test-hash",
    )

    db_session.add(duplicate)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


# --------------------------------------------------
# USER PROFILE MODEL
# --------------------------------------------------

def test_user_can_have_a_profile(db_session):
    user = create_user(db_session)

    profile = UserProfile(
        user_id=user.id,
        full_name="Test User",
        location="Pakistan",
        links={"github": "https://github.com/example"},
    )

    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)

    assert profile.id is not None
    assert profile.user_id == user.id
    assert user.profile.full_name == "Test User"


def test_user_cannot_have_two_profiles(db_session):
    user = create_user(db_session)

    profile1 = UserProfile(
        user_id=user.id,
        full_name="First Profile",
    )

    profile2 = UserProfile(
        user_id=user.id,
        full_name="Second Profile",
    )

    db_session.add_all([profile1, profile2])

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


# --------------------------------------------------
# DOCUMENT MODEL
# --------------------------------------------------

def test_document_can_be_inserted(db_session):
    user = create_user(db_session)
    document = create_document(db_session, user)

    assert document.id is not None
    assert document.user_id == user.id
    assert document.status == "pending"
    assert document.created_at is not None


def test_document_rejects_negative_file_size(db_session):
    user = create_user(db_session)

    document = Document(
        user_id=user.id,
        original_filename="resume.pdf",
        storage_path="uploads/resume.pdf",
        mime_type="application/pdf",
        file_size=-1,
        file_hash="b" * 64,
        source_type="upload",
    )

    db_session.add(document)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_same_file_hash_cannot_be_added_twice_for_one_user(db_session):
    user = create_user(db_session)

    create_document(db_session, user)

    duplicate = Document(
        user_id=user.id,
        original_filename="another-name.pdf",
        storage_path=f"uploads/{user.id}/another-name.pdf",
        mime_type="application/pdf",
        file_size=2048,
        file_hash="a" * 64,
        source_type="upload",
    )

    db_session.add(duplicate)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


# --------------------------------------------------
# JOB DESCRIPTION MODEL
# --------------------------------------------------

def test_job_description_can_be_inserted(db_session):
    user = create_user(db_session)
    job = create_job_description(db_session, user)

    assert job.id is not None
    assert job.title == "Backend Developer"
    assert job.user_id == user.id
    assert job.analysis_status == "pending"
    assert job.created_at is not None


# --------------------------------------------------
# EVIDENCE ITEM MODEL
# --------------------------------------------------

def test_evidence_item_can_be_inserted(db_session):
    user = create_user(db_session)
    document = create_document(db_session, user)

    evidence = EvidenceItem(
        user_id=user.id,
        document_id=document.id,
        evidence_type="project",
        title="Resume Builder",
        skills={"Python": "intermediate"},
        is_current=False,
    )

    db_session.add(evidence)
    db_session.commit()
    db_session.refresh(evidence)

    assert evidence.id is not None
    assert evidence.document_id == document.id
    assert evidence.status == "pending"
    assert evidence.created_at is not None
    assert evidence.updated_at is not None


def test_evidence_item_requires_existing_document(db_session):
    user = create_user(db_session)

    evidence = EvidenceItem(
        user_id=user.id,
        document_id=99999,
        evidence_type="project",
        title="Orphan Evidence",
    )

    db_session.add(evidence)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


# --------------------------------------------------
# RESUME MODEL
# --------------------------------------------------

def test_resume_can_be_inserted(db_session):
    user = create_user(db_session)
    job = create_job_description(db_session, user)

    resume = Resume(
        user_id=user.id,
        job_description_id=job.id,
        label="Backend Resume",
    )

    db_session.add(resume)
    db_session.commit()
    db_session.refresh(resume)

    assert resume.id is not None
    assert resume.version == 1
    assert resume.status == "pending"
    assert resume.created_at is not None
    assert resume.updated_at is not None


def test_duplicate_resume_version_is_rejected(db_session):
    user = create_user(db_session)
    job = create_job_description(db_session, user)

    resume1 = Resume(
        user_id=user.id,
        job_description_id=job.id,
        label="First Resume",
        version=1,
    )

    db_session.add(resume1)
    db_session.commit()

    resume2 = Resume(
        user_id=user.id,
        job_description_id=job.id,
        label="Duplicate Version",
        version=1,
    )

    db_session.add(resume2)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_resume_rejects_version_less_than_one(db_session):
    user = create_user(db_session)
    job = create_job_description(db_session, user)

    resume = Resume(
        user_id=user.id,
        job_description_id=job.id,
        label="Invalid Version",
        version=0,
    )

    db_session.add(resume)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()