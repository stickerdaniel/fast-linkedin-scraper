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

# Profile URL to scrape
PROFILE_URL: str = "https://www.linkedin.com/in/stickerdaniel/"

# Create output directory
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

with LinkedInSession.from_cookie(cookie, headless=False) as session:
    # Scrape the profile
    person: Person = session.get_profile(PROFILE_URL)

    # Print the person object as pretty JSON
    print(json.dumps(person.model_dump(), indent=2, default=str))
