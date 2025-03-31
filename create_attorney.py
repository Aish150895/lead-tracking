import logging
from sqlalchemy.orm import Session

from utils.database import engine, SessionLocal
from models import User, Base, UserRole
from utils.auth import get_password_hash

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_attorney_user(db: Session, email: str, password: str, full_name: str):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        logger.info(f"User with email {email} already exists")
        return existing_user
    
    # Create attorney user
    hashed_password = get_password_hash(password)
    db_user = User(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        role=UserRole.ATTORNEY,
        is_attorney=1  # Keeping for backward compatibility
    )
    
    # Add to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    logger.info(f"Attorney user created: {email}")
    return db_user

def main():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create database session
    db = SessionLocal()
    try:
        # Get attorney credentials from settings
        from config import settings
        
        # Use settings which already have defaults configured
        attorney_email = settings.DEFAULT_ATTORNEY_EMAIL
        attorney_password = settings.DEFAULT_ATTORNEY_PASSWORD
        attorney_name = settings.DEFAULT_ATTORNEY_NAME
        
        # Create default attorney user
        create_attorney_user(
            db=db,
            email=attorney_email,
            password=attorney_password,
            full_name=attorney_name
        )
        logger.info("Default attorney user verified/created")
    finally:
        db.close()

if __name__ == "__main__":
    main()