from fastapi import APIRouter, HTTPException, UploadFile, Depends, File, Form
from sqlalchemy.orm import Session
import os
import uuid
import json

import data_types
from database import crud, database, schemas
from datetime import datetime
from llm.network_analyze import retry_parse_LLMresponse
from llm.image2chat import image2text, parse_chatHistory, get_image2text


router = APIRouter()

@router.post("/create_contact_profile")
def create_contact_profile(request: data_types.ContactProfileCreate, locale: str, db: Session = Depends(database.get_db)):
    personal_info_id = crud.get_personal_id_by_name(db, request.personal_name)
    contact_data = schemas.ContactCreate(person_id=personal_info_id, 
                                        name=request.name, 
                                        tag=request.tag, 
                                        contact_relationship=request.contact_relationship)
    contact = crud.create_contact(db, contact_data)
    return {"contact_id": contact.id}


@router.post("/analyze/screenshot")
async def upload_image(file: UploadFile = File(...), locale: str="en"):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid image format. Please upload JPEG or PNG image.")
    
    # generate unique filename
    temp_filename = f"{uuid.uuid4()}.png"
    temp_filepath = os.path.join("temp_images", temp_filename)
    os.makedirs("temp_images", exist_ok=True)

    with open(temp_filepath, "wb") as f:
            f.write(await file.read())
    try:
        # json_data = image2text(image_path=temp_filepath)
        # res = parse_chatHistory(json_data)
        res = get_image2text(image_path=temp_filepath)
        chat_history = res['chat_history']
        chat_summary = res['summary']
        low_dim = res['low_dim']
    finally:
        # Delete the temporary file after processing
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
    
    return {"chat_history": chat_history, 'summary': chat_summary, 'low_dim': low_dim}


@router.post("/analyze/history")
async def analyze_history_from_image(locale: str = "en", user_id: int = Form(...), file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    chat_history_response = await upload_image(file)
    chat_history = chat_history_response["chat_history"]
    summary = chat_history_response["summary"]
    low_dim = chat_history_response["low_dim"]

    # request LLM analyze chat history
    analysis = retry_parse_LLMresponse(chat_history=chat_history, locale = locale)
    # print(analysis)

    # create it into db
    # print(summary1)
    chat_data = schemas.ChatHistoryCreate(user_id=user_id,
                                         chatHistory=json.dumps(chat_history, ensure_ascii=False),
                                         summary = summary,
                                         analysis=json.dumps(analysis, ensure_ascii=False),
                                         low_dim=low_dim)
    # print(chat_data)
    db_chat = crud.create_chat_history(db, chat_data)
    
    return {"id": db_chat.id, "chatHistory": chat_history, "summary": summary, "analysis": analysis}


@router.delete("/delete_chats/{chat_id}", response_model=schemas.ChatHistory)
def delete_chat(chat_id: int, locale: str, db: Session = Depends(database.get_db)):
    chat_history = crud.delete_chat_history(db=db, chat_id=chat_id)
    if chat_history is None:
        raise HTTPException(status_code=404, detail="Chat history not found")
    return chat_history

@router.get("/{user_id}/analysisList")
async def get_analysis(user_id: int, locale: str, db: Session = Depends(database.get_db)):
    return crud.get_chat_history_by_user(db, user_id=user_id)