from sqlalchemy_utils import create_database, database_exists

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from iex_app.db.core import (
    ALEMBIC_INI_PATH,
    ALEMBIC_REVISION_PATH,
    SQLALCHEMY_DATABASE_URI,
    Base,
)


def version_schema(script_location: str):
    """Applies alembic versioning to schema."""

    # add it to alembic table
    alembic_cfg = AlembicConfig(ALEMBIC_INI_PATH)
    alembic_cfg.set_main_option("script_location", script_location)
    alembic_command.stamp(alembic_cfg, "head")


def get_all_tables():
    """Fetches tables that belong to the 'dispatch_core' schema."""
    all_tables = []
    for _, table in Base.metadata.tables.items():
        all_tables.append(table)
    return all_tables


def init_database(engine):
    """Initializes the database."""
    if not database_exists(str(SQLALCHEMY_DATABASE_URI)):
        create_database(str(SQLALCHEMY_DATABASE_URI))

    tables = get_all_tables()

    Base.metadata.create_all(engine, tables=tables)

    version_schema(script_location=ALEMBIC_REVISION_PATH)
