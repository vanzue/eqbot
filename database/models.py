from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from .database import Base

# PersonalInfo Table
class PersonalInfo(Base):
    __tablename__ = 'PersonalInfo'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    tag = Column(String(50))
    tag_description = Column(Text)

    eq_scores = relationship("EQScore", back_populates="person")
    contacts = relationship("Contact", back_populates="person")
    chat_records = relationship("ChatRecords", back_populates="person")

# EQScore Table
class EQScore(Base):
    __tablename__ = 'EQScore'

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey('PersonalInfo.id'), nullable=False)
    dimension1_score = Column(Integer)
    dimension1_detail = Column(Text)
    dimension2_score = Column(Integer)
    dimension2_detail = Column(Text)
    dimension3_score = Column(Integer)
    dimension3_detail = Column(Text)
    dimension4_score = Column(Integer)
    dimension4_detail = Column(Text)
    dimension5_score = Column(Integer)
    dimension5_detail = Column(Text)
    summary = Column(Text)
    detail = Column(Text)
    overall_suggestion = Column(Text)

    person = relationship("PersonalInfo", back_populates="eq_scores")

# InternalTags Table
class InternalTags(Base):
    __tablename__ = 'InternalTags'

    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String(50), nullable=False)
    tag_description = Column(Text)

# Courses Table
class Courses(Base):
    __tablename__ = 'Courses'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_name = Column(String(100), nullable=False)
    course_description = Column(Text)

    personal_info_courses = relationship("PersonalInfoCourses", back_populates="course")

# PersonalInfoCourses Table (Many-to-Many relationship between PersonalInfo and Courses)
class PersonalInfoCourses(Base):
    __tablename__ = 'PersonalInfoCourses'

    person_id = Column(Integer, ForeignKey('PersonalInfo.id'), primary_key=True)
    course_id = Column(Integer, ForeignKey('Courses.id'), primary_key=True)

    # person = relationship("PersonalInfo", back_populates="courses")
    course = relationship("Courses", back_populates="personal_info_courses")

# Contact Table
class Contact(Base):
    __tablename__ = 'Contact'

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey('PersonalInfo.id'), nullable=False)
    name = Column(String(100), nullable=False)
    tag = Column(String(50))
    contact_relationship = Column(String(50))

    person = relationship("PersonalInfo", back_populates="contacts")
    chat_records = relationship("ChatRecords", back_populates="contact")

# ChatRecords Table
class ChatRecords(Base):
    __tablename__ = 'ChatRecords'

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey('PersonalInfo.id'), nullable=False)
    contact_id = Column(Integer, ForeignKey('Contact.id'), nullable=False)
    chat_time = Column(DateTime)  # Use DateTime instead of String
    chat_content = Column(Text)

    person = relationship("PersonalInfo", back_populates="chat_records")
    contact = relationship("Contact", back_populates="chat_records")
