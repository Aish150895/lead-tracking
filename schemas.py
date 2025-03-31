from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator
from models import LeadState, UserRole

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.USER
    # Keeping for backward compatibility
    is_attorney: int = 0

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Lead schemas
class LeadBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    notes: Optional[str] = None

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    state: Optional[LeadState] = None
    notes: Optional[str] = None

class LeadResponse(LeadBase):
    id: int
    state: LeadState
    resume_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    reached_out_at: Optional[datetime] = None
    reached_out_by: Optional[int] = None

    model_config = {
        "from_attributes": True
    }

class LeadList(BaseModel):
    leads: List[LeadResponse]
    total: int
