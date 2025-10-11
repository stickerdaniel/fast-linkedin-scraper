"""Scraper for company employees with pagination support."""

import re
from urllib.parse import urljoin

from playwright.async_api import Page, TimeoutError
from pydantic import HttpUrl

from ...config import BrowserConfig
from ...models.company import Company, Employee
from .utils import normalize_profile_url


async def scrape_employees(page: Page, company: Company, max_pages: int = 1) -> None:
    """Scrape company employees from the people page.

    Args:
        page: Authenticated Playwright page instance
        company: Company model to populate with scraped data
        max_pages: Maximum number of pages to scrape (default 1, ~10 employees per page)
    """
    # Click on the employees link to get to the search results page
    # This link should be present on the /people page
    current_url = page.url

    # If we're on /about page, navigate to /people first
    if "/about" in current_url:
        base_url = current_url.split("/about")[0].rstrip("/")
        people_url = urljoin(base_url + "/", "people/")
        await page.goto(people_url)
        await page.wait_for_timeout(
            BrowserConfig.WAIT_LONG
        )  # Wait for people page to load

    # Try to click on the employees link to get to actual employee listings
    try:
        # Look for the "10K+ employees" type link that leads to search results
        employees_link = page.locator('a:has-text("employees")').first
        if await employees_link.is_visible():
            await employees_link.click()
            await page.wait_for_timeout(
                BrowserConfig.WAIT_LONG
            )  # Wait for search results to load
    except Exception:
        # If we can't find the link, we might already be on search page or it failed
        pass

    processed_urls = set()
    page_num = 1

    # Check if we're on the search results page
    if "/search/results/people/" in page.url:
        # We're on the search results page, scrape from here
        while page_num <= max_pages:
            # Wait for search results to load
            try:
                await page.wait_for_selector(
                    "main [role='list'] > li", timeout=BrowserConfig.WAIT_TIMEOUT
                )
            except TimeoutError:
                # No results found
                break

            # Get all employee cards from search results
            employee_items = page.locator("main [role='list'] > li")
            item_count = await employee_items.count()

            if item_count == 0:
                break

            # Process each employee item
            for i in range(item_count):
                try:
                    item = employee_items.nth(i)

                    # Skip non-profile items (ads, etc.)
                    link_check = item.locator("a[href*='/in/']").first
                    if not await link_check.count() > 0:
                        continue

                    # Extract employee information
                    employee = Employee()

                    # Get profile URL and name
                    link_element = item.locator("a[href*='/in/']").first
                    if await link_element.is_visible():
                        profile_url = await link_element.get_attribute("href")
                        if profile_url:
                            # Normalize the URL to prevent duplicates
                            normalized_url = normalize_profile_url(profile_url)

                            # Skip if we've already processed this employee
                            if normalized_url in processed_urls:
                                continue

                            processed_urls.add(normalized_url)
                            employee.linkedin_url = HttpUrl(normalized_url)

                            # Try multiple strategies to get the name
                            name_text = None

                            # Strategy 1: Look for the actual visible name text in a span with specific attributes
                            name_element = item.locator(
                                "span[aria-hidden='true']"
                            ).first
                            if await name_element.count() > 0:
                                name_text = await name_element.inner_text()

                            # Strategy 2: If that didn't work, try any span that looks like a name
                            if not name_text:
                                # Get all text content and look for a name-like pattern
                                all_text = await item.inner_text()
                                lines = all_text.split("\n")
                                # The first non-empty line is often the name
                                for line in lines:
                                    line = line.strip()
                                    if line and not any(
                                        x in line.lower()
                                        for x in [
                                            "connect",
                                            "message",
                                            "degree",
                                            "•",
                                            "follow",
                                        ]
                                    ):
                                        name_text = line
                                        break

                            if name_text:
                                # Clean name - sometimes has "View X's profile" text
                                name = name_text.strip()
                                if "View" in name and "profile" in name:
                                    # Extract just the name part
                                    name_match = re.search(
                                        r"View (.+?)'s profile", name
                                    )
                                    if name_match:
                                        name = name_match.group(1)
                                if name and len(name) > 0:
                                    employee.name = name

                    # Get employee headline/position
                    # The job title is in a div with specific styling classes
                    position_element = item.locator("div.t-14.t-black.t-normal").first
                    if await position_element.count() > 0:
                        headline = (await position_element.inner_text()).strip()
                        # Clean the headline - remove any extraneous text
                        if headline and headline != employee.name:
                            # Sometimes the headline includes location or other info on same line
                            # Take only the job title part (before any location indicators)
                            headline = (
                                headline.split(" at ")[0].strip()
                                if " at " in headline
                                else headline
                            )
                            employee.headline = headline

                    # Add employee to company if we got at least a name
                    if employee.name:
                        company.add_employee(employee)

                except Exception as e:
                    # Track error for debugging but continue processing other employees
                    error_key = f"employee_extraction_{i}"
                    company.scraping_errors[error_key] = str(e)
                    continue

            # Try to go to next page if we haven't reached max_pages
            if page_num < max_pages:
                try:
                    # Look for Next button that is visible and enabled
                    next_button = page.locator(
                        'button:has-text("Next"):not([disabled])'
                    ).last
                    # Wait for button to be visible and clickable, with a short timeout
                    await next_button.wait_for(state="visible", timeout=2000)
                    await next_button.click()
                    await page.wait_for_timeout(BrowserConfig.WAIT_LONG)
                    page_num += 1
                except (TimeoutError, Exception):
                    # No more pages or button not clickable
                    break
            else:
                break
    else:
        # We're still on /people page, not search results
        # This might be a restricted view showing "People you may know" instead
        # In this case, we can't scrape employees
        pass
