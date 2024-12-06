from datetime import datetime
import uuid
from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional

from llm.reply_eval.autoreply_eval import autoreply_eval
from database import database, schemas, crud
from database.crud import create_reply_eval
import helper
import data_types

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
                            job_id=job_id,
                            registration_date=datetime.utcnow())
    db_personal_info = crud.create_personal_info(db, personal_info_data)
    return db_personal_info


# signup as a new user and get the EQ Score Report
@router.post("/create_profile")
async def create_profile(request: data_types.CreateUserRequest, locale: str, db: Session = Depends(database.get_db)):
    # Receive all the info from frontend
    # personal info
    job_id = str(uuid.uuid4())
    
    name = request.name
    auth_provider = request.auth_provider
    union_id = request.union_id
    unique_id = auth_provider + ":" + union_id
    gender = request.gender
    age = request.age
    phone = request.phone
    email = request.email
    avatar = request.avatar
    issues = request.issues

    personal_info_data = schemas.PersonalInfoCreate(
                            name=name, 
                            auth_provider=auth_provider,
                            union_id=union_id,
                            unique_id=unique_id,
                            gender=gender, 
                            age=age,
                            phone=phone,
                            email=email,
                            avatar=avatar,
                            issues=issues, 
                            job_id=job_id,
                            registration_date=datetime.utcnow())
    db_personal_info = crud.create_personal_info(db, personal_info_data)

    return {"job_id": job_id, "user_id": db_personal_info.id}


@router.post("/update_name")
def update_username(request: data_types.UpdateUserName, locale: str, db: Session = Depends(database.get_db)):
    person_id = request.person_id
    new_name = request.new_name

    # update
    crud.update_personal_name(db, person_id, new_name)
    return {"message": "updated new name"}

@router.post("/get_homepage/{personal_id}")
async def get_homepage(personal_id: int, locale: str, db: Session = Depends(database.get_db)):
    # profile & eq scores
    personal_info = crud.get_personal_info_by_personid(db, personal_id)
    eq_scores = crud.get_eq_scores_by_person_id(db, personal_info.id)

    if not eq_scores:
        return {"message": "Uncomplete eq scores"}
    
    scores = [eq_scores.perception_score, 
              eq_scores.social_skill_score, 
              eq_scores.self_regulation_score, 
              eq_scores.empathy_score, 
              eq_scores.motivation_score]
    overall_score = sum(scores)

    # num_star calculate
    num_star = crud.calculate_total_result(db, user_id=personal_id)

    # cal days
    days_till_reg = crud.calculate_days_since_registration(personal_info)

    response = {
        "personal_info": {
            "name": personal_info.name,
            "tag": personal_info.tag,
            "tag_description": personal_info.tag_description,
            "job_id": personal_info.job_id,
            "num_diamond": personal_info.num_diamond,
            "num_star": num_star,
            "days_till_reg": days_till_reg,
            "wordings": "Empathy is a cornerstone in building trust; validating others' feelings with phrases like \"I can see why you feel that way \" builds connection."
        },
        "eq_scores": {
            "score": overall_score, 
            "perception_score": eq_scores.perception_score, "perception_detail": eq_scores.perception_detail,
            "social_skill_score": eq_scores.social_skill_score, "social_skill_detail": eq_scores.social_skill_detail,
            "self_regulation_score": eq_scores.self_regulation_score, "self_regulation_detail": eq_scores.self_regulation_detail,
            "empathy_score": eq_scores.empathy_score, "empathy_detail": eq_scores.empathy_detail,
            "motivation_score": eq_scores.motivation_score, "motivation_detail": eq_scores.motivation_detail,
            "summary": eq_scores.summary,
            "detail": eq_scores.detail,
            "detail_summary": eq_scores.detail_summary,
            "overall_suggestion": eq_scores.overall_suggestion
        }
    }
    
    return {"response": response}

