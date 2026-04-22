from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os, urllib.parse

database = os.getenv("POSTGRES_DB")
password = urllib.parse.quote_plus(os.getenv("POSTGRES_PASSWORD"))
username = urllib.parse.quote_plus(os.getenv("POSTGRES_USER"))
server = os.getenv("POSTGRES_SERVER")

DATABASE_URL = f"postgresql+psycopg2://{username}:{password}@{server}:5432/{database}"
engine = create_engine(DATABASE_URL, pool_size=5, pool_pre_ping=True, pool_recycle=600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
