from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    iso2: Mapped[str] = mapped_column(String(2), unique=True, index=True, nullable=False)
    iso3: Mapped[str] = mapped_column(String(3), unique=True, index=True, nullable=False)
    phone_code: Mapped[str] = mapped_column(String(20), nullable=False)
    region: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # Asia, Europe, North America, etc.
    currency_code: Mapped[str] = mapped_column(String(10), default="USD")
    flag_emoji: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    states = relationship("StateProvince", back_populates="country", cascade="all, delete-orphan")

class StateProvince(Base):
    __tablename__ = "states_provinces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    country_id: Mapped[int] = mapped_column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    country = relationship("Country", back_populates="states")
    districts = relationship("District", back_populates="state", cascade="all, delete-orphan")
    cities = relationship("CityTown", back_populates="state", cascade="all, delete-orphan")

class District(Base):
    __tablename__ = "districts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    state_id: Mapped[int] = mapped_column(Integer, ForeignKey("states_provinces.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    state = relationship("StateProvince", back_populates="districts")
    mandals = relationship("MandalTehsil", back_populates="district", cascade="all, delete-orphan")

class MandalTehsil(Base):
    """Specific administrative division for India (Mandal / Tehsil / Taluk)."""
    __tablename__ = "mandals_tehsils"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    district_id: Mapped[int] = mapped_column(Integer, ForeignKey("districts.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    district = relationship("District", back_populates="mandals")

class CityTown(Base):
    __tablename__ = "cities_towns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    state_id: Mapped[int] = mapped_column(Integer, ForeignKey("states_provinces.id", ondelete="CASCADE"), nullable=False, index=True)
    district_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("districts.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    state = relationship("StateProvince", back_populates="cities")
    postal_codes = relationship("PostalCode", back_populates="city", cascade="all, delete-orphan")

class PostalCode(Base):
    __tablename__ = "postal_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    city_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("cities_towns.id", ondelete="CASCADE"), nullable=True)
    district_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("districts.id", ondelete="SET NULL"), nullable=True, index=True)
    mandal_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("mandals_tehsils.id", ondelete="SET NULL"), nullable=True, index=True)
    pin_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    locality_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)

    city = relationship("CityTown", back_populates="postal_codes")

