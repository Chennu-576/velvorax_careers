from typing import Optional, List, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.models.location import Country, StateProvince, District, MandalTehsil, CityTown, PostalCode
from app.models.job import Job

router = APIRouter(prefix="/locations", tags=["Geographic Database"])

class CountryResponse(BaseModel):
    id: int
    name: str
    iso2: str
    iso3: str
    phone_code: str
    region: str
    currency_code: str
    flag_emoji: Optional[str] = None
    is_active: bool
    active_jobs_count: int = 0

    class Config:
        from_attributes = True

class StateResponse(BaseModel):
    id: int
    country_id: int
    name: str
    code: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class DistrictResponse(BaseModel):
    id: int
    state_id: int
    name: str
    is_active: bool

    class Config:
        from_attributes = True

class MandalResponse(BaseModel):
    id: int
    district_id: int
    name: str
    is_active: bool

    class Config:
        from_attributes = True

class CityResponse(BaseModel):
    id: int
    state_id: int
    district_id: Optional[int] = None
    name: str
    is_active: bool

    class Config:
        from_attributes = True

class PostalCodeResponse(BaseModel):
    id: int
    city_id: Optional[int] = None
    district_id: Optional[int] = None
    mandal_id: Optional[int] = None
    pin_code: str
    locality_name: Optional[str] = None

    class Config:
        from_attributes = True

@router.get("/countries", response_model=List[CountryResponse])
async def list_countries(
    region: Optional[str] = Query(None, description="Asia, Europe, North America, etc."),
    db: AsyncSession = Depends(get_db)
) -> Any:
    conditions = [Country.is_active == True]
    if region:
        conditions.append(Country.region == region)

    stmt = select(Country).where(and_(*conditions)).order_by(Country.name.asc())
    countries = (await db.execute(stmt)).scalars().all()

    response_items = []
    for c in countries:
        job_count_stmt = select(func.count(Job.id)).where(
            Job.country == c.name,
            Job.status == "PUBLISHED"
        )
        active_jobs = (await db.execute(job_count_stmt)).scalar_one()

        item = CountryResponse(
            id=c.id,
            name=c.name,
            iso2=c.iso2,
            iso3=c.iso3,
            phone_code=c.phone_code,
            region=c.region,
            currency_code=c.currency_code,
            flag_emoji=c.flag_emoji,
            is_active=c.is_active,
            active_jobs_count=active_jobs
        )
        response_items.append(item)

    return response_items

@router.get("/states", response_model=List[StateResponse])
async def list_states(
    country_id: Optional[int] = Query(None),
    country: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
) -> Any:
    target_country_id = country_id
    if not target_country_id and country:
        stmt = select(Country.id).where(Country.name.ilike(f"%{country.strip()}%"))
        target_country_id = (await db.execute(stmt)).scalar_one_or_none()

    conditions = [StateProvince.is_active == True]
    if target_country_id:
        conditions.append(StateProvince.country_id == target_country_id)

    stmt = (
        select(StateProvince)
        .where(and_(*conditions))
        .order_by(StateProvince.name.asc())
    )
    states = (await db.execute(stmt)).scalars().all()
    return [StateResponse.model_validate(s) for s in states]

@router.get("/districts", response_model=List[DistrictResponse])
async def list_districts(
    state_id: Optional[int] = Query(None),
    state: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
) -> Any:
    target_state_id = state_id
    if not target_state_id and state:
        stmt = select(StateProvince.id).where(StateProvince.name.ilike(f"%{state.strip()}%"))
        target_state_id = (await db.execute(stmt)).scalar_one_or_none()

    conditions = [District.is_active == True]
    if target_state_id:
        conditions.append(District.state_id == target_state_id)

    stmt = (
        select(District)
        .where(and_(*conditions))
        .order_by(District.name.asc())
    )
    districts = (await db.execute(stmt)).scalars().all()
    return [DistrictResponse.model_validate(d) for d in districts]

@router.get("/mandals", response_model=List[MandalResponse])
async def list_mandals(
    district_id: Optional[int] = Query(None, description="Indian administrative Mandal/Tehsil lookup"),
    district: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
) -> Any:
    target_dist_id = district_id
    if not target_dist_id and district:
        stmt = select(District.id).where(District.name.ilike(f"%{district.strip()}%"))
        target_dist_id = (await db.execute(stmt)).scalar_one_or_none()

    conditions = [MandalTehsil.is_active == True]
    if target_dist_id:
        conditions.append(MandalTehsil.district_id == target_dist_id)

    stmt = (
        select(MandalTehsil)
        .where(and_(*conditions))
        .order_by(MandalTehsil.name.asc())
    )
    mandals = (await db.execute(stmt)).scalars().all()
    return [MandalResponse.model_validate(m) for m in mandals]

@router.get("/cities", response_model=List[CityResponse])
async def list_cities(
    state_id: Optional[int] = Query(None),
    state: Optional[str] = Query(None),
    district_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
) -> Any:
    conditions = [CityTown.is_active == True]
    if state_id:
        conditions.append(CityTown.state_id == state_id)
    elif state:
        stmt = select(StateProvince.id).where(StateProvince.name.ilike(f"%{state.strip()}%"))
        sid = (await db.execute(stmt)).scalar_one_or_none()
        if sid:
            conditions.append(CityTown.state_id == sid)

    if district_id:
        conditions.append(CityTown.district_id == district_id)

    stmt = select(CityTown).where(and_(*conditions)).order_by(CityTown.name.asc())
    cities = (await db.execute(stmt)).scalars().all()
    return [CityResponse.model_validate(c) for c in cities]

@router.get("/postal-codes", response_model=List[PostalCodeResponse])
async def list_postal_codes(
    q: Optional[str] = Query(None, description="PIN code or locality name search"),
    city_id: Optional[int] = Query(None),
    district_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
) -> Any:
    conditions = []
    if q:
        conditions.append(
            (PostalCode.pin_code.ilike(f"%{q.strip()}%")) |
            (PostalCode.locality_name.ilike(f"%{q.strip()}%"))
        )
    if city_id:
        conditions.append(PostalCode.city_id == city_id)
    if district_id:
        conditions.append(PostalCode.district_id == district_id)

    stmt = select(PostalCode).where(and_(*conditions)).limit(50)
    pins = (await db.execute(stmt)).scalars().all()
    return [PostalCodeResponse.model_validate(p) for p in pins]
