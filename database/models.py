from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    DateTime,
    JSON,
    LargeBinary,
)
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy.types import Unicode, UnicodeText
from datetime import datetime


# PersonalInfo Table
class PersonalInfo(Base):
    __tablename__ = "PersonalInfo"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(Unicode(100), nullable=False)

    auth_provider = Column(Unicode(100), nullable=False)  # eg. google, apple, wechat
    union_id = Column(Unicode(100), nullable=False)  # union_id
    unique_id = Column(Unicode(100), nullable=False, unique=True)  # auth:union_id

    gender = Column(Unicode(50))
    age = Column(Unicode(50))  # age
    phone = Column(Unicode(50))
    email = Column(Unicode(50))
    avatar = Column(UnicodeText)  # url

    tag = Column(Unicode(50), nullable=True)
    tag_description = Column(UnicodeText, nullable=True)
    issues = Column(Unicode(100))
    job_id = Column(Unicode(100))
    num_diamond = Column(Integer)
    registration_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    eq_scores = relationship("EQScore", back_populates="person")
    courses = relationship("PersonalInfoCourses", back_populates="person")
    chat_histories = relationship("ChatHistory", back_populates="person")


# EQScore Table
class EQScore(Base):
    __tablename__ = "EQScore"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("PersonalInfo.id"), nullable=False)
    perception_score = Column(Integer)
    perception_detail = Column(UnicodeText)
    social_skill_score = Column(Integer)
    social_skill_detail = Column(UnicodeText)
    self_regulation_score = Column(Integer)
    self_regulation_detail = Column(UnicodeText)
    empathy_score = Column(Integer)
    empathy_detail = Column(UnicodeText)
    motivation_score = Column(Integer)
    motivation_detail = Column(UnicodeText)
    summary = Column(UnicodeText)
    detail = Column(UnicodeText)
    detail_summary = Column(UnicodeText)
    overall_suggestion = Column(UnicodeText)
    job_id = Column(String(100))

    person = relationship("PersonalInfo", back_populates="eq_scores")


# Courses Table
class Courses(Base):
    __tablename__ = "Courses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_dim = Column(Unicode(50), nullable=False)  # zh: 掌控力， en：self-regulation
    course_level = Column(Integer)
    prompt = Column(UnicodeText)  # for LLM
    title = Column(UnicodeText)
    background = Column(UnicodeText)
    location = Column(UnicodeText)
    npc = Column(UnicodeText)
    locale = Column(UnicodeText)
    task = Column(UnicodeText)
    image = Column(UnicodeText)  # url
    border_color = Column(Unicode(50), nullable=True)  # Hex code
    background_color = Column(Unicode(50), nullable=True)  # Hex code
    theme = Column(UnicodeText, nullable=True)


# PersonalInfoCourses Table (Many-to-Many relationship between PersonalInfo and Courses)
class PersonalInfoCourses(Base):
    __tablename__ = "PersonalInfoCourses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("PersonalInfo.id"))
    course_id = Column(Integer, ForeignKey("Courses.id"))
    course_dim = Column(Unicode(50), nullable=False)
    course_level = Column(Integer)
    status = Column(Unicode(50))
    result = Column(Integer)  # number of stars
    comment1 = Column(UnicodeText)
    comment2 = Column(UnicodeText)
    comment3 = Column(UnicodeText)
    locale = Column(UnicodeText)

    person = relationship("PersonalInfo", back_populates="courses")


# ChatHistory Table
class ChatHistory(Base):
    __tablename__ = "ChatHistory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("PersonalInfo.id"), nullable=False)
    chatHistory = Column(UnicodeText, nullable=False)  # 存储聊天记录
    summary = Column(UnicodeText, nullable=False)  # 存储聊天记录总结
    low_dim = Column(UnicodeText, nullable=False)
    analysis = Column(UnicodeText, nullable=False)  # 存储分析信息

    # 定义与 User 表的关系
    person = relationship("PersonalInfo", back_populates="chat_histories")


# ReplyState Table
class ReplyState(Base):
    __tablename__ = "HighEqReplyState"

    product = Column(Unicode(100), primary_key=True)
    userId = Column(Unicode(100), primary_key=True)
    chat_history = Column(UnicodeText)
    stage2_output = Column(UnicodeText)
    stage_number = Column(Integer)


class ReplyEval(Base):
    __tablename__ = "ReplyEval"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_history = Column(UnicodeText, nullable=False)
    analysis = Column(UnicodeText, nullable=False)
    suggest_response = Column(UnicodeText, nullable=False)
    eval_score = Column(UnicodeText, nullable=False)
    eval_reason = Column(UnicodeText, nullable=False)
    eval_time = Column(DateTime, nullable=False)
