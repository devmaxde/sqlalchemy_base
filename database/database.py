import logging
import os

from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .utils import build_database_url

DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')

url = build_database_url(DB_USER, DB_PASS, DB_HOST, DB_NAME)
connect_args = {}
if url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
engine = create_engine(
    url, pool_pre_ping=True, pool_recycle=3600, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False,
                            bind=engine)

if url.startswith("sqlite://"):
    if not os.path.exists("../sql_app.db"):
        logging.info("Creating SQLite database")

        CustomBase = declarative_base()


        class Alembic(CustomBase):
            __tablename__ = "alembic_version"
            version_num = Column(String(32), primary_key=True)


        CustomBase.metadata.create_all(engine)
    else:
        logging.info("SQLite database already exists")

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
