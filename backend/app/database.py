from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# 1. Engine: the connection to PostgreSQL
engine = create_engine(settings.DATABASE_URL)

# 2. SessionLocal: creates a "session" to talk to the database
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


# 3. Base: every table class in models.py inherits from this
class Base(DeclarativeBase):
    pass


# 4. get_db: gives each API request its own session and closes it after
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()