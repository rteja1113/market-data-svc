from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/mydatabase"

engine = create_engine(
    DATABASE_URL,
)

Session = sessionmaker(bind=engine)
Base = declarative_base()
