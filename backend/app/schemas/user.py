"""User schemas for the application."""
from typing import List, Optional
from datetime import datetime
import uuid
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Base schema for User."""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating a User."""
    password: str


class UserUpdate(BaseModel):
    """Schema for updating a User."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


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