# Fast LinkedIn Scraper

> [!WARNING]
> This project is no longer maintained. I originally created this as a Playwright-based scraper for my [linkedin-mcp-server](https://github.com/stickerdaniel/linkedin-mcp-server). The [linkedin-scraper](https://github.com/joeyism/linkedin_scraper) library has since been rewritten with Playwright in v3.0, so I'm now using that instead.

<p align="left">
  <a href="https://github.com/stickerdaniel/fast-linkedin-scraper/actions/workflows/ci.yml" target="_blank"><img src="https://github.com/stickerdaniel/fast-linkedin-scraper/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI Status"></a>
  <a href="https://github.com/stickerdaniel/fast-linkedin-scraper/actions/workflows/release.yml" target="_blank"><img src="https://github.com/stickerdaniel/fast-linkedin-scraper/actions/workflows/release.yml/badge.svg?branch=main" alt="Release"></a>
  <a href="https://github.com/stickerdaniel/fast-linkedin-scraper/blob/main/LICENSE" target="_blank"><img src="https://img.shields.io/badge/License-MIT-brightgreen?labelColor=32383f" alt="License"></a>
</p>

A modern Python library for scraping LinkedIn.

## Overview

This library provides a high-level API for extracting LinkedIn profile data including work experience, education, and skills. Built with Playwright for reliable browser automation.

## Quick Start

```python
import asyncio
import json
from fast_linkedin_scraper import LinkedInSession
from fast_linkedin_scraper.config import PersonScrapingFields

async def main():
    # Using cookie authentication
    async with LinkedInSession.from_cookie(li_at_cookie) as session:
        # Minimal - just basic info (fastest, ~2s)
        person = await session.get_profile(
            "https://www.linkedin.com/in/stickerdaniel/",
            fields=PersonScrapingFields.MINIMAL
        )

        # Full - complete profile (~30s)
        person = await session.get_profile(
            "https://www.linkedin.com/in/stickerdaniel/",
            fields=PersonScrapingFields.ALL
        )
        print(json.dumps(person.model_dump(), indent=2, default=str))

asyncio.run(main())
```

<details>
<summary>Minimal Profile Output (fields=MINIMAL)</summary>

```json
{
  "linkedin_url": "https://www.linkedin.com/in/stickerdaniel/",
  "name": "Daniel Sticker",
  "headline": "Computer Science @ RWTH Aachen University",
  "location": "Aachen, North Rhine-Westphalia, Germany ",
  "about": [],
  "experiences": [],
  "educations": [],
  "interests": [],
  "honors": [],
  "languages": [],
  "contact_info": null,
  "connections": [],
  "connection_count": null
}
```
</details>

<details>
<summary>Full Profile Output (fields=ALL)</summary>

```json
{
  "linkedin_url": "https://www.linkedin.com/in/stickerdaniel/",
  "name": "Daniel Sticker",
  "headline": "Computer Science @ RWTH Aachen University",
  "location": "Aachen, North Rhine-Westphalia, Germany ",
  "about": [],
  "experiences": [],
  "educations": [
    {
      "institution_name": "RWTH Aachen University",
      "linkedin_url": "https://www.linkedin.com/company/9790/",
      "from_date": "Oct 2023",
      "to_date": "Aug 2026",
      "description": null,
      "degree": "Bachelor of Science - BS, Computer Science",
      "skills": [
        "Java",
        "iOS Development",
        "User Interface Design"
      ]
    }
  ],
  "interests": [],
  "honors": [
    {
      "title": "Award for Outstanding Contribution to School Event Management",
      "issuer": "Karl-Rehbein-Schule Hanau",
      "date": "Jul 2023\n Karl-Rehbein-Schule Hanau",
      "associated_with": "Karl-Rehbein-Schule",
      "document_url": "https://www.linkedin.com/in/stickerdaniel/details/honors/1738358859349/single-media-viewer?type=DOCUMENT&profileId=ACoAADxT9csB8ynBgQrXTkDJKnIAgazKRNKrflY"
    }
  ],
  "languages": [
    {
      "name": "English",
      "proficiency": "Full professional proficiency"
    },
    {
      "name": "French",
      "proficiency": "Limited working proficiency"
    },
    {
      "name": "German",
      "proficiency": "Native or bilingual proficiency"
    }
  ],
  "contact_info": {
    "email": "daniel@sticker.name",
    "phone": null,
    "website": "https://inframs.de",
    "linkedin_url": "https://linkedin.com/in/stickerdaniel"
  },
  "connections": [
    {
      "name": "Leon ten Brinke",
      "headline": "CCO & Consultant Time Traveler at BID4ONE, a JanLeon 🦁 company| Investor | Digital & AI Transformation sustainability XaaS 🧀 Kaaskop platform 🇳🇱 🇪🇺 in the 5.0 industry for our planet 🌎 .",
      "url": "https://www.linkedin.com/in/leon-ten-brinke-797360100"
    },
    {
      "name": "Sabri Derbent",
      "headline": "Frontend Developer | Experienced in turning mistakes into lessons Software Development, Data Management",
      "url": "https://www.linkedin.com/in/mustafasabriderbent"
    },
    {
      "name": "Max Winkler",
      "headline": "International Business Student at Vrije University Amsterdam",
      "url": "https://www.linkedin.com/in/max-winkler-1a9a80303"
    }
  ],
  "connection_count": 299
}
```
</details>

## Current Implementation

**Authentication**
- Cookie-based authentication (`li_at` cookie)
- Password authentication with manual captcha solving support
- Session management with headless or non-headless mode

**Profile Extraction**
- Personal information (name, headline, location, about)
- Work experiences with skills, descriptions, and dates
- Education history with degrees and institutions
- Robust content deduplication and cleaning

**Company Extraction**
- Basic company information (name, about, industry, size, headquarters)
- Company details (website, specialties, headcount)
- Employee scraping with pagination control and job titles
- Showcase pages and affiliated companies extraction
- Efficient navigation-based field configuration (flags control page visits, not data extraction)
- For every page visited, all available data is extracted

### Company Scraping Example

```python
import asyncio
import json
from fast_linkedin_scraper import LinkedInSession
from fast_linkedin_scraper.config import CompanyScrapingFields

async def scrape_company():
    async with LinkedInSession.from_cookie(li_at_cookie) as session:
        # Minimal - just /about page data (fastest)
        company = await session.get_company(
            "https://www.linkedin.com/company/microsoft/",
            fields=CompanyScrapingFields.MINIMAL,  # No additional navigations
            max_pages=0  # No employee scraping
        )
        print(json.dumps(company.model_dump(), indent=2, default=str))

        # Include showcase/affiliated pages
        company = await session.get_company(
            "https://www.linkedin.com/company/google/",
            fields=CompanyScrapingFields.ALL,  # Navigate to showcase/affiliated
            max_pages=3  # Also get ~30 employees (3 pages)
        )

        # Just employees, no showcase/affiliated
        company = await session.get_company(
            "https://www.linkedin.com/company/apple/",
            fields=CompanyScrapingFields.MINIMAL,
            max_pages=5  # Get ~50 employees
        )

        print(f"Company: {company.name}")
        print(f"Employees scraped: {len(company.employees)}")

asyncio.run(scrape_company())
```

### Company Profile Output Examples

<details>
<summary>Minimal Company Output (fields=MINIMAL, max_pages=0)</summary>

```json
{
  "linkedin_url": "https://www.linkedin.com/company/microsoft/",
  "name": "Microsoft",
  "about_us": "Every company has a mission. What's ours? To empower every person and every organization to achieve more. We believe technology can and should be a force for good and that meaningful innovation contributes to a brighter world in the future and today. Our culture doesn’t just encourage curiosity; it embraces it. Each day we make progress together by showing up as our authentic selves. We show up with a learn-it-all mentality. We show up cheering on others, knowing their success doesn't diminish our own. We show up every day open to learning our own biases, changing our behavior, and inviting in differences. Because impact matters. \n\nMicrosoft operates in 190 countries and is made up of approximately 228,000 passionate employees worldwide.",
  "website": "https://news.microsoft.com/",
  "headquarters": "Redmond, Washington",
  "industry": "Software Development",
  "company_size": "10,001+ employees",
  "specialties": [
    "Business Software",
    "Developer Tools",
    "Home & Educational Software",
    "Tablets",
    "Search",
    "Advertising",
    "Servers",
    "Windows Operating System",
    "Windows Applications & Platforms",
    "Smartphones",
    "Cloud Computing",
    "Quantum Computing",
    "Future of Work",
    "Productivity",
    "AI",
    "Artificial Intelligence",
    "Machine Learning",
    "Laptops",
    "Mixed Reality",
    "Virtual Reality",
    "Gaming",
    "Developers",
    "and IT Professional"
  ],
  "headcount": 10001,
  "showcase_pages": [
    {
      "name": "Microsoft Military Affairs",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-military-affairs"
    },
    {
      "name": "Microsoft On the Issues",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-on-the-issues"
    }
  ],
  "affiliated_companies": [
    {
      "name": "Skype",
      "linkedin_url": "https://www.linkedin.com/company/skype"
    }
  ],
  "followers": [],
  "employees": [],
  "scraping_errors": {}
}
```
</details>

<details>
<summary>All Company Output (fields=ALL, max_pages=3)</summary>

```json
{
  "linkedin_url": "https://www.linkedin.com/company/microsoft/",
  "name": "Microsoft",
  "about_us": "Every company has a mission. What's ours? To empower every person and every organization to achieve more. We believe technology can and should be a force for good and that meaningful innovation contributes to a brighter world in the future and today. Our culture doesn’t just encourage curiosity; it embraces it. Each day we make progress together by showing up as our authentic selves. We show up with a learn-it-all mentality. We show up cheering on others, knowing their success doesn't diminish our own. We show up every day open to learning our own biases, changing our behavior, and inviting in differences. Because impact matters. \n\nMicrosoft operates in 190 countries and is made up of approximately 228,000 passionate employees worldwide.",
  "website": "https://news.microsoft.com/",
  "headquarters": "Redmond, Washington",
  "industry": "Software Development",
  "company_size": "10,001+ employees",
  "specialties": [
    "Business Software",
    "Developer Tools",
    "Home & Educational Software",
    "Tablets",
    "Search",
    "Advertising",
    "Servers",
    "Windows Operating System",
    "Windows Applications & Platforms",
    "Smartphones",
    "Cloud Computing",
    "Quantum Computing",
    "Future of Work",
    "Productivity",
    "AI",
    "Artificial Intelligence",
    "Machine Learning",
    "Laptops",
    "Mixed Reality",
    "Virtual Reality",
    "Gaming",
    "Developers",
    "and IT Professional"
  ],
  "headcount": 10001,
  "showcase_pages": [
    {
      "name": "Microsoft Military Affairs",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-military-affairs"
    },
    {
      "name": "Microsoft On the Issues",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-on-the-issues"
    },
    {
      "name": "Microsoft Dynamics 365",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-dynamics"
    },
    {
      "name": "Microsoft 365",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-365"
    },
    {
      "name": "Microsoft Events",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-events"
    },
    {
      "name": "Microsoft News and Stories",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-news-and-stories"
    },
    {
      "name": "Microsoft Reactor",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-reactor"
    },
    {
      "name": "Microsoft 365 Insider Program",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-365-insider"
    },
    {
      "name": "Microsoft Developer",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-developers"
    },
    {
      "name": "Microsoft 365 Developer",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft365dev"
    },
    {
      "name": "Microsoft Copilot",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoftcopilot"
    },
    {
      "name": "M",
      "linkedin_url": "https://www.linkedin.com/showcase/covid19-business-resource-center"
    },
    {
      "name": "Microsoft Surface",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-surface"
    },
    {
      "name": "Microsoft Security Response Center",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-security-response-center"
    },
    {
      "name": "Microsoft Developers 365 page logo",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-developers-365"
    },
    {
      "name": "Microsoft for Healthcare",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-health"
    },
    {
      "name": "Microsoft Learn",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoftlearn"
    },
    {
      "name": "Microsoft in Business",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoftinbusiness"
    },
    {
      "name": "Microsoft Security",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-security"
    },
    {
      "name": "Go China Connection",
      "linkedin_url": "https://www.linkedin.com/showcase/go-china-connection"
    },
    {
      "name": "Microsoft Research",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoftresearch"
    },
    {
      "name": "Visual Studio Code",
      "linkedin_url": "https://www.linkedin.com/showcase/vs-code"
    },
    {
      "name": "Xbox",
      "linkedin_url": "https://www.linkedin.com/showcase/xbox"
    },
    {
      "name": "Microsoft Threat Intelligence",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-threat-intelligence"
    },
    {
      "name": "Microsoft's Entrepreneurship for Positive Impact",
      "linkedin_url": "https://www.linkedin.com/showcase/entrepreneurshipforpositiveimpact"
    },
    {
      "name": "Microsoft Advertising",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-advertising"
    },
    {
      "name": "Microsoft Fabric",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoftfabric"
    },
    {
      "name": "Microsoft for Nonprofits",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-for-nonprofits"
    },
    {
      "name": "Windows Developer",
      "linkedin_url": "https://www.linkedin.com/showcase/windows-developers"
    },
    {
      "name": "Microsoft Cloud",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-cloud-platform"
    },
    {
      "name": "Microsoft in Government",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-in-government"
    },
    {
      "name": "Microsoft Visual Studio",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-visual-studio"
    },
    {
      "name": "Microsoft Windows",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-windows"
    },
    {
      "name": "Microsoft Azure",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-azure"
    },
    {
      "name": "Microsoft AI Cloud Partner Program",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-cloud-partner-program"
    },
    {
      "name": "Microsoft Viva",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-viva"
    },
    {
      "name": "Microsoft Power Platform",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-power-platform"
    },
    {
      "name": "Microsoft SQL Server",
      "linkedin_url": "https://www.linkedin.com/showcase/msft-sql-server"
    }
  ],
  "affiliated_companies": [
    {
      "name": "Skype",
      "linkedin_url": "https://www.linkedin.com/company/skype"
    },
    {
      "name": "Nuance Communications",
      "linkedin_url": "https://www.linkedin.com/company/nuance-communications"
    },
    {
      "name": "Metanautix",
      "linkedin_url": "https://www.linkedin.com/company/metanautix"
    },
    {
      "name": "Lobe",
      "linkedin_url": "https://www.linkedin.com/company/lobeai"
    },
    {
      "name": "M12, Microsoft's Venture Fund",
      "linkedin_url": "https://www.linkedin.com/company/m12vc"
    },
    {
      "name": "Solair",
      "linkedin_url": "https://www.linkedin.com/company/solair"
    },
    {
      "name": "Parature",
      "linkedin_url": "https://www.linkedin.com/company/parature"
    },
    {
      "name": "Code Connect Inc.",
      "linkedin_url": "https://www.linkedin.com/company/code-connect-inc-"
    },
    {
      "name": "Flip",
      "linkedin_url": "https://www.linkedin.com/company/microsoftflip"
    },
    {
      "name": "Yammer, Inc.",
      "linkedin_url": "https://www.linkedin.com/company/yammer-inc"
    },
    {
      "name": "Studios Quality - Xbox Game Studios",
      "linkedin_url": "https://www.linkedin.com/company/studios-quality"
    },
    {
      "name": "Microsoft AI",
      "linkedin_url": "https://www.linkedin.com/company/microsoft-ai"
    },
    {
      "name": "Xamarin",
      "linkedin_url": "https://www.linkedin.com/company/xamarin"
    },
    {
      "name": "Semantic Machines",
      "linkedin_url": "https://www.linkedin.com/company/semantic-machines"
    },
    {
      "name": "Lumenisity Limited",
      "linkedin_url": "https://www.linkedin.com/company/lumenisity-limited"
    },
    {
      "name": "AltspaceVR",
      "linkedin_url": "https://www.linkedin.com/company/altspacevr"
    },
    {
      "name": "GitHub",
      "linkedin_url": "https://www.linkedin.com/company/github"
    },
    {
      "name": "Datazen Software",
      "linkedin_url": "https://www.linkedin.com/company/datazen"
    },
    {
      "name": "Event Zero",
      "linkedin_url": "https://www.linkedin.com/company/event-zero"
    },
    {
      "name": "Softomotive",
      "linkedin_url": "https://www.linkedin.com/company/softomotive"
    },
    {
      "name": "Microsoft Game Dev",
      "linkedin_url": "https://www.linkedin.com/company/msftgamedev"
    },
    {
      "name": "Revolution Analytics",
      "linkedin_url": "https://www.linkedin.com/company/revolution_analytics"
    },
    {
      "name": "Ulrich & 3 other connections follow this page",
      "linkedin_url": "https://www.linkedin.com/company/microsoft-cloud-platform"
    },
    {
      "name": "6Wunderkinder",
      "linkedin_url": "https://www.linkedin.com/company/6wunderkinder"
    },
    {
      "name": "Avere Systems",
      "linkedin_url": "https://www.linkedin.com/company/avere-systems"
    },
    {
      "name": "Cycle Computing",
      "linkedin_url": "https://www.linkedin.com/company/cycle-computing-llc"
    },
    {
      "name": "Aorato",
      "linkedin_url": "https://www.linkedin.com/company/aorato"
    },
    {
      "name": "Bonsai",
      "linkedin_url": "https://www.linkedin.com/company/bonsai-ai"
    },
    {
      "name": "InMage Systems",
      "linkedin_url": "https://www.linkedin.com/company/inmage-systems"
    },
    {
      "name": "Wand Labs, Inc.",
      "linkedin_url": "https://www.linkedin.com/company/wandlabs"
    },
    {
      "name": "Incent Games, Inc.",
      "linkedin_url": "https://www.linkedin.com/company/incent-games-llc"
    },
    {
      "name": "Halo Studios",
      "linkedin_url": "https://www.linkedin.com/company/halostudios"
    }
  ],
  "followers": [
    {
      "name": "Andrii Snurnikov",
      "headline": "B.Sc. Computer Science Student at RWTH Aachen University",
      "linkedin_url": "https://www.linkedin.com/in/andrii-snurnikov"
    },
    {
      "name": "Volodymyr Sheremeta",
      "headline": "B. Sc. Computer Science @ RWTH Aachen",
      "linkedin_url": "https://www.linkedin.com/in/volodymyr-sheremeta1"
    },
    {
      "name": "Michael Zaikin",
      "headline": "B. Sc. Computer Science @ RWTH Aachen University",
      "linkedin_url": "https://www.linkedin.com/in/michael-zaikin"
    },
    {
      "name": "Max Mingazzini",
      "headline": "CS @ RWTH Aachen | Head of Education @ ADSC | Student Research Assistant in Robotics | Undergraduate Researcher",
      "linkedin_url": "https://www.linkedin.com/in/max-mingazzini-3b97a1186"
    },
    {
      "name": "Bernardo Hakme",
      "headline": "Computer Engineering at RWTH",
      "linkedin_url": "https://www.linkedin.com/in/bernardo-hakme-70032234a"
    },
    {
      "name": "Felix Mertins",
      "headline": "Head of IT at Collective Incubator e.V. | Student Assistant at RWTH Innovation | CS-Student at RWTH-Aachen University",
      "linkedin_url": "https://www.linkedin.com/in/felix-mertins"
    },
    {
      "name": "Fadi Al Eliwi",
      "headline": "RWTH CS Student & Software Developer @ EFi",
      "linkedin_url": "https://www.linkedin.com/in/fadi-eliwi"
    },
    {
      "name": "Geonho Yun",
      "headline": "Software Developer @ SAP | CS @ RWTH Aachen",
      "linkedin_url": "https://www.linkedin.com/in/geonhoyun"
    },
    {
      "name": "Kawther Ben Elkahia",
      "headline": "B.Sc. Computer science at RWTH Aachen University",
      "linkedin_url": "https://www.linkedin.com/in/kawther-ben-elkahia-2a4559309"
    },
    {
      "name": "Tom Wesseling",
      "headline": "EE @RWTH @THU | Robotics | Studienstiftung",
      "linkedin_url": "https://www.linkedin.com/in/tomwesseling"
    },
    {
      "name": "Bader Aljaberi",
      "headline": "Aspiring Computer Engineer | Award-Winning Developer (Game Design & Robotics) | STEM Educator (AI, Robotics, Cybersecurity) | Honor Roll Student | Seeking Global Internships | Keywords: App Development, AI, Cybersecurity",
      "linkedin_url": "https://www.linkedin.com/in/bader-aljaberi-a593b8367"
    },
    {
      "name": "Constantin Ciupek",
      "headline": "Software Engineer, AWS Billing at Amazon Web Services (AWS)",
      "linkedin_url": "https://www.linkedin.com/in/constantin-ciupek"
    },
    {
      "name": "Vincent Nahn",
      "headline": "CS @ RWTH Aachen University | Studienstiftung | Mercura (YC W25)",
      "linkedin_url": "https://www.linkedin.com/in/vincent-nahn"
    },
    {
      "name": "Ulrich Sticker",
      "headline": "Senior CRM/ERP Manager bei DE-CIX Group AG",
      "linkedin_url": "https://www.linkedin.com/in/usticker"
    },
    {
      "name": "Lorenzo Guerrero",
      "headline": "Data Engineer | Azure | Cloud computing",
      "linkedin_url": "https://www.linkedin.com/in/lorenzoguerrero17"
    },
    {
      "name": "Danny Bodnar",
      "headline": "Revenue Operations at 🌖 Luminovo",
      "linkedin_url": "https://www.linkedin.com/in/danny-bodnar"
    },
    {
      "name": "Max Rahmsdorf",
      "headline": "McKinsey | Studienstiftung | RWTH | NTU Singapur",
      "linkedin_url": "https://www.linkedin.com/in/maxrahmsdorf"
    },
    {
      "name": "Artem Kolokoltsev",
      "headline": "​​Generalist, Engineer | 6+ years SWE experience | Docker, CI/CD | RAG, Prompt Engineering, Analytics",
      "linkedin_url": "https://www.linkedin.com/in/artem-kolokoltsev"
    },
    {
      "name": "Jan Niklas Lehmann",
      "headline": "University of Oxford | Deutsche Börse | Frankfurt School of Finance & Management | Computational Business Analytics",
      "linkedin_url": "https://www.linkedin.com/in/jan-niklas-lehmann-208580298"
    },
    {
      "name": "Yeganeh Khoshakhlagh",
      "headline": "Computer Engineering Student",
      "linkedin_url": "https://www.linkedin.com/in/yeganeh-khoshakhlagh-4221b3246"
    },
    {
      "name": "Simon Brebeck",
      "headline": "WorldSkills 2024 + EuroSkills 2025 Competitor | Full-Stack Software Developer | Student at RWTH Aachen University",
      "linkedin_url": "https://www.linkedin.com/in/simonbrebeck"
    },
    {
      "name": "Falguni Mahajan",
      "headline": "Social Media Marketing Officer @ Space Team Aachen e.V. | M.Sc MME TIME",
      "linkedin_url": "https://www.linkedin.com/in/falguni-mahajan-40a112173"
    },
    {
      "name": "Shlok Kakadia",
      "headline": "Computer Science @ KIT | ERP Software Engineer @ EIFER",
      "linkedin_url": "https://www.linkedin.com/in/shlok-kakadia-7b2656298"
    },
    {
      "name": "Amrutha Kannan",
      "headline": "M.Sc. Data Science at RWTH Aachen University",
      "linkedin_url": "https://www.linkedin.com/in/kannanamrutha"
    },
    {
      "name": "Hasan Al-Khazraji",
      "headline": "SWE Intern @ Tesla | Prev. @ Shopify, Rocket | Computer Engineering Student",
      "linkedin_url": "https://www.linkedin.com/in/hasan-al-khazraji"
    },
    {
      "name": "Jonas Diesberger",
      "headline": "Dual Student Business Administration & International Management at Engelbert Strauss",
      "linkedin_url": "https://www.linkedin.com/in/jonas-diesberger-63b66621a"
    },
    {
      "name": "Hritik Raj",
      "headline": "@Nutanix AI | BITS Pilani",
      "linkedin_url": "https://www.linkedin.com/in/hritik-raj-08176920a"
    },
    {
      "name": "Abdellahi Abdellahi",
      "headline": "Banking Software Engineer | Java & DevOps | Delivering Compliant, Secure & Scalable Financial Solutions",
      "linkedin_url": "https://www.linkedin.com/in/abdellahi-abdellahi"
    },
    {
      "name": "Animesh Mishra",
      "headline": "Software Development | Java | Springboot | Python | AI | ML | Computer Science @ShivNadarUniversity",
      "linkedin_url": "https://www.linkedin.com/in/animeshmishra0"
    },
    {
      "name": "Sri Meghana Yarlagadda",
      "headline": "Honours Mathematics | Statistics and Computational Mathematics",
      "linkedin_url": "https://www.linkedin.com/in/yarlas"
    },
    {
      "name": "Kemal Baykan",
      "headline": "\"Unlocking Success: Elevate Your Brand, Expand Your Reach, Boost Your Profits with Our Marketing Agency!\"",
      "linkedin_url": "https://www.linkedin.com/in/kemal-baykan-685489220"
    },
    {
      "name": "Dr. Lukas Voj",
      "headline": "🚀 M2M-Connectivity Experte | KI-getriebene B2B-Innovation | Effizienz- & Vertriebsbeschleuniger",
      "linkedin_url": "https://www.linkedin.com/in/dr-lukas-voj-340538146"
    },
    {
      "name": "William N",
      "headline": "Scaling content pipelines for local and global businesses with AI-driven systems, creative storytelling and strategy. **A word is worth a thousand pictures**",
      "linkedin_url": "https://www.linkedin.com/in/william-naayem"
    },
    {
      "name": "Charles d'Avernas",
      "headline": "Co-founder @ Neuroglia | Lead Maintainer @ CNCF Serverless Workflow | Creator @ CNCF Synapse WFMS | TSC @ AsyncAPI",
      "linkedin_url": "https://www.linkedin.com/in/charles-d-avernas-40836a13"
    },
    {
      "name": "Sam Shrestha",
      "headline": "Maths & CS @ University of Adelaide | AI Engineer",
      "linkedin_url": "https://www.linkedin.com/in/sshresthh"
    },
    {
      "name": "Julian Schulz",
      "headline": "CPO @ Stealth",
      "linkedin_url": "https://www.linkedin.com/in/julian-schulz"
    },
    {
      "name": "Anantyash Dixit",
      "headline": "Silicon Design | Embedded Systems | Entrepreneurship",
      "linkedin_url": "https://www.linkedin.com/in/anantyash-dixit-3906241b8"
    },
    {
      "name": "Rajveer Suneha (Raj)",
      "headline": "Computer Science Associate degree | Open to IT support/ Cloud support roles",
      "linkedin_url": "https://www.linkedin.com/in/rajveersuneha007"
    },
    {
      "name": "Hritik Chouhan",
      "headline": "Career Advisor at Apex Tech IT | Job Hunting Expert | Hiring OPT & STEM Extension students ⇒ GC / Citizens | Connecting Talent with Client | Resume Review | Interview Help |",
      "linkedin_url": "https://www.linkedin.com/in/hritik-chouhan-502b1321b"
    },
    {
      "name": "Jordan Renda",
      "headline": null,
      "linkedin_url": "https://www.linkedin.com/in/jordan-renda-ab941679"
    },
    {
      "name": "Francis Ifeanyi, MD, MBA",
      "headline": "Senior Business Leadership | Healthcare | Product Leadership | Marketing | Growth | Technology leadership | Digital Healthcare | Innovation | Product | Futurist | Health Tech | Insuretech",
      "linkedin_url": "https://www.linkedin.com/in/francis-n-product-innovation"
    },
    {
      "name": "Afsaneh Fazly",
      "headline": "CTO, and Co-founder",
      "linkedin_url": "https://www.linkedin.com/in/afsaneh-fazly"
    },
    {
      "name": "Jacque Swartz",
      "headline": "Technology innovator helping companies to deploy AI with ROI 🚀",
      "linkedin_url": "https://www.linkedin.com/in/jaywswartz"
    },
    {
      "name": "Wassim Attia",
      "headline": "AI & ML Engineer | Multi-Agent Systems | Generative AI | Computer Vision | LLM Applications",
      "linkedin_url": "https://www.linkedin.com/in/wassim-attia-006044250"
    },
    {
      "name": "Claudia Alphonso",
      "headline": "Quality Assurance Editor @SWZD",
      "linkedin_url": "https://www.linkedin.com/in/claudia-alphonso-ab9a5b227"
    },
    {
      "name": "Yuri Winche Achermann",
      "headline": "aerospace eng. ∩ data science | 2x fndr @ TD & Nomad | MSFT & INTC amb.",
      "linkedin_url": "https://www.linkedin.com/in/yuriachermann"
    },
    {
      "name": "Ria Bhaumik",
      "headline": "High school student",
      "linkedin_url": "https://www.linkedin.com/in/ria-bhaumik-97aa17318"
    },
    {
      "name": "Sabri Derbent",
      "headline": "Frontend Developer | Experienced in turning mistakes into lessons Software Development, Data Management",
      "linkedin_url": "https://www.linkedin.com/in/mustafasabriderbent"
    },
    {
      "name": "Jeremiah George",
      "headline": "Computer Engineering Student @ University of Guelph",
      "linkedin_url": "https://www.linkedin.com/in/jeremiah-george-61a5a3337"
    },
    {
      "name": "Kumoian Linhe DENG",
      "headline": "Simulation & Medical Software Developer | TUM & LMU Dual Degree",
      "linkedin_url": "https://www.linkedin.com/in/kumoian-linhe-d-05b4322a7"
    },
    {
      "name": "Ali Hariri Movahed",
      "headline": "Data Scientist & Developer @ Fraunhofer IPT, Software Engineer @ EFAB GmbH, Computer Science Student @ RWTH Aachen University",
      "linkedin_url": "https://www.linkedin.com/in/ali-hariri-mov"
    },
    {
      "name": "Jayashrinidhi Vijayaraghavan",
      "headline": "AIML Engineer | Data Scientist | Student | Researcher| NLP / LLM | Author/Poet",
      "linkedin_url": "https://www.linkedin.com/in/jayashrinidhi-vijayaraghavan-4a3861257"
    },
    {
      "name": "A. Murat Arslan",
      "headline": "Working student for Digitalization & Industrial IoT @ Saint-Gobain Group | RWTH Aachen University | Electrical Engineering & Information Technology",
      "linkedin_url": "https://www.linkedin.com/in/a-murat-arslan-20a468256"
    },
    {
      "name": "Sabalan Danaei",
      "headline": "Social Media Marketing Expert",
      "linkedin_url": "https://www.linkedin.com/in/sabalan"
    },
    {
      "name": "Glen Grant",
      "headline": "B.Sc. Informatik at RWTH Aachen University",
      "linkedin_url": "https://www.linkedin.com/in/glen-grant-ba2108238"
    },
    {
      "name": "Xiaorui Wang",
      "headline": "Masterstudent im Studiengang Informatik an der RWTH Aachen",
      "linkedin_url": "https://www.linkedin.com/in/xiaorui-wang-a2b941215"
    },
    {
      "name": "RASHMI YADAV",
      "headline": "SDE-2 @Intuit |Ex SDE-1 @Tekion Corp|| Ex ASDE-2 @Publicis-Sapient | Ex-Intern @Amdocs | Microsoft Engage'21 Mentee",
      "linkedin_url": "https://www.linkedin.com/in/rashmi-yadav-60b4871b4"
    },
    {
      "name": "Luka Sikic",
      "headline": "Co-Founder & CTO at onpreo AG",
      "linkedin_url": "https://www.linkedin.com/in/luka-sikic"
    },
    {
      "name": "KARIM MOHAMMEDI",
      "headline": "Managing Partner – Strategy & Global Leadership",
      "linkedin_url": "https://www.linkedin.com/in/karim-mohammedi-fastcube"
    },
    {
      "name": "Judy Retuerma, LPT, CHRA",
      "headline": "Hiring IT & Technical Professionals in the US market",
      "linkedin_url": "https://www.linkedin.com/in/judyannretuerma"
    },
    {
      "name": "Kunhao Wang",
      "headline": "Computer Science student at RWTH Aachen",
      "linkedin_url": "https://www.linkedin.com/in/kunhao-wang-949119106"
    },
    {
      "name": "Leon ten Brinke",
      "headline": "CCO & Consultant Time Traveler at BID4ONE, a JanLeon 🦁 company| Investor | Digital & AI Transformation sustainability XaaS 🧀 Kaaskop platform 🇳🇱 🇪🇺 in the 5.0 industry for our planet 🌎 .",
      "linkedin_url": "https://www.linkedin.com/in/leon-ten-brinke-797360100"
    },
    {
      "name": "John Peslar",
      "headline": "AI Automation Builder | Founder at getinterviews.ai, LaunchpadFast | $50M+ Revenue Impact | Building the Future of Work",
      "linkedin_url": "https://www.linkedin.com/in/jonathan-peslar"
    }
  ],
  "employees": [],
  "scraping_errors": {}
}
```
</details>

## Roadmap

- fix profile experience scraping
- fix company employees scraping
- Job search and extraction
- Connection and network analysis
- Advanced search filters

## License

This project is licensed under the MIT license.
