"""Contacts scraping module for LinkedIn profiles."""

import re

from playwright.async_api import Page
from pydantic import HttpUrl

from ...models.common import Connection, ContactInfo
from ...models.person import Person
from ..company.utils import normalize_profile_url


async def scrape_contacts(page: Page, person: Person) -> None:
    """Scrape contact information from LinkedIn profile.

    This includes:
    1. Contact info from the modal (email, website, phone)
    2. Connection count
    3. Actual connections list (only available when viewing own profile)

    Args:
        page: Playwright page instance
        person: Person model to populate with contacts
    """
    # First, get contact info from the modal
    await _scrape_contact_info_modal(page, person)

    # Get connection count
    await _scrape_connection_count(page, person)

    # Try to get actual connections (only works for own profile)
    await _scrape_connections_list(page, person)


async def _scrape_contact_info_modal(page: Page, person: Person) -> None:
    """Scrape contact information from the contact info modal."""
    try:
        # Navigate back to main profile
        await page.goto(str(person.linkedin_url))
        await page.wait_for_timeout(2000)

        # Find and click contact info button
        contact_button = page.locator("a[href*='overlay/contact-info']").first
        if not await contact_button.is_visible():
            # Try alternative selector
            contact_button = page.locator("button:has-text('Contact info')").first

        if await contact_button.is_visible():
            await contact_button.click()
            await page.wait_for_timeout(2000)

            # Get modal content
            modal = page.locator(".artdeco-modal__content").first
            if await modal.is_visible():
                modal_text = await modal.inner_text()

                contact_info = ContactInfo()

                # Extract email
                email_match = re.search(r"Email\s*\n\s*([^\n]+)", modal_text)
                if email_match:
                    email = email_match.group(1).strip()
                    if email and "@" in email:
                        contact_info.email = email

                # Extract website
                website_match = re.search(r"Website\s*\n\s*([^\n]+)", modal_text)
                if website_match:
                    website = website_match.group(1).strip()
                    # Remove any parenthetical info like "(Company)"
                    website = re.sub(r"\s*\([^)]*\)", "", website).strip()
                    if website:
                        # Ensure it has a protocol
                        if not website.startswith(("http://", "https://")):
                            website = f"https://{website}"
                        contact_info.website = website

                # Extract phone if present
                phone_match = re.search(r"Phone\s*\n\s*([^\n]+)", modal_text)
                if phone_match:
                    phone = phone_match.group(1).strip()
                    if phone:
                        contact_info.phone = phone

                # Extract LinkedIn URL (usually shown in modal)
                linkedin_match = re.search(r"linkedin\.com/in/[^\s]+", modal_text)
                if linkedin_match:
                    linkedin_url = linkedin_match.group(0)
                    if not linkedin_url.startswith("http"):
                        linkedin_url = f"https://{linkedin_url}"
                    contact_info.linkedin_url = linkedin_url

                # Set contact info if we found anything
                if contact_info.email or contact_info.phone or contact_info.website:
                    person.set_contact_info(contact_info)

                # Close modal
                close_button = page.locator("button[aria-label*='Dismiss']").first
                if await close_button.is_visible():
                    await close_button.click()
                    await page.wait_for_timeout(1000)

    except Exception:
        pass


async def _scrape_connection_count(page: Page, person: Person) -> None:
    """Extract the connection count from the profile."""
    try:
        # Look for connection count on main profile
        connection_elem = page.locator("span:has-text('connections')").first
        if await connection_elem.is_visible():
            text = await connection_elem.inner_text()
            # Extract number from text like "500+ connections" or "255 connections"
            match = re.search(r"(\d+)\+?\s*connections", text, re.IGNORECASE)
            if match:
                count_str = match.group(1)
                try:
                    count = int(count_str)
                    person.set_connection_count(count)
                except ValueError:
                    pass
    except Exception:
        pass


