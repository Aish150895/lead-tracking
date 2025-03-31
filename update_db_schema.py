import logging
from sqlalchemy import text, Column, Enum
from sqlalchemy.exc import SQLAlchemyError

from utils.database import engine, Base, SessionLocal
from models import User, UserRole

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_database_schema():
    """Add the role column to users table if it doesn't exist yet"""
    db = SessionLocal()
    conn = engine.connect()
    
    try:
        # Check if the role column exists by looking at the information schema
        # This is more reliable than trying to select data
        if engine.dialect.name == 'postgresql':
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='role';
            """))
            
            # If role column doesn't exist, add it
            if not result.fetchone():
                logger.info("Role column doesn't exist in PostgreSQL, adding it now...")
                
                # PostgreSQL - need to use raw connection for DDL operations
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN role VARCHAR(50) DEFAULT 'USER' NOT NULL;
                """))
                conn.execute(text("""
                    UPDATE users 
                    SET role = 'ATTORNEY' 
                    WHERE is_attorney = 1;
                """))
                conn.commit()
                logger.info("Successfully added role column and updated existing users in PostgreSQL")
            else:
                logger.info("Role column already exists in PostgreSQL users table")
        else:
            # SQLite approach - try with regular session
            try:
                # Try to check if column exists in SQLite
                db.execute(text("SELECT role FROM users LIMIT 1"))
                logger.info("Role column already exists in SQLite users table")
            except SQLAlchemyError:
                logger.info("Role column doesn't exist in SQLite, adding it now...")
                # SQLite syntax
                db.execute(text("""
                    ALTER TABLE users
                    ADD COLUMN role VARCHAR(50) DEFAULT 'USER' NOT NULL;
                """))
                # Set the role to ATTORNEY for any user with is_attorney = 1
                db.execute(text("""
                    UPDATE users
                    SET role = 'ATTORNEY'
                    WHERE is_attorney = 1;
                """))
                db.commit()
                logger.info("Successfully added role column and updated existing users in SQLite")
    except Exception as e:
        logger.error(f"Error updating database schema: {str(e)}")
        if engine.dialect.name == 'postgresql':
            conn.rollback()
        else:
            db.rollback()
        raise
    finally:
        db.close()
        conn.close()

if __name__ == "__main__":
    logger.info("Starting database schema update")
    update_database_schema()
    logger.info("Database schema update completed")