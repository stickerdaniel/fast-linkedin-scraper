"""Configuration settings for the LinkedIn scraper."""

from enum import Flag, auto
from playwright.async_api import ViewportSize


class BrowserConfig:
    """Browser configuration settings."""

    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
    VIEWPORT: ViewportSize = {"width": 1920, "height": 1080}
    TIMEOUT = 15000  # timeout in ms

    # Wait time constants (in milliseconds)
    WAIT_SHORT = 1000  # 1 second
    WAIT_MEDIUM = 2000  # 2 seconds
    WAIT_LONG = 3000  # 3 seconds
    WAIT_TIMEOUT = 5000  # 5 seconds

    CHROME_ARGS = [
        "--no-sandbox",
        "--disable-blink-features=AutomationControlled",
        "--disable-dev-shm-usage",
        "--disable-web-security",
        "--disable-features=VizDisplayCompositor",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
    ]


class PersonScrapingFields(Flag):
    """Fields that can be scraped from LinkedIn person profiles.

    Each field corresponds to specific profile sections and navigation requirements:

    - BASIC_INFO: Name, headline, location, about (scraped from main page, ~2s)
    - EXPERIENCE: Work history (navigates to /details/experience, ~5s)
    - EDUCATION: Education history (navigates to /details/education, ~5s)
    - INTERESTS: Following/interests (navigates to /details/interests, ~5s)
    - ACCOMPLISHMENTS: Honors and languages (multiple navigations, ~6s)
    - CONTACTS: Contact info and connections (modal + navigation, ~8s)
    """

    BASIC_INFO = auto()  # Name, headline, location, about
    EXPERIENCE = auto()  # Work history and employment details
    EDUCATION = auto()  # Educational background and degrees
    INTERESTS = auto()  # Following companies/people and interests
    ACCOMPLISHMENTS = auto()  # Honors, awards, and languages
    CONTACTS = auto()  # Contact information and connections

    # Presets for common use cases
    MINIMAL = BASIC_INFO  # Fastest: basic info only (~2s)
    CAREER = BASIC_INFO | EXPERIENCE | EDUCATION  # Career-focused (~12s)
    ALL = (
        BASIC_INFO | EXPERIENCE | EDUCATION | INTERESTS | ACCOMPLISHMENTS | CONTACTS
    )  # Complete profile (~30s)


class CompanyScrapingFields(Flag):
    """Navigation control flags for LinkedIn company profiles.

    These flags control additional page navigations beyond the default /about page.
    All available data from visited pages is always scraped.

    - SHOWCASE_PAGES: Navigate to showcase company pages (~3s per page)
    - AFFILIATED_COMPANIES: Navigate to affiliated company pages (~3s per page)

    Note: Employee scraping is controlled via the max_pages parameter, not a field flag.
    The /about page (containing name, industry, size, website, HQ, specialties, etc.) is always visited.
    """

    SHOWCASE_PAGES = auto()  # Navigate to showcase company pages
    AFFILIATED_COMPANIES = auto()  # Navigate to affiliated company pages

    # Presets for common use cases
    MINIMAL = 0  # Just /about page - fastest (~3s)
    ALL = SHOWCASE_PAGES | AFFILIATED_COMPANIES  # All additional navigations (~9s+)
