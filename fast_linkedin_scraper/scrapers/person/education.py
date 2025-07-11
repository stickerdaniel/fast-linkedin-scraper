"""Education scraping module for LinkedIn profiles."""

import os
from typing import Optional

from playwright.sync_api import Page, Locator
from pydantic import HttpUrl

from ...models.person import Person, Education
from ..utils import scroll_to_half, scroll_to_bottom
from .utils import (
    clean_single_string_duplicates,
    extract_description_and_skills,
    is_date_range,
    parse_date_range_smart,
)


def scrape_educations(page: Page, person: Person) -> None:
    """Scrape education information from LinkedIn profile.

    Args:
        page: Playwright page instance
        person: Person model to populate with education data
    """
    # Navigate to education details page
    education_url = os.path.join(str(person.linkedin_url), "details/education")
    page.goto(education_url)

    # Wait for page to load
    page.wait_for_timeout(2000)  # 2 seconds

    # Scroll to ensure all content is loaded
    scroll_to_half(page)
    page.wait_for_timeout(1000)  # 1 second
    scroll_to_bottom(page)
    page.wait_for_timeout(2000)  # 2 seconds for content to load

    # Find the main education container
    try:
        main_list = page.locator("main .pvs-list__container").first
        if not main_list.is_visible():
            return

        # Get all education items
        education_items = main_list.locator(".pvs-list__paged-list-item").all()

        for position_elem in education_items:
            try:
                # Find the main education container
                position_container = position_elem.locator(
                    "div[data-view-name='profile-component-entity']"
                ).first
                if not position_container.is_visible():
                    continue

                # Get main elements - logo and details
                elements = position_container.locator("> *").all()
                if len(elements) < 2:
                    continue

                institution_logo_elem = elements[0]
                position_details = elements[1]

                # Extract institution LinkedIn URL
                institution_linkedin_url = _extract_institution_url(
                    institution_logo_elem
                )

                # Extract position details
                position_details_list = position_details.locator("> *").all()
                position_summary_details = (
                    position_details_list[0] if len(position_details_list) > 0 else None
                )
                position_summary_text = (
                    position_details_list[1] if len(position_details_list) > 1 else None
                )

                if not position_summary_details:
                    continue

                # Extract education information
                education_info = _extract_education_info(position_summary_details)

                # Extract description and skills
                description = ""
                skills = []
                if position_summary_text and position_summary_text.is_visible():
                    raw_text = position_summary_text.inner_text()
                    print(f"DEBUG: Education raw text: {repr(raw_text)}")
                    # Clean single element duplicates before processing
                    cleaned_text = clean_single_string_duplicates(raw_text)
                    description, skills = extract_description_and_skills(cleaned_text)
                    print(
                        f"DEBUG: Education extracted - description: {repr(description)}, skills: {skills}"
                    )

                # Create education object
                education = Education(
                    from_date=education_info.get("from_date") or None,
                    to_date=education_info.get("to_date") or None,
                    description=description if description else None,
                    degree=education_info.get("degree") or None,
                    institution_name=education_info.get("institution_name", ""),
                    skills=skills,
                    linkedin_url=HttpUrl(institution_linkedin_url)
                    if institution_linkedin_url
                    else None,
                )
                person.add_education(education)

            except Exception:
                # Skip this education if extraction fails
                continue

    except Exception:
        # If main container not found, skip education scraping
        pass


def _extract_institution_url(institution_logo_elem: Locator) -> Optional[str]:
    """Extract institution LinkedIn URL from logo element."""
    try:
        link_elem = institution_logo_elem.locator("> *").first
        if link_elem.is_visible():
            href = link_elem.get_attribute("href")
            return href if href else None
    except Exception:
        pass
    return None


def _extract_education_info(position_summary_details: Locator) -> dict:
    """Extract education information from position summary element."""
    education_info = {
        "institution_name": "",
        "degree": "",
        "from_date": "",
        "to_date": "",
    }

    try:
        outer_positions = position_summary_details.locator("> *").locator("> *").all()

        # Extract institution name
        if len(outer_positions) > 0:
            institution_span = outer_positions[0].locator("span").first
            if institution_span.is_visible():
                education_info["institution_name"] = institution_span.inner_text()

        # Intelligently extract degree and dates using regex validation
        for i in range(1, len(outer_positions)):
            span = outer_positions[i].locator("span").first
            if span.is_visible():
                text = span.inner_text()

                # Use regex to check if this text is a date range
                if is_date_range(text) and not education_info["from_date"]:
                    # This is the dates field - use smart parser
                    from_date, to_date = parse_date_range_smart(text)
                    education_info["from_date"] = from_date
                    education_info["to_date"] = to_date
                elif not is_date_range(text) and not education_info["degree"]:
                    # This is the degree field
                    education_info["degree"] = text

    except Exception:
        pass

    return education_info
