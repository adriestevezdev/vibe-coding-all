"""Authentication router for user registration and login."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from loguru import logger

from app.database import get_db
from app.schemas.user import UserCreate, User as UserSchema, Token
from app.services.auth import create_user, authenticate_user
from app.core.security import create_access_token
from app.core.config import settings

# Create router
router = APIRouter()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user and return access token.
    
    Args:
        user_in: User registration data
        db: Database session
        
    Returns:
        JWT token for the newly registered user
    """
    # Create new user
    user = await create_user(db, user_in)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists or registration failed"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User registered successfully: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """Login and receive access token.
    
    Args:
        form_data: OAuth2 form with username (email) and password
        db: Database session
        
    Returns:
        JWT token for the authenticated user
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in successfully: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}