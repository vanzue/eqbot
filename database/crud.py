from sqlalchemy.orm import Session
from sqlalchemy import desc
from sqlalchemy.exc import NoResultFound
from . import models, schemas

# CRUD for PersonalInfo


def create_personal_info(db: Session, personal_info: schemas.PersonalInfoCreate):
    db_personal_info = models.PersonalInfo(
        name=personal_info.name,
        gender=personal_info.gender,
        tag=personal_info.tag,
        tag_description=personal_info.tag_description,
        job_level=personal_info.job_level,
        issues=personal_info.issues,
        job_id=personal_info.job_id,
        num_star=100
    )
    db.add(db_personal_info)
    db.commit()
    db.refresh(db_personal_info)
    return db_personal_info


def update_personal_info_by_name(
    db: Session,
    name: str,
    personal_info_update: schemas.PersonalInfoUpdate
):
    db_personal_info = db.query(models.PersonalInfo).filter(
        models.PersonalInfo.name == name).first()

    if db_personal_info is None:
        return None

    update_data = personal_info_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_personal_info, key, value)

    db.commit()
    db.refresh(db_personal_info)
    return db_personal_info


def update_personal_stars_by_name(db: Session, name: str, new_stars: int):
    try:
        person = db.query(models.PersonalInfo).filter(
            models.PersonalInfo.name == name).one()
        person.num_star = new_stars
        db.commit()
        return True
    except NoResultFound:
        print(f"No person found with name {name}")
        return False
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
        return False


def get_personal_info(db: Session, personal_info_id: str):
    return db.query(models.PersonalInfo).filter(models.PersonalInfo.id == personal_info_id).first()


def update_personal_stars(db: Session, id: int, num_stars: int):
    db_person = db.query(models.PersonalInfo).filter(
        models.PersonalInfo.id == id).one_or_none()
    db_person.num_star += num_stars

    db.commit()
    db.refresh(db_person)
    return db_person.num_star


def get_personal_infos(db: Session, id: int):
    return db.query(models.PersonalInfo).filter(models.PersonalInfo.id == id).one_or_none()


def get_personal_id_by_name(db: Session, name: str):
    personal_info = db.query(models.PersonalInfo).filter(
        models.PersonalInfo.name == name).limit(1).one_or_none()
    return getattr(personal_info, 'id', '')


def get_personal_info_by_personid(db: Session, personid: int):
    personal_info = db.query(models.PersonalInfo).filter(
        models.PersonalInfo.id == personid).first()
    return personal_info


def get_personal_info_by_name(db: Session, name: str):
    personal_info = db.query(models.PersonalInfo).filter(
        models.PersonalInfo.name == name).limit(1).one_or_none()
    return personal_info\



def get_personal_info_by_job_id(db: Session, job_id: str):
    personal_info = db.query(models.PersonalInfo).filter(
        models.PersonalInfo.job_id == job_id).one_or_none()
    return personal_info


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
        detail_summary=eq_score.detail_summary,
        overall_suggestion=eq_score.overall_suggestion,
        job_id=eq_score.job_id
    )
    db.add(db_eq_score)
    db.commit()
    db.refresh(db_eq_score)
    return db_eq_score


def get_eq_scores_by_person_id(db: Session, person_id: str):
    return db.query(models.EQScore).filter(models.EQScore.person_id == person_id).first()


def get_eq_scores_by_job_id(db: Session, job_id: str):
    return db.query(models.EQScore).filter(models.EQScore.job_id == job_id).one_or_none()


def delete_eq_score(db: Session, eq_score_id: int):
    db_eq_score = db.query(models.EQScore).filter(
        models.EQScore.id == eq_score_id).first()
    if db_eq_score:
        db.delete(db_eq_score)
        db.commit()
    return db_eq_score


# CRUD for Courses

def create_course(db: Session, course: schemas.CoursesCreate):
    db_course = models.Courses(
        course_type=course.course_type,
        course_level=course.course_level,
        prompt=course.prompt
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


def get_courses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Courses).offset(skip).limit(limit).all()


