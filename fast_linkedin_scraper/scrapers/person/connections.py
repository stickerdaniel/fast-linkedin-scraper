"""Connection scraping module for LinkedIn profiles."""

from typing import Optional

from playwright.sync_api import Locator, Page
from pydantic import HttpUrl

from ...models.common import Connection
from ...models.person import Person


def scrape_connections(page: Page, person: Person) -> None:
    """Scrape connections information from LinkedIn profile.

    Args:
        page: Playwright page instance
        person: Person model to populate with connection data
    """
    try:
        # Navigate to connections page
        connections_url = (
            "https://www.linkedin.com/mynetwork/invite-connect/connections/"
        )
        page.goto(connections_url)

        # Wait for page to load
        page.wait_for_timeout(3000)  # 3 seconds for connections to load

        # Find the connections container
        connections_container = page.locator(".mn-connections").first
        if not connections_container.is_visible():
            return

        # Get all connection cards
        connection_cards = connections_container.locator(".mn-connection-card").all()

        for card in connection_cards:
            try:
                connection_data = _extract_connection_data(card)
                if connection_data:
                    connection = Connection(
                        name=connection_data.get("name", ""),
                        headline=connection_data.get("occupation", "") or None,
                        url=HttpUrl(connection_data["url"])
                        if connection_data.get("url")
                        else None,
                    )
                    person.add_connection(connection)
            except Exception:
                # Skip this connection if extraction fails
                continue

    except Exception:
        # If connections page not accessible or not found, skip connections scraping
        pass


def _extract_connection_data(card: Locator) -> Optional[dict]:
    """Extract connection data from a connection card."""
    try:
        # Extract URL
        link_elem = card.locator(".mn-connection-card__link").first
        if not link_elem.is_visible():
            return None

        url = link_elem.get_attribute("href")
        if not url:
            return None

        # Extract name
        details_elem = card.locator(".mn-connection-card__details").first
        if not details_elem.is_visible():
            return None

        name_elem = details_elem.locator(".mn-connection-card__name").first
        name = name_elem.inner_text().strip() if name_elem.is_visible() else ""

        # Extract occupation
        occupation_elem = details_elem.locator(".mn-connection-card__occupation").first
        occupation = (
            occupation_elem.inner_text().strip() if occupation_elem.is_visible() else ""
        )

        return {
            "name": name,
            "occupation": occupation,
            "url": url,
        }

    except Exception:
        return None
