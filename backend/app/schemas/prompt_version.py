"""PromptVersion schemas for the application."""
from typing import Optional
from datetime import datetime
import uuid
from pydantic import BaseModel, Field, ConfigDict


class PromptVersionBase(BaseModel):
    """Base schema for PromptVersion."""
    version_number: int
    prompt_text: str
    generated_content: Optional[str] = None


class PromptVersionCreate(PromptVersionBase):
    """Schema for creating a PromptVersion."""
    prompt_id: uuid.UUID


class PromptVersionInDBBase(PromptVersionBase):
    """Base schema for PromptVersion in DB."""
    id: uuid.UUID
    prompt_id: uuid.UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PromptVersion(PromptVersionInDBBase):
    """Schema for PromptVersion response."""
    pass


class PromptVersionRead(BaseModel):
    """Schema for reading PromptVersion."""
    id: uuid.UUID
    version_number: int
    prompt_text: str
    generated_content: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)