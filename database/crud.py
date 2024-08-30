from sqlalchemy.orm import Session
from . import models, schemas

# CRUD for PersonalInfo

def create_personal_info(db: Session, personal_info: schemas.PersonalInfoCreate):
    db_personal_info = models.PersonalInfo(
        name=personal_info.name, 
        tag=personal_info.tag, 
        tag_description=personal_info.tag_description
    )
    db.add(db_personal_info)
    db.commit()
    db.refresh(db_personal_info)
    return db_personal_info


def get_personal_info(db: Session, personal_info_id: str):
    return db.query(models.PersonalInfo).filter(models.PersonalInfo.id == personal_info_id).first()


def get_personal_infos(db: Session, id: int):
    return db.query(models.PersonalInfo).filter(models.PersonalInfo.id == id).one_or_none()

def get_personal_id_by_name(db: Session, name: str):
    personal_info = db.query(models.PersonalInfo).filter(models.PersonalInfo.name == name).one_or_none()
    return personal_info.id

def delete_personal_info(db: Session, personal_info_id: str):
    db_personal_info = get_personal_info(db, personal_info_id)
    if db_personal_info:
        db.delete(db_personal_info)
        db.commit()
    return db_personal_info

# CRUD for EQScore

def create_eq_score(db: Session, eq_score: schemas.EQScoreCreate):
    db_eq_score = models.EQScore(
        person_id=eq_score.person_id,
        dimension1_score=eq_score.dimension1_score,
        dimension1_detail=eq_score.dimension1_detail,
        dimension2_score=eq_score.dimension2_score,
        dimension2_detail=eq_score.dimension2_detail,
        dimension3_score=eq_score.dimension3_score,
        dimension3_detail=eq_score.dimension3_detail,
        dimension4_score=eq_score.dimension4_score,
        dimension4_detail=eq_score.dimension4_detail,
        dimension5_score=eq_score.dimension5_score,
        dimension5_detail=eq_score.dimension5_detail,
        summary=eq_score.summary,
        detail=eq_score.detail,
        overall_suggestion=eq_score.overall_suggestion
    )
    db.add(db_eq_score)
    db.commit()
    db.refresh(db_eq_score)
    return db_eq_score


def get_eq_scores_by_person_id(db: Session, person_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.EQScore).filter(models.EQScore.person_id == person_id).offset(skip).limit(limit).all()


def delete_eq_score(db: Session, eq_score_id: int):
    db_eq_score = db.query(models.EQScore).filter(models.EQScore.id == eq_score_id).first()
    if db_eq_score:
        db.delete(db_eq_score)
        db.commit()
    return db_eq_score


# CRUD for Courses

def create_course(db: Session, course: schemas.CoursesCreate):
    db_course = models.Courses(
        course_name=course.course_name, 
        course_description=course.course_description
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


def get_courses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Courses).offset(skip).limit(limit).all()


def delete_course(db: Session, course_id: int):
    db_course = db.query(models.Courses).filter(models.Courses.id == course_id).first()
    if db_course:
        db.delete(db_course)
        db.commit()
    return db_course

# CRUD for PersonalInfoCourses (Many-to-Many Relationship)

def add_course_to_personal_info(db: Session, personal_info_courses: schemas.PersonalInfoCoursesCreate):
    db_personal_info_course = models.PersonalInfoCourses(
        person_id=personal_info_courses.person_id, 
        course_id=personal_info_courses.course_id
    )
    db.add(db_personal_info_course)
    db.commit()
    return db_personal_info_course


def get_personal_info_courses(db: Session, person_id: str):
    return db.query(models.PersonalInfoCourses).filter(models.PersonalInfoCourses.person_id == person_id).all()


def remove_course_from_personal_info(db: Session, person_id: str, course_id: int):
    db_personal_info_course = db.query(models.PersonalInfoCourses).filter(
        models.PersonalInfoCourses.person_id == person_id,
        models.PersonalInfoCourses.course_id == course_id
    ).first()
    if db_personal_info_course:
        db.delete(db_personal_info_course)
        db.commit()
    return db_personal_info_course

# CRUD for Contact

def create_contact(db: Session, contact: schemas.ContactCreate):
    db_contact = models.Contact(
        person_id=contact.person_id,
        name=contact.name,
        tag=contact.tag,
        contact_relationship =contact.contact_relationship 
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def get_contacts_by_person_id(db: Session, person_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.Contact).filter(models.Contact.person_id == person_id).offset(skip).limit(limit).all()


def delete_contact(db: Session, contact_id: str):
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact

# CRUD for ChatRecords

def create_chat_record(db: Session, chat_record: schemas.ChatRecordsCreate):
    db_chat_record = models.ChatRecords(
        person_id=chat_record.person_id,
        contact_id=chat_record.contact_id,
        chat_time=chat_record.chat_time,
        chat_content=chat_record.chat_content
    )
    db.add(db_chat_record)
    db.commit()
    db.refresh(db_chat_record)
    return db_chat_record


def get_chat_records_by_person_id(db: Session, person_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.ChatRecords).filter(models.ChatRecords.person_id == person_id).offset(skip).limit(limit).all()


def delete_chat_record(db: Session, chat_record_id: int):
    db_chat_record = db.query(models.ChatRecords).filter(models.ChatRecords.id == chat_record_id).first()
    if db_chat_record:
        db.delete(db_chat_record)
        db.commit()
    return db_chat_record
