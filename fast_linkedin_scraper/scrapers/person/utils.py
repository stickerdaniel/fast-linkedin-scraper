"""Person-specific utility functions for LinkedIn scraping operations."""

import re
from typing import Optional

from playwright.async_api import Locator
from rapidfuzz import fuzz


def clean_single_string_duplicates(text: str) -> str:
    """Clean duplicated content within a single string (e.g., 'Manager\nManager' -> 'Manager').

    Use this for single DOM element text that may have internal duplications.

    Args:
        text: Single string that may contain duplicated lines/words

    Returns:
        Cleaned string with duplications removed
    """
    if not text or len(text) < 5:
        return text.strip()

    # Split by newlines and remove duplicate lines
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return text.strip()

    # For simple cases, just take the first unique line
    if len(lines) == 2 and lines[0] == lines[1]:
        return lines[0]

    # For more complex cases, remove duplicated lines
    unique_lines = []
    for line in lines:
        if line not in unique_lines:
            unique_lines.append(line)

    return " ".join(unique_lines) if unique_lines else text.strip()


def is_content_essentially_same_when_building_from_multiple_elements(
    new_line: str, existing_lines: list[str], threshold: int = 80
) -> bool:
    """Check if new_line contains essentially the same content as existing lines using fuzzy matching.

    Use this when building description content from multiple DOM elements to prevent adding duplicates.
    NOTE: This function is for description text only. For skills, use exact matching instead.

    Args:
        new_line: The new line to check
        existing_lines: List of existing lines to compare against
        threshold: Similarity threshold (0-100), default 80%

    Returns:
        True if the new line contains essentially the same content as existing lines
    """
    if not new_line.strip() or not existing_lines:
        return False

    # Normalize the new line for comparison
    normalized_new = new_line.strip()
    # Remove common formatting markers
    normalized_new = re.sub(r"^[-•*]\s*", "", normalized_new)
    normalized_new = re.sub(r"^\d+\.\s*", "", normalized_new)

    if len(normalized_new) < 20:  # Too short to meaningfully compare
        return False

    # Check if the new line is just a combination of existing lines
    combined_existing = []
    for existing_line in existing_lines:
        normalized_existing = existing_line.strip()
        # Remove common formatting markers
        normalized_existing = re.sub(r"^[-•*]\s*", "", normalized_existing)
        normalized_existing = re.sub(r"^\d+\.\s*", "", normalized_existing)
        if len(normalized_existing) >= 20:
            combined_existing.append(normalized_existing)

    if not combined_existing:
        return False

    # Method 1: Check if new line is similar to any individual existing line
    for existing_content in combined_existing:
        similarity = fuzz.ratio(normalized_new.lower(), existing_content.lower())
        if similarity >= threshold:
            return True

    # Method 2: Check if new line is similar to combined existing lines (handles concatenation)
    combined_text = " ".join(combined_existing)
    combined_similarity = fuzz.ratio(normalized_new.lower(), combined_text.lower())
    if combined_similarity >= threshold:
        return True

    # Method 3: Check if new line contains most of the content from existing lines
    # Use partial_ratio which handles cases where one string is much longer
    for existing_content in combined_existing:
        partial_sim = fuzz.partial_ratio(
            existing_content.lower(), normalized_new.lower()
        )
        if partial_sim >= 90:  # High threshold for partial matching
            return True

    return False


