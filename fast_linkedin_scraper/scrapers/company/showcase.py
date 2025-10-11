"""Scraper for showcase pages and affiliated companies."""

from urllib.parse import urljoin

from playwright.async_api import Page
from pydantic import HttpUrl

from ...config import BrowserConfig, CompanyScrapingFields
from ...models.company import Company, CompanySummary
from .utils import clean_company_url


async def scrape_affiliated_pages(
    page: Page,
    company: Company,
    fields: CompanyScrapingFields = CompanyScrapingFields.ALL,
) -> None:
    """Scrape both showcase and affiliated company pages from the unified section.

    LinkedIn now combines showcase pages and affiliated companies under
    a single "Affiliated pages" section. This function handles both types.

    Args:
        page: Authenticated Playwright page instance
        company: Company model to populate with scraped data
        fields: CompanyScrapingFields enum to determine scraping behavior
    """
    # Ensure we're on the about page
    current_url = page.url
    if not current_url.endswith("/about/"):
        base_url = current_url.split("/people")[0].split("/about")[0].rstrip("/")
        about_url = urljoin(base_url + "/", "about/")
        await page.goto(about_url)
        await page.wait_for_timeout(BrowserConfig.WAIT_MEDIUM)

    try:
        # Look for the "Affiliated pages" heading
        affiliated_heading = (
            page.locator("h3").filter(has_text="Affiliated pages").first
        )

        if not await affiliated_heading.is_visible():
            # No affiliated pages section found
            return

        # Find the container that has the list
        # Navigate up from heading to find the parent with ul
        container = affiliated_heading
        for _ in range(5):  # Try up to 5 parent levels
            container = container.locator("..")
            if await container.locator("ul").count() > 0:
                break

        # Get the list
        list_element = container.locator("ul").first
        if not await list_element.is_visible():
            return

        # Step 1: Always scrape sidebar first (provides 3-5 items for MINIMAL config)
        # Get all list items from the sidebar
        items = list_element.locator("li")
        item_count = await items.count()

        for i in range(item_count):
            try:
                item = items.nth(i)

                # Skip if item is not visible
                if not await item.is_visible():
                    continue

                # Get the main link (there are usually 2 - logo and text)
                # Use the text link as it has more information
                links = item.locator("a")
                link_count = await links.count()

                if link_count < 2:
                    continue

                # The second link usually has the text content
                text_link = links.nth(1)
                if not await text_link.is_visible():
                    text_link = links.first  # Fallback to first link

                # Extract URL
                url = await text_link.get_attribute("href")
                if not url:
                    continue

                # Clean and normalize URL
                url = clean_company_url(url)

                # Extract text content
                link_text = (await text_link.inner_text()).strip()
                if not link_text:
                    continue

                # Parse the text (format: Name\nIndustry\nType)
                lines = link_text.split("\n")
                name = lines[0].strip() if lines else ""

                if not name:
                    continue

                # Determine if it's a showcase page or affiliated company
                is_showcase = "Showcase page" in link_text

                # Create the summary object
                page_summary = CompanySummary()
                page_summary.name = name
                if url:
                    page_summary.linkedin_url = HttpUrl(url)

                # Add to appropriate list based on type
                if is_showcase:
                    company.add_showcase_page(page_summary)
                else:
                    # It's an affiliated company (acquisition, subsidiary, etc.)
                    company.add_affiliated_company(page_summary)

            except Exception:
                # Skip problematic items but continue processing others
                continue

        # Step 2: If AFFILIATED_PAGES flag is set, scrape comprehensive modal data
        # This will replace the sidebar data with more complete information
        if CompanyScrapingFields.AFFILIATED_PAGES in fields:
            try:
                # Clear the lists since modal data is more comprehensive
                company.showcase_pages = []
                company.affiliated_companies = []

                # Find and click the "Show all" button
                show_all_btn = page.locator(
                    'button[aria-label="Show all affiliated pages"]'
                )

                if await show_all_btn.count() > 0:
                    await show_all_btn.scroll_into_view_if_needed()
                    await page.wait_for_timeout(BrowserConfig.WAIT_SHORT)

                    if await show_all_btn.is_visible():
                        await show_all_btn.click()
                        await page.wait_for_timeout(BrowserConfig.WAIT_MEDIUM)

                        # Check if modal opened (has role="dialog")
                        modal = page.locator('[role="dialog"]')

                        if await modal.is_visible():
                            # Wait for modal content to load
                            await page.wait_for_timeout(BrowserConfig.WAIT_LONG)

                            # Modal uses a grid layout - find all text links (not logo links)
                            all_links = modal.locator(
                                'a[href*="/company/"], a[href*="/showcase/"]'
                            )
                            link_count = await all_links.count()

                            # Two-pass approach: collect all data first, then merge duplicates
                            # Pass 1: Collect all link data grouped by URL
                            company_data = {}  # {url: {"names": [...], "is_showcase": bool, "is_acquisition": bool}}

                            for i in range(link_count):
                                try:
                                    link = all_links.nth(i)
                                    url = await link.get_attribute("href")

                                    if not url:
                                        continue

                                    # Clean and normalize URL
                                    url = clean_company_url(url)
                                    # Normalize to HTTPS (LinkedIn uses HTTPS, but some links might have HTTP)
                                    url = url.replace("http://", "https://")

                                    # Get link text
                                    link_text = await link.inner_text()
                                    if not link_text or link_text == "Follow":
                                        continue  # Skip logo links and follow buttons

                                    # Check if this is a follower-info-only link
                                    # These have ?showInNetworkFollowers=true query param
                                    is_follower_link = "showInNetworkFollowers" in url

                                    # Initialize data structure for this URL if first time seeing it
                                    if url not in company_data:
                                        company_data[url] = {
                                            "names": [],
                                            "is_showcase": False,
                                            "is_acquisition": False,
                                        }

                                    # Parse lines
                                    lines = [
                                        line.strip()
                                        for line in link_text.split("\n")
                                        if line.strip()
                                    ]

                                    if not lines:
                                        continue

                                    # Store first line as potential name ONLY if NOT a follower link
                                    # Follower links have person names or connection text, not company names
                                    if not is_follower_link:
                                        company_data[url]["names"].append(lines[0])

                                        # Check type indicators (only on company info links)
                                        if "Showcase page" in link_text:
                                            company_data[url]["is_showcase"] = True
                                        if "Acquisition" in link_text:
                                            company_data[url]["is_acquisition"] = True

                                except Exception as e:
                                    # Track error for debugging but continue processing other links
                                    error_key = f"showcase_link_extraction_{i}"
                                    company.scraping_errors[error_key] = str(e)
                                    continue

                            # Pass 2: Process collected data to create CompanySummary objects
                            for url, data in company_data.items():
                                try:
                                    # Pick company name - we've already filtered out person names in Pass 1
                                    # by skipping ?showInNetworkFollowers=true links, so just pick first name
                                    name = data["names"][0] if data["names"] else None

                                    if not name:
                                        continue  # No valid company name found

                                    # Create summary object
                                    page_summary = CompanySummary()
                                    page_summary.name = name
                                    page_summary.linkedin_url = HttpUrl(url)

                                    # Add to appropriate list
                                    if data["is_showcase"]:
                                        company.add_showcase_page(page_summary)
                                    elif data["is_acquisition"] or "/company/" in url:
                                        company.add_affiliated_company(page_summary)

                                except Exception:
                                    continue
            except Exception:
                # If modal scraping fails, sidebar data is preserved as fallback
                pass

    except Exception:
        # Section not found or error accessing it
        pass


async def scrape_showcase_pages(
    page: Page,
    company: Company,
    fields: CompanyScrapingFields = CompanyScrapingFields.ALL,
) -> None:
    """Legacy function for backward compatibility - delegates to unified function.

    Args:
        page: Authenticated Playwright page instance
        company: Company model to populate with scraped data
        fields: CompanyScrapingFields enum to determine scraping behavior
    """
    # LinkedIn now combines showcase and affiliated pages
    # The unified function will handle both
    await scrape_affiliated_pages(page, company, fields)


async def scrape_affiliated_companies(
    page: Page,
    company: Company,
    fields: CompanyScrapingFields = CompanyScrapingFields.ALL,
) -> None:
    """Legacy function for backward compatibility - delegates to unified function.

    Args:
        page: Authenticated Playwright page instance
        company: Company model to populate with scraped data
        fields: CompanyScrapingFields enum to determine scraping behavior
    """
    # LinkedIn now combines showcase and affiliated pages
    # The unified function will handle both
    await scrape_affiliated_pages(page, company, fields)
