"""Configuration settings for the LinkedIn scraper."""

from enum import Flag, auto
from playwright.async_api import ViewportSize


class BrowserConfig:
    """Browser configuration settings."""

    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
    VIEWPORT: ViewportSize = {"width": 1920, "height": 1080}
    TIMEOUT = 15000  # timeout in ms

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


class ScrapingFields(Flag):
    """Fields that can be scraped from LinkedIn profiles."""

    BASIC_INFO = auto()
    EXPERIENCE = auto()
    EDUCATION = auto()
    INTERESTS = auto()
    ACCOMPLISHMENTS = auto()
    CONTACTS = auto()

    # Presets
    MINIMAL = BASIC_INFO
    CAREER = BASIC_INFO | EXPERIENCE | EDUCATION
    ALL = BASIC_INFO | EXPERIENCE | EDUCATION | INTERESTS | ACCOMPLISHMENTS | CONTACTS
