from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import settings

# Create database engine
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Handle PostgreSQL in serverless environment
if SQLALCHEMY_DATABASE_URL.startswith("postgresql"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_size=20,  # Adjust based on expected usage
        max_overflow=0,
        pool_pre_ping=True,  # Verify connection before using from pool
        pool_recycle=300,  # Recycle connections after 5 minutes of inactivity
    )
else:
    # SQLite configuration
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_vercel_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()