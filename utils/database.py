import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import settings

# Set up logging
logger = logging.getLogger(__name__)

# Create database engine
logger.info(f"Creating database engine with URL: {settings.DATABASE_URL}")

# Set up engine with appropriate connect_args
if settings.DATABASE_URL.startswith('sqlite'):
    # SQLite specific settings
    engine = create_engine(
        settings.DATABASE_URL, 
        connect_args={"check_same_thread": False}  # Needed for SQLite
    )
else:
    raise ValueError("Unsupported database type")

logger.info("Database engine created successfully")

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    logger.debug("Creating database session")
    db = SessionLocal()
    try:
        logger.debug("Yielding database session")
        yield db
    finally:
        logger.debug("Closing database session")
        db.close()