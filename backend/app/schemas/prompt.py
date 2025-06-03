"""Prompt schemas for the application."""
from typing import List, Optional
from datetime import datetime
import uuid
from pydantic import BaseModel, Field, ConfigDict


class PromptBase(BaseModel):
    """Base schema for Prompt."""
    prompt_text: str
    prompt_type: Optional[str] = None


class PromptCreate(PromptBase):
    """Schema for creating a Prompt."""
    project_id: uuid.UUID


class PromptUpdate(BaseModel):
    """Schema for updating a Prompt."""
    prompt_text: Optional[str] = None
    generated_content: Optional[str] = None
    prompt_type: Optional[str] = None
    status: Optional[str] = None


class PromptInDBBase(PromptBase):
    """Base schema for Prompt in DB."""
    id: uuid.UUID
    project_id: uuid.UUID
    user_id: uuid.UUID
    generated_content: Optional[str] = None
    status: str = "pending"
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class Prompt(PromptInDBBase):
    """Schema for Prompt response."""
    pass


class PromptWithVersions(Prompt):
    """Schema for Prompt with Versions."""
    from app.schemas.prompt_version import PromptVersion  # Import here to avoid circular imports
    
    versions: List[PromptVersion] = []