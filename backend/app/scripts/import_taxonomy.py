import os
import sys
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.database import async_session_maker, engine, Base
from app.models.taxonomy import JobCategory, JobSubcategory

IT_CATEGORIES = [
    {
        "name": "Software Development & Engineering",
        "slug": "software-development",
        "description": "Core software engineering, algorithms, scalable architectures, and distributed systems",
        "icon": "Code",
        "subcategories": [
            ("Python Backend Engineer", "python-backend-engineer"),
            ("Java Microservices Developer", "java-microservices-developer"),
            ("Golang Systems Engineer", "golang-systems-engineer"),
            ("C# / .NET Core Engineer", "dotnet-core-engineer"),
            ("C++ High Performance Systems", "cpp-systems-engineer")
        ]
    },
    {
        "name": "Frontend Web Development",
        "slug": "frontend-development",
        "description": "Modern client-side web development React, Next.js, Vue, Angular, and web performance",
        "icon": "Layout",
        "subcategories": [
            ("React / Next.js Developer", "react-nextjs-developer"),
            ("Vue.js / Nuxt Engineer", "vue-nuxt-engineer"),
            ("Angular Frontend Architect", "angular-frontend-architect"),
            ("TypeScript Web Specialist", "typescript-web-specialist")
        ]
    },
    {
        "name": "Backend Systems & API Engineering",
        "slug": "backend-development",
        "description": "Server-side services, REST/gRPC/GraphQL APIs, microservices, and database query optimization",
        "icon": "Server",
        "subcategories": [
            ("FastAPI / Python Engineer", "fastapi-python-engineer"),
            ("Node.js / Express Developer", "nodejs-developer"),
            ("Spring Boot Architect", "spring-boot-architect"),
            ("Distributed Systems Specialist", "distributed-systems-specialist")
        ]
    },
    {
        "name": "Full-Stack Development",
        "slug": "full-stack-development",
        "description": "End-to-end full stack web applications, SaaS platform development, and integration",
        "icon": "Layers",
        "subcategories": [
            ("Next.js & Python Full-Stack Engineer", "nextjs-python-fullstack"),
            ("MERN Stack Developer", "mern-stack-developer"),
            ("Django & React Engineer", "django-react-engineer"),
            ("SaaS Product Engineer", "saas-product-engineer")
        ]
    },
    {
        "name": "Artificial Intelligence & Machine Learning",
        "slug": "artificial-intelligence-machine-learning",
        "description": "Predictive models, neural networks, PyTorch, TensorFlow, NLP, and Deep Learning",
        "icon": "Brain",
        "subcategories": [
            ("Machine Learning Engineer", "machine-learning-engineer"),
            ("Deep Learning Researcher", "deep-learning-researcher"),
            ("Computer Vision Engineer", "computer-vision-engineer"),
            ("Natural Language Processing (NLP)", "nlp-specialist")
        ]
    },
    {
        "name": "Generative AI & LLM Engineering",
        "slug": "generative-ai-llm-engineering",
        "description": "Large Language Models, RAG architectures, prompt engineering, LangChain, and Agentic AI",
        "icon": "Sparkles",
        "subcategories": [
            ("RAG & Vector DB Engineer", "rag-vector-db-engineer"),
            ("LLM Fine-Tuning Specialist", "llm-fine-tuning-specialist"),
            ("AI Agent Systems Architect", "ai-agent-systems-architect"),
            ("Prompt & Evaluation Engineer", "prompt-evaluation-engineer")
        ]
    },
    {
        "name": "DevOps & Site Reliability Engineering (SRE)",
        "slug": "devops-and-sre",
        "description": "CI/CD pipelines, Kubernetes, Docker, container orchestration, monitoring, and zero-downtime releases",
        "icon": "Cpu",
        "subcategories": [
            ("Kubernetes Administrator", "kubernetes-administrator"),
            ("CI/CD Pipeline Specialist", "cicd-pipeline-specialist"),
            ("Site Reliability Engineer", "site-reliability-engineer"),
            ("Terraform Infrastructure as Code", "terraform-iac-engineer")
        ]
    },
    {
        "name": "Cloud Architecture & Infrastructure",
        "slug": "cloud-architecture-infrastructure",
        "description": "Multi-cloud architecture across AWS, Microsoft Azure, and Google Cloud Platform (GCP)",
        "icon": "Cloud",
        "subcategories": [
            ("AWS Cloud Architect", "aws-cloud-architect"),
            ("Azure Enterprise Specialist", "azure-enterprise-specialist"),
            ("GCP Cloud Engineer", "gcp-cloud-engineer"),
            ("Hybrid Cloud Consultant", "hybrid-cloud-consultant")
        ]
    },
    {
        "name": "Cybersecurity & Information Defense",
        "slug": "cybersecurity-information-defense",
        "description": "SOC operations, penetration testing, threat modeling, vulnerability assessments, and cryptography",
        "icon": "Shield",
        "subcategories": [
            ("Penetration Tester / Ethical Hacker", "penetration-tester"),
            ("SOC Security Analyst", "soc-security-analyst"),
            ("Application Security Engineer (AppSec)", "appsec-engineer"),
            ("Identity & Access Management (IAM)", "iam-engineer")
        ]
    },
    {
        "name": "Data Science & Advanced Analytics",
        "slug": "data-science-analytics",
        "description": "Statistical modeling, business intelligence, Python, SQL, Tableau, PowerBI, and data mining",
        "icon": "BarChart3",
        "subcategories": [
            ("Senior Data Scientist", "senior-data-scientist"),
            ("BI & Reporting Analyst", "bi-reporting-analyst"),
            ("Statistical Modeler", "statistical-modeler"),
            ("Quantitative Analyst", "quantitative-analyst")
        ]
    },
    {
        "name": "Big Data & Data Engineering",
        "slug": "big-data-engineering",
        "description": "Data pipelines, Apache Spark, Kafka, Snowflake, Databricks, ETL/ELT pipelines, and data lakes",
        "icon": "Database",
        "subcategories": [
            ("Apache Spark / Kafka Engineer", "spark-kafka-engineer"),
            ("Snowflake / Databricks Specialist", "snowflake-databricks-specialist"),
            ("ETL Data Pipeline Developer", "etl-data-pipeline-developer"),
            ("Data Lakehouse Architect", "lakehouse-architect")
        ]
    },
    {
        "name": "Database Administration & Engineering",
        "slug": "database-administration-engineering",
        "description": "PostgreSQL, MySQL, Oracle, MongoDB, Redis, clustering, replication, and performance tuning",
        "icon": "HardDrive",
        "subcategories": [
            ("PostgreSQL Database Administrator", "postgresql-dba"),
            ("NoSQL & Document DB Specialist", "nosql-specialist"),
            ("Database Performance Tuner", "database-performance-tuner")
        ]
    },
    {
        "name": "Mobile Application Development",
        "slug": "mobile-app-development",
        "description": "Native iOS (Swift), Android (Kotlin), and cross-platform Flutter/React Native application engineering",
        "icon": "Smartphone",
        "subcategories": [
            ("iOS Swift Engineer", "ios-swift-engineer"),
            ("Android Kotlin Developer", "android-kotlin-developer"),
            ("Flutter Cross-Platform Developer", "flutter-developer"),
            ("React Native Specialist", "react-native-specialist")
        ]
    },
    {
        "name": "QA Engineering & Automated Testing",
        "slug": "qa-automation-testing",
        "description": "Test automation, Playwright, Cypress, Selenium, performance testing, and quality governance",
        "icon": "CheckCircle2",
        "subcategories": [
            ("Playwright / Cypress Automation Engineer", "playwright-cypress-engineer"),
            ("Selenium Framework Engineer", "selenium-framework-engineer"),
            ("API Performance & Load Tester", "api-performance-tester"),
            ("SDET (Software Development Engineer in Test)", "sdet-engineer")
        ]
    },
    {
        "name": "UI/UX & Digital Product Design",
        "slug": "ui-ux-product-design",
        "description": "User research, wireframing, interactive prototyping, design systems, Figma, and usability audits",
        "icon": "Palette",
        "subcategories": [
            ("Figma Design System Architect", "figma-design-system-architect"),
            ("User Experience (UX) Researcher", "ux-researcher"),
            ("UI / Visual Interaction Designer", "ui-visual-designer"),
            ("Product Designer", "product-designer")
        ]
    },
    {
        "name": "Technical Product Management",
        "slug": "technical-product-management",
        "description": "Product vision, roadmaps, agile development, feature prioritization, and stakeholder alignment",
        "icon": "Target",
        "subcategories": [
            ("Technical Product Manager", "technical-product-manager"),
            ("SaaS Product Owner", "saas-product-owner"),
            ("Scrum Master & Agile Coach", "scrum-master-agile-coach")
        ]
    },
    {
        "name": "Embedded Systems & IoT Engineering",
        "slug": "embedded-systems-iot",
        "description": "Firmware, microcontrollers, ARM, RTOS, sensors, Bluetooth LE, and industrial IoT devices",
        "icon": "Cpu",
        "subcategories": [
            ("Embedded C/C++ Firmware Engineer", "firmware-engineer"),
            ("IoT Device Architect", "iot-device-architect"),
            ("RTOS Systems Developer", "rtos-systems-developer")
        ]
    },
    {
        "name": "Blockchain & Web3 Technologies",
        "slug": "blockchain-web3",
        "description": "Smart contracts, Solidity, Ethereum, Rust, Solana, decentralized protocols, and digital assets",
        "icon": "Coins",
        "subcategories": [
            ("Solidity Smart Contract Engineer", "solidity-engineer"),
            ("Rust / Solana Protocol Developer", "rust-solana-developer"),
            ("Web3 Full-Stack Developer", "web3-fullstack-developer")
        ]
    },
    {
        "name": "Enterprise Resource Planning (ERP)",
        "slug": "enterprise-erp-solutions",
        "description": "SAP S/4HANA, Oracle ERP Cloud, Microsoft Dynamics, ABAP, integration, and enterprise processes",
        "icon": "Briefcase",
        "subcategories": [
            ("SAP S/4HANA Consultant", "sap-s4hana-consultant"),
            ("Oracle ERP Functional Consultant", "oracle-erp-consultant"),
            ("Microsoft Dynamics 365 Architect", "dynamics-365-architect")
        ]
    },
    {
        "name": "CRM & Business Automation",
        "slug": "crm-business-automation",
        "description": "Salesforce development, HubSpot, CRM workflows, Zapier, Make, and enterprise AI automation",
        "icon": "GitPullRequest",
        "subcategories": [
            ("Salesforce Apex / LWC Developer", "salesforce-developer"),
            ("HubSpot Solutions Consultant", "hubspot-consultant"),
            ("VELVORAX CRM Automation Specialist", "velvorax-crm-automation-specialist")
        ]
    },
    {
        "name": "Network Engineering & Telecommunications",
        "slug": "network-engineering-telecom",
        "description": "Cisco, routing & switching, SD-WAN, 5G, firewall administration, and enterprise telecommunications",
        "icon": "Radio",
        "subcategories": [
            ("Network Infrastructure Engineer", "network-infrastructure-engineer"),
            ("SD-WAN & Firewalls Specialist", "sdwan-firewall-specialist"),
            ("Telecom Systems Engineer", "telecom-systems-engineer")
        ]
    },
    {
        "name": "Game Development & Interactive Graphics",
        "slug": "game-development-graphics",
        "description": "Unity 3D, Unreal Engine, C++, shaders, DirectX, WebGL, and real-time graphics rendering",
        "icon": "Gamepad2",
        "subcategories": [
            ("Unity 3D Game Developer", "unity-developer"),
            ("Unreal Engine C++ Specialist", "unreal-engine-specialist"),
            ("3D Graphics & Shader Programmer", "graphics-shader-programmer")
        ]
    },
    {
        "name": "AR/VR & Spatial Computing",
        "slug": "ar-vr-spatial-computing",
        "description": "Augmented reality, virtual reality, Apple Vision Pro, Meta Quest, and spatial user interaction",
        "icon": "Glasses",
        "subcategories": [
            ("AR / VR Interaction Developer", "ar-vr-developer"),
            ("Spatial Computing Engineer", "spatial-computing-engineer")
        ]
    },
    {
        "name": "IT Support, Helpdesk & Systems Admin",
        "slug": "it-support-sysadmin",
        "description": "Desktop support, Windows/Linux server administration, Active Directory, and hardware maintenance",
        "icon": "HelpCircle",
        "subcategories": [
            ("L2 / L3 Technical Support Engineer", "tech-support-engineer"),
            ("Windows & Linux SysAdmin", "systems-administrator"),
            ("Enterprise IT Helpdesk Specialist", "it-helpdesk-specialist")
        ]
    },
    {
        "name": "Robotics, Computer Vision & Automation",
        "slug": "robotics-computer-vision",
        "description": "ROS (Robot Operating System), industrial robotics, SLAM, motion planning, and hardware automation",
        "icon": "Bot",
        "subcategories": [
            ("ROS Robotics Software Engineer", "ros-robotics-engineer"),
            ("Industrial Automation Specialist", "industrial-automation-specialist")
        ]
    }
]

