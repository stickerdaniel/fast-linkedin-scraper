"""Main company profile scraper using Playwright."""

import re
from urllib.parse import urljoin

from playwright.async_api import Page
from pydantic import HttpUrl

from ...config import BrowserConfig, CompanyScrapingFields
from ...models.company import Company
from .about import scrape_company_details
from .employees import scrape_employees
from .showcase import scrape_affiliated_pages


class CompanyScraper:
    """Scraper for LinkedIn company profiles."""

    def __init__(self, page: Page):
        """Initialize the scraper with a Playwright page.

        Args:
            page: Authenticated Playwright page instance
        """
        self.page = page

    async def scrape_profile(
        self,
        url: str,
        fields: CompanyScrapingFields = CompanyScrapingFields.MINIMAL,
        max_pages: int = 1,
    ) -> Company:
        """Scrape a LinkedIn company profile.

        Args:
            url: LinkedIn company URL as string
            fields: CompanyScrapingFields enum specifying which fields to scrape
            max_pages: Maximum number of employee pages to scrape (0 = no employees)

        Returns:
            Company model with scraped data
        """
        # Validate URL
        linkedin_url = HttpUrl(url)

        # Ensure we're going to the about page directly
        url_str = str(linkedin_url)
        if not url_str.endswith("/about/"):
            # Ensure base URL ends with /
            base_url = url_str.rstrip("/") + "/"
            url_str = urljoin(base_url, "about/")

        # Navigate directly to company about page
        await self.page.goto(url_str)

        # Wait for initial content to load
        await self.page.wait_for_timeout(BrowserConfig.WAIT_MEDIUM)

        # Initialize Company model
        company = Company(linkedin_url=linkedin_url)

        # Always scrape all available data from the /about page
        # This includes basic info and all details since we're already on the page
        try:
            await self._scrape_basic_info(company)
            await self.page.wait_for_timeout(BrowserConfig.WAIT_SHORT)
        except Exception as e:
            company.scraping_errors["basic_info"] = str(e)

        try:
            await scrape_company_details(self.page, company)
            await self.page.wait_for_timeout(BrowserConfig.WAIT_SHORT)
        except Exception as e:
            company.scraping_errors["details"] = str(e)

        # LinkedIn now combines showcase and affiliated pages in one section
        # So we only need to scrape once if either flag is set
        if (
            CompanyScrapingFields.SHOWCASE_PAGES in fields
            or CompanyScrapingFields.AFFILIATED_COMPANIES in fields
        ):
            try:
                await scrape_affiliated_pages(self.page, company)
                await self.page.wait_for_timeout(BrowserConfig.WAIT_SHORT)
            except Exception as e:
                company.scraping_errors["affiliated_pages"] = str(e)

        # Scrape employees if max_pages > 0
        if max_pages > 0:
            try:
                await scrape_employees(self.page, company, max_pages)
                await self.page.wait_for_timeout(BrowserConfig.WAIT_SHORT)
            except Exception as e:
                company.scraping_errors["employees"] = str(e)

        return company

    async def _scrape_basic_info(self, company: Company) -> None:
        """Scrape basic company information (name, industry, size) from about page header."""
        # Get company name from h1 element
        try:
            # Wait for h1 to be visible
            await self.page.wait_for_selector(
                "h1", state="visible", timeout=BrowserConfig.WAIT_TIMEOUT
            )
            name_element = self.page.locator("h1").first
            if await name_element.is_visible():
                company.name = (await name_element.inner_text()).strip()
        except Exception:
            # h1 might not be visible yet, skip
            pass

        # Get industry from the header - it's right after the company name
        try:
            # The industry appears after · in the header section
            industry_element = self.page.locator("text='· Software Development'").first
            if not await industry_element.is_visible():
                # Try a more generic approach
                industry_element = (
                    self.page.locator("h1")
                    .locator("..")
                    .locator("..")
                    .locator("text=/·\\s+[A-Za-z]/")
                    .first
                )

            if await industry_element.is_visible():
                text = await industry_element.inner_text()
                # Extract the part after ·
                if "·" in text:
                    industry = text.split("·")[1].strip()
                    # Make sure it's the industry and not something else
                    if industry and not any(
                        x in industry.lower()
                        for x in [
                            "followers",
                            "employees",
                            "ca",
                            "ny",
                            "wa",
                            "mountain",
                        ]
                    ):
                        company.industry = industry
        except Exception:
            pass

        # Get company size from the "10K+ employees" link in header
        try:
            # Look for the employees link which contains the size info
            employees_link = self.page.locator("a:has-text('employees')").first
            if await employees_link.is_visible():
                item_text = await employees_link.inner_text()
                if "employees" in item_text.lower():
                    # Clean up the text (remove leading ·)
                    clean_text = item_text.replace("·", "").strip()
                    company.company_size = clean_text
                    # Try to extract headcount number
                    numbers = re.findall(r"[\d,]+", clean_text)
                    if numbers:
                        try:
                            # Take the first number, handle "10K+" format
                            num_str = numbers[0].replace(",", "")
                            if "k" in clean_text.lower():
                                # Convert K notation using constant
                                from .utils import K_NOTATION_MULTIPLIER

                                company.headcount = int(
                                    float(num_str) * K_NOTATION_MULTIPLIER
                                )
                            else:
                                company.headcount = int(num_str)
                        except (ValueError, IndexError):
                            pass
        except Exception:
            pass
