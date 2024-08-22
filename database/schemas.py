from pydantic import BaseModel
from typing import List, Optional

# PersonalInfo Schema


class PersonalInfoBase(BaseModel):
    name: str


class PersonalInfoCreate(PersonalInfoBase):
    pass


class PersonalInfo(PersonalInfoBase):
    id: int

    class Config:
        orm_mode = True

# EQScore Schema


class EQScoreBase(BaseModel):
    person_id: int
    dimension1_score: int
    dimension2_score: int
    dimension3_score: int
    dimension4_score: int
    dimension5_score: int
    overall_analysis: Optional[str]


class EQScoreCreate(EQScoreBase):
    pass


class EQScore(EQScoreBase):
    id: int

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

# PersonalInfoCourses Schema


class PersonalInfoCoursesBase(BaseModel):
    person_id: int
    course_id: int


class PersonalInfoCoursesCreate(PersonalInfoCoursesBase):
    pass


class PersonalInfoCourses(PersonalInfoCoursesBase):
    class Config:
        orm_mode = True

# Contact Schema


class ContactBase(BaseModel):
    person_id: int
    name: str
    tag: Optional[str]
    relationship_type: Optional[str]


class ContactCreate(ContactBase):
    pass


class Contact(ContactBase):
    id: int

    class Config:
        orm_mode = True

# ChatRecords Schema


class ChatRecordsBase(BaseModel):
    person_id: int
    other_id: int
    chat_time: str  # Use datetime in real case
    chat_content: str


class ChatRecordsCreate(ChatRecordsBase):
    pass


class ChatRecords(ChatRecordsBase):
    id: int

    class Config:
        orm_mode = True
