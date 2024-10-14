import uuid
import json
from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

import data_types
from database import database, crud

from llm.chat_battlefield import request_LLM_response, chat_eval

router = APIRouter()



@router.post("/chat/batttlefield")
def chat_battlefield(request: data_types.BattlefieldRequest, db: Session = Depends(database.get_db)):
    personal_id = request.person_id

    eq_scores = crud.get_eq_scores_by_person_id(db, person_id=personal_id)

    if not eq_scores:
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
        lowest_dimension = min(scores, key=scores.get)
        
    eq_dimensions = ["情绪侦查力", "情绪掌控力", "人际平衡术", "沟通表达力", "社交得体度"]
    eq_type = eq_dimensions[lowest_dimension]

    person_course = crud.get_courses_by_person_id(db, person_id=personal_id)
    if not person_course:
        matching_courses = crud.get_course_by_course_type_and_level(db, course_type=eq_type, course_level=1)
    
    # TBD：根据个人进度，匹配的课程
    matching_courses = crud.get_course_by_course_type_and_level(db, course_type=eq_type, course_level=1)

    response = request_LLM_response(json.loads(request.chat_content), matching_courses.prompt)
    return response

@router.post("/eval/battlefield") 
def create_course_eval(request: data_types.BattlefieldRequest, db: Session = Depends(database.get_db)):
    return chat_eval(request.chat_content)
    # TODO: Implement this 存db库
    # course_eval = schemas.CourseEvalCreate(course_id=request.course_id,
    #                                        eval_content=request.chat_content,
    #                                        eval_time=datetime.now())
    # crud.create_course_eval(db, course_eval)
    # return {"course_eval_id": course_eval.id}
