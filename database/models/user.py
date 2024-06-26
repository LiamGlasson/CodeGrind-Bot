from datetime import UTC, datetime
from typing import List, Optional

from beanie import Document
from pydantic import BaseModel, Field


class Votes(BaseModel):
    count: Optional[int] = 0
    last_voted: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC))


class Submissions(BaseModel):
    easy: Optional[int] = 0
    medium: Optional[int] = 0
    hard: Optional[int] = 0
    score: Optional[int] = 0


class Stats(BaseModel):
    submissions: Optional[Submissions] = Field(default_factory=Submissions)
    streak: Optional[int] = 0


class LanguageProblemCount(BaseModel):
    language: str
    count: int


class SkillProblemCount(BaseModel):
    skill: str
    count: int


class SkillsProblemCount(BaseModel):
    fundamental: Optional[List[SkillProblemCount]] = Field(default_factory=list)
    intermediate: Optional[List[SkillProblemCount]] = Field(default_factory=list)
    advanced: Optional[List[SkillProblemCount]] = Field(default_factory=list)


class User(Document):
    id: int
    leetcode_id: str
    stats: Optional[Stats] = Field(default_factory=Stats)
    votes: Optional[Votes] = Field(default_factory=Votes)

    last_updated: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "users"
        use_state_management = True
