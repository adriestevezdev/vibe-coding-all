"""User schemas for the application."""
from typing import List, Optional
from datetime import datetime
import uuid
from pydantic import BaseModel, EmailStr, Field, ConfigDict, validator


class UserBase(BaseModel):
    """Base schema for User."""
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, description="User full name")
    is_active: bool = Field(True, description="Whether the user is active")
    is_premium: bool = Field(False, description="Whether the user has premium subscription")


class UserCreate(UserBase):
    """Schema for creating a User."""
    password: str = Field(..., min_length=8, description="User password, minimum 8 characters")
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v
    
    @validator('email')
    def email_format(cls, v):
        """Additional email validation if needed."""
        # EmailStr already validates basic email format
        return v


class UserUpdate(BaseModel):
    """Schema for updating a User."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_premium: Optional[bool] = None


class UserInDBBase(UserBase):
    """Base schema for User in DB."""
    id: uuid.UUID
    is_superuser: bool = False
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class User(UserInDBBase):
    """Schema for User response."""
    pass


class UserInDB(UserInDBBase):
    """Schema for User in DB with password hash."""
    password_hash: str


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema for JWT token payload."""
    sub: str  # User ID
    exp: Optional[int] = None  # Expiration time