NON_IT_CATEGORIES = [
    {
        "name": "Human Resources & Talent Acquisition",
        "slug": "human-resources-recruitment",
        "description": "Global recruitment, executive search, candidate pipelining, and interview coordination",
        "icon": "Users",
        "subcategories": [
            ("Technical Recruiter (IT / Non-IT)", "technical-recruiter"),
            ("Talent Acquisition Lead", "talent-acquisition-lead"),
            ("Executive Search Consultant", "executive-search-consultant")
        ]
    },
    {
        "name": "Talent Sourcing & HR Operations",
        "slug": "talent-sourcing-operations",
        "description": "Onboarding, payroll compliance, HR policies, employee engagement, and performance appraisals",
        "icon": "UserCheck",
        "subcategories": [
            ("HR Operations Specialist", "hr-operations-specialist"),
            ("Employee Relations Manager", "employee-relations-manager"),
            ("Compensation & Benefits Analyst", "compensation-benefits-analyst")
        ]
    },
    {
        "name": "Corporate Finance & Financial Planning",
        "slug": "corporate-finance-planning",
        "description": "FP&A, financial modeling, budgeting, treasury, capital allocation, and valuation",
        "icon": "TrendingUp",
        "subcategories": [
            ("Financial Planning & Analysis (FP&A) Manager", "fpa-manager"),
            ("Corporate Financial Analyst", "corporate-financial-analyst"),
            ("Treasury & Cash Management Specialist", "treasury-specialist")
        ]
    },
    {
        "name": "Accounting, Auditing & Taxation",
        "slug": "accounting-auditing-taxation",
        "description": "General ledger, statutory audit, GST/TDS tax filing, corporate accounts, and reconciliation",
        "icon": "Calculator",
        "subcategories": [
            ("Chartered Accountant (CA)", "chartered-accountant"),
            ("Statutory Auditor", "statutory-auditor"),
            ("GST & Direct Taxation Specialist", "gst-tax-specialist"),
            ("Senior Accountant", "senior-accountant")
        ]
    },
    {
        "name": "Investment Banking & Advisory",
        "slug": "investment-banking-advisory",
        "description": "Mergers & acquisitions, debt syndication, private equity advisory, and pitch deck preparation",
        "icon": "DollarSign",
        "subcategories": [
            ("M&A Investment Banking Analyst", "ma-analyst"),
            ("Private Equity Associate", "private-equity-associate"),
            ("Equity Research Specialist", "equity-research-specialist")
        ]
    },
    {
        "name": "B2B Enterprise Sales & Strategic Partnerships",
        "slug": "b2b-enterprise-sales",
        "description": "Large corporate contracts, enterprise SaaS sales, quota achievement, and client negotiations",
        "icon": "Briefcase",
        "subcategories": [
            ("Enterprise Account Executive", "enterprise-account-executive"),
            ("B2B Sales Director", "b2b-sales-director"),
            ("Strategic Alliance Manager", "strategic-alliance-manager")
        ]
    },
    {
        "name": "Retail & Direct Sales",
        "slug": "retail-direct-sales",
        "description": "Store operations, field sales, franchise management, and retail merchandising",
        "icon": "ShoppingBag",
        "subcategories": [
            ("Retail Store Manager", "retail-store-manager"),
            ("Field Sales Representative", "field-sales-representative"),
            ("Territory Sales Manager", "territory-sales-manager")
        ]
    },
    {
        "name": "Business Development & Growth",
        "slug": "business-development-growth",
        "description": "Lead generation, pipeline generation, market expansion, and strategic deal closure",
        "icon": "Maximize",
        "subcategories": [
            ("Business Development Executive (BDE)", "bde-specialist"),
            ("International Market Expansion Lead", "market-expansion-lead"),
            ("Key Account Manager (KAM)", "key-account-manager")
        ]
    },
    {
        "name": "Digital Marketing & Growth Hacking",
        "slug": "digital-marketing-growth",
        "description": "Omnichannel marketing, performance ads (Meta/Google), email campaigns, and growth strategies",
        "icon": "Megaphone",
        "subcategories": [
            ("Performance Marketing Specialist", "performance-marketing-specialist"),
            ("Growth Marketing Manager", "growth-marketing-manager"),
            ("Email & Lifecycle Marketer", "email-lifecycle-marketer")
        ]
    },
    {
        "name": "Content Strategy, Copywriting & Media",
        "slug": "content-strategy-copywriting",
        "description": "Brand storytelling, technical writing, video scripts, blog management, and creative copy",
        "icon": "FileText",
        "subcategories": [
            ("Senior Content Strategist", "senior-content-strategist"),
            ("Creative Copywriter", "creative-copywriter"),
            ("Technical Documentation Writer", "technical-documentation-writer")
        ]
    },
    {
        "name": "Search Engine Optimization & SEM",
        "slug": "seo-sem-search-marketing",
        "description": "On-page/off-page SEO, technical audits, Google Search Console, keyword analysis, and backlinks",
        "icon": "Search",
        "subcategories": [
            ("Technical SEO Specialist", "technical-seo-specialist"),
            ("Google Ads / SEM Manager", "google-ads-manager"),
            ("Organic Search Lead", "organic-search-lead")
        ]
    },
    {
        "name": "Public Relations & Corporate Communications",
        "slug": "pr-corporate-communications",
        "description": "Media relations, press releases, crisis management, internal communications, and branding",
        "icon": "Radio",
        "subcategories": [
            ("PR & Media Relations Specialist", "pr-media-relations"),
            ("Corporate Communications Manager", "corporate-communications-manager")
        ]
    },
    {
        "name": "Customer Success Management",
        "slug": "customer-success-management",
        "description": "Retention, churn mitigation, customer onboarding, quarterly business reviews (QBR), and upsells",
        "icon": "HeartHandshake",
        "subcategories": [
            ("Customer Success Manager (CSM)", "customer-success-manager"),
            ("Enterprise Client Onboarding Lead", "client-onboarding-lead")
        ]
    },
    {
        "name": "Customer Support & Technical Helpdesk",
        "slug": "customer-support-helpdesk",
        "description": "Inbound voice support, ticketing (Zendesk/Freshdesk), live chat, and troubleshooting resolution",
        "icon": "Headphones",
        "subcategories": [
            ("International Voice Support Executive", "voice-support-executive"),
            ("Customer Service Team Lead", "customer-service-team-lead"),
            ("Technical Support Helpdesk Agent", "technical-helpdesk-agent")
        ]
    },
    {
        "name": "Business Process Operations (BPO/KPO)",
        "slug": "bpo-kpo-operations",
        "description": "Back-office processing, data validation, underwriting, transaction processing, and SLA compliance",
        "icon": "Repeat",
        "subcategories": [
            ("BPO Operations Team Leader", "bpo-team-leader"),
            ("KPO Research Associate", "kpo-research-associate"),
            ("Quality Assurance Analyst (BPO)", "bpo-qa-analyst")
        ]
    },
    {
        "name": "Supply Chain Management & Logistics",
        "slug": "supply-chain-logistics",
        "description": "Freight forwarding, route planning, fleet management, international customs, and shipping",
        "icon": "Truck",
        "subcategories": [
            ("Supply Chain Planner", "supply-chain-planner"),
            ("Logistics & Freight Coordinator", "logistics-coordinator"),
            ("Fleet & Route Operations Lead", "fleet-operations-lead")
        ]
    },
    {
        "name": "Procurement, Vendor & Sourcing Management",
        "slug": "procurement-vendor-management",
        "description": "RFP/RFQ evaluation, contract negotiation, vendor audits, materials sourcing, and cost reduction",
        "icon": "ShoppingBag",
        "subcategories": [
            ("Procurement Manager", "procurement-manager"),
            ("Strategic Sourcing Specialist", "strategic-sourcing-specialist"),
            ("Vendor Contract Negotiator", "vendor-contract-negotiator")
        ]
    },
    {
        "name": "Warehouse Operations & Inventory Management",
        "slug": "warehouse-inventory-management",
        "description": "Fulfillment center oversight, inventory audits, barcode/RFID tracking, and dispatch planning",
        "icon": "Package",
        "subcategories": [
            ("Warehouse Manager", "warehouse-manager"),
            ("Inventory Control Specialist", "inventory-control-specialist"),
            ("Fulfillment Supervisor", "fulfillment-supervisor")
        ]
    },
    {
        "name": "Healthcare & Clinical Operations",
        "slug": "healthcare-clinical-operations",
        "description": "Hospital administration, clinical care, medical records, NABH compliance, and patient care",
        "icon": "Activity",
        "subcategories": [
            ("Hospital Operations Manager", "hospital-operations-manager"),
            ("Clinical Research Coordinator", "clinical-research-coordinator"),
            ("Medical Billing & Coding Specialist", "medical-billing-specialist")
        ]
    },
    {
        "name": "Pharmaceutical & Medical Affairs",
        "slug": "pharmaceutical-medical-affairs",
        "description": "Drug discovery, FDA/DCGI regulatory filings, pharmacovigilance, and medical affairs",
        "icon": "Pill",
        "subcategories": [
            ("Pharmacovigilance Officer", "pharmacovigilance-officer"),
            ("Pharma Regulatory Affairs Lead", "pharma-regulatory-lead"),
            ("Medical Science Liaison", "medical-science-liaison")
        ]
    },
    {
        "name": "Legal Affairs, Contracts & Intellectual Property",
        "slug": "legal-affairs-contracts",
        "description": "Commercial drafting, corporate advisory, dispute resolution, IP patents, and litigation oversight",
        "icon": "Scale",
        "subcategories": [
            ("Corporate Legal Counsel", "corporate-legal-counsel"),
            ("Contracts & Commercial Drafting Specialist", "contracts-drafting-specialist"),
            ("IP & Patent Attorney", "patent-attorney")
        ]
    },
    {
        "name": "Regulatory Compliance & Governance",
        "slug": "regulatory-compliance-governance",
        "description": "Anti-money laundering (AML), RBI/SEBI regulations, GDPR compliance, and internal audits",
        "icon": "CheckSquare",
        "subcategories": [
            ("Compliance Officer", "compliance-officer"),
            ("AML / KYC Risk Analyst", "aml-kyc-analyst"),
            ("Data Privacy (GDPR/DPDP) Consultant", "data-privacy-consultant")
        ]
    },
    {
        "name": "Civil Engineering & Construction Management",
        "slug": "civil-engineering-construction",
        "description": "Structural design, site project management, quality inspection, EPC projects, and AutoCAD/Revit",
        "icon": "Building",
        "subcategories": [
            ("Site Construction Engineer", "site-construction-engineer"),
            ("Structural Design Engineer", "structural-design-engineer"),
            ("EPC Project Manager", "epc-project-manager")
        ]
    },
    {
        "name": "Mechanical Engineering & Manufacturing",
        "slug": "mechanical-engineering-manufacturing",
        "description": "Plant maintenance, CAD/CAM design, CNC machining, Six Sigma quality control, and tooling",
        "icon": "Wrench",
        "subcategories": [
            ("Manufacturing Process Engineer", "manufacturing-process-engineer"),
            ("Mechanical CAD Designer (SolidWorks/CATIA)", "mechanical-cad-designer"),
            ("Quality Assurance (Six Sigma) Lead", "six-sigma-qa-lead")
        ]
    },
    {
        "name": "Electrical & Electronics Engineering",
        "slug": "electrical-electronics-engineering",
        "description": "Power distribution, circuit design, PCB layouts, electrical testing, and automation control systems",
        "icon": "Zap",
        "subcategories": [
            ("Electrical Power Engineer", "electrical-power-engineer"),
            ("PCB Design & Hardware Engineer", "pcb-hardware-engineer"),
            ("PLC & SCADA Automation Engineer", "plc-scada-engineer")
        ]
    },
    {
        "name": "Architecture, Real Estate & Urban Planning",
        "slug": "architecture-real-estate-planning",
        "description": "Architectural design, interior fit-outs, commercial leasing, property valuation, and urban masterplans",
        "icon": "Compass",
        "subcategories": [
            ("Senior Commercial Architect", "commercial-architect"),
            ("Interior Design & Fitout Specialist", "interior-design-specialist"),
            ("Real Estate Acquisition Manager", "real-estate-acquisition-manager")
        ]
    },
    {
        "name": "Hospitality, Travel & Tourism Management",
        "slug": "hospitality-travel-tourism",
        "description": "Hotel management, food & beverage (F&B), travel operations, corporate concierge, and event hosting",
        "icon": "Coffee",
        "subcategories": [
            ("Hotel General Manager", "hotel-general-manager"),
            ("Corporate Events & Banquet Director", "events-banquet-director"),
            ("Travel & Ticketing Consultant", "travel-ticketing-consultant")
        ]
    },
    {
        "name": "Education, Corporate Training & Instructional Design",
        "slug": "education-corporate-training",
        "description": "Corporate L&D, curriculum design, online learning management (LMS), and executive coaching",
        "icon": "GraduationCap",
        "subcategories": [
            ("Corporate L&D Trainer", "corporate-ld-trainer"),
            ("Instructional Designer", "instructional-designer"),
            ("Executive Leadership Coach", "executive-leadership-coach")
        ]
    },
    {
        "name": "Administration & Executive Office Support",
        "slug": "administration-office-support",
        "description": "Executive assistance, facility management, vendor coordination, front desk, and office admin",
        "icon": "Clipboard",
        "subcategories": [
            ("Executive Assistant to C-Suite", "executive-assistant"),
            ("Facility & Office Operations Manager", "facility-operations-manager"),
            ("Administrative Officer", "administrative-officer")
        ]
    },
    {
        "name": "ESG, Sustainability & Environmental Safety",
        "slug": "esg-sustainability-environmental",
        "description": "Carbon accounting, environmental impact audits, OSHA industrial safety, and renewable energy",
        "icon": "Leaf",
        "subcategories": [
            ("ESG & Sustainability Reporting Officer", "esg-reporting-officer"),
            ("Health, Safety & Environment (HSE) Manager", "hse-manager"),
            ("Renewable Energy Project Specialist", "renewable-energy-specialist")
        ]
    }
]

