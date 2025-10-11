# Fast LinkedIn Scraper

<p align="left">
  <a href="https://github.com/stickerdaniel/fast-linkedin-scraper/actions/workflows/ci.yml" target="_blank"><img src="https://github.com/stickerdaniel/fast-linkedin-scraper/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI Status"></a>
  <a href="https://github.com/stickerdaniel/fast-linkedin-scraper/actions/workflows/release.yml" target="_blank"><img src="https://github.com/stickerdaniel/fast-linkedin-scraper/actions/workflows/release.yml/badge.svg?branch=main" alt="Release"></a>
  <a href="https://github.com/stickerdaniel/fast-linkedin-scraper/blob/main/LICENSE" target="_blank"><img src="https://img.shields.io/badge/License-MIT-brightgreen?labelColor=32383f" alt="License"></a>
</p>

A modern Python library for efficiently scraping LinkedIn.

## Overview

This library provides a high-level API for extracting LinkedIn profile data including work experience, education, and skills. Built with Playwright for reliable browser automation.

## Quick Start

```python
import asyncio
from fast_linkedin_scraper import LinkedInSession

async def main():
    # Using cookie authentication
    async with LinkedInSession.from_cookie(li_at_cookie) as session:
        person = await session.get_profile("https://www.linkedin.com/in/stickerdaniel/")
        print(json.dumps(person.model_dump(), indent=2, default=str))

asyncio.run(main())
```
**Output**
```json
{
  "linkedin_url": "https://www.linkedin.com/in/stickerdaniel/",
  "name": "Daniel Sticker",
  "headline": "Computer Science @ RWTH Aachen University",
  "location": "Greater Toronto Area, Canada ",
  "about": [],
  "experiences": [
    {
      "institution_name": "nGENn GmbH",
      "linkedin_url": "https://www.linkedin.com/company/41217272/",
      "from_date": "Oct 2024",
      "to_date": "Apr 2025",
      "description": "Automating compliance and documentation processes for businesses, optimizing operational efficiency, enhancing data security management, and auditing.",
      "position_title": "Software Developer",
      "duration": "7 mos",
      "location": "Frankfurt Rhine-Main Metropolitan Area · Remote",
      "employment_type": "Work Study",
      "skills": [
        "Gitlab",
        "Python (Programming Language)",
        "Engineering"
      ]
    },
    {
      "institution_name": "Hytek GmbH",
      "linkedin_url": "https://www.linkedin.com/company/6860848/",
      "from_date": "Sep 2023",
      "to_date": "Jan 2024",
      "description": "Following my short-term developer role, I was commissioned for a freelance project to create software that automatically synchronized products from the ERP system to the web catalog and online shop using Shopify & Webflow APIs.",
      "position_title": "Software Developer",
      "duration": "5 mos",
      "location": "Remote",
      "employment_type": "Freelance",
      "skills": [
        "Shopify API",
        "Webflow API",
        "Flutter"
      ]
      ...
```

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

**Company Extraction** ✅ Fully Implemented
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
<summary>Basic Company Information (fields=MINIMAL, max_pages=0)</summary>

```json
{
  "linkedin_url": "https://www.linkedin.com/company/microsoft/",
  "name": "Microsoft",
  "about_us": "Every company has a mission. What's ours? To empower every person and every organization to achieve more...",
  "website": "https://news.microsoft.com/",
  "headquarters": "Redmond, Washington",
  "industry": "Software Development",
  "company_size": "10,001+ employees",
  "specialties": [
    "Business Software",
    "Developer Tools",
    "Home & Educational Software",
    "Cloud Computing",
    "Artificial Intelligence",
    "Machine Learning"
  ],
  "headcount": 10001,
  "showcase_pages": [],
  "affiliated_companies": [],
  "employees": []
}
```
</details>

<details>
<summary>Company with Showcase/Affiliated Pages (fields=ALL, max_pages=0)</summary>

