#!/usr/bin/env python3
"""Contacts-only scraping test using cookie authentication.

This test authenticates once, visits each profile, runs only the contacts
scraper (contact info, connection count, and connection list when available),
and writes the resulting `Person` model to JSON under `tests/output/`.
"""

import json
import os

from dotenv import load_dotenv
from pydantic import HttpUrl

from fast_linkedin_scraper import LinkedInSession
from fast_linkedin_scraper.models import Person
from fast_linkedin_scraper.scrapers.person.contacts import scrape_contacts

load_dotenv()

# Ensure LI_AT_COOKIE is set in environment
cookie = os.getenv("LI_AT_COOKIE")
assert cookie is not None, "LI_AT_COOKIE environment variable must be set"

# Profile usernames to scrape contacts for (mirrors real test subjects)
USERNAMES = [
    "anistji",
    "stickerdaniel",
]

# Output directory relative to tests/
OUTPUT_DIR = "output"


with LinkedInSession.from_cookie(cookie, headless=True) as session:
    # Get authenticated Playwright page
    page = session._ensure_authenticated()

    for username in USERNAMES:
        profile_url = f"https://www.linkedin.com/in/{username}/"

        # Initialize Person with validated LinkedIn URL
        person: Person = Person(linkedin_url=HttpUrl(profile_url))

        # Run only the contacts scraping logic
        scrape_contacts(page, person)

        # Prepare output path (auto-increment if file exists)
        tests_output_dir = os.path.join("tests", OUTPUT_DIR)
        os.makedirs(tests_output_dir, exist_ok=True)

        base_filename = f"{username}_contacts"
        extension = ".json"
        filename = os.path.join(tests_output_dir, f"{base_filename}{extension}")

        counter = 1
        while os.path.exists(filename):
            filename = os.path.join(
                tests_output_dir, f"{base_filename}_{counter}{extension}"
            )
            counter += 1

        # Write Person model to JSON
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(person.model_dump(), f, indent=2, default=str, ensure_ascii=False)

        print(f"Contacts saved to: {filename}")
