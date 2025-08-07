"""Accomplishments scraping module for LinkedIn profiles."""

import os
from typing import Optional

from playwright.sync_api import Page, Locator
from pydantic import HttpUrl

from ...models.person import Person, Accomplishment
from ..utils import scroll_to_bottom


def scrape_accomplishments(page: Page, person: Person) -> None:
    """Scrape accomplishments information from LinkedIn profile.

    This includes honors/awards, languages, and potentially other accomplishment types.

    Args:
        page: Playwright page instance
        person: Person model to populate with accomplishments
    """
    # First try to scrape from main profile page (some accomplishments are shown there)
    _scrape_main_profile_accomplishments(page, person)

    # Then try detail pages for more complete information
    _scrape_honors_details(page, person)
    _scrape_languages_details(page, person)


def _scrape_main_profile_accomplishments(page: Page, person: Person) -> None:
    """Scrape accomplishments visible on the main profile page."""
    try:
        # Navigate back to main profile if needed
        page.goto(str(person.linkedin_url))
        page.wait_for_timeout(2000)

        # Scroll to load all sections
        scroll_to_bottom(page)
        page.wait_for_timeout(2000)

        # Look for honors & awards section
        try:
            honors_section = page.locator("section:has-text('Honors & awards')").first
            if honors_section.is_visible():
                items = honors_section.locator("li").all()
                for item in items[:10]:  # Limit to first 10 to avoid too many
                    accomplishment = _extract_honor_from_main_profile(item)
                    if accomplishment:
                        person.add_accomplishment(accomplishment)
        except Exception:
            pass

        # Look for languages section
        try:
            languages_section = page.locator("section:has-text('Languages')").first
            if languages_section.is_visible():
                items = languages_section.locator("li").all()
                for item in items[:10]:  # Limit to first 10
                    accomplishment = _extract_language_from_main_profile(item)
                    if accomplishment:
                        # Check if not already added (to avoid duplicates)
                        if not any(
                            a.title == accomplishment.title and a.category == "Language"
                            for a in person.accomplishments
                        ):
                            person.add_accomplishment(accomplishment)
        except Exception:
            pass

    except Exception:
        pass


def _scrape_honors_details(page: Page, person: Person) -> None:
    """Scrape honors/awards from the details page."""
    try:
        honors_url = os.path.join(str(person.linkedin_url), "details/honors")
        page.goto(honors_url)
        page.wait_for_timeout(2000)

        # Check if page exists
        if "Page not found" in page.content() or "/404/" in page.url:
            return

        main_content = page.locator("main").first
        if not main_content.is_visible():
            return

        # Get all list containers
        list_containers = main_content.locator(".pvs-list__container").all()

        for list_container in list_containers:
            items = list_container.locator(".pvs-list__paged-list-item").all()

            for item in items[:20]:  # Limit to prevent too many
                accomplishment = _extract_honor_from_details(item)
                if accomplishment:
                    # Check if not already added from main profile
                    if not any(
                        a.title == accomplishment.title and a.category == "Honor"
                        for a in person.accomplishments
                    ):
                        person.add_accomplishment(accomplishment)

    except Exception:
        pass


def _scrape_languages_details(page: Page, person: Person) -> None:
    """Scrape languages from the details page."""
    try:
        languages_url = os.path.join(str(person.linkedin_url), "details/languages")
        page.goto(languages_url)
        page.wait_for_timeout(2000)

        # Check if page exists
        if "Page not found" in page.content() or "/404/" in page.url:
            return

        main_content = page.locator("main").first
        if not main_content.is_visible():
            return

        # Get all list containers
        list_containers = main_content.locator(".pvs-list__container").all()

        for list_container in list_containers:
            items = list_container.locator(".pvs-list__paged-list-item").all()

            for item in items[:20]:  # Limit to prevent too many
                accomplishment = _extract_language_from_details(item)
                if accomplishment:
                    # Check if not already added from main profile
                    if not any(
                        a.title == accomplishment.title and a.category == "Language"
                        for a in person.accomplishments
                    ):
                        person.add_accomplishment(accomplishment)

    except Exception:
        pass


