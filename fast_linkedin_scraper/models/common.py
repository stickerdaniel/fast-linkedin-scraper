from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class Contact(BaseModel):
    """Contact information for a person."""

    name: Optional[str] = None
    occupation: Optional[str] = None
    url: Optional[HttpUrl] = None


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
    founded: Optional[int] = Field(None, ge=1800, le=2030)
