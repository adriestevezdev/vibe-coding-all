"""Prompt router module."""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.database import get_db
from app.models.user import User
from app.models.prompt import Prompt
from app.schemas.prompt import PromptCreate, PromptUpdate, Prompt as PromptSchema
from app.services import prompt as prompt_service
from app.services.openai import openai_service
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


@router.post("/prompts/{prompt_id}/process", response_model=PromptSchema)
async def process_prompt(
    prompt_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process a prompt using OpenAI API.
    
    This endpoint initiates the processing of a prompt using OpenAI.
    The processing is done asynchronously in the background.
    """
    try:
        # Get the prompt and validate ownership
        prompt = await prompt_service.get_prompt(db, prompt_id, current_user.id)
        
        # Check if prompt is already processing or completed
        if prompt.status == "processing":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prompt is already being processed"
            )
        
        # Update prompt status to processing
        await prompt_service.update_prompt(
            db, 
            prompt_id, 
            PromptUpdate(status="processing"),
            current_user.id
        )
        
        # Add background task to process with OpenAI
        background_tasks.add_task(
            process_prompt_with_openai,
            prompt_id,
            prompt.prompt_text,
            current_user.id
        )
        
        # Return the updated prompt
        return await prompt_service.get_prompt(db, prompt_id, current_user.id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process prompt"
        )


async def process_prompt_with_openai(
    prompt_id: UUID, 
    prompt_text: str,
    user_id: UUID
):
    """Background task to process prompt with OpenAI.
    
    Args:
        prompt_id: The ID of the prompt to process
        prompt_text: The text of the prompt
        user_id: The ID of the user who owns the prompt
    """
    from app.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            logger.info(f"Processing prompt {prompt_id} with OpenAI")
            
            # Generate completion using OpenAI
            generated_content = await openai_service.generate_completion(
                prompt=prompt_text,
                max_tokens=2000,
                temperature=0.7
            )
            
            # Update prompt with generated content
            await prompt_service.update_prompt(
                db,
                prompt_id,
                PromptUpdate(
                    generated_content=generated_content,
                    status="completed"
                ),
                user_id
            )
            
            logger.info(f"Successfully processed prompt {prompt_id}")
            
        except Exception as e:
            logger.error(f"Error in background task processing prompt {prompt_id}: {e}")
            
            # Update prompt status to failed
            try:
                await prompt_service.update_prompt(
                    db,
                    prompt_id,
                    PromptUpdate(status="failed"),
                    user_id
                )
            except Exception as update_error:
                logger.error(f"Failed to update prompt status to failed: {update_error}")


# Additional endpoints that don't require project_id in path

@router.get("/prompts/{prompt_id}/status", response_model=dict)
async def get_prompt_status(
    prompt_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the processing status of a prompt.
    
    Returns:
        Dictionary with status and generated_at timestamp (if available)
    """
    try:
        # Get prompt (will validate ownership)
        prompt = await prompt_service.get_prompt(db, prompt_id, current_user.id)
        
        response = {
            "id": str(prompt.id),
            "status": prompt.status,
            "generated_at": prompt.generated_at.isoformat() if prompt.generated_at else None
        }
        
        # Include partial content if processing is complete
        if prompt.status == "completed" and prompt.generated_content:
            response["content_preview"] = prompt.generated_content[:200] + "..." if len(prompt.generated_content) > 200 else prompt.generated_content
            
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prompt status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get prompt status"
        )


@router.post("/prompts/{prompt_id}/share", response_model=dict)
async def create_share_link(
    prompt_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a share link for a prompt.
    
    Returns:
        Dictionary with the share URL
    """
    try:
        # Create share link
        share_token = await prompt_service.create_share_link(db, prompt_id, current_user.id)
        
        # Return the share URL
        return {
            "share_token": share_token,
            "share_url": f"/share/{share_token}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating share link: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create share link"
        )
