from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

# PersonalInfo Schema
class PersonalInfoBase(BaseModel):
    name: str
    auth_provider: str
    union_id: str
    unique_id: str
    gender: str
    age: str
    phone: str
    email: str
    avatar: str
    tag: Optional[str] = None
    tag_description: Optional[str] = None
    issues: str
    job_id: str
    num_diamond: Optional[int] = 500


class PersonalInfoCreate(PersonalInfoBase):
    pass


class PersonalInfoUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    tag: Optional[str] = None
    tag_description: Optional[str] = None
    age: Optional[str] = None
    issues: Optional[str] = None
    job_id: Optional[str] = None

    class Config:
        from_attributes = True


class PersonalInfo(PersonalInfoBase):
    id: str  # Changed to str to match the SQLAlchemy model
    eq_scores: List['EQScore'] = []  # Relationship

    class Config:
        # orm_mode = True
        from_attributes = True


# EQScore Schema
class EQScoreBase(BaseModel):
    perception_score: int
    perception_detail: Optional[str]
    social_skill_score: int
    social_skill_detail: Optional[str]
    self_regulaton_score: int
    self_regulaton_detail: Optional[str]
    empathy_score: int
    empathy_detail: Optional[str]
    motivation_score: int
    motivation_detail: Optional[str]
    summary: Optional[str]
    detail: Optional[str]
    detail_summary: Optional[str]
    overall_suggestion: Optional[str]
    job_id: str


class EQScoreCreate(EQScoreBase):
    user_id: int  # ForeignKey to PersonalInfo.id


class EQScore(EQScoreBase):
    id: int
    user_id: int  # ForeignKey to PersonalInfo.id

    class Config:
        from_attributes = True


# Courses Schema
class CoursesBase(BaseModel):
    course_dim: str
    course_level: int
    prompt: str
    title: str
    background: Optional[str]
    npc: str
    task: Optional[str]
    image: Optional[str]


class CoursesCreate(CoursesBase):
    pass


class Courses(CoursesBase):
    id: int

    class Config:
        from_attributes = True


# PersonalInfoCourses Schema (Many-to-Many relationship between PersonalInfo and Courses)
class PersonalInfoCoursesBase(BaseModel):
    user_id: int  # ForeignKey to PersonalInfo.id
    course_id: int  # ForeignKey to Courses.id
    course_dim: str
    course_level: int
    status: str
    result: Optional[int]
    comment1: Optional[str]
    comment2: Optional[str]
    comment3: Optional[str]


class PersonalInfoCoursesCreate(PersonalInfoCoursesBase):
    pass


class PersonalInfoCourses(PersonalInfoCoursesBase):
    class Config:
        from_attributes = True


# ChatHistory
class ChatHistoryBase(BaseModel):
    chatHistory: str
    summary: str
    analysis: str
    low_dim: str


class ChatHistoryCreate(ChatHistoryBase):
    user_id: int


class ChatHistory(ChatHistoryBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


# ReplyState Schema
class ReplyStateBase(BaseModel):
    product: str
    userId: str
    chat_history: str
    stage2_output: Optional[str] = None
    stage_number: Optional[int] = None


class ReplyStateCreate(ReplyStateBase):
    pass


class ReplyState(ReplyStateBase):
    id: int

    class Config:
        from_attributes = True




