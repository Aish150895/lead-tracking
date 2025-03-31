from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db
from models import User, UserRole
from schemas import TokenData
from config import settings

# Password hashing utilities
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 setup for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    """Verify that the provided password matches the hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hash a password for storing."""
    return pwd_context.hash(password)

def authenticate_user(db: Session, email: str, password: str):
    """Authenticate a user by email and password."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get the current authenticated user from the token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user
    
# Cookie-based authentication
async def get_token_from_cookie(access_token: str = Cookie(None)):
    if not access_token:
        return None
    return access_token

# Alternative user dependency that checks both header and cookie
async def get_current_user_from_header_or_cookie(
    token: Optional[str] = Depends(oauth2_scheme),
    cookie_token: Optional[str] = Cookie(None, alias="access_token"),
    db: Session = Depends(get_db)
):
    """Get the current user from either an auth header or a cookie."""
    # Use header token if provided, otherwise use cookie
    if not token and not cookie_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    effective_token = token if token else cookie_token
    
    # Check the token
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(effective_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_attorney(current_user: User = Depends(get_current_user)):
    """Check if the current user is an attorney, otherwise raise an error."""
    # Use role-based check
    if current_user.role == UserRole.ATTORNEY:
        return current_user
    
    # Fall back to legacy check for backward compatibility
    if current_user.is_attorney == 1:
        return current_user
        
    # If neither check passed, the user is not an attorney
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to access this resource",
    )

# Attorney check that works with the alternative user dependency
def get_current_attorney_from_header_or_cookie(
    current_user: User = Depends(get_current_user_from_header_or_cookie)
):
    """Check if the current user is an attorney, otherwise raise an error."""
    # Use role-based check
    if current_user.role == UserRole.ATTORNEY:
        return current_user
        
    # Fall back to legacy check for backward compatibility
    if current_user.is_attorney == 1:
        return current_user
    
    # If neither check passed, the user is not an attorney
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to access this resource",
    )
