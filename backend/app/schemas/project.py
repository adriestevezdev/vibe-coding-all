"""Project schemas for the application."""
from typing import List, Optional
from datetime import datetime
import uuid
from pydantic import BaseModel, Field, ConfigDict


class ProjectBase(BaseModel):
    """Base schema for Project."""
    name: str
    description: Optional[str] = None
    idea_text: Optional[str] = None
    vibe_coding_tags: Optional[List[str]] = None
    is_public: bool = False


class ProjectCreate(ProjectBase):
    """Schema for creating a Project."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a Project."""
    name: Optional[str] = None
    description: Optional[str] = None
    idea_text: Optional[str] = None
    vibe_coding_tags: Optional[List[str]] = None
    is_public: Optional[bool] = None


class ProjectInDBBase(ProjectBase):
    """Base schema for Project in DB."""
    id: uuid.UUID
    user_id: uuid.UUID
    share_token: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class Project(ProjectInDBBase):
    """Schema for Project response."""
    pass


class ProjectWithPrompts(Project):
    """Schema for Project with Prompts."""
    from app.schemas.prompt import Prompt  # Import here to avoid circular imports
    
    prompts: List[Prompt] = []