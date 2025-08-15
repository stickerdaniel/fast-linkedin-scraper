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

## Roadmap

- Company profile scraping
- Job search and extraction
- Connection and network analysis

## License

This project is licensed under the MIT license.