async def _scrape_connections_list(page: Page, person: Person) -> None:
    """Scrape connections list (mutual connections or own connections)."""
    try:
        # First, go back to the profile page
        await page.goto(str(person.linkedin_url))
        await page.wait_for_timeout(2000)

        # Look for the connections link on the profile (e.g., "452 connections")
        connections_link = None
        navigated_to_connections_page = False

        # Try to find the connections link - it's usually a link with "connections" text
        try:
            # First try the top card area selector
            connections_link = page.locator(
                ".pv-top-card--list a:has-text('connections')"
            ).first

            # If not found or not visible, try other selectors
            if not connections_link or not await connections_link.is_visible():
                # Try to find any link with "connections" text
                all_connection_links = await page.locator(
                    "a:has-text('connections')"
                ).all()
                for link in all_connection_links:
                    if await link.is_visible():
                        text = await link.inner_text()
                        # Skip if it's a "follow this page" link
                        if "follow" not in text.lower():
                            # Check if it looks like a connection count (e.g., "255 connections")
                            if any(char.isdigit() for char in text):
                                connections_link = link
                                break
        except Exception:
            connections_link = None

        if connections_link and await connections_link.is_visible():
            # Click the connections link to see mutual connections or all connections
            await connections_link.click()
            await page.wait_for_timeout(3000)
            navigated_to_connections_page = True
        else:
            # Fallback: attempt to open own connections page (works for logged-in user's profile)
            try:
                await page.goto(
                    "https://www.linkedin.com/mynetwork/invite-connect/connections/"
                )
                # Wait for known containers/selectors to appear
                try:
                    await page.wait_for_selector(
                        ".mn-connection-card, a.mn-connection-card__link", timeout=6000
                    )
                except Exception:
                    # Try via My Network root then click Connections in the Manage my network panel
                    try:
                        await page.goto("https://www.linkedin.com/mynetwork/")
                        await page.wait_for_timeout(2000)
                        # Try several ways to click the Connections entry
                        link_to_connections = None
                        try:
                            link_to_connections = page.locator(
                                "a[href*='mynetwork/invite-connect/connections']"
                            ).first
                            if (
                                link_to_connections
                                and await link_to_connections.is_visible()
                            ):
                                await link_to_connections.click()
                            else:
                                # Button with label text
                                btn = page.locator(
                                    "button[aria-label*='Connections' i]"
                                ).first
                                if btn and await btn.is_visible():
                                    await btn.click()
                                else:
                                    # Fallback to text search on buttons/links
                                    btn2 = page.locator(
                                        "button:has-text('Connections')"
                                    ).first
                                    if btn2 and await btn2.is_visible():
                                        await btn2.click()
                                    else:
                                        a2 = page.locator(
                                            "a:has-text('Connections')"
                                        ).first
                                        if a2 and await a2.is_visible():
                                            await a2.click()
                        except Exception:
                            pass
                        await page.wait_for_selector(
                            ".mn-connection-card, a.mn-connection-card__link",
                            timeout=6000,
                        )
                    except Exception:
                        pass
                await page.wait_for_timeout(1000)
                navigated_to_connections_page = True
            except Exception:
                navigated_to_connections_page = False

        # Verify we are on some connections-like page; otherwise try the network-manager people page
        if not navigated_to_connections_page:
            return
        current_url = page.url.lower()
        if not any(
            x in current_url
            for x in [
                "connections",
                "network-manager/people",
                "search/results/people",
                "mynetwork",
            ]
        ):
            try:
                await page.goto(
                    "https://www.linkedin.com/mynetwork/network-manager/people/"
                )
                await page.wait_for_timeout(2500)
                current_url = page.url.lower()
            except Exception:
                return

        # Scroll to load more connections (reduced for faster execution)
        for _ in range(2):  # Scroll 2 times to load more
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1500)

        # If we're on the My Network connections page, parse structured cards
        if (
            "mynetwork" in current_url
            or page.locator(".mn-connection-card").count() > 0
        ):
            try:
                cards = await page.locator(".mn-connection-card").all()
                seen_urls = set()
                connections_added = 0
                max_connections = 20
                for card in cards:
                    if connections_added >= max_connections:
                        break
                    try:
                        link_el = card.locator(
                            "a.mn-connection-card__link, a[href*='/in/']"
                        ).first
                        href = (
                            await link_el.get_attribute("href")
                            if link_el and await link_el.is_visible()
                            else None
                        )
                        if not href or "/in/" not in href:
                            continue
                        clean_url = normalize_profile_url(href)
                        if clean_url in seen_urls:
                            continue
                        seen_urls.add(clean_url)

                        name = ""
                        headline = ""
                        name_el = card.locator(
                            ".mn-connection-card__name, .update-components-actor__name, .entity-result__title-text a span"
                        ).first
                        if name_el and await name_el.is_visible():
                            name = (await name_el.inner_text()).strip()
                        headline_el = card.locator(
                            ".mn-connection-card__occupation, .entity-result__primary-subtitle"
                        ).first
                        if headline_el and await headline_el.is_visible():
                            headline = (await headline_el.inner_text()).strip()

                        if name:
                            connection = Connection(
                                name=name,
                                headline=headline if headline else None,
                                url=HttpUrl(clean_url),
                            )
                            person.add_connection(connection)
                            connections_added += 1
                    except Exception:
                        continue
                # If we collected any connections, stop here
                if connections_added > 0:
                    return
            except Exception:
                # Fall back to generic parsing
                pass

        # If we're on the network-manager people page, parse list entries
        if "network-manager/people" in current_url:
            try:
                seen_urls = set()
                connections_added = 0
                max_connections = 20
                # Items often rendered as entity results with links to profiles
                items = await page.locator("main a[href*='/in/']").all()
                for link_el in items:
                    if connections_added >= max_connections:
                        break
                    try:
                        href = (
                            await link_el.get_attribute("href")
                            if link_el and await link_el.is_visible()
                            else None
                        )
                        if not href or "/in/" not in href:
                            continue
                        clean_url = normalize_profile_url(href)
                        if clean_url in seen_urls:
                            continue
                        seen_urls.add(clean_url)

                        name = ""
                        headline = ""
                        # Try to extract name from accessible text spans near link
                        name_el = link_el.locator("span[aria-hidden='true']").first
                        if name_el and await name_el.is_visible():
                            candidate = (await name_el.inner_text()).strip()
                            if candidate:
                                name = candidate
                        if not name:
                            candidate = (await link_el.inner_text()).strip()
                            # Clean excessive whitespace/newlines
                            candidate = re.sub(r"\s+", " ", candidate)
                            if 2 <= len(candidate) <= 120:
                                name = candidate

                        # Headline may be in a nearby subtitle element
                        container = link_el
                        for _ in range(4):
                            container = container.locator("..")
                        headline_el = container.locator(
                            ".entity-result__primary-subtitle, .t-14.t-normal"
                        ).first
                        if headline_el and await headline_el.is_visible():
                            headline_candidate = (
                                await headline_el.inner_text()
                            ).strip()
                            if headline_candidate:
                                headline = headline_candidate

                        if name:
                            connection = Connection(
                                name=name,
                                headline=headline if headline else None,
                                url=HttpUrl(clean_url),
                            )
                            person.add_connection(connection)
                            connections_added += 1
                    except Exception:
                        continue

                if connections_added > 0:
                    return
            except Exception:
                pass

        # Generic parsing: collect anchors to profiles and infer name/headline
        connection_links = await page.locator("a[href*='/in/']").all()

        # Track unique profiles to avoid duplicates
        seen_urls = set()
        connections_added = 0
        max_connections = 20  # Limit to avoid too many (reduced for faster execution)

        for link in connection_links:
            if connections_added >= max_connections:
                break

            try:
                href = await link.get_attribute("href")
                if not href or "/in/" not in href:
                    continue

                # Clean URL (remove query parameters)
                clean_url = normalize_profile_url(href)
                if clean_url in seen_urls:
                    continue
                seen_urls.add(clean_url)

                # Try to extract name and headline from structured elements first
                name = ""
                headline = ""
                try:
                    card_parent = link
                    for _ in range(4):
                        card_parent = card_parent.locator("..")
                    # Common selectors on connections page
                    name_el = card_parent.locator(
                        ".mn-connection-card__name, .entity-result__title-text a span, .update-components-actor__name"
                    ).first
                    if name_el and await name_el.is_visible():
                        candidate = (await name_el.inner_text()).strip()
                        if candidate:
                            name = candidate
                    headline_el = card_parent.locator(
                        ".mn-connection-card__occupation, .entity-result__primary-subtitle"
                    ).first
                    if headline_el and await headline_el.is_visible():
                        candidate = (await headline_el.inner_text()).strip()
                        if candidate:
                            headline = candidate
                except Exception:
                    pass

                # Fallback: parse nearby text block if structured elements not found
                if not name:
                    parent = link
                    for _ in range(3):  # Go up max 3 levels
                        parent = parent.locator("..")
                        text = await parent.inner_text()
                        if len(text) > 10 and "\n" in text:
                            break
                    lines = text.split("\n")
                    # Skip common placeholder text
                    skip_phrases = [
                        "Member's name",
                        "Member's occupation",
                        "Status is",
                        "View",
                        "is a mutual connection",
                    ]
                    for line in lines:
                        line = line.strip()
                        if not line or any(skip in line for skip in skip_phrases):
                            continue
                        if not name and len(line) > 2:
                            name = line
                            continue
                        if name and not headline and len(line) > 5:
                            if not line.startswith("View ") or not line.endswith(
                                "'s profile"
                            ):
                                headline = line
                                break

                if name and "/in/" in clean_url:
                    connection = Connection(
                        name=name,
                        headline=headline if headline else None,
                        url=HttpUrl(clean_url),
                    )
                    person.add_connection(connection)
                    connections_added += 1

            except Exception:
                continue

    except Exception:
        pass
