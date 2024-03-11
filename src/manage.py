import logging
from time import sleep

import psycopg2

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from src.database import (
    ALEMBIC_INI_PATH,
    ALEMBIC_REVISION_PATH,
    DB_HOST,
    DB_PASSWORD,
    DB_PORT,
    DB_USER,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Add formatter to console handler
console_handler.setFormatter(formatter)

# Add console handler to logger
logger.addHandler(console_handler)


def wait_for_postgres():
    num_attempts = 5
    current_attempt = 0
    while current_attempt < num_attempts:
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT,
            )
            logger.info("Postgres is ready ! Closing the test connection")
            conn.close()
            break
        except psycopg2.OperationalError:
            logger.info("Postgres is not ready yet. Waiting...")
            sleep(1)
            current_attempt += 1


def apply_migrations():
    """Applies alembic versioning to schema."""

    # add it to alembic table
    alembic_cfg = AlembicConfig(ALEMBIC_INI_PATH)
    alembic_cfg.set_main_option("script_location", ALEMBIC_REVISION_PATH)
    alembic_command.upgrade(alembic_cfg, "head")
