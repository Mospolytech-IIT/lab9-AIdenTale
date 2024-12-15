from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from models.db import Base

DATABASE_URL = "postgresql+psycopg2://service:test@88.218.66.164:5432/shopdb"

def create_db() -> sessionmaker[Session]:
    engine = create_engine(DATABASE_URL, echo=True)
    sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    return sessionLocal