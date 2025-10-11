"""Scraper for company about section and detailed information."""

import re

from playwright.async_api import Page

from ...models.company import Company


async def scrape_company_details(page: Page, company: Company) -> None:
    """Scrape detailed company information from the about page.

    Args:
        page: Authenticated Playwright page instance (should already be on /about page)
        company: Company model to populate with scraped data
    """
    # We should already be on the /about page

    # Get the company name from h1 if not already set
    if not company.name:
        try:
            name_element = page.locator("h1").first
            if await name_element.is_visible():
                company.name = (await name_element.inner_text()).strip()
        except Exception:
            pass

    # Try to find the overview section
    try:
        # Look for the Overview heading and get its parent section
        overview_heading = page.locator("h2:has-text('Overview')")
        if await overview_heading.is_visible():
            # Get the next sibling paragraph which contains the about text
            overview_paragraph = overview_heading.locator("~ p").first
            if await overview_paragraph.is_visible():
                about_text = await overview_paragraph.inner_text()
                if about_text:
                    company.about_us = about_text.strip()
    except Exception:
        pass

    # Scrape the detailed information from the grid
    # Handle dt/dd pairs where some dt elements have multiple dd elements
    try:
        # Get all dt elements and their following dd siblings
        dt_elements = page.locator("dt")
        dt_count = await dt_elements.count()

        for i in range(dt_count):
            try:
                dt_element = dt_elements.nth(i)
                label_text = (await dt_element.inner_text()).strip()

                # Get all dd elements that follow this dt until the next dt
                # Use JavaScript to find the correct dd elements for this dt
                dd_elements = await page.evaluate(
                    """(dtIndex) => {
                        const dts = Array.from(document.querySelectorAll('dt'));
                        const dt = dts[dtIndex];
                        if (!dt) return [];

                        const values = [];
                        let sibling = dt.nextElementSibling;

                        while (sibling && sibling.tagName === 'DD') {
                            values.push(sibling.innerText.trim());
                            sibling = sibling.nextElementSibling;
                        }

                        return values;
                    }""",
                    i,
                )

                if not dd_elements:
                    continue

                # Join multiple dd values if present
                value_text = dd_elements[0] if dd_elements else ""

                if label_text == "Website":
                    if value_text:
                        company.website = value_text
                elif label_text == "Industry":
                    company.industry = value_text
                elif label_text == "Company size":
                    # Company size has two dd elements: employee count and associated members
                    if dd_elements:
                        company.company_size = dd_elements[
                            0
                        ]  # First dd is employee count
                        # Try to extract headcount from the employee count
                        numbers = re.findall(r"[\d,]+", dd_elements[0])
                        if numbers:
                            try:
                                # For "10,001+" format, extract the number
                                headcount_str = (
                                    numbers[0].replace(",", "").replace("+", "")
                                )
                                company.headcount = int(headcount_str)
                            except (ValueError, IndexError):
                                pass

                        # If there's a second dd with associated members, we could store it
                        # but for now we'll just use the employee count
                elif label_text == "Headquarters":
                    company.headquarters = value_text
                elif label_text == "Specialties":
                    # Split specialties by comma
                    specialties = [
                        s.strip() for s in value_text.split(",") if s.strip()
                    ]
                    company.specialties = specialties
            except Exception:
                # Skip errors in individual dt/dd pairs
                continue
    except Exception:
        pass

    # Try to get employee count from the "See all X employees on LinkedIn" link
    try:
        employee_link = page.locator("a").filter(has_text="employees on LinkedIn")
        if await employee_link.is_visible():
            link_text = await employee_link.inner_text()
            match = re.search(r"See all ([\d,]+) employees", link_text)
            if match:
                try:
                    company.headcount = int(match.group(1).replace(",", ""))
                except ValueError:
                    pass
    except Exception:
        pass