def get_course_by_id(db: Session, course_id: int):
    course = db.query(models.Courses.course_type, models.Courses.course_level).filter(
        models.Courses.id == course_id).first()

    return course.course_type, course.course_level


def get_course_by_course_type_and_level(db: Session, course_type: str, course_level: int):
    return db.query(models.Courses).filter(
        models.Courses.course_type == course_type,
        models.Courses.course_level == course_level
    ).first()


def get_course_by_coursid(db: Session, course_id: int):
    return db.query(models.Courses).filter(
        models.Courses.id == course_id
    ).first()


def delete_course(db: Session, course_id: int):
    db_course = db.query(models.Courses).filter(
        models.Courses.id == course_id).first()
    if db_course:
        db.delete(db_course)
        db.commit()
    return db_course

# CRUD for PersonalInfoCourses (Many-to-Many Relationship)


def create_personal_info_course(db: Session, course_data: schemas.PersonalInfoCoursesCreate):
    new_course = models.PersonalInfoCourses(
        person_id=course_data.person_id,
        course_id=course_data.course_id,
        course_type=course_data.course_type,
        course_level=course_data.course_level,
        status=course_data.status,
        result=course_data.result,
        comment1=course_data.comment1,
        comment2=course_data.comment2,
        comment3=course_data.comment3
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course


def get_coursesperson_by_person_id(db: Session, person_id: int, course_id: int):
    return db.query(models.PersonalInfoCourses).filter(models.PersonalInfoCourses.person_id == person_id,
                                                       models.PersonalInfoCourses.course_id == course_id).one_or_none()


def course_exists(db: Session, person_id: int):
    return db.query(models.PersonalInfoCourses).filter(models.PersonalInfoCourses.person_id == person_id).first() is not None


def update_personal_info_course(db: Session, person_id: int, course_id: int, course_level: int = None, status: str = None, result: int = None, comment1: str = None, comment2: str = None, comment3: str = None):
    course = db.query(models.PersonalInfoCourses).filter(models.PersonalInfoCourses.person_id == person_id,
                                                         models.PersonalInfoCourses.course_id == course_id).first()
    if not course:
        return None

    # 更新字段（如果传递了新的值）
    if course_level is not None:
        course.course_level = course_level
    if status is not None:
        course.status = status
    if result is not None:
        course.result = result
    if comment1 is not None:
        course.comment1 = comment1
    if comment2 is not None:
        course.comment2 = comment2
    if comment3 is not None:
        course.comment3 = comment3

    db.commit()
    db.refresh(course)
    return course


def get_coursesperson_by_person_id_all(db: Session, person_id: str):
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
        contact_relationship=contact.contact_relationship
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def get_contacts_by_person_id(db: Session, person_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.Contact).filter(models.Contact.person_id == person_id).offset(skip).limit(limit).all()


def get_contacts_by_contact_id(db: Session, contact_id: str):
    return db.query(models.Contact).filter(models.Contact.id == contact_id).one_or_none()


def get_contacts_by_contact_name(db: Session, contact_name: str):
    return db.query(models.Contact).filter(models.Contact.name == contact_name).one_or_none()


def get_contacts_by_person_name(db: Session, person_name: str, skip: int = 0, limit: int = 100):
    db_personal_info = db.query(models.PersonalInfo).filter(
        models.PersonalInfo.name == person_name).first()
    if db_personal_info:
        return db.query(models.Contact).filter(models.Contact.person_id == db_personal_info.id)\
            .order_by(desc(models.Contact.id))\
            .offset(skip).limit(limit).all()
    return []


def delete_contact(db: Session, contact_id: str):
    db_contact = db.query(models.Contact).filter(
        models.Contact.id == contact_id).first()
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


def get_chat_records_by_person_id(db: Session, person_id: str):
    return db.query(models.ChatRecords).filter(models.ChatRecords.person_id == person_id).all()


def delete_chat_record(db: Session, chat_record_id: int):
    db_chat_record = db.query(models.ChatRecords).filter(
        models.ChatRecords.id == chat_record_id).first()
    if db_chat_record:
        db.delete(db_chat_record)
        db.commit()
    return db_chat_record

# CRUD for SubordinateAnalysis


def create_subordinate_analysis(db: Session, analysis: schemas.SubordinateAnalysisCreate):
    db_analysis = models.SubordinateAnalysis(
        contact_id=analysis.contact_id,
        relationship_analysis=analysis.relationship_analysis,
        work_compatibility=analysis.work_compatibility,
        cunning_index=analysis.cunning_index,
        work_personality=analysis.work_personality,
        interests=analysis.interests,
        bad_colleague_risk=analysis.bad_colleague_risk
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    return db_analysis


def create_supervisor_analysis(db: Session, analysis: schemas.SupervisorAnalysisCreate):
    db_analysis = models.SupervisorAnalysis(
        contact_id=analysis.contact_id,
        relationship_analysis=analysis.relationship_analysis,
        interaction_suggestions=analysis.interaction_suggestions,
        leader_opinion_of_me=analysis.leader_opinion_of_me,
        pua_detection=analysis.pua_detection,
        preferred_subordinate=analysis.preferred_subordinate,
        gift_recommendation=analysis.gift_recommendation
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    return db_analysis


def get_subordinate_analysis_by_contact_id(db: Session, contact_id: str):
    return db.query(models.SubordinateAnalysis).filter(models.SubordinateAnalysis.contact_id == contact_id).first()


def get_supervisor_analysis_by_contact_id(db: Session, contact_id: str):
    return db.query(models.SupervisorAnalysis).filter(models.SupervisorAnalysis.contact_id == contact_id).first()

# Chat History


def create_chat_history(db: Session, chat: schemas.ChatHistoryCreate):
    db_chat = models.ChatHistory(userId=chat.userId, chatHistory=chat.chatHistory,
                                 summary=chat.summary, analysis=chat.analysis, low_dim=chat.low_dim)
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

# CRUD 操作：获取用户的聊天记录


def get_chat_history_by_user(db: Session, user_id: int):
    return db.query(models.ChatHistory).filter(models.ChatHistory.userId == user_id).all()


def delete_chat_history(db: Session, chat_id: int):
    chat_history = db.query(models.ChatHistory).filter(
        models.ChatHistory.id == chat_id).first()
    if chat_history:
        db.delete(chat_history)
        db.commit()
        return chat_history
    return None

# Get ReplyState by product and userId (composite primary key)


def get_reply_state_by_product_and_user(db: Session, product: str, user_id: str):
    return db.query(models.ReplyState).filter(
        models.ReplyState.product == product,
        models.ReplyState.userId == user_id
    ).first()


def replace_reply_state(db: Session, reply_state_data: schemas.ReplyStateCreate):
    # Try to get the existing record
    db_reply_state = get_reply_state_by_product_and_user(
        db, reply_state_data.product, reply_state_data.userId)

    # If it doesn't exist, create a new one
    if not db_reply_state:
        db_reply_state = models.ReplyState(
            product=reply_state_data.product,
            userId=reply_state_data.userId,
            chat_history=reply_state_data.chat_history,
            stage2_output=reply_state_data.stage2_output,
            stage_number=reply_state_data.stage_number
        )
        db.add(db_reply_state)
    else:
        # Update fields if it exists
        for field, value in reply_state_data.dict(exclude_unset=True).items():
            setattr(db_reply_state, field, value)

    db.commit()
    db.refresh(db_reply_state)
    return db_reply_state


# Delete ReplyState


def delete_reply_state(db: Session, product: str, user_id: str):
    db_reply_state = get_reply_state_by_product_and_user(db, product, user_id)
    if db_reply_state:
        db.delete(db_reply_state)
        db.commit()
        return db_reply_state
    return None

# Get all ReplyState entries


def get_all_reply_states(db: Session):
    return db.query(models.ReplyState).all()
