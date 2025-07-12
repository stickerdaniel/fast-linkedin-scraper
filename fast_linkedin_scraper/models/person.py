from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl

from .common import Contact, BaseInstitution


class Experience(BaseInstitution):
    """Work experience entry."""

    from_date: Optional[str] = None
    to_date: Optional[str] = None
    description: Optional[str] = None
    position_title: Optional[str] = None
    duration: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    skills: List[str] = Field(default_factory=list)


class Education(BaseInstitution):
    """Education entry."""

    from_date: Optional[str] = None
    to_date: Optional[str] = None
    description: Optional[str] = None
    degree: Optional[str] = None
    skills: List[str] = Field(default_factory=list)


class Interest(BaseModel):
    """Interest/hobby entry."""

    title: Optional[str] = None
    institution_name: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None


class Accomplishment(BaseModel):
    """Achievement/accomplishment entry."""

    category: Optional[str] = None
    title: Optional[str] = None
    institution_name: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None


class Person(BaseModel):
    """LinkedIn person profile."""

    linkedin_url: Optional[HttpUrl] = None
    name: Optional[str] = None
    headline: Optional[str] = None
    location: Optional[str] = None
    about: List[str] = Field(default_factory=list)
    experiences: List[Experience] = Field(default_factory=list)
    educations: List[Education] = Field(default_factory=list)
    interests: List[Interest] = Field(default_factory=list)
    accomplishments: List[Accomplishment] = Field(default_factory=list)
    contacts: List[Contact] = Field(default_factory=list)
    also_viewed_urls: List[HttpUrl] = Field(default_factory=list)
    company: Optional[str] = None
    job_title: Optional[str] = None
    open_to_work: Optional[bool] = None

    def add_experience(self, experience: Experience) -> None:
        """Add an experience entry."""
        self.experiences.append(experience)

    def add_education(self, education: Education) -> None:
        """Add an education entry."""
        self.educations.append(education)

    def add_interest(self, interest: Interest) -> None:
        """Add an interest entry."""
        self.interests.append(interest)

    def add_accomplishment(self, accomplishment: Accomplishment) -> None:
        """Add an accomplishment entry."""
        self.accomplishments.append(accomplishment)

    def add_contact(self, contact: Contact) -> None:
        """Add a contact entry."""
        self.contacts.append(contact)

    def add_location(self, location: str) -> None:
        """Add location information."""
        self.location = location

    def add_about(self, about: str) -> None:
        """Add about information."""
        self.about.append(about)

    def add_headline(self, headline: str) -> None:
        """Add headline information."""
        self.headline = headline

    @property
    def current_company(self) -> Optional[str]:
        """Get the current company from the most recent experience."""
        if self.experiences:
            return (
                self.experiences[0].institution_name
                if self.experiences[0].institution_name
                else None
            )
        return None

    @property
    def current_job_title(self) -> Optional[str]:
        """Get the current job title from the most recent experience."""
        if self.experiences:
            return (
                self.experiences[0].position_title
                if self.experiences[0].position_title
                else None
            )
        return None
