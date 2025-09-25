#!/usr/bin/env python3
"""Example of scraping a LinkedIn company profile."""

import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from fast_linkedin_scraper import LinkedInSession
from fast_linkedin_scraper.config import CompanyScrapingFields

# Load environment variables
load_dotenv()


async def main():
    """Run company scraping example."""
    # Get LinkedIn cookie from environment variable
    cookie = os.getenv("LI_AT_COOKIE")
    if not cookie:
        print("Error: LI_AT_COOKIE environment variable not set")
        return

    # Company URL to scrape
    company_url = "https://www.linkedin.com/company/microsoft/"

    # Use context manager for automatic cleanup
    async with LinkedInSession.from_cookie(cookie, headless=False) as session:
        # Example 1: Scrape basic company information (fastest)
        company = await session.get_company(
            company_url,
            fields=CompanyScrapingFields.MINIMAL,
            max_pages=0,  # No employees
        )
        print(json.dumps(company.model_dump(), indent=2, default=str))

        # Example 2: Scrape with all fields and some employees
        company = await session.get_company(
            company_url,
            fields=CompanyScrapingFields.ALL,
            max_pages=2,  # Get 2 pages of employees (~20)
        )
        print(json.dumps(company.model_dump(), indent=2, default=str))

        # Optionally save to file
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "company_data.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                company.model_dump(), f, indent=2, ensure_ascii=False, default=str
            )


if __name__ == "__main__":
    asyncio.run(main())
