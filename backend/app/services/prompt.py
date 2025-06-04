"""Prompt service module."""
from typing import List, Optional
from uuid import UUID
import re
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from fastapi import HTTPException, status
from loguru import logger

from app.models.prompt import Prompt
from app.models.project import Project
from app.models.prompt_version import PromptVersion
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
        
        # Store the current state as a version before updating
        should_create_version = False
        version_prompt_text = prompt.prompt_text
        version_generated_content = prompt.generated_content
        
        # Update prompt
        update_data = prompt_in.model_dump(exclude_unset=True)
        
        # Sanitizar el texto del prompt si está presente
        if "prompt_text" in update_data and update_data["prompt_text"]:
            update_data["prompt_text"] = sanitize_prompt_text(update_data["prompt_text"])
            # If prompt text is changing, we should create a version
            if update_data["prompt_text"] != prompt.prompt_text:
                should_create_version = True
        
        # Si se está actualizando el contenido generado, establecer generated_at
        if "generated_content" in update_data and update_data["generated_content"]:
            update_data["generated_at"] = datetime.now(timezone.utc)
            # If generated content is being added/changed, we should create a version
            if update_data["generated_content"] != prompt.generated_content:
                should_create_version = True
        
        # Create version if we're making significant changes
        if should_create_version and (version_prompt_text or version_generated_content):
            await create_prompt_version(
                db, 
                prompt_id, 
                version_prompt_text, 
                version_generated_content
            )
        
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


async def create_share_link(db: AsyncSession, prompt_id: UUID, user_id: UUID) -> str:
    """Create a share link for a prompt.
    
    Args:
        db: Database session
        prompt_id: Prompt ID
        user_id: User ID
        
    Returns:
        Share token
        
    Raises:
        HTTPException: If prompt not found or user is not the owner
    """
    try:
        # Get prompt and validate ownership
        prompt = await get_prompt(db, prompt_id, user_id)
        
        # Generate unique share token if not exists
        if not prompt.share_token:
            share_token = str(uuid.uuid4())
            
            # Update prompt with share token
            await db.execute(
                update(Prompt)
                .where(Prompt.id == prompt_id)
                .values(share_token=share_token)
            )
            await db.commit()
            await db.refresh(prompt)
            
            return share_token
        
        return prompt.share_token
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating share link: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create share link"
        )


async def get_shared_prompt(db: AsyncSession, share_token: str) -> Optional[Prompt]:
    """Get a prompt by share token without authentication.
    
    Args:
        db: Database session
        share_token: Share token
        
    Returns:
        Prompt if found, None otherwise
    """
    try:
        # Get prompt by share token
        result = await db.execute(
            select(Prompt).where(
                Prompt.share_token == share_token
            )
        )
        prompt = result.scalars().first()
        
        return prompt
    except Exception as e:
        logger.error(f"Error getting shared prompt: {e}")
        return None


async def create_prompt_version(
    db: AsyncSession, 
    prompt_id: UUID, 
    prompt_text: str, 
    generated_content: Optional[str] = None
) -> PromptVersion:
    """Create a new version of a prompt.
    
    Args:
        db: Database session
        prompt_id: Prompt ID
        prompt_text: Prompt text content
        generated_content: Generated content (optional)
        
    Returns:
        Created prompt version
    """
    try:
        # Get the current highest version number for this prompt
        result = await db.execute(
            select(PromptVersion.version_number)
            .where(PromptVersion.prompt_id == prompt_id)
            .order_by(PromptVersion.version_number.desc())
            .limit(1)
        )
        max_version = result.scalars().first()
        next_version = (max_version or 0) + 1
        
        # Create new version
        db_version = PromptVersion(
            prompt_id=prompt_id,
            version_number=next_version,
            prompt_text=prompt_text,
            generated_content=generated_content
        )
        
        db.add(db_version)
        await db.commit()
        await db.refresh(db_version)
        
        return db_version
    except Exception as e:
        logger.error(f"Error creating prompt version: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create prompt version"
        )


async def get_prompt_versions(db: AsyncSession, prompt_id: UUID, user_id: UUID) -> List[PromptVersion]:
    """Get all versions of a prompt.
    
    Args:
        db: Database session
        prompt_id: Prompt ID
        user_id: User ID
        
    Returns:
        List of prompt versions
    """
    try:
        # First validate prompt ownership
        await get_prompt(db, prompt_id, user_id)
        
        # Get all versions for this prompt
        result = await db.execute(
            select(PromptVersion)
            .where(PromptVersion.prompt_id == prompt_id)
            .order_by(PromptVersion.version_number.desc())
        )
        versions = result.scalars().all()
        
        return list(versions)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prompt versions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get prompt versions"
        )


async def get_prompt_version(
    db: AsyncSession, 
    prompt_id: UUID, 
    version_number: int, 
    user_id: UUID
) -> PromptVersion:
    """Get a specific version of a prompt.
    
    Args:
        db: Database session
        prompt_id: Prompt ID
        version_number: Version number
        user_id: User ID
        
    Returns:
        Prompt version
    """
    try:
        # First validate prompt ownership
        await get_prompt(db, prompt_id, user_id)
        
        # Get specific version
        result = await db.execute(
            select(PromptVersion)
            .where(
                PromptVersion.prompt_id == prompt_id,
                PromptVersion.version_number == version_number
            )
        )
        version = result.scalars().first()
        
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prompt version not found"
            )
            
        return version
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prompt version: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get prompt version"
        )