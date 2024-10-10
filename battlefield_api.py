import uuid
import json
from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

import data_types
from database import database

from llm.chat_battlefield import request_LLM_response, chat_eval

router = APIRouter()



@router.post("/chat/batttlefield")
def chat_battlefield(request: data_types.BattlefieldRequest, db: Session = Depends(database.get_db)):
    response = request_LLM_response(json.loads(request.chat_content))
    return response

@router.post("/eval/battlefield") 
def create_course_eval(request: data_types.BattlefieldRequest, db: Session = Depends(database.get_db)):
    return chat_eval(request.chat_content)
    # TODO: Implement this
    # course_eval = schemas.CourseEvalCreate(course_id=request.course_id,
    #                                        eval_content=request.chat_content,
    #                                        eval_time=datetime.now())
    # crud.create_course_eval(db, course_eval)
    # return {"course_eval_id": course_eval.id}
