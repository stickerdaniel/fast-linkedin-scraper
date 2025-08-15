"""Accomplishments scraping module for LinkedIn profiles."""

import os
from typing import Optional

from playwright.async_api import Page, Locator
from pydantic import HttpUrl

from ...models.person import Person, Honor, Language
from ..utils import scroll_to_bottom


async def scrape_accomplishments(page: Page, person: Person) -> None:
    """Scrape accomplishments information from LinkedIn profile.

    This includes honors/awards, languages, and potentially other accomplishment types.

    Args:
        page: Playwright page instance
        person: Person model to populate with accomplishments
    """
    # First try to scrape from main profile page (some accomplishments are shown there)
    await _scrape_main_profile_accomplishments(page, person)

    # Then try detail pages for more complete information
    await _scrape_honors_details(page, person)
    await _scrape_languages_details(page, person)


async def _scrape_main_profile_accomplishments(page: Page, person: Person) -> None:
    """Scrape accomplishments visible on the main profile page."""
    try:
        # Navigate back to main profile if needed
        await page.goto(str(person.linkedin_url))
        await page.wait_for_timeout(2000)

        # Scroll to load all sections
        await scroll_to_bottom(page)
        await page.wait_for_timeout(2000)

        # Look for honors & awards section
        try:
            honors_section = page.locator("section:has-text('Honors & awards')").first
            if await honors_section.is_visible():
                items = await honors_section.locator("li").all()
                for item in items[:10]:  # Limit to first 10 to avoid too many
                    honor = await _extract_honor_from_main_profile(item)
                    if honor:
                        person.add_honor(honor)
        except Exception:
            pass

        # Look for languages section
        try:
            languages_section = page.locator("section:has-text('Languages')").first
            if await languages_section.is_visible():
                items = await languages_section.locator("li").all()
                for item in items[:10]:  # Limit to first 10
                    language = await _extract_language_from_main_profile(item)
                    if language:
                        # Check if not already added (to avoid duplicates)
                        if not any(
                            lang.name == language.name for lang in person.languages
                        ):
                            person.add_language(language)
        except Exception:
            pass

    except Exception:
        pass


async def _scrape_honors_details(page: Page, person: Person) -> None:
    """Scrape honors/awards from the details page."""
    try:
        honors_url = os.path.join(str(person.linkedin_url), "details/honors")
        await page.goto(honors_url)
        await page.wait_for_timeout(2000)

        # Check if page exists
        if "Page not found" in await page.content() or "/404/" in page.url:
            return

        main_content = page.locator("main").first
        if not await main_content.is_visible():
            return

        # Get all list containers
        list_containers = await main_content.locator(".pvs-list__container").all()

        for list_container in list_containers:
            items = await list_container.locator(".pvs-list__paged-list-item").all()

            for item in items[:20]:  # Limit to prevent too many
                honor = await _extract_honor_from_details(item)
                if honor:
                    # Check if not already added from main profile
                    if not any(h.title == honor.title for h in person.honors):
                        person.add_honor(honor)

    except Exception:
        pass


async def _scrape_languages_details(page: Page, person: Person) -> None:
    """Scrape languages from the details page."""
    try:
        languages_url = os.path.join(str(person.linkedin_url), "details/languages")
        await page.goto(languages_url)
        await page.wait_for_timeout(2000)

        # Check if page exists
        if "Page not found" in await page.content() or "/404/" in page.url:
            return

        main_content = page.locator("main").first
        if not await main_content.is_visible():
            return

        # Get all list containers
        list_containers = await main_content.locator(".pvs-list__container").all()

        for list_container in list_containers:
            items = await list_container.locator(".pvs-list__paged-list-item").all()

            for item in items[:20]:  # Limit to prevent too many
                language = await _extract_language_from_details(item)
                if language:
                    # Check if not already added from main profile
                    if not any(lang.name == language.name for lang in person.languages):
                        person.add_language(language)

    except Exception:
        pass