def extract_description_and_skills(text: str) -> tuple[str, list[str]]:
    """Extract description and skills from LinkedIn text content.

    This function processes raw text (typically from a single DOM element) and separates
    description content from skills. Skills are deduplicated using exact string matching.

    Args:
        text: Raw text that may contain skills prefixed with "Skills:"

    Returns:
        Tuple of (description_text, skills_list)
    """
    if not text:
        return "", []

    # Use the text as-is since we prevent duplicates during extraction

    # Check if content is actually skills, not description
    if text.startswith("Skills:"):
        # Extract skills from the text
        skills_text = text.replace("Skills:", "").strip()
        if skills_text:
            # Split by common LinkedIn separators (· or ,) and clean
            if "·" in skills_text:
                skills = [
                    skill.strip() for skill in skills_text.split("·") if skill.strip()
                ]
            else:
                skills = [
                    skill.strip() for skill in skills_text.split(",") if skill.strip()
                ]

            # Remove any skills that contain newlines or institution names
            clean_skills = []
            for skill in skills:
                if (
                    skill
                    and "\n" not in skill
                    and not any(
                        word in skill.lower()
                        for word in [
                            "university",
                            "college",
                            "school",
                            "institute",
                            "hochschule",
                            "aachen",
                            "technische",
                        ]
                    )
                ):
                    clean_skills.append(skill)

            return "", clean_skills
        return "", []

    # Handle mixed content (description with skills section)
    lines = text.split("\n")
    description_lines = []
    skills = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("Skills:"):
            # Extract skills from line like "Skills: Java · Python · etc"
            skills_text = line[7:].strip()  # Remove "Skills: " prefix
            if skills_text:
                # Stop processing if we encounter institution names or non-skill content
                # Skills should only contain skill names, not institution info
                if any(
                    word in skills_text.lower()
                    for word in [
                        "university",
                        "college",
                        "school",
                        "institute",
                        "hochschule",
                        "english",
                        "german",
                        "technische",
                    ]
                ):
                    # Only take the part before institution names
                    skill_parts = skills_text.split()
                    clean_skills_text = ""
                    for part in skill_parts:
                        if any(
                            word in part.lower()
                            for word in [
                                "university",
                                "college",
                                "school",
                                "institute",
                                "hochschule",
                            ]
                        ):
                            break
                        clean_skills_text += part + " "
                    skills_text = clean_skills_text.strip()

                if skills_text:
                    if "·" in skills_text:
                        extracted_skills = [
                            skill.strip() for skill in skills_text.split("·")
                        ]
                    else:
                        extracted_skills = [
                            skill.strip() for skill in skills_text.split(",")
                        ]
                    # Filter out any skills that contain newlines or institution names
                    clean_skills = []
                    for skill in extracted_skills:
                        if (
                            skill
                            and "\n" not in skill
                            and not any(
                                word in skill.lower()
                                for word in [
                                    "university",
                                    "college",
                                    "school",
                                    "institute",
                                    "hochschule",
                                    "aachen",
                                    "technische",
                                ]
                            )
                        ):
                            clean_skills.append(skill)
                    skills.extend(clean_skills)
        elif not any(
            word in line.lower()
            for word in [
                "university",
                "college",
                "school",
                "institute",
                "hochschule",
                "english",
                "german",
            ]
        ) and not is_content_essentially_same_when_building_from_multiple_elements(
            line, description_lines
        ):
            description_lines.append(line)

    description = "\n".join(description_lines) if description_lines else ""

    # Deduplicate skills while preserving order - use exact matching for skills
    unique_skills = []
    for skill in skills:
        # For skills, use exact string matching for consistency
        if skill not in unique_skills:
            unique_skills.append(skill)

    return description, unique_skills


