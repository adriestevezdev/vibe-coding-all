"""Authentication service for user management."""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from loguru import logger

from app.models.user import User
from app.schemas.user import UserCreate, UserInDB, User as UserSchema
from app.core.security import get_password_hash, verify_password, create_access_token


async def create_user(db: AsyncSession, user_in: UserCreate) -> Optional[UserSchema]:
    """Create a new user in the database.
    
    Args:
        db: Database session
        user_in: User data for creation
        
    Returns:
        Created user or None if creation failed
    """
    try:
        # Check if user with this email already exists
        result = await db.execute(select(User).where(User.email == user_in.email))
        existing_user = result.scalars().first()
        
        if existing_user:
            logger.warning(f"User with email {user_in.email} already exists")
            return None
        
        # Create new user with hashed password
        db_user = User(
            email=user_in.email,
            password_hash=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            is_active=True,
            is_superuser=False
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        logger.info(f"User created successfully: {db_user.email}")
        return UserSchema.model_validate(db_user)
    
    except IntegrityError as e:
        logger.error(f"Database integrity error when creating user: {e}")
        await db.rollback()
        return None
    except Exception as e:
        logger.error(f"Unexpected error when creating user: {e}")
        await db.rollback()
        return None


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[UserSchema]:
    """Authenticate a user by email and password.
    
    Args:
        db: Database session
        email: User email
        password: User password
        
    Returns:
        Authenticated user or None if authentication failed
    """
    try:
        # Find user by email
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        
        # Check if user exists and password is correct
        if not user or not verify_password(password, user.password_hash):
            return None
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"Inactive user attempted login: {email}")
            return None
            
        return UserSchema.model_validate(user)
    
    except Exception as e:
        logger.error(f"Error during authentication: {e}")
        return None