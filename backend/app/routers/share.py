"""Share router module for public access to shared prompts."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.database import get_db
from app.schemas.prompt import Prompt as PromptSchema
from app.services import prompt as prompt_service

# Create router
router = APIRouter(tags=["share"])


@router.get("/share/{token}", response_model=PromptSchema)
async def get_shared_prompt(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a shared prompt by token (public access, no authentication required).
    
    Args:
        token: Share token
        db: Database session
        
    Returns:
        Prompt data
        
    Raises:
        HTTPException: If token is invalid or prompt not found
    """
    try:
        # Get shared prompt
        prompt = await prompt_service.get_shared_prompt(db, token)
        
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shared prompt not found or token is invalid"
            )
            
        return prompt
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting shared prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get shared prompt"
        )