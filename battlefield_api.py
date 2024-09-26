import uuid
from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional

import data_types
from database import database, schemas, crud
import helper

from llm.chat_battlefield import request_LLM_response

router = APIRouter()



@router.post("/chat/batttlefield")
def chat_battlefield(request: data_types.ChatBattlefieldRequest, db: Session = Depends(database.get_db)):
    response = request_LLM_response(request.chat_content)
    return response
    