async def import_taxonomy_data():
    print("=" * 70)
    print("VELVORAX CAREERS - Enterprise Taxonomy Import (25 IT & 30 Non-IT)")
    print("=" * 70)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as db:
        # Import IT
        print(f"\n[1/2] Importing {len(IT_CATEGORIES)} IT Categories & Subcategories...")
        it_order = 1
        for item in IT_CATEGORIES:
            stmt = select(JobCategory).where(JobCategory.slug == item["slug"])
            cat = (await db.execute(stmt)).scalar_one_or_none()
            if not cat:
                cat = JobCategory(
                    name=item["name"],
                    slug=item["slug"],
                    category_type="IT",
                    description=item["description"],
                    icon=item["icon"],
                    display_order=it_order,
                    is_active=True
                )
                db.add(cat)
                await db.flush()
            else:
                cat.name = item["name"]
                cat.description = item["description"]
                cat.icon = item["icon"]
                cat.category_type = "IT"
                cat.display_order = it_order

            it_order += 1

            # Subcategories
            for sub_name, sub_slug in item["subcategories"]:
                sub_stmt = select(JobSubcategory).where(
                    JobSubcategory.category_id == cat.id,
                    JobSubcategory.slug == sub_slug
                )
                sub = (await db.execute(sub_stmt)).scalar_one_or_none()
                if not sub:
                    sub = JobSubcategory(
                        category_id=cat.id,
                        name=sub_name,
                        slug=sub_slug,
                        description=f"Specialized {sub_name} role in {cat.name}."
                    )
                    db.add(sub)

        # Import Non-IT
        print(f"\n[2/2] Importing {len(NON_IT_CATEGORIES)} Non-IT Categories & Subcategories...")
        non_it_order = 1
        for item in NON_IT_CATEGORIES:
            stmt = select(JobCategory).where(JobCategory.slug == item["slug"])
            cat = (await db.execute(stmt)).scalar_one_or_none()
            if not cat:
                cat = JobCategory(
                    name=item["name"],
                    slug=item["slug"],
                    category_type="NON_IT",
                    description=item["description"],
                    icon=item["icon"],
                    display_order=non_it_order,
                    is_active=True
                )
                db.add(cat)
                await db.flush()
            else:
                cat.name = item["name"]
                cat.description = item["description"]
                cat.icon = item["icon"]
                cat.category_type = "NON_IT"
                cat.display_order = non_it_order

            non_it_order += 1

            # Subcategories
            for sub_name, sub_slug in item["subcategories"]:
                sub_stmt = select(JobSubcategory).where(
                    JobSubcategory.category_id == cat.id,
                    JobSubcategory.slug == sub_slug
                )
                sub = (await db.execute(sub_stmt)).scalar_one_or_none()
                if not sub:
                    sub = JobSubcategory(
                        category_id=cat.id,
                        name=sub_name,
                        slug=sub_slug,
                        description=f"Specialized {sub_name} role in {cat.name}."
                    )
                    db.add(sub)

        await db.commit()
        print(f"\n[SUCCESS] Successfully populated 25 IT and 30 Non-IT categories and subcategories!")
        print("=" * 70)

def main():
    asyncio.run(import_taxonomy_data())

if __name__ == "__main__":
    main()
