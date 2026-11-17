from typing import Optional, List, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.permissions import require_admin
from app.models.user import User
from app.models.taxonomy import JobCategory, JobSubcategory
from app.models.job import Job

router = APIRouter(prefix="/categories", tags=["Categories & Taxonomy"])

class SubcategorySummary(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class CategoryWithJobsResponse(BaseModel):
    id: int
    name: str
    slug: str
    category_type: str
    description: Optional[str] = None
    icon: Optional[str] = None
    is_active: bool
    display_order: int
    active_jobs_count: int = 0
    subcategories: List[SubcategorySummary] = []

    class Config:
        from_attributes = True

class CategoryCreate(BaseModel):
    name: str
    slug: str
    category_type: str = "IT"  # IT or NON_IT
    description: Optional[str] = None
    icon: Optional[str] = "Briefcase"
    display_order: int = 0

@router.get("", response_model=List[CategoryWithJobsResponse])
async def list_categories(
    category_type: Optional[str] = Query(None, description="IT or NON_IT"),
    is_active: bool = True,
    db: AsyncSession = Depends(get_db)
) -> Any:
    conditions = [JobCategory.is_active == is_active]
    if category_type:
        conditions.append(JobCategory.category_type == category_type.upper())

    stmt = (
        select(JobCategory)
        .where(and_(*conditions))
        .options(selectinload(JobCategory.subcategories))
        .order_by(JobCategory.display_order.asc(), JobCategory.name.asc())
    )
    result = await db.execute(stmt)
    categories = result.scalars().all()

    # Calculate active job counts
    response_items = []
    for cat in categories:
        job_count_stmt = select(func.count(Job.id)).where(
            Job.category_id == cat.id,
            Job.status == "PUBLISHED"
        )
        active_count = (await db.execute(job_count_stmt)).scalar_one()

        item = CategoryWithJobsResponse(
            id=cat.id,
            name=cat.name,
            slug=cat.slug,
            category_type=cat.category_type,
            description=cat.description,
            icon=cat.icon,
            is_active=cat.is_active,
            display_order=cat.display_order,
            active_jobs_count=active_count,
            subcategories=[SubcategorySummary.model_validate(sub) for sub in cat.subcategories if sub.is_active]
        )
        response_items.append(item)

    return response_items

@router.get("/{slug}", response_model=CategoryWithJobsResponse)
async def get_category_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = (
        select(JobCategory)
        .where(JobCategory.slug == slug)
        .options(selectinload(JobCategory.subcategories))
    )
    cat = (await db.execute(stmt)).scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category '{slug}' not found.")

    job_count_stmt = select(func.count(Job.id)).where(
        Job.category_id == cat.id,
        Job.status == "PUBLISHED"
    )
    active_count = (await db.execute(job_count_stmt)).scalar_one()

    return CategoryWithJobsResponse(
        id=cat.id,
        name=cat.name,
        slug=cat.slug,
        category_type=cat.category_type,
        description=cat.description,
        icon=cat.icon,
        is_active=cat.is_active,
        display_order=cat.display_order,
        active_jobs_count=active_count,
        subcategories=[SubcategorySummary.model_validate(sub) for sub in cat.subcategories]
    )

@router.post("", response_model=CategoryWithJobsResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    category = JobCategory(
        name=payload.name,
        slug=payload.slug.lower().replace(" ", "-"),
        category_type=payload.category_type.upper(),
        description=payload.description,
        icon=payload.icon,
        display_order=payload.display_order,
        is_active=True
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return CategoryWithJobsResponse(
        id=category.id,
        name=category.name,
        slug=category.slug,
        category_type=category.category_type,
        description=category.description,
        icon=category.icon,
        is_active=category.is_active,
        display_order=category.display_order,
        active_jobs_count=0,
        subcategories=[]
    )
