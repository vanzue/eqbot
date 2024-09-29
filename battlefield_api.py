import uuid
import json
from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

import data_types
from database import database

from llm.chat_battlefield import request_LLM_response

router = APIRouter()



@router.post("/chat/batttlefield")
def chat_battlefield(request: data_types.ChatBattlefieldRequest, db: Session = Depends(database.get_db)):
    response = request_LLM_response(json.loads(request.chat_content))
    return response
    