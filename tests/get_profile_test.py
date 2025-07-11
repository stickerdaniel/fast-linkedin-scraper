#!/usr/bin/env python3
"""Example: Profile scraping with cookie authentication"""

import json
import os

from dotenv import load_dotenv

from fast_linkedin_scraper import LinkedInSession
from fast_linkedin_scraper.models import Person

load_dotenv()
# Make sure to set LI_AT_COOKIE in your environment
cookie = os.getenv("LI_AT_COOKIE")
assert cookie is not None
# Profile URLs to scrape
USERNAMES = [
    "rayan-siddiqui-511822303",
    # "anistji",
    # "stickerdaniel",
]

# Create output directory
output_dir = "output"

with LinkedInSession.from_cookie(cookie, headless=False) as session:
    # Scrape both profiles
    for username in USERNAMES:
        profile_url = f"https://www.linkedin.com/in/{username}/"
        person: Person = session.get_profile(profile_url)

        # Print the person object as pretty JSON
        # print(json.dumps(person.model_dump(), indent=2, default=str))

        # Save the person object to a JSON file with auto-incrementing filename
        # Extract username from URL (e.g., "anistji" from "https://www.linkedin.com/in/anistji/")
        username = profile_url.split("/in/")[1].rstrip("/")
        base_filename = username
        extension = ".json"

        # Ensure tests/output directory exists
        tests_output_dir = os.path.join("tests", output_dir)
        os.makedirs(tests_output_dir, exist_ok=True)

        filename = os.path.join(tests_output_dir, f"{base_filename}{extension}")

        counter = 1
        while os.path.exists(filename):
            filename = os.path.join(
                tests_output_dir, f"{base_filename}_{counter}{extension}"
            )
            counter += 1

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(person.model_dump(), f, indent=2, default=str, ensure_ascii=False)

        print(f"Profile saved to: {filename}")
