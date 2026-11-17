from typing import Optional, List, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.permissions import require_admin
from app.models.user import User
from app.models.cms import CMSContent, PlatformSetting
from app.schemas.cms import CMSContentResponse, CMSContentUpdate, PlatformSettingResponse

router = APIRouter(prefix="/cms", tags=["Content Management System"])

@router.get("/content/{section_key}", response_model=CMSContentResponse)
async def get_cms_content(
    section_key: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(CMSContent).where(CMSContent.section_key == section_key)
    content = (await db.execute(stmt)).scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"CMS section '{section_key}' not found.")
    return CMSContentResponse.model_validate(content)

@router.put("/content/{section_key}", response_model=CMSContentResponse)
async def update_cms_content(
    section_key: str,
    payload: CMSContentUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(CMSContent).where(CMSContent.section_key == section_key)
    content = (await db.execute(stmt)).scalar_one_or_none()
    if not content:
        content = CMSContent(section_key=section_key)
        db.add(content)

    if payload.title is not None:
        content.title = payload.title
    if payload.subtitle is not None:
        content.subtitle = payload.subtitle
    if payload.body is not None:
        content.body = payload.body
    if payload.metadata_json is not None:
        content.metadata_json = payload.metadata_json
    if payload.is_active is not None:
        content.is_active = payload.is_active

    content.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(content)
    return CMSContentResponse.model_validate(content)

@router.get("/settings", response_model=List[PlatformSettingResponse])
async def get_platform_settings(
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(PlatformSetting).where(PlatformSetting.is_public == True)
    settings = (await db.execute(stmt)).scalars().all()
    return [PlatformSettingResponse.model_validate(s) for s in settings]
