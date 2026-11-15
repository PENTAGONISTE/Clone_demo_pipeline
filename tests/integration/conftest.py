import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import Base


@pytest.fixture(scope="session")
def engine():
    """Base fournie par le pipeline (service postgres), sinon conteneur jetable Testcontainers."""
    if url := os.getenv("TEST_DATABASE_URL"):
        engine = create_engine(url)
        Base.metadata.create_all(engine)
        yield engine
        return
    from testcontainers.postgres import PostgresContainer

    with PostgresContainer("postgres:16", driver="psycopg") as pg:
        engine = create_engine(pg.get_connection_url())
        Base.metadata.create_all(engine)
        yield engine


@pytest.fixture
def session(engine):
    with Session(engine) as session:
        yield session
        session.rollback()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
