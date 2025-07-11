from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class Job(BaseModel):
    """LinkedIn job posting."""

    job_id: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None
    title: Optional[str] = None
    company: Optional[str] = None
    company_url: Optional[HttpUrl] = None
    location: Optional[str] = None
    description: Optional[str] = None
    seniority_level: Optional[str] = None
    employment_type: Optional[str] = None
    job_function: Optional[str] = None
    industries: List[str] = Field(default_factory=list)
    posted_date: Optional[str] = None
    num_applicants: Optional[int] = Field(None, ge=0)


class JobSearch(BaseModel):
    """Job search results."""

    search_query: Optional[str] = None
    location: Optional[str] = None
    jobs: List[Job] = Field(default_factory=list)
    total_results: Optional[int] = Field(None, ge=0)

    def add_job(self, job: Job) -> None:
        """Add a job to the search results."""
        self.jobs.append(job)
