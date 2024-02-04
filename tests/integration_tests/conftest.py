import pytest
from sqlalchemy_utils import database_exists, drop_database
from starlette.config import environ

environ["DB_USER"] = "postgres"  # noqa
environ["DB_PASSWORD"] = "RaviTeja_93"  # noqa
environ["DB_HOST"] = "localhost"  # noqa
environ["DB_PORT"] = "5432"  # noqa
environ["DB_NAME"] = "test_iex_app"  # noqa
environ[
    "ALEMBIC_REVISION_PATH"
] = "/Users/ravigutta/Documents/python-projects/iex_app/alembic"  # noqa
environ[
    "ALEMBIC_INI_PATH"
] = "/Users/ravigutta/Documents/python-projects/iex_app/alembic.ini"  # noqa

from iex_app.db.core import SQLALCHEMY_DATABASE_URI, engine  # noqa
from iex_app.db.manage import init_database  # noqa
from tests.integration_tests.database import Session  # noqa


@pytest.fixture(scope="session")
def db():
    if database_exists(str(SQLALCHEMY_DATABASE_URI)):
        drop_database(str(SQLALCHEMY_DATABASE_URI))

    init_database(engine)
    Session.configure(bind=engine)
    yield
    drop_database(str(SQLALCHEMY_DATABASE_URI))


@pytest.fixture(scope="function", autouse=True)
def session(db):
    """
    Creates a new database session with (with working transaction)
    for test duration.
    """
    session = Session()
    session.begin_nested()
    yield session
    session.rollback()
