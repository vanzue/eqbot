from pydantic import BaseModel, Field
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
    overall_suggestion: Optional[str]


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
    course_name: str
    course_description: Optional[str]


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
    contact_relationship : Optional[str]


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



class UserInfo(BaseModel):
    username: str = Field(None, example="Jay Park")

class UserPreference(BaseModel):
    gender: str = Field(None, example="男")
    issues: List[str] = Field(None, example=["不太擅长回复消息"])

class UserTest(BaseModel):
    answer1: str = Field(None, example="等待领导决定")
    answer2: str = Field(None, example="不理他")
    answer3: str = Field(None, example="那我喝吧")
    answer4: str = Field(None, example="帮客户清理并解释项目情况")

class CreateUserRequest(BaseModel):
    info: UserInfo
    preference: UserPreference
    test: UserTest