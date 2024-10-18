import uuid
import json
from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

import data_types
from database import database, crud, schemas

from llm.chat_battlefield_agent import request_LLM_response, chat_eval, request_LLM_response_v2

router = APIRouter()


@router.post("/chat/battlefield_agent/v2")
def chat_battlefield(request: data_types.BattlefieldRequest, db: Session = Depends(database.get_db)):
    personal_id = request.person_id
    course_id = request.course_id
    
    matching_course = crud.get_course_by_coursid(db, course_id=course_id)
    print(matching_course.prompt)

    response = request_LLM_response_v2(json.loads(request.chat_content), matching_course.prompt)
    return response

@router.post("/chat/battlefield_agent")
def chat_battlefield(request: data_types.BattlefieldRequest, db: Session = Depends(database.get_db)):
    personal_id = request.person_id
    course_id = request.course_id

    matching_course = crud.get_course_by_coursid(db, course_id=course_id)
    print(matching_course.prompt)

    response = request_LLM_response(json.loads(request.chat_content), matching_course.prompt)
    return response


@router.post("/eval/battlefield_agent") 
def create_course_eval(request: data_types.BattlefieldEval, db: Session = Depends(database.get_db)):
    # return chat_eval(request.chat_content)
    eval_data = chat_eval(request.chat_content)['eval']
    course_type, course_level = crud.get_course_by_id(db, course_id=request.course_id)
    # print(course_type, course_level)

    # update stars
    person_star = request.person_star
    # db_person = crud.get_personal_id_by_personid(db, personid=request.person_id)
    # db_person.num_star += person_star
    db_star = crud.update_personal_stars(db, id=request.person_id, num_stars=person_star)
    # print("number of stars: ", db_star)

    # 创建新的数据库条目
    course_entry = schemas.PersonalInfoCoursesCreate(
        person_id=request.person_id,
        course_id=request.course_id,
        course_type=course_type,
        course_level=course_level, 
        status=request.status,
        result=request.result,
        comment1=eval_data[0]['analysis'] if len(eval_data) > 0 else None,
        comment2=eval_data[1]['analysis'] if len(eval_data) > 1 else None,
        comment3=eval_data[2]['analysis'] if len(eval_data) > 2 else None
    )
    # print(eval_data[0]['analysis'] if len(eval_data) > 0 else None)
    # print(eval_data[1]['analysis'] if len(eval_data) > 1 else None)
    # print(eval_data[2]['analysis'] if len(eval_data) > 2 else None)

    # create new
    db_course = crud.get_coursesperson_by_person_id(db, request.person_id, request.course_id)
    # print(db_course.person_id, db_course.course_id)
    if db_course is None:
        print("not have")
        db_course = crud.create_personal_info_course(db, course_entry)
    else:
        print("have")
        db_course = crud.update_personal_info_course(db, 
                                                    person_id=request.person_id,
                                                    course_id=request.course_id,
                                                    course_level=course_level,
                                                    status=request.status,
                                                    result=request.result,
                                                    comment1=eval_data[0]['analysis'] if len(eval_data) > 0 else None,
                                                    comment2=eval_data[1]['analysis'] if len(eval_data) > 1 else None,
                                                    comment3=eval_data[2]['analysis'] if len(eval_data) > 2 else None)
    return {"db_course": db_course}



@router.get("/get_battlefield_agent/{person_id}")
def get_battlefield(person_id: int, db: Session = Depends(database.get_db)):
    eq_scores = crud.get_eq_scores_by_person_id(db, person_id=person_id)

    if not eq_scores:
        print("no eq scores")
        lowest_dimension = 1
    else:
        scores = {
            "dimension1": eq_scores.dimension1_score,
            "dimension2": eq_scores.dimension2_score,
            "dimension3": eq_scores.dimension3_score,
            "dimension4": eq_scores.dimension4_score,
            "dimension5": eq_scores.dimension5_score
        }
        
        # 找到最低分的维度
        lowest_dimension_key = min(scores, key=scores.get)
        lowest_dimension = int(lowest_dimension_key.replace("dimension", ""))
        
    eq_dimensions = ["情绪侦查力", "情绪掌控力", "人际平衡术", "沟通表达力", "社交得体度"]
    # eq_type = eq_dimensions[lowest_dimension]
    eq_type = "情绪掌控力"

    person_course = crud.get_coursesperson_by_person_id_all(db, person_id=person_id)
    if not person_course:
        new_course = crud.get_course_by_course_type_and_level(db, course_type=eq_type, course_level=1)
        return {"courses": [new_course.id]}
    else:
        return {"courses": person_course}
    # return {"course": person_course}