from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class CMSContent(Base):
    __tablename__ = "cms_contents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    section_key: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    subtitle: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string for structured fields
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

class Announcement(Base):
    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    announcement_type: Mapped[str] = mapped_column(String(50), default="INFO")  # INFO, ALERT, BANNER
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class PlatformSetting(Base):
    __tablename__ = "platform_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    setting_key: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    setting_value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
