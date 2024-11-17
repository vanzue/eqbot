from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# PersonalInfo Schema


class PersonalInfoBase(BaseModel):
    name: str
    gender: str
    tag: Optional[str] = None
    tag_description: Optional[str] = None
    job_level: str
    issues: str
    job_id: str


class PersonalInfoCreate(PersonalInfoBase):
    pass


class PersonalInfoUpdate(BaseModel):
    gender: Optional[str] = None
    tag: Optional[str] = None
    tag_description: Optional[str] = None
    job_level: Optional[str] = None
    issues: Optional[str] = None
    job_id: Optional[str] = None

    class Config:
        from_attributes = True


class PersonalInfo(PersonalInfoBase):
    id: str  # Changed to str to match the SQLAlchemy model
    eq_scores: List['EQScore'] = []  # Relationship
    contacts: List['Contact'] = []  # Relationship
    chat_records: List['ChatRecords'] = []  # Relationship

    class Config:
        # orm_mode = True
        from_attributes = True

# EQScore Schema


class EQScoreBase(BaseModel):
    dimension1_score: int
    dimension1_detail: Optional[str]
    dimension2_score: int
    dimension2_detail: Optional[str]
    dimension3_score: int
    dimension3_detail: Optional[str]
    dimension4_score: int
    dimension4_detail: Optional[str]
    dimension5_score: int
    dimension5_detail: Optional[str]
    summary: Optional[str]
    detail: Optional[str]
    detail_summary: Optional[str]
    overall_suggestion: Optional[str]
    job_id: str


class EQScoreCreate(EQScoreBase):
    person_id: int  # ForeignKey to PersonalInfo.id


class EQScore(EQScoreBase):
    id: int
    person_id: int  # ForeignKey to PersonalInfo.id

    class Config:
        # orm_mode = True
        from_attributes = True

# Courses Schema


class CoursesBase(BaseModel):
    course_type: str
    course_level: int
    prompt: str


class CoursesCreate(CoursesBase):
    pass


class Courses(CoursesBase):
    id: int

    class Config:
        # orm_mode = True
        from_attributes = True

# PersonalInfoCourses Schema (Many-to-Many relationship between PersonalInfo and Courses)


class PersonalInfoCoursesBase(BaseModel):
    person_id: int  # ForeignKey to PersonalInfo.id
    course_id: int  # ForeignKey to Courses.id
    course_type: str
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
        # orm_mode = True
        from_attributes = True

# Contact Schema


class ContactBase(BaseModel):
    person_id: int  # ForeignKey to PersonalInfo.id
    name: str
    tag: Optional[str]
    contact_relationship: Optional[str]


class ContactCreate(ContactBase):
    pass


class Contact(ContactBase):
    id: int  # Changed to str to match the SQLAlchemy model

    class Config:
        # orm_mode = True
        from_attributes = True

# ChatRecords Schema


class ChatRecordsBase(BaseModel):
    person_id: int  # ForeignKey to PersonalInfo.id
    contact_id: int  # ForeignKey to Contact.id
    chat_time: datetime  # Use DateTime
    chat_content: str


class ChatRecordsCreate(ChatRecordsBase):
    pass


class ChatRecords(ChatRecordsBase):
    id: int

    class Config:
        # orm_mode = True
        from_attributes = True


# Subordinate Analysis Schema
class SubordinateAnalysisBase(BaseModel):
    contact_id: int
    relationship_analysis: str
    work_compatibility: str
    cunning_index: str
    work_personality: str
    interests: str
    bad_colleague_risk: str


class SubordinateAnalysisCreate(SubordinateAnalysisBase):
    pass


class SubordinateAnalysis(SubordinateAnalysisBase):
    id: int

    class Config:
        # orm_mode = True
        from_attributes = True


# Supervisor Analysis Schema
class SupervisorAnalysisBase(BaseModel):
    contact_id: int
    relationship_analysis: str
    interaction_suggestions: str
    leader_opinion_of_me: str
    pua_detection: str
    preferred_subordinate: str
    gift_recommendation: str


class SupervisorAnalysisCreate(SupervisorAnalysisBase):
    pass


class SupervisorAnalysis(SupervisorAnalysisBase):
    id: int

    class Config:
        # orm_mode = True
        from_attributes = True


# Patterns

class CreateUserRequest(BaseModel):
    name: str
    job_level: str
    gender: str
    concerns: List[str]


class ChatHistoryBase(BaseModel):
    chatHistory: str
    summary: str
    analysis: str
    low_dim: str


class ChatHistoryCreate(ChatHistoryBase):
    userId: int


class ChatHistory(ChatHistoryBase):
    id: int
    userId: int

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

class ReplyEvalBase(BaseModel):
    chat_history: str
    analysis: str
    suggest_response: str

class ReplyEvalCreate(ReplyEvalBase):
    eval_score: str
    eval_reason: str
    eval_time: datetime

class ReplyEval(ReplyEvalBase):
    pass