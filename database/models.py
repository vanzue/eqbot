from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from .database import Base

# PersonalInfo Table


class PersonalInfo(Base):
    __tablename__ = 'PersonalInfo'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    eq_scores = relationship("EQScore", back_populates="person")
    contacts = relationship("Contact", back_populates="person")
    courses = relationship("PersonalInfoCourses", back_populates="person")
    chat_records = relationship("ChatRecords", back_populates="person")

# EQScore Table


class EQScore(Base):
    __tablename__ = 'EQScore'

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey('PersonalInfo.id'))
    dimension1_score = Column(Integer)
    dimension2_score = Column(Integer)
    dimension3_score = Column(Integer)
    dimension4_score = Column(Integer)
    dimension5_score = Column(Integer)
    overall_analysis = Column(Text)

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

    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String(100), nullable=False)
    course_description = Column(Text)

# PersonalInfoCourses Table


class PersonalInfoCourses(Base):
    __tablename__ = 'PersonalInfoCourses'

    person_id = Column(Integer, ForeignKey(
        'PersonalInfo.id'), primary_key=True)
    course_id = Column(Integer, ForeignKey('Courses.id'), primary_key=True)

    person = relationship("PersonalInfo", back_populates="courses")
    course = relationship("Courses")

# Contact Table


class Contact(Base):
    __tablename__ = 'Contact'

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey('PersonalInfo.id'))
    name = Column(String(100), nullable=False)
    tag = Column(String(50))
    relationship_type = Column(String(50))

    person = relationship("PersonalInfo", back_populates="contacts")

# ChatRecords Table


class ChatRecords(Base):
    __tablename__ = 'ChatRecords'

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey('PersonalInfo.id'))
    other_id = Column(Integer, ForeignKey('Contact.id'))
    chat_time = Column(String)  # Use datetime in real case
    chat_content = Column(Text)

    person = relationship("PersonalInfo", back_populates="chat_records")
    contact = relationship("Contact")