async def extract_description_and_skills_from_element(
    element: Optional[Locator],
) -> tuple[str, list[str]]:
    """Extract clean description and skills from DOM element with nested list structure.

    This function handles complex DOM traversal and delegates to extract_description_and_skills()
    for text processing. It applies deduplication at the DOM level (cleaning individual elements)
    and at the content level (exact matching for skills, fuzzy matching for descriptions).

    Args:
        element: The DOM element containing description lists

    Returns:
        Tuple of (description_text, skills_list)
    """
    if not element or not await element.is_visible():
        return "", []

    description_lines = []
    skills = []

    try:
        # Navigate to nested list structure based on DOM analysis
        # Look for list containers and their items
        lists = await element.locator("list, ul, .pvs-list").all()
        if lists:
            for list_elem in lists:
                list_items = await list_elem.locator(
                    "listitem, li, .pvs-list__item"
                ).all()
                for item in list_items:
                    text = (await item.inner_text()).strip()
                    if text:
                        # When building from multiple elements, clean each element's content first
                        cleaned_text = clean_single_string_duplicates(text)
                        lines = cleaned_text.split("\n")
                        for line in lines:
                            line = line.strip()
                            if line:
                                if line.startswith("Skills:"):
                                    # Extract skills from line like "Skills: Java · Python · etc"
                                    skills_text = line[
                                        7:
                                    ].strip()  # Remove "Skills: " prefix
                                    if skills_text:
                                        if "·" in skills_text:
                                            extracted_skills = [
                                                skill.strip()
                                                for skill in skills_text.split("·")
                                            ]
                                        else:
                                            extracted_skills = [
                                                skill.strip()
                                                for skill in skills_text.split(",")
                                            ]
                                        skills.extend(
                                            [
                                                skill
                                                for skill in extracted_skills
                                                if skill
                                            ]
                                        )
                                elif not is_content_essentially_same_when_building_from_multiple_elements(
                                    line, description_lines
                                ):
                                    description_lines.append(line)
        else:
            # Fallback: extract text directly from element
            text = (await element.inner_text()).strip()
            if text:
                # For single element, clean duplicates first then extract
                cleaned_text = clean_single_string_duplicates(text)
                return extract_description_and_skills(cleaned_text)

    except Exception:
        # Fallback: try to extract text directly
        try:
            text = (await element.inner_text()).strip()
            if text:
                # For single element, clean duplicates first then extract
                cleaned_text = clean_single_string_duplicates(text)
                return extract_description_and_skills(cleaned_text)
        except Exception:
            pass

    description = "\n".join(description_lines) if description_lines else ""

    # Deduplicate skills while preserving order - use exact matching for skills
    unique_skills = []
    for skill in skills:
        # For skills, use exact string matching for better deduplication
        if skill not in unique_skills:
            unique_skills.append(skill)

    return description, unique_skills


def is_date_range(text: str) -> bool:
    """Check if text contains a LinkedIn date range pattern.

    Args:
        text: Text to check for date patterns

    Returns:
        True if text matches a date range pattern, False otherwise

    Examples:
        >>> is_date_range("2020 - 2024")
        True
        >>> is_date_range("Oct 2024 - Apr 2025")
        True
        >>> is_date_range("May 2024 - Present")
        True
        >>> is_date_range("2015 -")
        True
        >>> is_date_range("Bachelor of Science")
        False
    """
    if not text or "-" not in text:
        return False

    # Match patterns like:
    # "2020 - 2024", "Oct 2024 - Apr 2025", "May 2024 - Present", "2015 -"
    date_pattern = r"^\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+)?\d{4}\s*-\s*(?:(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+)?\d{4}|Present)?\s*$"
    return bool(re.match(date_pattern, text.strip(), re.IGNORECASE))


def parse_date_range_smart(text: str) -> tuple[str, str]:
    """Parse date range with regex validation and return (from_date, to_date).

    Args:
        text: Date range text like "2020 - 2024" or "Oct 2024 - Present"

    Returns:
        Tuple of (from_date, to_date) strings

    Examples:
        >>> parse_date_range_smart("2020 - 2024")
        ("2020", "2024")
        >>> parse_date_range_smart("Oct 2024 - Apr 2025")
        ("Oct 2024", "Apr 2025")
        >>> parse_date_range_smart("May 2024 - Present")
        ("May 2024", "Present")
        >>> parse_date_range_smart("2015 -")
        ("2015", "")
    """
    if not text or "-" not in text:
        return "", ""

    # Split at dash and clean up
    parts = text.split("-", 1)  # Split only at first dash
    from_date = parts[0].strip()
    to_date = parts[1].strip() if len(parts) > 1 else ""

    # Validate that from_date looks like a date
    from_date_pattern = (
        r"^(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+)?\d{4}$"
    )
    if not re.match(from_date_pattern, from_date, re.IGNORECASE):
        return "", ""

    # Validate to_date (can be empty for ongoing, "Present", or another date)
    if to_date:
        to_date_pattern = r"^(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+)?\d{4}$|^Present$"
        if not re.match(to_date_pattern, to_date, re.IGNORECASE):
            return "", ""

    return from_date, to_date


