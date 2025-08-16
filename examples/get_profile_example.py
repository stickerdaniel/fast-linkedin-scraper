#!/usr/bin/env python3
"""Example: Profile scraping with cookie authentication"""

import asyncio
import json
import os

from dotenv import load_dotenv

from fast_linkedin_scraper import LinkedInSession, PersonScrapingFields
from fast_linkedin_scraper.models import Person

load_dotenv()

# Make sure to set LI_AT_COOKIE in your environment
cookie = os.getenv("LI_AT_COOKIE")
assert cookie is not None

# Profile URL to scrape
PROFILE_URL: str = "https://www.linkedin.com/in/stickerdaniel/"

# Create output directory
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)


async def main():
    assert cookie is not None  # Type narrowing for type checker
    async with LinkedInSession.from_cookie(cookie, headless=False) as session:
        # Example 1: Minimal scraping (fastest - only basic info)
        print("=== Minimal scraping (basic info only) ===")
        person_minimal: Person = await session.get_profile(
            PROFILE_URL, fields=PersonScrapingFields.MINIMAL
        )
        print(f"Name: {person_minimal.name}")
        print(f"Headline: {person_minimal.headline}")
        print(f"Location: {person_minimal.location}")
        print()

        # Example 2: Career-focused scraping (basic info + experience + education)
        print("=== Career scraping (basic + experience + education) ===")
        person_career: Person = await session.get_profile(
            PROFILE_URL, fields=PersonScrapingFields.CAREER
        )
        print(f"Name: {person_career.name}")
        print(f"Experience count: {len(person_career.experiences)}")
        print(f"Education count: {len(person_career.educations)}")
        print()

        # Example 3: Specific fields
        print("=== Custom field selection ===")
        custom_fields = (
            PersonScrapingFields.BASIC_INFO
            | PersonScrapingFields.EXPERIENCE
            | PersonScrapingFields.CONTACTS
        )
        person_custom: Person = await session.get_profile(
            PROFILE_URL, fields=custom_fields
        )
        print(f"Name: {person_custom.name}")
        print(f"Experience count: {len(person_custom.experiences)}")
        print(f"Connection count: {person_custom.connection_count}")
        print()

        # Example 4: All fields (slowest but most complete)
        print("=== All fields (complete profile) ===")
        person_all: Person = await session.get_profile(
            PROFILE_URL, fields=PersonScrapingFields.ALL
        )

        # Print the complete person object as pretty JSON
        print(json.dumps(person_all.model_dump(), indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
