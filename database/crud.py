from sqlalchemy.orm import Session
from . import models, schemas

# CRUD for PersonalInfo


def create_personal_info(db: Session, personal_info: schemas.PersonalInfoCreate):
    db_personal_info = models.PersonalInfo(name=personal_info.name)
    db.add(db_personal_info)
    db.commit()
    db.refresh(db_personal_info)
    return db_personal_info


def get_personal_info(db: Session, personal_info_id: int):
    return db.query(models.PersonalInfo).filter(models.PersonalInfo.id == personal_info_id).first()


def get_personal_infos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.PersonalInfo).offset(skip).limit(limit).all()

# Similarly, you can implement CRUD functions for other models.
