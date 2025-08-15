#!/usr/bin/env python3
"""Example: Password authentication"""

import asyncio
import os

from dotenv import load_dotenv

from fast_linkedin_scraper import LinkedInSession, PasswordAuth

load_dotenv()

# Make sure to set credentials in your environment
email = os.getenv("LINKEDIN_EMAIL")
password = os.getenv("LINKEDIN_PASSWORD")
assert email is not None
assert password is not None


async def main():
    assert email is not None and password is not None  # Type narrowing for type checker
    # Interactive mode (only when no-headless) waits for user to manually solve captcha or security challenge if needed
    auth = PasswordAuth(email, password, interactive=True)

    async with LinkedInSession(auth=auth, headless=False) as _:
        print("✅ Logged in successfully!")
        input("Press Enter to close...")

    # Alternative: Convenience method
    # async with LinkedInSession.from_password(email, password, interactive=True, headless=False) as session:
    #     print("✅ Logged in successfully!")
    #     input("Press Enter to close...")


if __name__ == "__main__":
    asyncio.run(main())
