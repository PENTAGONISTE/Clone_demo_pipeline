import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import config
from app.db import get_session, make_engine
from app.main import app, init_db


@pytest.fixture
def client():
    engine = make_engine("sqlite://")
    init_db(engine)

    def override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def auth():
    return {"Authorization": f"Bearer {config.API_TOKEN}"}
