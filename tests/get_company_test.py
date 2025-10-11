"""Test script for company scraping functionality."""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from fast_linkedin_scraper import LinkedInSession
from fast_linkedin_scraper.config import CompanyScrapingFields

# Load environment variables
load_dotenv()


async def test_company_scraping():
    """Test company scraping with different field configurations."""
    # Get cookie from environment
    cookie = os.getenv("LI_AT_COOKIE")
    if not cookie:
        print("Error: LI_AT_COOKIE environment variable not set")
        return

    # Test company URL
    company_url = "https://www.linkedin.com/company/microsoft/"

    # Create output directory
    output_dir = Path("tests/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Test 1: Minimal fields (fastest) with no employees
    async with LinkedInSession.from_cookie(cookie, headless=False) as session:
        company = await session.get_company(
            company_url,
            fields=CompanyScrapingFields.MINIMAL,
            max_pages=0,  # No employees
        )

        # Save to JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"company_minimal_{timestamp}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                company.model_dump(), f, indent=2, ensure_ascii=False, default=str
            )

        print(json.dumps(company.model_dump(), indent=2, default=str))

    # Test 2: All fields with 1 page of employees
    async with LinkedInSession.from_cookie(cookie, headless=False) as session:
        company = await session.get_company(
            company_url,
            fields=CompanyScrapingFields.ALL,
            max_pages=1,  # Default: 1 page of employees (~10 employees)
        )

        # Save to JSON
        output_file = output_dir / f"company_1page_{timestamp}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                company.model_dump(), f, indent=2, ensure_ascii=False, default=str
            )

        print(json.dumps(company.model_dump(), indent=2, default=str))

    # Test 3: All fields with 3 pages of employees
    async with LinkedInSession.from_cookie(cookie, headless=False) as session:
        company = await session.get_company(
            company_url,
            fields=CompanyScrapingFields.ALL,
            max_pages=3,  # More employees (~30)
        )

        # Save to JSON
        output_file = output_dir / f"company_all_{timestamp}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                company.model_dump(), f, indent=2, ensure_ascii=False, default=str
            )

        print(json.dumps(company.model_dump(), indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(test_company_scraping())
