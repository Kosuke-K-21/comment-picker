from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings # Assuming settings will have DATABASE_URL

# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db" # For local testing without PostgreSQL
# For now, using a placeholder. Will be replaced by settings.DATABASE_URL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL if hasattr(settings, 'DATABASE_URL') and settings.DATABASE_URL else "sqlite:///./temp_comment_picker.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    # connect_args={"check_same_thread": False} # Only needed for SQLite
)
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False} # Only needed for SQLite
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