def _extract_honor_from_main_profile(item: Locator) -> Optional[Accomplishment]:
    """Extract honor/award from main profile list item."""
    try:
        # Get title
        title_elem = item.locator("div[aria-hidden='true'] span").first
        title = title_elem.inner_text() if title_elem.is_visible() else ""

        if not title:
            return None

        # Get issuer and date info
        institution_name = ""
        issuer_elem = item.locator("span:has-text('Issued by')").first
        if issuer_elem.is_visible():
            issuer_text = issuer_elem.inner_text()
            # Parse out institution name from "Issued by X · Date"
            if "Issued by" in issuer_text:
                parts = issuer_text.replace("Issued by", "").split("·")
                if parts:
                    institution_name = parts[0].strip()

        return Accomplishment(
            category="Honor",
            title=title,
            institution_name=institution_name if institution_name else None,
        )

    except Exception:
        return None


def _extract_honor_from_details(item: Locator) -> Optional[Accomplishment]:
    """Extract honor/award from details page list item."""
    try:
        container = item.locator("div[data-view-name='profile-component-entity']").first
        if not container.is_visible():
            return None

        # Get the details section (usually second div)
        parts = container.locator("> div").all()
        if len(parts) < 2:
            return None

        details = parts[1]

        # Get title
        title_elem = details.locator("span[aria-hidden='true']").first
        title = title_elem.inner_text() if title_elem.is_visible() else ""

        if not title:
            return None

        # Get institution
        institution_name = ""

        # Try "Issued by" first
        issuer_elem = details.locator("span:has-text('Issued by')").first
        if issuer_elem.is_visible():
            issuer_text = issuer_elem.inner_text()
            if "Issued by" in issuer_text:
                parts = issuer_text.replace("Issued by", "").split("·")
                if parts:
                    institution_name = parts[0].strip()

        # If no issuer, try "Associated with"
        if not institution_name:
            assoc_elem = details.locator("span:has-text('Associated with')").first
            if assoc_elem.is_visible():
                assoc_text = assoc_elem.inner_text()
                if "Associated with" in assoc_text:
                    institution_name = assoc_text.replace("Associated with", "").strip()

        # Try to get LinkedIn URL - could be institution link or document link
        linkedin_url = None
        try:
            links = container.locator("a").all()
            for link in links:
                if link.is_visible():
                    href = link.get_attribute("href")
                    if href:
                        # Check for various types of links
                        if "/company/" in href or "/school/" in href:
                            # Institution link
                            linkedin_url = href
                            break
                        elif "single-media-viewer" in href or "type=DOCUMENT" in href:
                            # Document/media link (e.g., certificate PDF)
                            linkedin_url = href
                            break
                        elif "/in/" in href and "add-edit" not in href:
                            # Person link (rare but possible for recommendations)
                            linkedin_url = href
                            break
        except Exception:
            pass

        return Accomplishment(
            category="Honor",
            title=title,
            institution_name=institution_name if institution_name else None,
            linkedin_url=HttpUrl(linkedin_url) if linkedin_url else None,
        )

    except Exception:
        return None


def _extract_language_from_main_profile(item: Locator) -> Optional[Accomplishment]:
    """Extract language from main profile list item."""
    try:
        text = item.inner_text()
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
                title = f"{language} - {proficiency}" if proficiency else language
                return Accomplishment(
                    category="Language", title=title, institution_name=None
                )

        return None

    except Exception:
        return None


def _extract_language_from_details(item: Locator) -> Optional[Accomplishment]:
    """Extract language from details page list item."""
    try:
        # Get language name
        name_elem = item.locator("span[aria-hidden='true']").first
        language = name_elem.inner_text() if name_elem.is_visible() else ""

        if not language:
            return None

        # Get proficiency level
        proficiency = ""
        prof_elem = item.locator("span.t-14").first
        if prof_elem.is_visible():
            prof_text = prof_elem.inner_text()
            # Clean up duplicate text that sometimes appears
            lines = prof_text.split("\n")
            if lines:
                proficiency = lines[0].strip()

        title = f"{language} - {proficiency}" if proficiency else language

        return Accomplishment(category="Language", title=title, institution_name=None)

    except Exception:
        return None