async def _extract_honor_from_main_profile(item: Locator) -> Optional[Honor]:
    """Extract honor/award from main profile list item."""
    try:
        # Get title
        title_elem = item.locator("div[aria-hidden='true'] span").first
        title = await title_elem.inner_text() if await title_elem.is_visible() else ""

        if not title:
            return None

        # Get issuer and date info
        issuer = ""
        date = ""
        issuer_elem = item.locator("span:has-text('Issued by')").first
        if await issuer_elem.is_visible():
            issuer_text = await issuer_elem.inner_text()
            # Parse out institution name from "Issued by X · Date"
            if "Issued by" in issuer_text:
                parts = issuer_text.replace("Issued by", "").split("·")
                if parts:
                    issuer = parts[0].strip()
                    if len(parts) > 1:
                        date = parts[1].strip()

        return Honor(
            title=title,
            issuer=issuer if issuer else None,
            date=date if date else None,
        )

    except Exception:
        return None


async def _extract_honor_from_details(item: Locator) -> Optional[Honor]:
    """Extract honor/award from details page list item."""
    try:
        container = item.locator("div[data-view-name='profile-component-entity']").first
        if not await container.is_visible():
            return None

        # Get the details section (usually second div)
        parts = await container.locator("> div").all()
        if len(parts) < 2:
            return None

        details = parts[1]

        # Get title
        title_elem = details.locator("span[aria-hidden='true']").first
        title = await title_elem.inner_text() if await title_elem.is_visible() else ""

        if not title:
            return None

        # Get institution
        issuer = ""
        date = ""
        associated_with = ""

        # Try "Issued by" first
        issuer_elem = details.locator("span:has-text('Issued by')").first
        if await issuer_elem.is_visible():
            issuer_text = await issuer_elem.inner_text()
            if "Issued by" in issuer_text:
                parts = issuer_text.replace("Issued by", "").split("·")
                if parts:
                    issuer = parts[0].strip()
                    if len(parts) > 1:
                        date = parts[1].strip()

        # Try "Associated with"
        assoc_elem = details.locator("span:has-text('Associated with')").first
        if await assoc_elem.is_visible():
            assoc_text = await assoc_elem.inner_text()
            if "Associated with" in assoc_text:
                associated_with = assoc_text.replace("Associated with", "").strip()

        # Try to get document URL
        document_url = None
        try:
            links = await container.locator("a").all()
            for link in links:
                if await link.is_visible():
                    href = await link.get_attribute("href")
                    if href:
                        # Check for document/media links
                        if "single-media-viewer" in href or "type=DOCUMENT" in href:
                            # Document/media link (e.g., certificate PDF)
                            document_url = href
                            break
        except Exception:
            pass

        return Honor(
            title=title,
            issuer=issuer if issuer else None,
            date=date if date else None,
            associated_with=associated_with if associated_with else None,
            document_url=HttpUrl(document_url) if document_url else None,
        )

    except Exception:
        return None


async def _extract_language_from_main_profile(item: Locator) -> Optional[Language]:
    """Extract language from main profile list item."""
    try:
        text = await item.inner_text()
        if not text:
            return None

        # Parse language and proficiency
        lines = text.split("\n")
        if len(lines) >= 2:
            # First line is usually the language name (appears twice)
            language = lines[0].strip()
            # Look for proficiency level
            proficiency = ""
            for line in lines:
                if "proficiency" in line.lower():
                    proficiency = line.strip()
                    break

            if language:
                return Language(
                    name=language, proficiency=proficiency if proficiency else None
                )

        return None

    except Exception:
        return None


async def _extract_language_from_details(item: Locator) -> Optional[Language]:
    """Extract language from details page list item."""
    try:
        # Get language name
        name_elem = item.locator("span[aria-hidden='true']").first
        language = await name_elem.inner_text() if await name_elem.is_visible() else ""

        if not language:
            return None

        # Get proficiency level
        proficiency = ""
        prof_elem = item.locator("span.t-14").first
        if await prof_elem.is_visible():
            prof_text = await prof_elem.inner_text()
            # Clean up duplicate text that sometimes appears
            lines = prof_text.split("\n")
            if lines:
                proficiency = lines[0].strip()

        return Language(name=language, proficiency=proficiency if proficiency else None)

    except Exception:
        return None
