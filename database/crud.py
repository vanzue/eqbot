from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from sqlalchemy.exc import NoResultFound
from . import models, schemas

# CRUD for PersonalInfo


def create_personal_info(db: Session, personal_info: schemas.PersonalInfoCreate):
    db_personal_info = models.PersonalInfo(
        name=personal_info.name,
        auth_provider = personal_info.auth_provider,
        union_id = personal_info.union_id,
        unique_id = personal_info.unique_id,
        gender=personal_info.gender,
        age=personal_info.age,
        phone=personal_info.phone,
        email=personal_info.email,
        avatar=personal_info.avatar,
        tag=personal_info.tag,
        tag_description=personal_info.tag_description,
        issues=personal_info.issues,
        job_id=personal_info.job_id,
        num_diamond=500
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


def update_personal_diamond_by_name(db: Session, name: str, new_diamond: int):
    try:
        person = db.query(models.PersonalInfo).filter(
            models.PersonalInfo.name == name).one()
        person.num_diamond = new_diamond
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


def update_personal_diamond(db: Session, id: int, num_diamond: int):
    db_person = db.query(models.PersonalInfo).filter(
        models.PersonalInfo.id == id).one_or_none()
    db_person.num_diamond += num_diamond

    db.commit()
    db.refresh(db_person)
    return db_person.num_diamond

def update_personal_name(db: Session, id: int, new_name: int):
    db_person = db.query(models.PersonalInfo).filter(
        models.PersonalInfo.id == id).one_or_none()
    db_person.name = new_name

    db.commit()
    db.refresh(db_person)
    return db_person.id


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

def get_personal_info_by_unqiueid(db: Session, unique_id: int):
    personal_info = db.query(models.PersonalInfo).filter(
        models.PersonalInfo.unique_id == unique_id).first()
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
        user_id=eq_score.user_id,
        perception_score = eq_score.perception_score,
        perception_detail = eq_score.perception_detail,
        social_skill_score = eq_score.social_skill_score,
        social_skill_detail = eq_score.social_skill_detail,
        self_regulaton_score = eq_score.self_regulaton_score,
        self_regulaton_detail = eq_score.self_regulaton_detail,
        empathy_score = eq_score.empathy_score,
        empathy_detail = eq_score.empathy_detail,
        motivation_score = eq_score.motivation_score,
        motivation_detail = eq_score.motivation_detail,
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


def get_eq_scores_by_person_id(db: Session, user_id: str):
    return db.query(models.EQScore).filter(models.EQScore.user_id == user_id).first()


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
        course_dim=course.course_dim,
        course_level=course.course_level,
        prompt=course.prompt,
        title=course.title,
        npc=course.npc,
        image=course.image
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


def get_courses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Courses).offset(skip).limit(limit).all()


def get_course_by_id(db: Session, course_id: int):
    course = db.query(models.Courses.course_dim, models.Courses.course_level).filter(
        models.Courses.id == course_id).first()

    return course.course_dim, course.course_level


def get_course_by_course_dim_and_level(db: Session, course_dim: str, course_level: int):
    return db.query(models.Courses).filter(
        models.Courses.course_dim == course_dim,
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
        user_id=course_data.user_id,
        course_id=course_data.course_id,
        course_dim=course_data.course_dim,
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

def calculate_total_result(db: Session, user_id: int) -> int:
    # 查询并计算指定用户的所有 result 总和
    total_result = (
        db.query(func.sum(models.PersonalInfoCourses.result))
        .filter(models.PersonalInfoCourses.user_id == user_id)
        .scalar()
    )
    # 如果没有记录，则返回 0
    return total_result or 0

def get_coursesperson_by_person_id(db: Session, person_id: int, course_id: int):
    return db.query(models.PersonalInfoCourses).filter(models.PersonalInfoCourses.user_id == person_id,
                                                       models.PersonalInfoCourses.course_id == course_id).one_or_none()


def course_exists(db: Session, person_id: int):
    return db.query(models.PersonalInfoCourses).filter(models.PersonalInfoCourses.user_id == person_id).first() is not None


def update_personal_info_course(db: Session, person_id: int, course_id: int, course_level: int = None, status: str = None, result: int = None, comment1: str = None, comment2: str = None, comment3: str = None):
    course = db.query(models.PersonalInfoCourses).filter(models.PersonalInfoCourses.user_id == person_id,
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
    return db.query(models.PersonalInfoCourses).filter(models.PersonalInfoCourses.user_id == person_id).all()


def remove_course_from_personal_info(db: Session, person_id: str, course_id: int):
    db_personal_info_course = db.query(models.PersonalInfoCourses).filter(
        models.PersonalInfoCourses.user_id == person_id,
        models.PersonalInfoCourses.course_id == course_id
    ).first()
    if db_personal_info_course:
        db.delete(db_personal_info_course)
        db.commit()
    return db_personal_info_course



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
