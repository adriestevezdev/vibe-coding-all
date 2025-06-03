"""Prompt service module."""
from typing import List, Optional
from uuid import UUID
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from fastapi import HTTPException, status
from loguru import logger

from app.models.prompt import Prompt
from app.models.project import Project
from app.schemas.prompt import PromptCreate, PromptUpdate


async def validate_project_ownership(db: AsyncSession, project_id: UUID, user_id: UUID) -> Project:
    """Validate that the user owns the project.
    
    Args:
        db: Database session
        project_id: Project ID
        user_id: User ID
        
    Returns:
        Project if user is the owner
        
    Raises:
        HTTPException: If project not found or user is not the owner
    """
    try:
        # Get project
        result = await db.execute(
            select(Project).where(
                Project.id == project_id
            )
        )
        project = result.scalars().first()
        
        # Check if project exists
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
            
        # Check if user is the owner
        if project.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
            
        return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating project ownership: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate project ownership"
        )


def sanitize_prompt_text(text: str) -> str:
    """Sanitiza el texto del prompt eliminando caracteres no deseados.
    
    Args:
        text: Texto del prompt
        
    Returns:
        Texto sanitizado
    """
    if not text:
        return ""
        
    # Eliminar espacios múltiples y recortar
    sanitized = re.sub(r'\s+', ' ', text).strip()
    
    # Eliminar caracteres especiales no deseados
    sanitized = re.sub(r'[<>{}\[\]\\^~]', '', sanitized)
    
    return sanitized


async def create_prompt(db: AsyncSession, prompt_in: PromptCreate, user_id: UUID) -> Prompt:
    """Create a new prompt.
    
    Args:
        db: Database session
        prompt_in: Prompt data
        user_id: User ID
        
    Returns:
        Created prompt
    """
    try:
        # Validate project ownership
        await validate_project_ownership(db, prompt_in.project_id, user_id)
        
        # Sanitizar el texto del prompt
        prompt_data = prompt_in.model_dump()
        prompt_data["prompt_text"] = sanitize_prompt_text(prompt_data["prompt_text"])
        
        # Create prompt object
        db_prompt = Prompt(
            **prompt_data,
            user_id=user_id
        )
        
        # Add to database
        db.add(db_prompt)
        await db.commit()
        await db.refresh(db_prompt)
        
        return db_prompt
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating prompt: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create prompt"
        )


async def get_prompt(db: AsyncSession, prompt_id: UUID, user_id: UUID) -> Prompt:
    """Get a prompt by ID.
    
    Args:
        db: Database session
        prompt_id: Prompt ID
        user_id: User ID
        
    Returns:
        Prompt
        
    Raises:
        HTTPException: If prompt not found or user is not the owner
    """
    try:
        # Get prompt
        result = await db.execute(
            select(Prompt).where(
                Prompt.id == prompt_id
            )
        )
        prompt = result.scalars().first()
        
        # Check if prompt exists
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prompt not found"
            )
            
        # Validate project ownership
        await validate_project_ownership(db, prompt.project_id, user_id)
            
        return prompt
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get prompt"
        )


async def get_prompts_by_project(db: AsyncSession, project_id: UUID, user_id: UUID) -> List[Prompt]:
    """Get all prompts for a project.
    
    Args:
        db: Database session
        project_id: Project ID
        user_id: User ID
        
    Returns:
        List of prompts
    """
    try:
        # Validate project ownership
        await validate_project_ownership(db, project_id, user_id)
        
        # Get prompts
        result = await db.execute(
            select(Prompt).where(
                Prompt.project_id == project_id
            )
        )
        prompts = result.scalars().all()
        
        return list(prompts)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prompts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get prompts"
        )


async def update_prompt(
    db: AsyncSession, 
    prompt_id: UUID, 
    prompt_in: PromptUpdate, 
    user_id: UUID
) -> Prompt:
    """Update a prompt.
    
    Args:
        db: Database session
        prompt_id: Prompt ID
        prompt_in: Prompt data
        user_id: User ID
        
    Returns:
        Updated prompt
        
    Raises:
        HTTPException: If prompt not found or user is not the owner
    """
    try:
        # Get prompt
        prompt = await get_prompt(db, prompt_id, user_id)
        
        # Update prompt
        update_data = prompt_in.model_dump(exclude_unset=True)
        
        # Sanitizar el texto del prompt si está presente
        if "prompt_text" in update_data and update_data["prompt_text"]:
            update_data["prompt_text"] = sanitize_prompt_text(update_data["prompt_text"])
        
        if update_data:
            await db.execute(
                update(Prompt)
                .where(Prompt.id == prompt_id)
                .values(**update_data)
            )
            await db.commit()
            await db.refresh(prompt)
            
        return prompt
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating prompt: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update prompt"
        )


async def delete_prompt(db: AsyncSession, prompt_id: UUID, user_id: UUID) -> Prompt:
    """Delete a prompt.
    
    Args:
        db: Database session
        prompt_id: Prompt ID
        user_id: User ID
        
    Returns:
        Deleted prompt
        
    Raises:
        HTTPException: If prompt not found or user is not the owner
    """
    try:
        # Get prompt
        prompt = await get_prompt(db, prompt_id, user_id)
        
        # Delete prompt
        await db.execute(
            delete(Prompt)
            .where(Prompt.id == prompt_id)
        )
        await db.commit()
        
        return prompt
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting prompt: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete prompt"
        )