#!/usr/bin/env python3
"""Example: Cookie authentication"""

import os

from dotenv import load_dotenv

from fast_linkedin_scraper import CookieAuth, LinkedInSession

load_dotenv()

# Make sure to set LINKEDIN_COOKIE in your environment
cookie = os.getenv("LI_AT_COOKIE")
assert cookie is not None

auth = CookieAuth(cookie)

with LinkedInSession(auth=auth, headless=False) as session:
    print("✅ Logged in successfully!")
    input("Press Enter to close...")

# Alternative: Convenience method
# with LinkedInSession.from_cookie(cookie, headless=True) as session:
#     print("✅ Logged in successfully!")
#     input("Press Enter to close...")