```json
{
  "name": "Microsoft",
  "industry": "Software Development",
  "showcase_pages": [
    {
      "name": "Microsoft Military Affairs",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-military-affairs/",
      "followers": null
    },
    {
      "name": "Microsoft On the Issues",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-on-the-issues/",
      "followers": null
    }
  ],
  "affiliated_companies": [
    {
      "name": "Skype",
      "linkedin_url": "https://www.linkedin.com/company/skype/",
      "followers": null
    }
  ],
  "employees": []
}
```
</details>

<details>
<summary>Company with Employees (fields=MINIMAL, max_pages=2)</summary>

```json
{
  "name": "Microsoft",
  "industry": "Software Development",
  "employees": [
    {
      "name": "Christian Remmelberger",
      "designation": "CS @ TUM | SWE @ Microsoft",
      "linkedin_url": "https://www.linkedin.com/in/christian-remmelberger"
    },
    {
      "name": "Zhou Wang",
      "designation": "Principal Software Engineer",
      "linkedin_url": "https://www.linkedin.com/in/zhou-wang-9bb24952"
    },
    {
      "name": "Laetitia Maar",
      "designation": "Solution Engineer | Cloud & AI Apps | Microsoft",
      "linkedin_url": "https://www.linkedin.com/in/laetitia-maar-4a98a11b6"
    }
  ]
}
```
</details>

<details>
<summary>Complete Company Profile (fields=ALL, max_pages=2)</summary>

```json
{
  "linkedin_url": "https://www.linkedin.com/company/microsoft/",
  "name": "Microsoft",
  "about_us": "Every company has a mission. What's ours? To empower every person and every organization to achieve more. We believe technology can and should be a force for good...",
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
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-military-affairs/"
    },
    {
      "name": "Microsoft On the Issues",
      "linkedin_url": "https://www.linkedin.com/showcase/microsoft-on-the-issues/"
    }
  ],
  "affiliated_companies": [
    {
      "name": "Skype",
      "linkedin_url": "https://www.linkedin.com/company/skype/"
    }
  ],
  "employees": [
    {
      "name": "Christian Remmelberger",
      "designation": "CS @ TUM | SWE @ Microsoft",
      "linkedin_url": "https://www.linkedin.com/in/christian-remmelberger"
    },
    {
      "name": "Zhou Wang",
      "designation": "Principal Software Engineer",
      "linkedin_url": "https://www.linkedin.com/in/zhou-wang-9bb24952"
    }
  ]
}
```
</details>

### Company Fields Documentation

| Field | Type | Description | Navigation Required |
|-------|------|-------------|--------------------|
| `name` | string | Company name | Always from /about |
| `linkedin_url` | string | Company LinkedIn URL | Always from /about |
| `about_us` | string | Company description/mission | Always from /about |
| `website` | string | Company website URL | Always from /about |
| `headquarters` | string | Company HQ location | Always from /about |
| `industry` | string | Primary industry | Always from /about |
| `company_size` | string | Employee range (e.g., "10,001+") | Always from /about |
| `specialties` | list[string] | Areas of expertise | Always from /about |
| `headcount` | integer | Numeric employee count | Always from /about |
| `showcase_pages` | list[CompanySummary] | Showcase/brand pages | Requires `ALL` flag |
| `affiliated_companies` | list[CompanySummary] | Affiliated companies | Requires `ALL` flag |
| `employees` | list[Employee] | Employee profiles | Controlled by `max_pages` |

### Scraping Performance Guide

| Configuration | Time | Data Scraped |
|--------------|------|-------------|
| `fields=MINIMAL, max_pages=0` | ~3s | All /about page data (name, industry, website, HQ, etc.) |
| `fields=ALL, max_pages=0` | ~9s+ | /about + showcase/affiliated pages |
| `fields=MINIMAL, max_pages=1` | ~6s | /about data + ~10 employees (default) |
| `fields=ALL, max_pages=5` | ~24s+ | All pages + ~50 employees |

## Roadmap

- Job search and extraction
- Connection and network analysis
- Advanced search filters
- Bulk profile processing

## License

This project is licensed under the MIT license.
