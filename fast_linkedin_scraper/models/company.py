from typing import Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class Employee(BaseModel):
    """Employee information."""

    name: Optional[str] = None
    designation: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None


class CompanySummary(BaseModel):
    """Summary information for showcase or affiliated companies."""

    name: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None
    followers: Optional[str] = None


class Company(BaseModel):
    """LinkedIn company profile."""

    linkedin_url: Optional[HttpUrl] = None
    name: Optional[str] = None
    about_us: Optional[str] = None
    website: Optional[HttpUrl] = None
    headquarters: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    specialties: List[str] = Field(default_factory=list)
    headcount: Optional[int] = None
    showcase_pages: List[CompanySummary] = Field(default_factory=list)
    affiliated_companies: List[CompanySummary] = Field(default_factory=list)
    employees: List[Employee] = Field(default_factory=list)
    scraping_errors: Dict[str, str] = Field(default_factory=dict)

    def add_employee(self, employee: Employee) -> None:
        """Add an employee to the company."""
        self.employees.append(employee)

    def add_showcase_page(self, company: CompanySummary) -> None:
        """Add a showcase page to the company."""
        self.showcase_pages.append(company)

    def add_affiliated_company(self, company: CompanySummary) -> None:
        """Add an affiliated company."""
        self.affiliated_companies.append(company)
