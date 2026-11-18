# from typing import AsyncGenerator
# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
# from sqlalchemy.orm import DeclarativeBase

# from app.core.config import settings

# class Base(DeclarativeBase):
#     pass

# DATABASE_URL = settings.DATABASE_URL
# # Engine initialization
# engine = create_async_engine(
#     DATABASE_URL,
#     echo=False,
#     future=True
# )

# async_session_maker = async_sessionmaker(
#     engine,
#     class_=AsyncSession,
#     expire_on_commit=False,
#     autocommit=False,
#     autoflush=False
# )

# async def get_db() -> AsyncGenerator[AsyncSession, None]:
#     async with async_session_maker() as session:
#         try:
#             yield session
#         finally:
#             await session.close()




from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


# Read database URL from environment settings
DATABASE_URL = settings.DATABASE_URL.strip()

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not configured")

# Convert Render PostgreSQL URL to async SQLAlchemy format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql+asyncpg://",
        1
    )
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+asyncpg://",
        1
    )

# Initialize asynchronous PostgreSQL engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

