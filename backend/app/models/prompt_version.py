"""PromptVersion model for the application."""
from typing import Optional
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class PromptVersion(Base):
    """PromptVersion model for version control of prompts."""
    
    __tablename__ = "prompt_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt_id = Column(UUID(as_uuid=True), ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    prompt_text = Column(Text, nullable=False)
    generated_content = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    prompt = relationship("Prompt", back_populates="versions")
    
    def __repr__(self):
        return f"<PromptVersion {self.prompt_id}-{self.version_number}>"