"""Script to initialize Alembic and generate initial migration."""
import os
import subprocess
from loguru import logger


def init_alembic():
    """Initialize Alembic and generate initial migration."""
    try:
        # Initialize Alembic
        logger.info("Initializing Alembic...")
        subprocess.run(["alembic", "init", "alembic"], check=True)
        
        # Update env.py to use async SQLAlchemy
        logger.info("Updating env.py...")
        env_path = os.path.join("alembic", "env.py")
        with open(env_path, "r") as file:
            content = file.read()
        
        # Replace content with async SQLAlchemy configuration
        content = content.replace(
            "from sqlalchemy import pool",
            "from sqlalchemy import pool\nfrom sqlalchemy.ext.asyncio import AsyncEngine"
        )
        
        content = content.replace(
            "from alembic import context",
            "from alembic import context\nfrom app.models import Base\nfrom app.core.config import settings"
        )
        
        content = content.replace(
            "target_metadata = None",
            "target_metadata = Base.metadata"
        )
        
        content = content.replace(
            "    with connectable.connect() as connection:",
            "    connectable = AsyncEngine(connectable)\n    with connectable.connect() as connection:"
        )
        
        # Add configuration for async SQLAlchemy
        content = content.replace(
            "config.set_main_option('sqlalchemy.url', url)",
            "config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)\n    if settings.DATABASE_URL.startswith('postgresql://'):"  # noqa
            "\n        config.set_main_option('sqlalchemy.url', settings.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://', 1))"  # noqa
        )
        
        with open(env_path, "w") as file:
            file.write(content)
        
        # Generate initial migration
        logger.info("Generating initial migration...")
        subprocess.run(["alembic", "revision", "--autogenerate", "-m", "Initial migration"], check=True)
        
        logger.success("Alembic initialized and initial migration generated successfully!")
        logger.info("You can now run 'alembic upgrade head' to apply the migration.")
        
    except Exception as e:
        logger.error(f"Error initializing Alembic: {e}")
        raise


if __name__ == "__main__":
    init_alembic()