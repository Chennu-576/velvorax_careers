import os
import sys
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.database import async_session_maker, engine, Base
from app.models.location import Country, StateProvince, District, MandalTehsil, CityTown, PostalCode

async def import_geographic_data():
    print("=" * 70)
    print("VELVORAX CAREERS - Global Geographic Hierarchy Import Utility")
    print("=" * 70)

    # Initialize tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as db:
        # 1. Countries
        countries_data = [
            {"name": "India", "iso2": "IN", "iso3": "IND", "phone_code": "+91", "region": "Asia", "currency_code": "INR", "flag_emoji": "🇮🇳"},
            {"name": "United States", "iso2": "US", "iso3": "USA", "phone_code": "+1", "region": "North America", "currency_code": "USD", "flag_emoji": "🇺🇸"},
            {"name": "United Kingdom", "iso2": "GB", "iso3": "GBR", "phone_code": "+44", "region": "Europe", "currency_code": "GBP", "flag_emoji": "🇬🇧"},
            {"name": "United Arab Emirates", "iso2": "AE", "iso3": "ARE", "phone_code": "+971", "region": "Middle East", "currency_code": "AED", "flag_emoji": "🇦🇪"},
            {"name": "Germany", "iso2": "DE", "iso3": "DEU", "phone_code": "+49", "region": "Europe", "currency_code": "EUR", "flag_emoji": "🇩🇪"},
            {"name": "Canada", "iso2": "CA", "iso3": "CAN", "phone_code": "+1", "region": "North America", "currency_code": "CAD", "flag_emoji": "🇨🇦"},
            {"name": "Singapore", "iso2": "SG", "iso3": "SGP", "phone_code": "+65", "region": "Asia", "currency_code": "SGD", "flag_emoji": "🇸🇬"},
            {"name": "Australia", "iso2": "AU", "iso3": "AUS", "phone_code": "+61", "region": "Oceania", "currency_code": "AUD", "flag_emoji": "🇦🇺"},
        ]

        print("[1/5] Importing Countries...")
        country_map = {}
        for c in countries_data:
            stmt = select(Country).where(Country.iso2 == c["iso2"])
            existing = (await db.execute(stmt)).scalar_one_or_none()
            if not existing:
                existing = Country(**c)
                db.add(existing)
                await db.flush()
            country_map[c["name"]] = existing

        # 2. States / Provinces
        print("[2/5] Importing States & Provinces...")
        states_data = [
            # India
            {"country": "India", "name": "Telangana", "code": "TG"},
            {"country": "India", "name": "Andhra Pradesh", "code": "AP"},
            {"country": "India", "name": "Karnataka", "code": "KA"},
            {"country": "India", "name": "Maharashtra", "code": "MH"},
            {"country": "India", "name": "Tamil Nadu", "code": "TN"},
            {"country": "India", "name": "Delhi", "code": "DL"},
            {"country": "India", "name": "Uttar Pradesh", "code": "UP"},
            {"country": "India", "name": "West Bengal", "code": "WB"},
            {"country": "India", "name": "Gujarat", "code": "GJ"},
            {"country": "India", "name": "Kerala", "code": "KL"},
            # US
            {"country": "United States", "name": "California", "code": "CA"},
            {"country": "United States", "name": "New York", "code": "NY"},
            {"country": "United States", "name": "Texas", "code": "TX"},
            {"country": "United States", "name": "Washington", "code": "WA"},
            # UK
            {"country": "United Kingdom", "name": "Greater London", "code": "LON"},
            {"country": "United Kingdom", "name": "Manchester", "code": "MAN"},
            # UAE
            {"country": "United Arab Emirates", "name": "Dubai", "code": "DXB"},
            {"country": "United Arab Emirates", "name": "Abu Dhabi", "code": "AUH"},
            # Germany
            {"country": "Germany", "name": "Bavaria", "code": "BY"},
            {"country": "Germany", "name": "Berlin", "code": "BE"},
            # Canada
            {"country": "Canada", "name": "Ontario", "code": "ON"},
            {"country": "Canada", "name": "British Columbia", "code": "BC"},
            # Singapore
            {"country": "Singapore", "name": "Central Region", "code": "CR"},
            # Australia
            {"country": "Australia", "name": "New South Wales", "code": "NSW"},
            {"country": "Australia", "name": "Victoria", "code": "VIC"},
        ]

        state_map = {}
        for s in states_data:
            country = country_map.get(s["country"])
            if not country:
                continue
            stmt = select(StateProvince).where(
                StateProvince.country_id == country.id,
                StateProvince.name == s["name"]
            )
            existing = (await db.execute(stmt)).scalar_one_or_none()
            if not existing:
                existing = StateProvince(country_id=country.id, name=s["name"], code=s["code"])
                db.add(existing)
                await db.flush()
            state_map[s["name"]] = existing

        # 3. Districts (Focus on Telangana and key hubs)
        print("[3/5] Importing Districts & Administrative Subdivisions...")
        districts_data = [
            {"state": "Telangana", "name": "Medchal-Malkajgiri"},
            {"state": "Telangana", "name": "Hyderabad"},
            {"state": "Telangana", "name": "Rangareddy"},
            {"state": "Telangana", "name": "Sangareddy"},
            {"state": "Telangana", "name": "Warangal"},
            {"state": "Andhra Pradesh", "name": "Visakhapatnam"},
            {"state": "Andhra Pradesh", "name": "Vijayawada (NTR)"},
            {"state": "Karnataka", "name": "Bengaluru Urban"},
            {"state": "Maharashtra", "name": "Mumbai City"},
            {"state": "Maharashtra", "name": "Pune"},
            {"state": "Tamil Nadu", "name": "Chennai"},
            {"state": "Delhi", "name": "New Delhi"},
        ]

        district_map = {}
        for d in districts_data:
            state = state_map.get(d["state"])
            if not state:
                continue
            stmt = select(District).where(
                District.state_id == state.id,
                District.name == d["name"]
            )
            existing = (await db.execute(stmt)).scalar_one_or_none()
            if not existing:
                existing = District(state_id=state.id, name=d["name"])
                db.add(existing)
                await db.flush()
            district_map[d["name"]] = existing

        # 4. Mandals / Tehsils (Specifically including Serilingampally, Quthbullapur, Kukatpally)
        print("[4/5] Importing Mandals / Tehsils...")
        mandals_data = [
            {"district": "Medchal-Malkajgiri", "name": "Kukatpally"},
            {"district": "Medchal-Malkajgiri", "name": "Quthbullapur"},
            {"district": "Medchal-Malkajgiri", "name": "Malkajgiri"},
            {"district": "Rangareddy", "name": "Serilingampally"},
            {"district": "Rangareddy", "name": "Rajendranagar"},
            {"district": "Hyderabad", "name": "Ameerpet"},
            {"district": "Hyderabad", "name": "Khairatabad"},
            {"district": "Hyderabad", "name": "Secunderabad"},
        ]

        mandal_map = {}
        for m in mandals_data:
            district = district_map.get(m["district"])
            if not district:
                continue
            stmt = select(MandalTehsil).where(
                MandalTehsil.district_id == district.id,
                MandalTehsil.name == m["name"]
            )
            existing = (await db.execute(stmt)).scalar_one_or_none()
            if not existing:
                existing = MandalTehsil(district_id=district.id, name=m["name"])
                db.add(existing)
                await db.flush()
            mandal_map[m["name"]] = existing

        # 5. Cities, Towns & Postal Codes
        print("[5/5] Importing Cities, Localities & PIN Codes (including Miyapur PIN 500049)...")
        cities_data = [
            # India
            {"state": "Telangana", "district": "Hyderabad", "name": "Hyderabad"},
            {"state": "Telangana", "district": "Medchal-Malkajgiri", "name": "Secunderabad"},
            {"state": "Karnataka", "district": "Bengaluru Urban", "name": "Bengaluru"},
            {"state": "Maharashtra", "district": "Mumbai City", "name": "Mumbai"},
            {"state": "Maharashtra", "district": "Pune", "name": "Pune"},
            {"state": "Tamil Nadu", "district": "Chennai", "name": "Chennai"},
            {"state": "Delhi", "district": "New Delhi", "name": "New Delhi"},
            # International
            {"state": "California", "district": None, "name": "San Francisco"},
            {"state": "California", "district": None, "name": "San Jose"},
            {"state": "New York", "district": None, "name": "New York City"},
            {"state": "Washington", "district": None, "name": "Seattle"},
            {"state": "Texas", "district": None, "name": "Austin"},
            {"state": "Greater London", "district": None, "name": "London"},
            {"state": "Dubai", "district": None, "name": "Dubai"},
            {"state": "Berlin", "district": None, "name": "Berlin"},
            {"state": "Ontario", "district": None, "name": "Toronto"},
            {"state": "Central Region", "district": None, "name": "Singapore"},
            {"state": "New South Wales", "district": None, "name": "Sydney"},
        ]

        city_map = {}
        for c in cities_data:
            state = state_map.get(c["state"])
            if not state:
                continue
            dist = district_map.get(c["district"]) if c.get("district") else None
            stmt = select(CityTown).where(
                CityTown.state_id == state.id,
                CityTown.name == c["name"]
            )
            existing = (await db.execute(stmt)).scalar_one_or_none()
            if not existing:
                existing = CityTown(
                    state_id=state.id,
                    district_id=dist.id if dist else None,
                    name=c["name"]
                )
                db.add(existing)
                await db.flush()
            city_map[c["name"]] = existing

        # Specific PIN Codes (Mandatory: PIN 500049 Miyapur, Medchal-Malkajgiri)
        postal_codes_data = [
            {
                "city": "Hyderabad",
                "pin_code": "500049",
                "locality_name": "Miyapur, Medchal-Malkajgiri",
                "district": "Medchal-Malkajgiri",
                "mandal": "Kukatpally"
            },
            {
                "city": "Hyderabad",
                "pin_code": "500081",
                "locality_name": "Madhapur / HITEC City",
                "district": "Rangareddy",
                "mandal": "Serilingampally"
            },
            {
                "city": "Hyderabad",
                "pin_code": "500032",
                "locality_name": "Gachibowli / Financial District",
                "district": "Rangareddy",
                "mandal": "Serilingampally"
            },
            {
                "city": "Hyderabad",
                "pin_code": "500072",
                "locality_name": "KPHB Colony / Kukatpally",
                "district": "Medchal-Malkajgiri",
                "mandal": "Kukatpally"
            },
            {
                "city": "Bengaluru",
                "pin_code": "560100",
                "locality_name": "Electronic City",
                "district": "Bengaluru Urban",
                "mandal": None
            },
            {
                "city": "Bengaluru",
                "pin_code": "560066",
                "locality_name": "Whitefield",
                "district": "Bengaluru Urban",
                "mandal": None
            },
            {
                "city": "San Francisco",
                "pin_code": "94105",
                "locality_name": "South of Market (SoMa)",
                "district": None,
                "mandal": None
            },
            {
                "city": "London",
                "pin_code": "EC2A",
                "locality_name": "Tech City / Shoreditch",
                "district": None,
                "mandal": None
            }
        ]

        for p in postal_codes_data:
            city = city_map.get(p["city"])
            dist = district_map.get(p["district"]) if p.get("district") else None
            mandal = mandal_map.get(p["mandal"]) if p.get("mandal") else None
            stmt = select(PostalCode).where(
                PostalCode.pin_code == p["pin_code"],
                PostalCode.locality_name == p["locality_name"]
            )
            existing = (await db.execute(stmt)).scalar_one_or_none()
            if not existing:
                existing = PostalCode(
                    city_id=city.id if city else None,
                    district_id=dist.id if dist else None,
                    mandal_id=mandal.id if mandal else None,
                    pin_code=p["pin_code"],
                    locality_name=p["locality_name"]
                )
                db.add(existing)

        await db.commit()
        print("\n[SUCCESS] Global Geographic Hierarchy successfully imported and indexed.")
        print("=" * 70)

def main():
    asyncio.run(import_geographic_data())

if __name__ == "__main__":
    main()