@router.post("/get_analysis/{job_id}")
async def get_analysis(job_id: str, locale: str, db: Session = Depends(database.get_db)):
    # profile & eq scores
    personal_info = crud.get_personal_info_by_job_id(db, job_id)
    eq_scores = crud.get_eq_scores_by_job_id(db, job_id)

    # if not personal_info.tag:
    #     return {"message": "Uncomplete personal info"}
    if not eq_scores:
        return {"message": "Uncomplete eq scores"}
    
    scores = [eq_scores.perception_score, 
              eq_scores.social_skill_score, 
              eq_scores.self_regulation_score, 
              eq_scores.empathy_score, 
              eq_scores.motivation_score]
    overall_score = helper.calculate_average(*scores)

    response = {
        "personal_info": {
            "name": personal_info.name,
            "tag": personal_info.tag,
            "tag_description": personal_info.tag_description,
            "job_id": personal_info.job_id
        },
        "eq_scores": {
            "score": overall_score, 
            "perception_score": eq_scores.perception_score, "perception_detail": eq_scores.perception_detail,
            "social_skill_score": eq_scores.social_skill_score, "social_skill_detail": eq_scores.social_skill_detail,
            "self_regulation_score": eq_scores.self_regulation_score, "self_regulation_detail": eq_scores.self_regulation_detail,
            "empathy_score": eq_scores.empathy_score, "empathy_detail": eq_scores.empathy_detail,
            "motivation_score": eq_scores.motivation_score, "motivation_detail": eq_scores.motivation_detail,
            "summary": eq_scores.summary,
            "detail": eq_scores.detail,
            "detail_summary": eq_scores.detail_summary,
            "overall_suggestion": eq_scores.overall_suggestion
        }
    }
    
    return {"response": response}


@router.post("/get_analysis_detail/{name}")
async def get_analysis_detail(name: str, db: Session = Depends(database.get_db)):
    # profile & eq scores
    personal_info = crud.get_personal_info_by_name(db, name)
    eq_scores = crud.get_eq_scores_by_person_id(db, personal_info.id)
    
    scores = [eq_scores.perception_score, 
              eq_scores.social_skill_score, 
              eq_scores.self_regulation_score, 
              eq_scores.empathy_score, 
              eq_scores.motivation_score]
    overall_score = helper.calculate_average(*scores)

    response = {
        "personal_info": {
            "name": personal_info.name,
            "tag": personal_info.tag,
            "tag_description": personal_info.tag_description,
            "job_id": personal_info.job_id
        },
        "eq_scores": {
            "score": overall_score, 
            "perception_score": eq_scores.perception_score, "perception_detail": eq_scores.perception_detail,
            "social_skill_score": eq_scores.social_skill_score, "social_skill_detail": eq_scores.social_skill_detail,
            "self_regulation_score": eq_scores.self_regulation_score, "self_regulation_detail": eq_scores.self_regulation_detail,
            "empathy_score": eq_scores.empathy_score, "empathy_detail": eq_scores.empathy_detail,
            "motivation_score": eq_scores.motivation_score, "motivation_detail": eq_scores.motivation_detail,
            "summary": eq_scores.summary,
            "detail": eq_scores.detail,
            "detail_summary": eq_scores.detail_summary,
            "overall_suggestion": eq_scores.overall_suggestion
        }
    }
    
    return {"response": response}


# login to the existed user
@router.post("/login_personal_info/{name}")
def loginin_user(request: Request, name: str, db: Session = Depends(database.get_db)):
    personal_id = crud.get_personal_id_by_name(db, name=name)

    return personal_id


# evaluate the user's EQ score
@router.post("/evaluate_reply_eqscore")
def evaluate_eqscore(request: schemas.ReplyEval, db: Session = Depends(database.get_db)):
    # 将 eval_result 拆分成 eval_score 和 eval_reason
    def split_eval_result(eval_result: str):
        eval_parts = eval_result.split("评分依据：")
        eval_score = eval_parts[0].replace("分数：", "").strip()
        eval_reason = eval_parts[1].strip()
        return {"eval_score": eval_score, "eval_reason": eval_reason}
    chat_history = request.chat_history
    analysis = request.analysis
    suggest_response = request.suggest_response
    eval_result = autoreply_eval(chat_history, analysis, suggest_response)
    eval_parts = split_eval_result(eval_result)

    # 获取拆分后的 eval_score 和 eval_reason
    eval_score = eval_parts['eval_score']
    eval_reason = eval_parts['eval_reason']
    print("eval_result: ", eval_result) 
    print("eval_score: ", eval_score)
    print("eval_reason: ", eval_reason)
    reply_eval_create = schemas.ReplyEvalCreate(
        chat_history=chat_history,
        analysis=analysis,
        suggest_response=suggest_response,
        eval_score=eval_score,
        eval_reason=eval_reason,
        eval_time=datetime.utcnow()  # 使用当前时间
    )
    # 创建 reply_eval 数据
    db_reply_eval = create_reply_eval(db, reply_eval_create)
    return db_reply_eval
    # await create_eqscore_endpoint(person_id=person_id, scores_details=scores_details, job_id=job_id, db=db)
    
    # return db_eq_score