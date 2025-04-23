import logging
from sqlalchemy.ext.asyncio import AsyncEngine
from app.db.session import Base, engine

logger = logging.getLogger(__name__)

async def init_db() -> None:
    """
    Initialize the database by creating all tables
    """
    try:
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise 