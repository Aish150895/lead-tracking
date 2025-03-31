import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class LeadState(str, enum.Enum):
    PENDING = "PENDING"
    REACHED_OUT = "REACHED_OUT"

class UserRole(str, enum.Enum):
    USER = "USER"
    ATTORNEY = "ATTORNEY"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.USER)
    # Keep is_attorney for backward compatibility but we'll use 'role' going forward
    is_attorney = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    resume_path = Column(String, nullable=True)  # Path to the resume file
    state = Column(Enum(LeadState), default=LeadState.PENDING)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # If a lead is reached out to, track the attorney who did it
    reached_out_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reached_out_at = Column(DateTime, nullable=True)
    
    # Relationship to the user who reached out
    attorney = relationship("User", foreign_keys=[reached_out_by])
