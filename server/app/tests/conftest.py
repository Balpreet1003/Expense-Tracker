import os

import pytest
from alembic import command
from alembic.config import Config
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database.session import get_db
from app.main import app
from app.features.expense.models.expense import Expense


# Load environment variables from .env
load_dotenv()


# Get the test database URL
DB_TEST_URL = os.getenv("DB_TEST_URL")


if not DB_TEST_URL:
    raise RuntimeError(
        "DB_TEST_URL is not set"
    )


# Create the SQLAlchemy engine for the test database
test_engine = create_engine(
    DB_TEST_URL,
    pool_pre_ping=True,
)


# Create test database sessions
TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Apply all Alembic migrations to the test database
    before running the test suite.
    """

    # Load Alembic configuration
    alembic_config = Config("alembic.ini")


    # Override the database URL specifically for tests
    alembic_config.set_main_option(
        "sqlalchemy.url",
        DB_TEST_URL,
    )


    # Apply all migrations up to the latest revision
    command.upgrade(
        alembic_config,
        "head",
    )


    yield


@pytest.fixture()
def db():
    """
    Create a database session for an individual test.
    """

    session = TestingSessionLocal()

    try:
        yield session

    finally:
        session.rollback()

        # Clean test data after every test
        session.query(Expense).delete()
        session.commit()

        session.close()


@pytest.fixture()
def client(db: Session):
    """
    Create a FastAPI TestClient that uses the test database session.
    """

    def override_get_db():
        try:
            yield db
        finally:
            pass


    # Override the application's database dependency
    app.dependency_overrides[get_db] = override_get_db


    with TestClient(app) as test_client:
        yield test_client


    # Remove dependency overrides after the test
    app.dependency_overrides.clear()