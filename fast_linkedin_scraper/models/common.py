from typing import Optional

from pydantic import BaseModel, Field, HttpUrl

# Constants
MIN_FOUNDED_YEAR = 1800  # Earliest reasonable founding year
MAX_FOUNDED_YEAR = 2030  # Latest reasonable founding year


class ContactInfo(BaseModel):
    """Contact information (email, phone, website, etc.)."""

    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    linkedin_url: Optional[str] = None


class Connection(BaseModel):
    """A connection/contact person on LinkedIn."""

    name: str
    headline: Optional[str] = None  # Their professional headline/title
    url: Optional[HttpUrl] = None  # Their LinkedIn profile URL


class BaseInstitution(BaseModel):
    """Minimal institution model with just name and LinkedIn URL."""

    institution_name: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None


class Institution(BaseInstitution):
    """Full institution model with company-specific fields for company profiles."""

    website: Optional[HttpUrl] = None
    industry: Optional[str] = None
    type: Optional[str] = None
    headquarters: Optional[str] = None
    company_size: Optional[int] = Field(None, ge=1)
    founded: Optional[int] = Field(None, ge=MIN_FOUNDED_YEAR, le=MAX_FOUNDED_YEAR)
