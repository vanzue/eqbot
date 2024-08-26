from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# PersonalInfo Schema
class PersonalInfoBase(BaseModel):
    name: str
    tag: Optional[str]
    tag_description: Optional[str]


class PersonalInfoCreate(PersonalInfoBase):
    pass


class PersonalInfo(PersonalInfoBase):
    id: str  # Changed to str to match the SQLAlchemy model
    eq_scores: List['EQScore'] = []  # Relationship
    contacts: List['Contact'] = []  # Relationship
    chat_records: List['ChatRecords'] = []  # Relationship

    class Config:
        orm_mode = True

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
    overall_suggestion: Optional[str]


class EQScoreCreate(EQScoreBase):
    person_id: str  # ForeignKey to PersonalInfo.id


class EQScore(EQScoreBase):
    id: int
    person_id: str  # ForeignKey to PersonalInfo.id

    class Config:
        orm_mode = True

# InternalTags Schema
class InternalTagsBase(BaseModel):
    tag: str
    tag_description: Optional[str]


class InternalTagsCreate(InternalTagsBase):
    pass


class InternalTags(InternalTagsBase):
    id: int

    class Config:
        orm_mode = True

# Courses Schema
class CoursesBase(BaseModel):
    course_name: str
    course_description: Optional[str]


class CoursesCreate(CoursesBase):
    pass


class Courses(CoursesBase):
    id: int

    class Config:
        orm_mode = True

# PersonalInfoCourses Schema (Many-to-Many relationship between PersonalInfo and Courses)
class PersonalInfoCoursesBase(BaseModel):
    person_id: str  # ForeignKey to PersonalInfo.id
    course_id: int  # ForeignKey to Courses.id


class PersonalInfoCoursesCreate(PersonalInfoCoursesBase):
    pass


class PersonalInfoCourses(PersonalInfoCoursesBase):
    class Config:
        orm_mode = True

# Contact Schema
class ContactBase(BaseModel):
    person_id: str  # ForeignKey to PersonalInfo.id
    name: str
    tag: Optional[str]
    relationship: Optional[str]


class ContactCreate(ContactBase):
    pass


class Contact(ContactBase):
    id: str  # Changed to str to match the SQLAlchemy model

    class Config:
        orm_mode = True

# ChatRecords Schema
class ChatRecordsBase(BaseModel):
    person_id: str  # ForeignKey to PersonalInfo.id
    contact_id: str  # ForeignKey to Contact.id
    chat_time: datetime  # Use DateTime
    chat_content: str


class ChatRecordsCreate(ChatRecordsBase):
    pass


class ChatRecords(ChatRecordsBase):
    id: int

    class Config:
        orm_mode = True
