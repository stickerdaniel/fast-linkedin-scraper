"""Utility functions for LinkedIn scraping operations."""

import re
from typing import Dict, Optional

from playwright.sync_api import Locator, Page
from pydantic import HttpUrl


def scroll_to_half(page: Page) -> None:
    """Scroll to half of the page to trigger content loading."""
    page.evaluate("window.scrollTo(0, Math.ceil(document.body.scrollHeight/2))")


def scroll_to_bottom(page: Page) -> None:
    """Scroll to bottom of the page to trigger content loading."""
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")


def safe_text_extract(locator: Locator) -> str:
    """Safely extract text from a locator, returning empty string if not found."""
    try:
        if locator.is_visible():
            return locator.inner_text().strip()
    except Exception:
        pass
    return ""


def safe_attribute_extract(locator: Locator, attribute: str) -> Optional[str]:
    """Safely extract an attribute from a locator, returning None if not found."""
    try:
        if locator.is_visible():
            return locator.get_attribute(attribute)
    except Exception:
        pass
    return None


def extract_linkedin_url(element: Locator) -> Optional[str]:
    """Extract LinkedIn URL from an element, typically from href attribute."""
    try:
        # Look for direct href
        href = safe_attribute_extract(element, "href")
        if href:
            return href

        # Look for href in child elements
        child_with_href = element.locator("a, [href]").first
        if child_with_href.is_visible():
            return safe_attribute_extract(child_with_href, "href")

    except Exception:
        pass
    return None


def parse_date_range(date_text: str) -> Dict[str, Optional[str]]:
    """Parse date range text into from_date, to_date, and duration.

    Args:
        date_text: Text like "Jan 2020 - Dec 2023 · 4 yrs"

    Returns:
        Dict with from_date, to_date, and duration keys
    """
    result: Dict[str, Optional[str]] = {
        "from_date": None,
        "to_date": None,
        "duration": None,
    }

    if not date_text:
        return result

    try:
        # Split by middle dot (·) to separate dates from duration
        parts = date_text.split("·")
        date_part = parts[0].strip() if parts else ""
        duration_part = parts[1].strip() if len(parts) > 1 else None

        # Parse dates
        if date_part and "-" in date_part:
            date_components = date_part.split("-")
            if len(date_components) >= 2:
                result["from_date"] = date_components[0].strip()
                result["to_date"] = date_components[1].strip()
        elif date_part:
            # Single date (ongoing or single point)
            result["from_date"] = date_part.strip()

        # Parse duration
        if duration_part:
            result["duration"] = duration_part

    except Exception:
        pass

    return result


def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    if not text:
        return ""

    # Remove extra whitespace and normalize
    cleaned = re.sub(r"\s+", " ", text.strip())

    # Remove common LinkedIn artifacts
    cleaned = re.sub(r"\n+", "\n", cleaned)
    cleaned = re.sub(r"·+", "·", cleaned)

    return cleaned


def clean_duplicated_text(text: str) -> str:
    """Remove duplicated content from text that appears due to LinkedIn's DOM structure.

    Args:
        text: Raw text that may contain duplicated lines or content

    Returns:
        Clean text with duplications removed while preserving meaningful content
    """
    if not text:
        return ""

    # Split into lines and process each line
    lines = text.split("\n")
    unique_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if this exact line already exists
        if line not in unique_lines:
            unique_lines.append(line)

    # Join the unique lines back together
    result = "\n".join(unique_lines)

    # Additional cleanup for within-line duplications
    # Handle cases where same text appears multiple times in one line
    result = re.sub(r"\b(\w+(?:\s+\w+)*)\s+\1\b", r"\1", result)

    # Universal approach: detect if content is duplicated regardless of formatting
    lines = result.split("\n")
    if len(lines) >= 2:
        # Check if any line contains most/all content from other lines (suggesting duplication)
        for i, line_to_check in enumerate(lines):
            line_to_check = line_to_check.strip()
            if len(line_to_check) < 30:  # Skip very short lines
                continue

            # Get content from all other lines
            other_lines_content = []
            for j, other_line in enumerate(lines):
                if i != j:  # Skip the line we're checking
                    # Remove common formatting markers (not just bullets)
                    clean_line = re.sub(r"^[-•*]\s*", "", other_line.strip())
                    clean_line = re.sub(
                        r"^\d+\.\s*", "", clean_line
                    )  # Remove numbered lists
                    if clean_line:
                        other_lines_content.append(clean_line)

            if other_lines_content:
                # Check if this line contains the same content as other lines combined
                combined_others = " ".join(other_lines_content)

                # Normalize both for comparison (remove all non-alphanumeric chars)
                normalized_line = re.sub(r"[^\w\s]", "", line_to_check.lower())
                normalized_others = re.sub(r"[^\w\s]", "", combined_others.lower())

                # Split into words and check overlap
                words_line = set(normalized_line.split())
                words_others = set(normalized_others.split())

                # If the line contains >80% of words from other lines, it's likely a duplicate
                if len(words_others) > 0:
                    overlap = len(words_line.intersection(words_others))
                    coverage = overlap / len(words_others)

                    if coverage > 0.8 and len(words_line) > len(words_others) * 0.5:
                        # This line appears to be a duplicate - remove it
                        lines.pop(i)
                        result = "\n".join(lines)
                        break  # Only remove one duplicate per pass

    # Clean up any remaining artifacts from the removal
    result = re.sub(r"\s+", " ", result)  # Multiple spaces
    result = re.sub(r"\n\s*\n", "\n", result)  # Multiple newlines
    result = re.sub(r"\s*-\s*$", "", result)  # Trailing dash from removed content

    return result.strip()


def validate_linkedin_url(url: str) -> Optional[HttpUrl]:
    """Validate and return a LinkedIn URL, or None if invalid."""
    if not url:
        return None

    try:
        # Basic LinkedIn URL validation
        if "linkedin.com" in url:
            return HttpUrl(url)
    except Exception:
        pass

    return None
