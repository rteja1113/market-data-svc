import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "")
DB_PORT = os.getenv("DB_PORT", "")
DB_NAME = os.getenv("DB_NAME", "")
SQLALCHEMY_DATABASE_URI = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
ALEMBIC_REVISION_PATH = os.getenv("ALEMBIC_REVISION_PATH", "")
ALEMBIC_INI_PATH = os.getenv("ALEMBIC_INI_PATH", "")

engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
)

Session = sessionmaker(bind=engine)
Base = declarative_base()