# LinkedIn Employment Types based on UI options
LINKEDIN_EMPLOYMENT_TYPES = {
    "self-employed",
    "freelance",
    "internship",
    "apprenticeship",
    "contract full-time",
    "permanent part-time",
    "contract part-time",
    "casual / on-call",
    "seasonal",
    "permanent full-time",
    "co-op",
    "full-time",
    "part-time",
    "contract",
    "temporary",
    "volunteer",
    "work study",
}


def is_employment_type(text: str) -> bool:
    """Check if text contains a LinkedIn employment type.

    Args:
        text: Text to check for employment type keywords

    Returns:
        True if text contains employment type keywords, False otherwise

    Examples:
        >>> is_employment_type("Freelance")
        True
        >>> is_employment_type("Full-time")
        True
        >>> is_employment_type("Linz, Upper Austria")
        False
    """
    if not text:
        return False

    text_lower = text.lower().strip()

    # Check exact matches first
    if text_lower in LINKEDIN_EMPLOYMENT_TYPES:
        return True

    # Check if any employment type is contained in the text
    for emp_type in LINKEDIN_EMPLOYMENT_TYPES:
        if emp_type in text_lower:
            return True

    return False


def extract_employment_type(text: str) -> Optional[str]:
    """Extract employment type from text that may contain mixed content.

    Args:
        text: Text that may contain employment type mixed with other content

    Returns:
        Employment type string if found, None otherwise

    Examples:
        >>> extract_employment_type("Company Name · Freelance")
        "Freelance"
        >>> extract_employment_type("Full-time")
        "Full-time"
        >>> extract_employment_type("Linz, Upper Austria")
        None
    """
    if not text:
        return None

    text_lower = text.lower().strip()

    # Check exact match first
    if text_lower in LINKEDIN_EMPLOYMENT_TYPES:
        return text.strip()

    # Split by common separators and check each part
    for separator in ["·", ",", "-", "•"]:
        if separator in text:
            parts = text.split(separator)
            for part in parts:
                part_lower = part.strip().lower()
                if part_lower in LINKEDIN_EMPLOYMENT_TYPES:
                    return part.strip()

    # Check if any employment type is contained in the text
    for emp_type in LINKEDIN_EMPLOYMENT_TYPES:
        if emp_type in text_lower:
            # Try to extract just the employment type part
            words = text.split()
            for word in words:
                if word.lower().strip() in LINKEDIN_EMPLOYMENT_TYPES:
                    return word.strip()

    return None


def is_geographic_location(text: str) -> bool:
    """Check if text appears to be a geographic location rather than employment type.

    Args:
        text: Text to check

    Returns:
        True if text appears to be a geographic location, False otherwise

    Examples:
        >>> is_geographic_location("Linz, Upper Austria")
        True
        >>> is_geographic_location("Frankfurt Rhine-Main Metropolitan Area")
        True
        >>> is_geographic_location("Remote")
        True
        >>> is_geographic_location("Freelance")
        False
    """
    if not text:
        return False

    text_lower = text.lower().strip()

    # If it's an employment type, it's not a location
    if is_employment_type(text):
        return False

    # Geographic indicators
    location_indicators = [
        ",",  # "City, State/Province"
        "area",
        "region",
        "metropolitan",
        "remote",
        "on-site",
        "hybrid",
        "germany",
        "austria",
        "canada",
        "usa",
        "united states",
        "uk",
        "france",
        "city",
        "state",
        "province",
        "country",
        "district",
        "county",
        "am main",
        "rhine-main",
        "greater",
        "toronto",
        "frankfurt",
        "linz",
        "hanau",
        "aachen",
        "hesse",
        "upper austria",
        "ontario",
    ]

    return any(indicator in text_lower for indicator in location_indicators)
