import datetime
import os.path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.config import environ

from alembic import command
from alembic.config import Config as AlembicConfig
from iex_app.api.models.pydantic_models import MARKETTYPE_TO_PRICE_PYD_MODEL_MAP
from iex_app.common.constants import MARKET_TZ
from iex_app.common.enums import Markets

environ["DB_USER"] = "test_user"  # noqa
environ["DB_PASSWORD"] = "test_password"  # noqa
environ["DB_HOST"] = "localhost"  # noqa
environ["DB_PORT"] = "5432"  # noqa
environ["DB_NAME"] = "test_iex_db"  # noqa
environ["ALEMBIC_REVISION_PATH"] = os.path.join(os.getcwd(), "alembic")  # noqa
environ["ALEMBIC_INI_PATH"] = os.path.join(os.getcwd(), "alembic.ini")  # noqa

from iex_app.db.core import SQLALCHEMY_DATABASE_URI  # noqa


@pytest.fixture(scope="session")
def engine():
    db_url = SQLALCHEMY_DATABASE_URI
    engine = create_engine(db_url)
    return engine


@pytest.fixture(scope="session", autouse=True)
def apply_migrations(engine):
    alembic_config = AlembicConfig("alembic.ini")  # Adjust the path as necessary
    alembic_config.set_main_option("sqlalchemy.url", str(engine.url))

    # Apply migrations
    command.upgrade(alembic_config, "head")


@pytest.fixture(scope="session")
def Session(engine):
    Session = sessionmaker(bind=engine)
    return Session


@pytest.fixture(scope="function")
def session(Session):
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def mock_datetime():
    return MARKET_TZ.localize(datetime.datetime(2022, 1, 1))


@pytest.fixture
def mock_prices():
    return [10.0] * 14


@pytest.fixture
def pyd_price_model(request, mock_datetime, mock_prices):
    pyd_class = MARKETTYPE_TO_PRICE_PYD_MODEL_MAP.get(Markets[request.param])
    return pyd_class(
        settlement_period_start_datetime=mock_datetime,
        a1_price_in_rs_per_mwh=mock_prices[0],
        a2_price_in_rs_per_mwh=mock_prices[1],
        e1_price_in_rs_per_mwh=mock_prices[2],
        e2_price_in_rs_per_mwh=mock_prices[3],
        n1_price_in_rs_per_mwh=mock_prices[4],
        n2_price_in_rs_per_mwh=mock_prices[5],
        n3_price_in_rs_per_mwh=mock_prices[6],
        s1_price_in_rs_per_mwh=mock_prices[7],
        s2_price_in_rs_per_mwh=mock_prices[8],
        s3_price_in_rs_per_mwh=mock_prices[9],
        w1_price_in_rs_per_mwh=mock_prices[10],
        w2_price_in_rs_per_mwh=mock_prices[11],
        w3_price_in_rs_per_mwh=mock_prices[12],
        mcp_price_in_rs_per_mwh=mock_prices[13],
    )
