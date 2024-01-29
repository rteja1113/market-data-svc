from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/mydatabase"

engine = create_engine(
    DATABASE_URL,
)


Base = declarative_base()
