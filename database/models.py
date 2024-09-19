from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy.types import Unicode, UnicodeText

# PersonalInfo Table
class PersonalInfo(Base):
    __tablename__ = 'PersonalInfo'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(Unicode(100), nullable=False)
    gender = Column(Unicode(50))
    tag = Column(Unicode(50), nullable=True)
    tag_description = Column(UnicodeText, nullable=True)
    job_level = Column(Unicode(50))
    issues = Column(Unicode(100))
    job_id = Column(Unicode(100))

    eq_scores = relationship("EQScore", back_populates="person")
    contacts = relationship("Contact", back_populates="person")
    chat_records = relationship("ChatRecords", back_populates="person")

# EQScore Table
class EQScore(Base):
    __tablename__ = 'EQScore'

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey('PersonalInfo.id'), nullable=False)
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
    overall_suggestion = Column(UnicodeText)
    job_id = Column(String(100))

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
    name = Column(Unicode(100), nullable=False)
    tag = Column(Unicode(50))
    contact_relationship = Column(Unicode(50))

    person = relationship("PersonalInfo", back_populates="contacts")
    chat_records = relationship("ChatRecords", back_populates="contact")
    subordinate_analysis = relationship("SubordinateAnalysis", back_populates="contact", uselist=False)  # 一对一关系
    supervisor_analysis = relationship("SupervisorAnalysis", back_populates="contact", uselist=False)  # 一对一关系

# ChatRecords Table
class ChatRecords(Base):
    __tablename__ = 'ChatRecords'

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey('PersonalInfo.id'), nullable=False)
    contact_id = Column(Integer, ForeignKey('Contact.id'), nullable=False)
    chat_time = Column(DateTime)  # Use DateTime instead of String
    chat_content = Column(UnicodeText)

    person = relationship("PersonalInfo", back_populates="chat_records")
    contact = relationship("Contact", back_populates="chat_records")

# Subordinate Analysis
class SubordinateAnalysis(Base):
    __tablename__ = 'subordinate_analysis'

    id = Column(Integer, primary_key=True, autoincrement=True)
    contact_id = Column(Integer, ForeignKey('Contact.id'), nullable=False)
    relationship_analysis = Column(UnicodeText, nullable=False)
    work_compatibility = Column(UnicodeText, nullable=False)  # 共事契合度（1-5分）
    cunning_index = Column(UnicodeText, nullable=False)       # 心眼子指数（0-100分）
    work_personality = Column(UnicodeText, nullable=False)       # 职场性格分析
    interests = Column(UnicodeText, nullable=False)              # 感兴趣的话题
    bad_colleague_risk = Column(UnicodeText, nullable=False)     # 鉴别坏同事的结论

    # 定义与同事表的关系
    contact = relationship("Contact", back_populates="subordinate_analysis")


class SupervisorAnalysis(Base):
    __tablename__ = 'supervisor_analysis'

    id = Column(Integer, primary_key=True, autoincrement=True)
    contact_id = Column(Integer, ForeignKey('Contact.id'), nullable=False)
    relationship_analysis = Column(UnicodeText, nullable=False)  # 关系分析
    interaction_suggestions = Column(UnicodeText, nullable=False)  # 相处建议
    leader_opinion_of_me = Column(UnicodeText, nullable=False)  # 对我的看法
    pua_detection = Column(UnicodeText, nullable=False)  # PUA鉴别
    preferred_subordinate = Column(UnicodeText, nullable=False)  # 喜欢什么样的下属
    gift_recommendation = Column(UnicodeText, nullable=False)  # 礼物推荐

    # 关系定义：关联领导信息
    contact = relationship("Contact", back_populates="supervisor_analysis")