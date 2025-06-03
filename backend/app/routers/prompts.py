"""Prompt router module."""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.database import get_db
from app.models.user import User
from app.models.prompt import Prompt
from app.schemas.prompt import PromptCreate, PromptUpdate, Prompt as PromptSchema
from app.services import prompt as prompt_service
from app.core.deps import get_current_user

# Create router
router = APIRouter(tags=["prompts"])


@router.post("/projects/{project_id}/prompts/", response_model=PromptSchema, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    project_id: UUID,
    prompt_in: PromptCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new prompt for a project."""
    try:
        # Ensure project_id in path matches project_id in body
        if prompt_in.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project ID in path does not match project ID in body"
            )
            
        return await prompt_service.create_prompt(db, prompt_in, current_user.id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create prompt"
        )


@router.get("/projects/{project_id}/prompts/", response_model=List[PromptSchema])
async def get_prompts(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all prompts for a project."""
    try:
        return await prompt_service.get_prompts_by_project(db, project_id, current_user.id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prompts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get prompts"
        )


@router.get("/projects/{project_id}/prompts/{prompt_id}", response_model=PromptSchema)
async def get_prompt(
    project_id: UUID,
    prompt_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a prompt by ID."""
    try:
        prompt = await prompt_service.get_prompt(db, prompt_id, current_user.id)
        
        # Ensure prompt belongs to the specified project
        if prompt.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prompt not found in this project"
            )
            
        return prompt
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get prompt"
        )


@router.put("/projects/{project_id}/prompts/{prompt_id}", response_model=PromptSchema)
async def update_prompt(
    project_id: UUID,
    prompt_id: UUID,
    prompt_in: PromptUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a prompt."""
    try:
        prompt = await prompt_service.get_prompt(db, prompt_id, current_user.id)
        
        # Ensure prompt belongs to the specified project
        if prompt.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prompt not found in this project"
            )
            
        return await prompt_service.update_prompt(db, prompt_id, prompt_in, current_user.id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update prompt"
        )


@router.delete("/projects/{project_id}/prompts/{prompt_id}", response_model=PromptSchema)
async def delete_prompt(
    project_id: UUID,
    prompt_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a prompt."""
    try:
        prompt = await prompt_service.get_prompt(db, prompt_id, current_user.id)
        
        # Ensure prompt belongs to the specified project
        if prompt.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prompt not found in this project"
            )
            
        return await prompt_service.delete_prompt(db, prompt_id, current_user.id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete prompt"
        )