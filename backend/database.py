"""
Database configuration and models for Ferienhaus Kalender
Using SQLAlchemy async with PostgreSQL
"""
import os
from datetime import date, datetime
from typing import AsyncGenerator

from sqlalchemy import String, Text, Date, DateTime, Integer, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///ferienhaus.db"
)

# Engine options
engine_options = {
    "echo": os.getenv("DEBUG", "false").lower() == "true",
}

# PostgreSQL-specific options
if DATABASE_URL.startswith("postgresql"):
    engine_options["pool_pre_ping"] = True

# Create async engine
engine = create_async_engine(DATABASE_URL, **engine_options)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Base class for models
class Base(DeclarativeBase):
    pass


# Models
class Booking(Base):
    """Booking model for vacation rental reservations"""
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    party_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Booking(id={self.id}, party_id={self.party_id}, {self.start_date} - {self.end_date})>"


class Party(Base):
    """Party model (optional - for future extensibility)"""
    __tablename__ = "parties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str] = mapped_column(String(7), nullable=False)  # Hex color

    def __repr__(self) -> str:
        return f"<Party(id={self.id}, name={self.name})>"


# Database initialization
async def init_db():
    """Initialize database - create all tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides a database session"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
