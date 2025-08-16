from typing import Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl

from .common import BaseInstitution, Connection, ContactInfo


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

    name: str
    type: str  # "influencer", "company", "group", "newsletter", "school"
    url: Optional[str] = None
    followers: Optional[str] = None


class Honor(BaseModel):
    """Honor/award entry."""

    title: str
    issuer: Optional[str] = None  # Institution that issued the honor
    date: Optional[str] = None  # Date issued
    associated_with: Optional[str] = None  # Associated organization
    document_url: Optional[HttpUrl] = None  # Link to certificate/document


class Language(BaseModel):
    """Language proficiency entry."""

    name: str
    proficiency: Optional[str] = None  # e.g., "Native or bilingual proficiency"


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
    honors: List[Honor] = Field(default_factory=list)
    languages: List[Language] = Field(default_factory=list)
    contact_info: Optional[ContactInfo] = None
    connections: List[Connection] = Field(default_factory=list)
    connection_count: Optional[int] = None  # Total number of connections
    also_viewed_urls: List[HttpUrl] = Field(default_factory=list)
    company: Optional[str] = None
    job_title: Optional[str] = None
    open_to_work: Optional[bool] = None
    scraping_errors: Dict[str, str] = Field(default_factory=dict)

    def add_experience(self, experience: Experience) -> None:
        """Add an experience entry."""
        self.experiences.append(experience)

    def add_education(self, education: Education) -> None:
        """Add an education entry."""
        self.educations.append(education)

    def add_interest(self, interest: Interest) -> None:
        """Add an interest entry."""
        self.interests.append(interest)

    def add_honor(self, honor: Honor) -> None:
        """Add an honor/award entry."""
        self.honors.append(honor)

    def add_language(self, language: Language) -> None:
        """Add a language entry."""
        self.languages.append(language)

    def add_connection(self, connection: Connection) -> None:
        """Add a connection entry."""
        self.connections.append(connection)

    def set_contact_info(self, contact_info: ContactInfo) -> None:
        """Set contact information."""
        self.contact_info = contact_info

    def set_connection_count(self, count: int) -> None:
        """Set the total connection count."""
        self.connection_count = count

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
