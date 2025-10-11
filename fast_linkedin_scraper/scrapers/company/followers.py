"""Scraper for company followers (people who follow the company)."""

from urllib.parse import urljoin

from playwright.async_api import Page
from pydantic import HttpUrl

from ...config import BrowserConfig
from ...models.company import Company, Follower


async def scrape_company_followers(
    page: Page,
    company: Company,
    base_url: str,
) -> None:
    """Scrape people who follow the company.

    Args:
        page: Authenticated Playwright page instance
        company: Company model to populate with follower data
        base_url: Base company URL (will add ?showInNetworkFollowers=true)
    """
    # Construct follower URL
    clean_base_url = str(base_url).rstrip("/")
    if "/about" in clean_base_url:
        clean_base_url = clean_base_url.split("/about")[0]

    follower_url = f"{clean_base_url}/?showInNetworkFollowers=true"

    try:
        # Navigate to follower page
        await page.goto(follower_url)
        await page.wait_for_timeout(BrowserConfig.WAIT_MEDIUM)

        # Wait for modal to appear
        modal = page.locator('[role="dialog"]')
        if not await modal.is_visible():
            return

        await page.wait_for_timeout(BrowserConfig.WAIT_MEDIUM)

        # Keep clicking "Show more results" until all followers are loaded
        while True:
            try:
                show_more_btn = modal.locator('button:has-text("Show more results")')
                if await show_more_btn.count() > 0 and await show_more_btn.is_visible():
                    await show_more_btn.click()
                    await page.wait_for_timeout(BrowserConfig.WAIT_MEDIUM)
                else:
                    break
            except Exception:
                break

        # Get all follower list items
        items = modal.locator("li")
        item_count = await items.count()

        for i in range(item_count):
            try:
                item = items.nth(i)

                # Find profile link
                link = item.locator('a[href*="/in/"]').first
                if not await link.is_visible():
                    continue

                # Get URL
                url = await link.get_attribute("href")
                if not url:
                    continue

                # Normalize URL
                if not url.startswith("http"):
                    url = urljoin("https://www.linkedin.com", url)
                url = url.split("?")[0].rstrip("/")

                # Get all text divs inside the link
                divs = link.locator("div")
                div_count = await divs.count()

                texts = []
                for j in range(div_count):
                    div_text = await divs.nth(j).inner_text()
                    if div_text and div_text.strip():
                        texts.append(div_text.strip())

                # Parse name and headline from text array
                # Based on investigation: index 2 is name, index 4 is headline
                name = None
                headline = None

                if len(texts) >= 3:
                    # Find the name (usually the third unique text element)
                    # Skip connection degree texts like "1st degree connection"
                    for text in texts:
                        if (
                            "degree connection" not in text.lower()
                            and "· 1st" not in text
                            and "· 2nd" not in text
                            and "· 3rd" not in text
                            and len(text.split()) <= 5  # Names are typically short
                        ):
                            name = text
                            break

                if len(texts) >= 5:
                    # Headline is typically the last text element (longer description)
                    # Find the longest text that's not the name or connection info
                    for text in reversed(texts):
                        if (
                            text != name
                            and "degree connection" not in text.lower()
                            and "· 1st" not in text
                            and len(text) > 10  # Headlines are usually longer
                        ):
                            headline = text
                            break

                if not name:
                    continue

                # Create follower object
                follower = Follower(
                    name=name,
                    headline=headline,
                    linkedin_url=HttpUrl(url),
                )

                company.followers.append(follower)

            except Exception:
                continue

    except Exception:
        # If follower scraping fails, just skip it
        pass
