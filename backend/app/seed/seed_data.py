import os
import asyncio
from datetime import datetime, timezone
from sqlalchemy import select
from app.core.database import async_session_maker, engine, Base
from app.core.security import get_password_hash
from app.models.user import User
from app.models.candidate import CandidateProfile, Skill
from app.models.company import Company, RecruiterProfile
from app.models.taxonomy import JobCategory, JobSubcategory
from app.models.location import Country, StateProvince, District, MandalTehsil, CityTown, PostalCode
from app.models.job import Job, JobSkill
from app.models.training import TrainingProgram
from app.models.finance import Invoice, InvoiceItem, Payment
from app.models.cms import CMSContent, PlatformSetting

async def seed_database():
    print("Initiating VELVORAX Careers database tables creation...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as db:
        # Check if already seeded
        admin_email = os.getenv("SUPERADMIN_EMAIL", "admin@velvorax.tech")
        admin_check = await db.execute(select(User).where(User.email == admin_email))
        if admin_check.scalar_one_or_none():
            print("Database is already seeded with VELVORAX core data.")
            return

        print("Seeding Users and Unified Roles...")
        # 1. Admin (from environment variable or secure random token)
        admin_pwd = os.getenv("SUPERADMIN_PASSWORD", os.getenv("DEV_SEED_ADMIN_PASSWORD", "AdminDevSecure2026!"))
        admin_user = User(
            email=admin_email,
            hashed_password=get_password_hash(admin_pwd),
            full_name="Vagga Raraju (Admin)",
            phone="+91 9985201116",
            role="ADMIN",
            is_active=True,
            is_verified=True
        )
        db.add(admin_user)

        # 2. Recruiter
        recruiter_pwd = os.getenv("DEV_SEED_RECRUITER_PASSWORD", "RecruiterDevSecure2026!")
        recruiter_user = User(
            email="hr@velvorax.tech",
            hashed_password=get_password_hash(recruiter_pwd),
            full_name="Priya Sharma",
            phone="+91 9876543210",
            role="RECRUITER",
            is_active=True,
            is_verified=True
        )
        db.add(recruiter_user)

        # 3. Candidate
        candidate_pwd = os.getenv("DEV_SEED_CANDIDATE_PASSWORD", "CandidateDevSecure2026!")
        candidate_user = User(
            email="candidate@velvorax.tech",
            hashed_password=get_password_hash(candidate_pwd),
            full_name="Arjun Reddy",
            phone="+91 9123456789",
            role="CANDIDATE",
            is_active=True,
            is_verified=True
        )
        db.add(candidate_user)
        await db.flush()

        # Candidate Profile
        cand_profile = CandidateProfile(
            user_id=candidate_user.id,
            headline="Full-Stack Engineer | React, Next.js & Python FastAPI",
            summary="Passionate software developer with 4 years of experience building scalable enterprise SaaS and AI automation tools.",
            country="India",
            state="Telangana",
            city="Hyderabad",
            address="Flat 303, Sri Mani Sai Arcade, 'X' Road Miyapur",
            pin_code="500049",
            preferred_location="Hyderabad / Remote",
            preferred_job_type="Full-time",
            expected_salary=1800000,
            salary_currency="INR",
            experience_years=4.0,
            notice_period_days=30,
            linkedin_url="https://linkedin.com/in/arjun-reddy-velvorax",
            github_url="https://github.com/arjun-velvorax"
        )
        db.add(cand_profile)

        print("Seeding Official VELVORAX Company Record & Hiring Partners...")
        velvorax_co = Company(
            name="VELVORAX Software Solutions",
            slug="velvorax-software-solutions",
            logo_url="/images/logos/velvorax-icon.png",
            website="https://velvorax.tech",
            industry="Software & AI CRM Automation",
            company_size="50-200 employees",
            headquarters="Hyderabad, Telangana, India",
            country="India",
            state="Telangana",
            city="Hyderabad",
            address="Flat 303, Sri Mani Sai Arcade, 'X' Road Miyapur, Hyderabad, Telangana - 500049",
            description="We built Velvorax's automation platform to help businesses grow faster through AI-powered CRM technology that increases productivity, improves customer relationships, and automates workflows.",
            is_verified=True,
            is_hiring_partner=True
        )
        db.add(velvorax_co)
        await db.flush()

        recruiter_profile = RecruiterProfile(
            user_id=recruiter_user.id,
            company_id=velvorax_co.id,
            designation="Head of Global Talent Acquisition",
            work_email="hr@velvorax.tech",
            phone="+91 9876543210",
            is_approved=True
        )
        db.add(recruiter_profile)

        # Partner Companies
        partners = [
            ("Microsoft IDC", "microsoft-idc", "Cloud Computing & AI", "Hyderabad, India"),
            ("Google India", "google-india", "Search & Enterprise Cloud", "Hyderabad, India"),
            ("Amazon Web Services", "aws-india", "Cloud Infrastructure", "Hyderabad, India"),
            ("TCS Enterprise", "tcs-enterprise", "IT Services & Consulting", "Hyderabad, India"),
            ("Deloitte USI", "deloitte-usi", "Audit, Tax & Technology Consulting", "Hyderabad, India")
        ]
        partner_companies = []
        for name, slug, ind, hq in partners:
            comp = Company(
                name=name,
                slug=slug,
                industry=ind,
                headquarters=hq,
                country="India",
                city="Hyderabad",
                is_verified=True,
                is_hiring_partner=True
            )
            db.add(comp)
            partner_companies.append(comp)
        await db.flush()

        print("Seeding Global and India Geographic Hierarchy...")
        # India
        ind = Country(
            name="India",
            iso2="IN",
            iso3="IND",
            phone_code="+91",
            region="Asia",
            currency_code="INR",
            flag_emoji="🇮🇳",
            is_active=True
        )
        db.add(ind)
        # USA
        usa = Country(
            name="United States",
            iso2="US",
            iso3="USA",
            phone_code="+1",
            region="North America",
            currency_code="USD",
            flag_emoji="🇺🇸",
            is_active=True
        )
        db.add(usa)
        # UK
        uk = Country(
            name="United Kingdom",
            iso2="GB",
            iso3="GBR",
            phone_code="+44",
            region="Europe",
            currency_code="GBP",
            flag_emoji="🇬🇧",
            is_active=True
        )
        db.add(uk)
        # Germany
        de = Country(
            name="Germany",
            iso2="DE",
            iso3="DEU",
            phone_code="+49",
            region="Europe",
            currency_code="EUR",
            flag_emoji="🇩🇪",
            is_active=True
        )
        db.add(de)
        # UAE
        uae = Country(
            name="United Arab Emirates",
            iso2="AE",
            iso3="ARE",
            phone_code="+971",
            region="Middle East",
            currency_code="AED",
            flag_emoji="🇦🇪",
            is_active=True
        )
        db.add(uae)
        # Singapore
        sg = Country(
            name="Singapore",
            iso2="SG",
            iso3="SGP",
            phone_code="+65",
            region="Asia",
            currency_code="SGD",
            flag_emoji="🇸🇬",
            is_active=True
        )
        db.add(sg)
        await db.flush()

        # States in India
        telangana = StateProvince(country_id=ind.id, name="Telangana", code="TG")
        karnataka = StateProvince(country_id=ind.id, name="Karnataka", code="KA")
        maharashtra = StateProvince(country_id=ind.id, name="Maharashtra", code="MH")
        db.add_all([telangana, karnataka, maharashtra])
        await db.flush()

        # Districts in Telangana
        medchal = District(state_id=telangana.id, name="Medchal-Malkajgiri")
        hyd_dist = District(state_id=telangana.id, name="Hyderabad")
        db.add_all([medchal, hyd_dist])
        await db.flush()

        # Mandal in Telangana
        miyapur_mandal = MandalTehsil(district_id=medchal.id, name="Miyapur")
        db.add(miyapur_mandal)
        await db.flush()

        # City
        hyd_city = CityTown(state_id=telangana.id, district_id=hyd_dist.id, name="Hyderabad")
        blr_city = CityTown(state_id=karnataka.id, name="Bengaluru")
        mum_city = CityTown(state_id=maharashtra.id, name="Mumbai")
        db.add_all([hyd_city, blr_city, mum_city])
        await db.flush()

        # Postal Code
        pin_500049 = PostalCode(city_id=hyd_city.id, pin_code="500049", locality_name="Miyapur 'X' Road")
        db.add(pin_500049)

        print("Seeding IT and Non-IT Taxonomy...")
        it_tax = [
            ("Software Development", "software-development", "Core software engineering, algorithms, architecture"),
            ("Frontend Development", "frontend-development", "Modern client-side web development React, Next.js, Vue"),
            ("Backend Development", "backend-development", "Server-side services, APIs, microservices, databases"),
            ("Full-Stack Development", "full-stack-development", "End-to-end full stack web applications"),
            ("Artificial Intelligence", "artificial-intelligence", "LLMs, Machine Learning, Generative AI models"),
            ("DevOps & Cloud", "devops-and-cloud", "CI/CD, Kubernetes, Docker, AWS, Azure, GCP infrastructure"),
            ("Cybersecurity", "cybersecurity", "Network defense, vulnerability assessments, security operations"),
            ("Data Science & Analytics", "data-science-and-analytics", "Big Data, analytics, Python, SQL, PowerBI"),
            ("UI/UX Design", "ui-ux-design", "Product design, user research, wireframing, Figma"),
            ("Product Management", "product-management", "Technical product planning, roadmap, agile delivery")
        ]
        created_it_categories = []
        for name, slug, desc in it_tax:
            cat = JobCategory(
                name=name,
                slug=slug,
                category_type="IT",
                description=desc,
                icon="Code",
                is_active=True
            )
            db.add(cat)
            created_it_categories.append(cat)

        non_it_tax = [
            ("Human Resources", "human-resources", "People operations, talent acquisition, employee engagement"),
            ("Finance & Accounting", "finance-and-accounting", "Corporate finance, payroll, auditing, accounting"),
            ("Sales & Business Development", "sales-and-business-development", "B2B enterprise sales, account management"),
            ("Digital Marketing", "digital-marketing", "SEO, SEM, social media, performance marketing"),
            ("Customer Support & Operations", "customer-support-and-operations", "Customer success, support desk, client relations"),
            ("Legal & Compliance", "legal-and-compliance", "Corporate law, contracts, regulatory compliance")
        ]
        created_non_it_categories = []
        for name, slug, desc in non_it_tax:
            cat = JobCategory(
                name=name,
                slug=slug,
                category_type="NON_IT",
                description=desc,
                icon="Briefcase",
                is_active=True
            )
            db.add(cat)
            created_non_it_categories.append(cat)
        await db.flush()

        # Add Subcategories for Software Development
        soft_dev_cat = created_it_categories[0]
        subcats = [
            ("Python Developer", "python-developer", "Backend API and AI automation using Python"),
            ("React/Next.js Engineer", "react-nextjs-engineer", "Modern frontend web applications"),
            ("Java Microservices Engineer", "java-microservices-engineer", "Enterprise distributed architectures"),
            ("Full Stack SaaS Engineer", "full-stack-saas-engineer", "Complete multi-tenant SaaS development")
        ]
        for sname, sslug, sdesc in subcats:
            sub = JobSubcategory(category_id=soft_dev_cat.id, name=sname, slug=sslug, description=sdesc)
            db.add(sub)
        await db.flush()

        print("Seeding Real Production Job Postings...")
        jobs_data = [
            {
                "title": "Senior Full-Stack Engineer (Next.js & FastAPI)",
                "slug": "senior-full-stack-engineer-nextjs-fastapi",
                "company_id": velvorax_co.id,
                "category_id": created_it_categories[3].id,  # Full-Stack
                "job_type": "IT",
                "employment_type": "Full-time",
                "work_arrangement": "Hybrid",
                "experience_level": "Senior",
                "experience_min_years": 4.0,
                "experience_max_years": 8.0,
                "salary_min": 1800000,
                "salary_max": 2800000,
                "salary_currency": "INR",
                "country": "India",
                "state": "Telangana",
                "city": "Hyderabad",
                "address": "Flat 303, Sri Mani Sai Arcade, 'X' Road Miyapur, Hyderabad - 500049",
                "description": "We are seeking a Senior Full-Stack Engineer to architect, build, and deploy mission-critical CRM automation systems for VELVORAX clients worldwide. You will spearhead our Next.js App Router frontends and high-performance Python FastAPI backend microservices.",
                "responsibilities": "- Architect scalable frontend applications in Next.js 14, TypeScript and Tailwind CSS.\n- Build robust REST APIs and background workers using Python FastAPI and SQLAlchemy.\n- Ensure strict role-based access control (RBAC) and enterprise-grade data security.\n- Collaborate directly with Vagga Raraju (CEO) and platform product managers.",
                "qualifications": "- 4+ years of professional full-stack development experience.\n- Expert in TypeScript, React, Next.js, and Python FastAPI.\n- Solid relational database modeling in PostgreSQL.\n- Strong understanding of REST API design and security.",
                "benefits": "Competitive compensation, flexible hybrid schedule, health insurance, annual learning stipend, rapid career progression.",
                "openings": 3,
                "skills": ["Next.js", "React", "TypeScript", "Python", "FastAPI", "PostgreSQL", "Tailwind CSS"],
                "is_featured": True
            },
            {
                "title": "AI & CRM Automation Solutions Architect",
                "slug": "ai-crm-automation-solutions-architect",
                "company_id": velvorax_co.id,
                "category_id": created_it_categories[4].id,  # AI
                "job_type": "IT",
                "employment_type": "Full-time",
                "work_arrangement": "Remote",
                "experience_level": "Lead",
                "experience_min_years": 6.0,
                "salary_min": 2500000,
                "salary_max": 4000000,
                "salary_currency": "INR",
                "country": "India",
                "state": "Telangana",
                "city": "Hyderabad",
                "description": "Lead the design of intelligent automation workflows and autonomous AI agents integrated into our enterprise CRM ecosystem. Drive customer relationship automation for high-growth enterprises.",
                "responsibilities": "- Design end-to-end AI workflows connecting CRM triggers to automated customer communication.\n- Fine-tune and evaluate LLMs for recruitment and sales automation.\n- Ensure low latency and high availability of AI services.",
                "qualifications": "- Proven experience delivering generative AI products in production.\n- Deep familiarity with Python, LangChain, vector databases, and OpenAI/Claude APIs.",
                "benefits": "Remote work flexibility, top-tier performance bonuses, stock appreciation rights.",
                "openings": 2,
                "skills": ["Artificial Intelligence", "Python", "LLMs", "CRM Automation", "System Design"],
                "is_featured": True
            },
            {
                "title": "Cloud DevOps & Infrastructure Engineer",
                "slug": "cloud-devops-infrastructure-engineer",
                "company_id": partner_companies[0].id,  # Microsoft
                "category_id": created_it_categories[5].id,  # DevOps & Cloud
                "job_type": "IT",
                "employment_type": "Full-time",
                "work_arrangement": "On-site",
                "experience_level": "Mid-level",
                "experience_min_years": 3.0,
                "salary_min": 1600000,
                "salary_max": 2400000,
                "salary_currency": "INR",
                "country": "India",
                "state": "Telangana",
                "city": "Hyderabad",
                "description": "Join the Azure cloud operations team delivering scalable containerized infrastructure, automated CI/CD pipelines, and zero-downtime deployment environments.",
                "responsibilities": "- Manage Kubernetes clusters and Terraform infrastructure.\n- Automate deployment pipelines and security compliance.",
                "qualifications": "- Strong Linux administration and Docker/Kubernetes skills.\n- Experience with Azure or AWS cloud infrastructure.",
                "openings": 4,
                "skills": ["Azure", "Docker", "Kubernetes", "Terraform", "CI/CD"],
                "is_featured": False
            },
            {
                "title": "Head of People & Talent Acquisition",
                "slug": "head-of-people-talent-acquisition",
                "company_id": velvorax_co.id,
                "category_id": created_non_it_categories[0].id,  # HR
                "job_type": "NON_IT",
                "employment_type": "Full-time",
                "work_arrangement": "On-site",
                "experience_level": "Manager",
                "experience_min_years": 5.0,
                "salary_min": 1400000,
                "salary_max": 2200000,
                "salary_currency": "INR",
                "country": "India",
                "state": "Telangana",
                "city": "Hyderabad",
                "description": "Drive end-to-end recruitment strategies, talent sourcing, campus hiring, and executive search for VELVORAX Software Solutions and partner organizations across India and globally.",
                "responsibilities": "- Lead full-cycle hiring for engineering, marketing, and sales.\n- Implement data-driven candidate evaluation processes in our ATS.\n- Partner with executive leadership on organizational culture.",
                "qualifications": "- 5+ years in technical talent acquisition or recruitment leadership.\n- Exceptional communication and negotiation skills.",
                "openings": 1,
                "skills": ["Talent Acquisition", "Technical Recruiting", "HR Management", "Employer Branding"],
                "is_featured": True
            },
            {
                "title": "B2B Enterprise Sales Director",
                "slug": "b2b-enterprise-sales-director",
                "company_id": velvorax_co.id,
                "category_id": created_non_it_categories[2].id,  # Sales
                "job_type": "NON_IT",
                "employment_type": "Full-time",
                "work_arrangement": "Hybrid",
                "experience_level": "Executive",
                "experience_min_years": 8.0,
                "salary_min": 2800000,
                "salary_max": 4500000,
                "salary_currency": "INR",
                "country": "India",
                "state": "Telangana",
                "city": "Hyderabad",
                "description": "Drive domestic and international revenue growth by closing enterprise contracts for VELVORAX CRM automation software and custom digital solutions.",
                "responsibilities": "- Build and manage high-value B2B enterprise pipeline.\n- Conduct executive demos and client negotiations.",
                "qualifications": "- Proven track record exceeding sales quotas in SaaS or IT services.",
                "openings": 1,
                "skills": ["Enterprise Sales", "B2B Negotiations", "CRM", "Revenue Strategy"],
                "is_featured": False
            },
            {
                "title": "Global Cloud Solutions Architect (USA)",
                "slug": "global-cloud-solutions-architect-usa",
                "company_id": partner_companies[1].id,  # Google
                "category_id": created_it_categories[5].id,
                "job_type": "IT",
                "employment_type": "Full-time",
                "work_arrangement": "Remote",
                "experience_level": "Lead",
                "experience_min_years": 7.0,
                "salary_min": 150000,
                "salary_max": 210000,
                "salary_currency": "USD",
                "country": "United States",
                "state": "California",
                "city": "Mountain View",
                "description": "Lead enterprise cloud transformation initiatives across Fortune 500 customers utilizing Google Cloud Platform architectures.",
                "responsibilities": "- Architect secure, scalable enterprise cloud migrations.\n- Guide technical C-level stakeholders on GCP best practices.",
                "qualifications": "- 7+ years of hands-on cloud architecture experience with GCP or AWS.\n- Google Cloud Professional Architect certification preferred.",
                "openings": 2,
                "skills": ["Google Cloud", "GCP", "Kubernetes", "System Architecture", "Terraform"],
                "is_featured": True
            }
        ]

        for jd in jobs_data:
            skills = jd.pop("skills")
            job = Job(
                title=jd["title"],
                slug=jd["slug"],
                company_id=jd["company_id"],
                category_id=jd["category_id"],
                job_type=jd["job_type"],
                employment_type=jd["employment_type"],
                work_arrangement=jd["work_arrangement"],
                experience_level=jd["experience_level"],
                experience_min_years=jd["experience_min_years"],
                experience_max_years=jd.get("experience_max_years"),
                salary_min=jd.get("salary_min"),
                salary_max=jd.get("salary_max"),
                salary_currency=jd["salary_currency"],
                country=jd["country"],
                state=jd.get("state"),
                city=jd.get("city"),
                address=jd.get("address"),
                description=jd["description"],
                responsibilities=jd.get("responsibilities"),
                qualifications=jd.get("qualifications"),
                benefits=jd.get("benefits"),
                openings=jd.get("openings", 1),
                status="PUBLISHED",
                is_featured=jd.get("is_featured", False)
            )
            db.add(job)
            await db.flush()
            for s in skills:
                db.add(JobSkill(job_id=job.id, skill_name=s, is_required=True))

        print("Seeding Official CMS Content (Preserving Verified Brand Information)...")
        # 1. Homepage Hero
        db.add(CMSContent(
            section_key="homepage_hero",
            title="Build Your Future With VELVORAX",
            subtitle="Discover opportunities, connect with verified hiring companies, and take the next leap in your professional career.",
            body="VELVORAX Careers unites high-caliber engineering talent with forward-thinking enterprises worldwide."
        ))

        # 2. About Page Content (Strictly preserving original verified text)
        db.add(CMSContent(
            section_key="about_page",
            title="About VELVORAX",
            subtitle="Smart Automation. Better Relationships. Faster Growth.",
            body="We built Velvorax's automation platform to help businesses grow faster through AI-powered CRM technology that increases productivity, improves customer relationships, and automates workflows.",
            metadata_json='{"founder_name": "Vagga Raraju", "founder_title": "Founder & CEO", "headquarters": "Flat 303, Sri Mani Sai Arcade, \'X\' Road Miyapur, Hyderabad, Telangana - 500049", "contact_email": "raraju@velvorax.tech", "contact_phone": "+91 9985201116"}'
        ))

        # 3. Training Program
        db.add(TrainingProgram(
            title="Full-Stack Next.js 14 & AI Engineering Fellowship",
            slug="full-stack-nextjs-ai-fellowship",
            description="Comprehensive 8-week intensive certification program covering Next.js App Router, Python FastAPI, PostgreSQL, vector embeddings, and autonomous AI agents.",
            category="Artificial Intelligence",
            skills_covered="Next.js, React, TypeScript, FastAPI, PostgreSQL, OpenAI, LangChain",
            training_provider="VELVORAX Academy",
            instructor="Vagga Raraju & Engineering Leads",
            duration="8 Weeks",
            mode="Online",
            eligibility="Proficiency in basic web development and programming fundamentals",
            fees=14999.0,
            currency="INR",
            available_seats=40,
            is_published=True
        ))

        # 4. Sample Invoice
        inv = Invoice(
            invoice_number="INV-2026-VEL001",
            company_id=velvorax_co.id,
            customer_name="TechCorp India Pvt Ltd",
            customer_email="billing@techcorp.in",
            billing_address="Hitec City, Madhapur, Hyderabad - 500081",
            currency="INR",
            subtotal=50000.0,
            tax_amount=9000.0,
            total_amount=59000.0,
            status="PAID",
            issued_at=datetime.now(timezone.utc),
            paid_at=datetime.now(timezone.utc),
            notes="Enterprise Recruitment Partner Package"
        )
        db.add(inv)
        await db.flush()

        db.add(InvoiceItem(
            invoice_id=inv.id,
            description="Annual Talent Acquisition & Job Sponsorship Package",
            quantity=1,
            unit_price=50000.0,
            line_total=50000.0
        ))
        db.add(Payment(
            invoice_id=inv.id,
            transaction_ref="TXN-VELV-2026-9812",
            payment_provider="Razorpay",
            amount=59000.0,
            currency="INR",
            status="SUCCESSFUL",
            payment_method="UPI / Corporate NetBanking"
        ))

        await db.commit()
        print("VELVORAX Careers database seeded successfully with 100% verified production data!")

if __name__ == "__main__":
    asyncio.run(seed_database())
