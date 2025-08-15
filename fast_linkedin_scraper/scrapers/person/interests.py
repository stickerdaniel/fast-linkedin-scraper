"""Interests scraping module for LinkedIn profiles."""

import os
from typing import Optional

from playwright.async_api import Page, Locator

from ...models.person import Person, Interest
from ..utils import scroll_to_half, scroll_to_bottom


async def scrape_interests(page: Page, person: Person) -> None:
    """Scrape interests information from LinkedIn profile.

    Args:
        page: Playwright page instance
        person: Person model to populate with interests
    """
    # Navigate to interests details page
    interests_url = os.path.join(str(person.linkedin_url), "details/interests")
    await page.goto(interests_url)

    # Wait for page to load
    await page.wait_for_timeout(2000)  # 2 seconds

    # Scroll to ensure all content is loaded
    await scroll_to_half(page)
    await page.wait_for_timeout(1000)  # 1 second
    await scroll_to_bottom(page)
    await page.wait_for_timeout(2000)  # 2 seconds for content to load

    # Find the main interests container
    try:
        main_content = page.locator("main").first
        if not await main_content.is_visible():
            return

        # Get all list containers (different categories of interests)
        list_containers = await main_content.locator(".pvs-list__container").all()

        for list_container in list_containers:
            # Get all items in this list
            items = await list_container.locator(".pvs-list__paged-list-item").all()

            for item in items:
                try:
                    interest = await _extract_interest_from_item(item)
                    if interest:
                        person.add_interest(interest)
                except Exception:
                    # Skip this interest if extraction fails
                    continue

    except Exception:
        # If main container not found, skip interests scraping
        pass


async def _extract_interest_from_item(item: Locator) -> Optional[Interest]:
    """Extract interest information from a list item.

    Args:
        item: The list item locator containing interest information

    Returns:
        Interest object or None if extraction fails
    """
    try:
        # Try to find the main link in the item
        link = item.locator("a").first
        if not await link.is_visible():
            return None

        # Get the URL
        url = link.get_attribute("href")
        if not url:
            return None

        # Determine the type and extract name based on URL pattern
        interest_type = "unknown"
        name = ""

        if "/in/" in url:
            # This is a person/influencer
            interest_type = "influencer"
            # Try to extract name from image alt text or link text
            img = link.locator("img").first
            if await img.is_visible():
                name = await img.get_attribute("alt") or ""
            if not name:
                # Try to get from span with aria-hidden
                name_elem = link.locator("span[aria-hidden='true']").first
                if await name_elem.is_visible():
                    name = (await name_elem.inner_text()).strip()
        elif "/company/" in url:
            # This is a company
            interest_type = "company"
            # Try to get company name from aria-label
            aria_label = await link.get_attribute("aria-label")
            if aria_label and "company page for" in aria_label.lower():
                name = aria_label.replace("Company page for", "").strip()
            else:
                # Try from image alt text
                img = link.locator("img").first
                if await img.is_visible():
                    name = await img.get_attribute("alt") or ""
        elif "/groups/" in url:
            # This is a group
            interest_type = "group"
            # Extract group name from link text or image
            img = link.locator("img").first
            if await img.is_visible():
                name = await img.get_attribute("alt") or ""
        elif "/newsletters/" in url:
            # This is a newsletter
            interest_type = "newsletter"
            # Extract newsletter name
            img = link.locator("img").first
            if await img.is_visible():
                name = await img.get_attribute("alt") or ""
        elif "/school/" in url:
            # This is a school
            interest_type = "school"
            # Extract school name
            img = link.locator("img").first
            if await img.is_visible():
                name = await img.get_attribute("alt") or ""

        # If we couldn't extract a name, skip this item
        if not name:
            return None

        # Extract follower count if available
        followers = None
        try:
            follower_elem = item.locator("span:has-text('followers')").first
            if await follower_elem.is_visible():
                followers_text = await follower_elem.inner_text()
                # Extract number from text like "1,029,906 followers"
                followers = followers_text.split(" ")[0].replace(",", "")
        except Exception:
            pass

        return Interest(name=name, type=interest_type, url=url, followers=followers)

    except Exception:
        return None
