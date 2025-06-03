"""Prompt schemas for the application."""
from typing import List, Optional
from datetime import datetime
import uuid
from pydantic import BaseModel, Field, ConfigDict, validator
import re


class PromptBase(BaseModel):
    """Base schema for Prompt."""
    prompt_text: str = Field(..., min_length=10, description="Texto del prompt con mínimo 10 caracteres")
    prompt_type: Optional[str] = Field(None, regex="^(feature|bug|improvement|documentation)$")
    
    @validator('prompt_text')
    def validate_vibe_coding_style(cls, v):
        """Validar que el prompt siga el estilo Vibe Coding."""
        if not v or len(v.strip()) < 10:
            raise ValueError('El prompt debe tener al menos 10 caracteres')
        
        # Palabras clave que deben estar presentes en un prompt de "Vibe Coding"
        vibe_coding_keywords = ['vibe', 'coding', 'desarrollo', 'proyecto', 'feature']
        text_lower = v.lower()
        
        if not any(keyword in text_lower for keyword in vibe_coding_keywords):
            raise ValueError('El prompt debe contener al menos una palabra clave de Vibe Coding')
        
        # Eliminar caracteres especiales no deseados
        if re.search(r'[<>{}\[\]\\^~]', v):
            raise ValueError('El prompt contiene caracteres no permitidos')
        
        return v.strip()


class PromptCreate(PromptBase):
    """Schema for creating a Prompt."""
    project_id: uuid.UUID


class PromptUpdate(BaseModel):
    """Schema for updating a Prompt."""
    prompt_text: Optional[str] = Field(None, min_length=10)
    generated_content: Optional[str] = None
    prompt_type: Optional[str] = Field(None, regex="^(feature|bug|improvement|documentation)$")
    status: Optional[str] = Field(None, regex="^(pending|processing|completed|failed)$")
    
    @validator('prompt_text')
    def validate_prompt_text_update(cls, v):
        """Validar texto del prompt en actualizaciones."""
        if v is not None:
            if len(v.strip()) < 10:
                raise ValueError('El prompt debe tener al menos 10 caracteres')
            
            vibe_coding_keywords = ['vibe', 'coding', 'desarrollo', 'proyecto', 'feature']
            text_lower = v.lower()
            
            if not any(keyword in text_lower for keyword in vibe_coding_keywords):
                raise ValueError('El prompt debe contener al menos una palabra clave de Vibe Coding')
            
            if re.search(r'[<>{}\[\]\\^~]', v):
                raise ValueError('El prompt contiene caracteres no permitidos')
            
            return v.strip()
        return v


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