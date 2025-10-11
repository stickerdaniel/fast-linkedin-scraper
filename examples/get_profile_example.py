#!/usr/bin/env python3
"""Example of scraping a LinkedIn profile with different field configurations."""

import asyncio
import json
import os
from dotenv import load_dotenv

from fast_linkedin_scraper import LinkedInSession
from fast_linkedin_scraper.config import PersonScrapingFields
from fast_linkedin_scraper.models import Person

# Load environment variables
load_dotenv()


async def main():
    """Run profile scraping examples."""
    # Get LinkedIn cookie from environment variable
    cookie = os.getenv("LI_AT_COOKIE")
    if not cookie:
        print("Error: LI_AT_COOKIE environment variable not set")
        return

    # Profile to scrape
    PROFILE_URL = "https://www.linkedin.com/in/anistji/"

    # Use context manager for automatic cleanup
    async with LinkedInSession.from_cookie(cookie, headless=False) as session:
        # Example 1: Minimal scraping (fastest - only basic info)
        person_minimal: Person = await session.get_profile(
            PROFILE_URL, fields=PersonScrapingFields.MINIMAL
        )
        print(json.dumps(person_minimal.model_dump(), indent=2, default=str))

        # Example 2: Career-focused scraping (basic info + experience + education)
        person_career: Person = await session.get_profile(
            PROFILE_URL, fields=PersonScrapingFields.CAREER
        )
        print(json.dumps(person_career.model_dump(), indent=2, default=str))

        # Example 3: Specific fields
        custom_fields: PersonScrapingFields = (
            PersonScrapingFields.BASIC_INFO
            | PersonScrapingFields.EXPERIENCE
            | PersonScrapingFields.CONTACTS
        )
        person_custom: Person = await session.get_profile(
            PROFILE_URL, fields=custom_fields
        )
        print(json.dumps(person_custom.model_dump(), indent=2, default=str))

        # Example 4: All fields (slowest but most complete)
        person_all: Person = await session.get_profile(
            PROFILE_URL, fields=PersonScrapingFields.ALL
        )
        print(json.dumps(person_all.model_dump(), indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
