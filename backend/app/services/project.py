"""Project service module."""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from fastapi import HTTPException, status
from loguru import logger

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


async def create_project(db: AsyncSession, project_in: ProjectCreate, user_id: UUID) -> Project:
    """Create a new project.
    
    Args:
        db: Database session
        project_in: Project data
        user_id: User ID
        
    Returns:
        Created project
    """
    try:
        # Create project object
        db_project = Project(
            **project_in.model_dump(),
            user_id=user_id
        )
        
        # Add to database
        db.add(db_project)
        await db.commit()
        await db.refresh(db_project)
        
        return db_project
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project"
        )


async def get_project(db: AsyncSession, project_id: UUID, user_id: UUID) -> Project:
    """Get a project by ID.
    
    Args:
        db: Database session
        project_id: Project ID
        user_id: User ID
        
    Returns:
        Project
        
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
        logger.error(f"Error getting project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project"
        )


async def get_projects(db: AsyncSession, user_id: UUID) -> List[Project]:
    """Get all projects for a user.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        List of projects
    """
    try:
        # Get projects
        result = await db.execute(
            select(Project).where(
                Project.user_id == user_id
            )
        )
        projects = result.scalars().all()
        
        return list(projects)
    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get projects"
        )


async def update_project(
    db: AsyncSession, 
    project_id: UUID, 
    project_in: ProjectUpdate, 
    user_id: UUID
) -> Project:
    """Update a project.
    
    Args:
        db: Database session
        project_id: Project ID
        project_in: Project data
        user_id: User ID
        
    Returns:
        Updated project
        
    Raises:
        HTTPException: If project not found or user is not the owner
    """
    try:
        # Get project
        project = await get_project(db, project_id, user_id)
        
        # Update project
        update_data = project_in.model_dump(exclude_unset=True)
        
        if update_data:
            await db.execute(
                update(Project)
                .where(Project.id == project_id)
                .values(**update_data)
            )
            await db.commit()
            await db.refresh(project)
            
        return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update project"
        )


async def delete_project(db: AsyncSession, project_id: UUID, user_id: UUID) -> Project:
    """Delete a project.
    
    Args:
        db: Database session
        project_id: Project ID
        user_id: User ID
        
    Returns:
        Deleted project
        
    Raises:
        HTTPException: If project not found or user is not the owner
    """
    try:
        # Get project
        project = await get_project(db, project_id, user_id)
        
        # Delete project
        await db.execute(
            delete(Project)
            .where(Project.id == project_id)
        )
        await db.commit()
        
        return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )