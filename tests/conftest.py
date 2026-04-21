import pytest
import os
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient
from main import app
from opsai.database import get_session
import opsai.database 
import opsai.models # Force registration of models

# Use an in-memory database with a static connection for persistence across test steps
from sqlalchemy import event, StaticPool
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

@pytest.fixture(name="session", autouse=True)
def session_fixture(monkeypatch):
    """
    Creates a new database session for a test and patches the global engine.
    """
    # Provide dummy keys so services can initialize
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
    
    # Patch the global engine so all code uses the test DB
    monkeypatch.setattr(opsai.database, "engine", test_engine)
    
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    Creates a FastAPI TestClient that uses the test database.
    """
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
