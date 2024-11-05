from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy.types import Unicode, UnicodeText

# PersonalInfo Table
class PersonalInfo(Base):
    __tablename__ = 'PersonalInfo'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(Unicode(100), nullable=False)

    source = Column(Unicode(100), nullable=False)   # eg. google, apple
    unique_id = Column(Unicode(100), nullable=False) # openid

    gender = Column(Unicode(50))
    tag = Column(Unicode(50), nullable=True)
    tag_description = Column(UnicodeText, nullable=True)
    job_level = Column(Unicode(50))
    issues = Column(Unicode(100))
    job_id = Column(Unicode(100))
    num_diamond = Column(Integer)

    eq_scores = relationship("EQScore", back_populates="person")
    courses = relationship("PersonalInfoCourses", back_populates="person")
    chat_histories = relationship("ChatHistory", back_populates="person")


# EQScore Table
class EQScore(Base):
    __tablename__ = 'EQScore'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('PersonalInfo.id'), nullable=False)
    dimension1_score = Column(Integer)
    dimension1_detail = Column(UnicodeText)
    dimension2_score = Column(Integer)
    dimension2_detail = Column(UnicodeText)
    dimension3_score = Column(Integer)
    dimension3_detail = Column(UnicodeText)
    dimension4_score = Column(Integer)
    dimension4_detail = Column(UnicodeText)
    dimension5_score = Column(Integer)
    dimension5_detail = Column(UnicodeText)
    summary = Column(UnicodeText)
    detail = Column(UnicodeText)
    detail_summary = Column(UnicodeText)
    overall_suggestion = Column(UnicodeText)
    job_id = Column(String(100))

    person = relationship("PersonalInfo", back_populates="eq_scores")


# Courses Table
class Courses(Base):
    __tablename__ = 'Courses'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_dim = Column(Unicode(50), nullable=False)
    course_level = Column(Integer)
    prompt = Column(UnicodeText)


# PersonalInfoCourses Table (Many-to-Many relationship between PersonalInfo and Courses)
class PersonalInfoCourses(Base):
    __tablename__ = 'PersonalInfoCourses'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('PersonalInfo.id'))
    course_id = Column(Integer, ForeignKey('Courses.id'))
    course_type = Column(Unicode(50), nullable=False)
    course_level = Column(Integer)
    status = Column(Unicode(50))
    result = Column(Integer)    # number of stars
    comment1 = Column(UnicodeText)
    comment2 = Column(UnicodeText)
    comment3 = Column(UnicodeText)

    person = relationship("PersonalInfo", back_populates="courses")
    # course = relationship("Courses", back_populates="personal_info_courses")


# ChatHistory Table
class ChatHistory(Base):
    __tablename__ = 'ChatHistory'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('PersonalInfo.id'), nullable=False)
    chatHistory = Column(UnicodeText, nullable=False)  # 存储聊天记录
    summary = Column(UnicodeText, nullable=False)  # 存储聊天记录总结
    low_dim = Column(UnicodeText, nullable=False)
    analysis = Column(UnicodeText, nullable=False)  # 存储分析信息

    # 定义与 User 表的关系
    person = relationship("PersonalInfo", back_populates="chat_histories")


# ReplyState Table
class ReplyState(Base):
    __tablename__ = 'HighEqReplyState'

    product = Column(Unicode(100), primary_key=True)
    userId = Column(Unicode(100), primary_key=True)
    chat_history = Column(UnicodeText)
    stage2_output = Column(UnicodeText)
    stage_number = Column(Integer)
