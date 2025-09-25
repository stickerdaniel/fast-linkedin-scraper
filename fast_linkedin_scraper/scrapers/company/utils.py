"""Utility functions for company scraping."""

import re
from typing import Optional


def extract_employee_count(text: str) -> Optional[int]:
    """Extract employee count from text like 'See all 12,345 employees on LinkedIn'.

    Args:
        text: Text containing employee count

    Returns:
        Employee count as integer or None if not found
    """
    if not text:
        return None

    # Remove commas and find all numbers
    numbers = re.findall(r"[\d,]+", text)
    if numbers:
        for num_str in numbers:
            try:
                num = int(num_str.replace(",", ""))
                # Return the first reasonable employee count (not year-like numbers)
                if (
                    num > 0 and num < 10000000
                ):  # Max 10 million employees seems reasonable
                    return num
            except ValueError:
                continue
    return None


def clean_company_url(url: str) -> str:
    """Clean and normalize a LinkedIn company URL.

    Args:
        url: Raw LinkedIn URL

    Returns:
        Cleaned URL without query parameters
    """
    if not url:
        return url

    # Add protocol if missing
    if not url.startswith("http"):
        url = "https://www.linkedin.com" + url

    # Remove query parameters
    url = url.split("?")[0]

    # Remove trailing slashes
    url = url.rstrip("/")

    return url


def parse_company_size(size_text: str) -> tuple[Optional[int], Optional[int]]:
    """Parse company size text to get min and max employee counts.

    Args:
        size_text: Text like '51-200 employees' or '10,001+ employees'

    Returns:
        Tuple of (min_size, max_size) or (None, None) if parsing fails
    """
    if not size_text:
        return None, None

    # Remove commas and find numbers
    numbers = re.findall(r"[\d,]+", size_text)
    if not numbers:
        return None, None

    try:
        if len(numbers) >= 2:
            # Range like "51-200"
            min_size = int(numbers[0].replace(",", ""))
            max_size = int(numbers[1].replace(",", ""))
            return min_size, max_size
        elif len(numbers) == 1:
            # Single number, might be "10,001+"
            size = int(numbers[0].replace(",", ""))
            if "+" in size_text:
                # It's a minimum like "10,001+"
                return size, None
            else:
                # It's an exact count or maximum
                return None, size
    except ValueError:
        pass

    return None, None


def normalize_industry(industry_text: str) -> str:
    """Normalize industry text by removing extra whitespace and standardizing case.

    Args:
        industry_text: Raw industry text

    Returns:
        Normalized industry string
    """
    if not industry_text:
        return industry_text

    # Remove extra whitespace
    industry_text = " ".join(industry_text.split())

    # Remove common suffixes like "Industry" if present
    industry_text = re.sub(r"\s+Industry$", "", industry_text, flags=re.IGNORECASE)

    return industry_text.strip()
