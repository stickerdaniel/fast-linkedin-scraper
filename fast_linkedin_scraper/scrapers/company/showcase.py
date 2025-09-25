"""Scraper for showcase pages and affiliated companies."""

from playwright.async_api import Page

from ...models.company import Company, CompanySummary


async def scrape_affiliated_pages(page: Page, company: Company) -> None:
    """Scrape both showcase and affiliated company pages from the unified section.

    LinkedIn now combines showcase pages and affiliated companies under
    a single "Affiliated pages" section. This function handles both types.

    Args:
        page: Authenticated Playwright page instance
        company: Company model to populate with scraped data
    """
    # Ensure we're on the about page
    current_url = page.url
    if not current_url.endswith("/about/"):
        about_url = (
            current_url.split("/people")[0].split("/about")[0].rstrip("/") + "/about/"
        )
        await page.goto(about_url)
        await page.wait_for_timeout(2000)

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

        # Check if there's a "Show all" button and click it
        try:
            show_all_btn = container.locator("button").filter(
                has_text="Show all affiliated"
            )
            if await show_all_btn.is_visible():
                await show_all_btn.click()
                await page.wait_for_timeout(1000)
        except Exception:
            pass

        # Get all list items
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

                if not url.startswith("http"):
                    url = "https://www.linkedin.com" + url
                url = url.split("?")[0]  # Remove query parameters

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

                # Extract followers if present (not always available)
                followers = None
                for line in lines:
                    if "follower" in line.lower():
                        followers = line.strip()
                        break

                # Create the summary object
                page_summary = CompanySummary()
                page_summary.name = name
                page_summary.linkedin_url = url
                if followers:
                    page_summary.followers = followers

                # Add to appropriate list based on type
                if is_showcase:
                    company.add_showcase_page(page_summary)
                else:
                    # It's an affiliated company (acquisition, subsidiary, etc.)
                    company.add_affiliated_company(page_summary)

            except Exception:
                # Skip problematic items but continue processing others
                continue

    except Exception:
        # Section not found or error accessing it
        pass


async def scrape_showcase_pages(page: Page, company: Company) -> None:
    """Legacy function for backward compatibility - delegates to unified function.

    Args:
        page: Authenticated Playwright page instance
        company: Company model to populate with scraped data
    """
    # LinkedIn now combines showcase and affiliated pages
    # The unified function will handle both
    await scrape_affiliated_pages(page, company)


async def scrape_affiliated_companies(page: Page, company: Company) -> None:
    """Legacy function for backward compatibility - delegates to unified function.

    Args:
        page: Authenticated Playwright page instance
        company: Company model to populate with scraped data
    """
    # LinkedIn now combines showcase and affiliated pages
    # The unified function will handle both
    await scrape_affiliated_pages(page, company)
