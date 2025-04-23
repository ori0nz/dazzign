#!/usr/bin/env python
"""
Script to reset the database by dropping and recreating all tables
"""
import asyncio
import logging
import sys
import os

# Add the parent directory to sys.path to allow imports from app package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.ext.asyncio import create_async_engine
from app.db.session import Base
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def reset_database():
    """Drop and recreate all tables in the database"""
    
    logger.info("Connecting to database...")
    engine = create_async_engine(
        str(settings.DATABASE_URL),
        echo=settings.LOG_LEVEL == "DEBUG"
    )
    
    try:
        # Drop all tables
        logger.info("Dropping all tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        # Recreate all tables
        logger.info("Recreating all tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("Database reset completed successfully.")
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    logger.info("Starting database reset...")
    asyncio.run(reset_database()) 