from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Create async engine
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.LOG_LEVEL == "DEBUG",
    future=True,
)

# Create async session factory
async_session = sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Create base class for models
Base = declarative_base()

async def get_db() -> AsyncSession:
    """
    Dependency for database session
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close() 