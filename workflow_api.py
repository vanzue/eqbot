import uuid
from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional

from database import database, schemas, crud
import helper

router = APIRouter()

# create a new user
async def create_personal_info_endpoint(    
    name: str,
    gender: str,
    job_level: str,
    issues: str,
    job_id: str,
    tag: Optional[str] = None,
    tag_description: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    personal_info_data = schemas.PersonalInfoCreate(
                            name=name, 
                            gender=gender, 
                            tag=tag, 
                            tag_description=tag_description, 
                            job_level=job_level, 
                            issues=issues, 
                            job_id=job_id)
    db_personal_info = crud.create_personal_info(db, personal_info_data)
    return db_personal_info


# create a new eq score report
async def create_eqscore_endpoint(person_id: int, scores_details:dict, job_id: str, db: Session = Depends(database.get_db)):
    eq_score_data = schemas.EQScoreCreate(
            person_id=person_id,
            dimension1_score=scores_details['dimension1_score'],
            dimension1_detail=scores_details['dimension1_detail'],
            dimension2_score=scores_details['dimension2_score'],
            dimension2_detail=scores_details['dimension2_detail'],
            dimension3_score=scores_details['dimension3_score'],
            dimension3_detail=scores_details['dimension3_detail'],
            dimension4_score=scores_details['dimension4_score'],
            dimension4_detail=scores_details['dimension4_detail'],
            dimension5_score=scores_details['dimension5_score'],
            dimension5_detail=scores_details['dimension5_detail'],
            summary=scores_details['summary'],
            detail=scores_details['detail'],
            overall_suggestion=scores_details['overall_suggestion'],
            job_id=job_id
        )
    db_eq_score = crud.create_eq_score(db, eq_score_data)
    return db_eq_score


# signup as a new user and get the EQ Score Report
@router.post("/create_profile")
async def create_profile(request: schemas.CreateUserRequest, db: Session = Depends(database.get_db)):
    # Receive all the info from frontend
    # personal info
    name = request.name
    
    # preference
    job_level = request.job_level
    gender = request.gender
    concerns = request.concerns
    issues = ", ".join(concerns)

    # tags = ["超绝顿感力", "情绪小火山", "职场隐士", "交流绝缘体", "交流绝缘体"]
    # tag_description = ["超绝顿感力tag_description", "情绪小火山tag_description", "职场隐士tag_description", "交流绝缘体tag_description", "交流绝缘体tag_description"]
    job_id = str(uuid.uuid4())

    await create_personal_info_endpoint(name=name, gender=gender, job_level=job_level, issues=issues, job_id=job_id, db=db)
    
    return {"job_id": job_id}



@router.get("/get_page/{job_id}")
async def get_homepage(job_id: str, db: Session = Depends(database.get_db)):
    # profile & eq scores
    personal_info = crud.get_personal_info_by_job_id(db, job_id)
    eq_scores = crud.get_eq_scores_by_job_id(db, job_id)

    if not personal_info:
        return {"message": "Uncomplete personal info"}
    if not eq_scores:
        return {"message": "Uncomplete eq scores"}
    
    scores = [eq_scores.dimension1_score, 
              eq_scores.dimension2_score, 
              eq_scores.dimension3_score, 
              eq_scores.dimension4_score, 
              eq_scores.dimension5_score]
    overall_score = helper.calculate_average(*scores)
    
    # network
    contacts = crud.get_contacts_by_person_name(db, personal_info.name)
    contacts_list = []
    for contact in contacts:
        contacts_list.append(contact.name)


    response = {
        "personal_info": {
            "name": personal_info.name,
            "tag": personal_info.tag,
            "tag_description": personal_info.tag_description,
            "job_id": personal_info.job_id
        },
        "eq_scores": {
            "score": overall_score, 
            "dimension1_score": eq_scores.dimension1_score, "dimension1_detail": eq_scores.dimension1_detail,
            "dimension2_score": eq_scores.dimension2_score, "dimension2_detail": eq_scores.dimension2_detail,
            "dimension3_score": eq_scores.dimension3_score, "dimension3_detail": eq_scores.dimension3_detail,
            "dimension4_score": eq_scores.dimension4_score, "dimension4_detail": eq_scores.dimension4_detail,
            "dimension5_score": eq_scores.dimension5_score, "dimension5_detail": eq_scores.dimension5_detail,
            "summary": eq_scores.summary,
            "detail": eq_scores.detail,
            "overall_suggestion": eq_scores.overall_suggestion
        },
        "contacts": contacts_list
    }
    
    return {"response": response}


@router.get("/get_analysis_detail/{job_id}")
async def get_analysis_detail(job_id: str, db: Session = Depends(database.get_db)):
    eq_scores = crud.get_eq_scores_by_job_id(db, job_id)

    if not eq_scores:
        return {"message": "Uncomplete eq scores"}
    
    response = {
        "dimension1_score": eq_scores.dimension1_score, "dimension1_detail": eq_scores.dimension1_detail,
        "dimension2_score": eq_scores.dimension2_score, "dimension2_detail": eq_scores.dimension2_detail,
        "dimension3_score": eq_scores.dimension3_score, "dimension3_detail": eq_scores.dimension3_detail,
        "dimension4_score": eq_scores.dimension4_score, "dimension4_detail": eq_scores.dimension4_detail,
        "dimension5_score": eq_scores.dimension5_score, "dimension5_detail": eq_scores.dimension5_detail,
    }
    
    return {"response": response}


# login to the existed user
@router.post("/login_personal_info/{name}")
def loginin_user(request: Request, name: str, db: Session = Depends(database.get_db)):
    personal_id = crud.get_personal_id_by_name(db, name=name)

    return personal_id