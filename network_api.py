from fastapi import APIRouter, HTTPException, UploadFile, Depends, File
from sqlalchemy.orm import Session
import os
import uuid

import data_types
from database import crud, database, schemas
from datetime import datetime
from llm.chat_eval import retry_parse_LLMresponse_with_subordinate, retry_parse_LLMresponse_with_supervisor
from llm.image2chat import image2text


router = APIRouter()

@router.post("/create_contact_profile")
def create_contact_profile(request: data_types.ContactProfileCreate, db: Session = Depends(database.get_db)):
    personal_info_id = crud.get_personal_id_by_name(db, request.personal_name)
    contact_data = schemas.ContactCreate(person_id=personal_info_id, 
                                        name=request.name, 
                                        tag=request.tag, 
                                        contact_relationship=request.contact_relationship)
    contact = crud.create_contact(db, contact_data)
    return {"contact_id": contact.id}



@router.post("/create_subordinate_analysis")
def create_subordinate_analysis(request: data_types.ChatCreate, db: Session = Depends(database.get_db)):
    personal_info_id = crud.get_personal_id_by_name(db, request.personal_name)
    chat_record = schemas.ChatRecordsCreate(person_id=personal_info_id, 
                                            contact_id=request.contact_id, 
                                            chat_time=datetime.now(),
                                            chat_content=request.chat_content)
    crud.create_chat_record(db, chat_record)

    response = retry_parse_LLMresponse_with_subordinate(request.chat_content)

    analysis_data = schemas.SubordinateAnalysisCreate(contact_id=request.contact_id, 
                                                      relationship_analysis=response['relationship_analysis'], 
                                                      work_compatibility=response['work_compatibility'], 
                                                      cunning_index=response['cunning_index'], 
                                                      work_personality=response['work_personality'], 
                                                      interests=response['interests'], 
                                                      bad_colleague_risk=response['bad_colleague_risk'])
    db_analysis = crud.create_subordinate_analysis(db, analysis_data)
    return {"analysis_id": db_analysis.id}



@router.post("/create_subordinate_by_chat")
def create_subordinate_by_chat(request: data_types.ChatCreate, db: Session = Depends(database.get_db)):
    personal_id = crud.get_personal_id_by_name(db, request.personal_name)
    db_contact_profile = crud.get_contacts_by_contact_name(db, request.name)


    if not db_contact_profile or db_contact_profile.person_id != personal_id:
        print("新的contact subordinate")
        contact_profile = create_contact_profile(request, db)
        request.contact_id = contact_profile["contact_id"]
    else:
        print("已有的contact subordinate")
        request.contact_id = db_contact_profile.id
    
    create_subordinate_analysis(request, db)
    return {"message": "Subordinate created successfully"}


@router.post("/create_supervisor_analysis")
def create_supervisor_analysis(request: data_types.ChatCreate, db: Session = Depends(database.get_db)):
    personal_info_id = crud.get_personal_id_by_name(db, request.personal_name)
    chat_record = schemas.ChatRecordsCreate(person_id=personal_info_id, 
                                            contact_id=request.contact_id, 
                                            chat_time=datetime.now(),
                                            chat_content=request.chat_content)
    crud.create_chat_record(db, chat_record)

    response = retry_parse_LLMresponse_with_supervisor(request.chat_content)

    analysis_data = schemas.SupervisorAnalysisCreate(contact_id=request.contact_id, 
                                                      relationship_analysis=response['relationship_analysis'], 
                                                      interaction_suggestions=response['interaction_suggestions'], 
                                                      leader_opinion_of_me=response['leader_opinion_of_me'], 
                                                      pua_detection=response['pua_detection'], 
                                                      preferred_subordinate=response['preferred_subordinate'], 
                                                      gift_recommendation=response['gift_recommendation'])
    db_analysis = crud.create_supervisor_analysis(db, analysis_data)
    return {"analysis_id": db_analysis.id}


@router.post("/create_supervisor_by_chat")
def create_supervisor_by_chat(request: data_types.ChatCreate, db: Session = Depends(database.get_db)):
    personal_id = crud.get_personal_id_by_name(db, request.personal_name)
    db_contact_profile = crud.get_contacts_by_contact_name(db, request.name)

    if not db_contact_profile or db_contact_profile.person_id != personal_id:
        print("新的contact supervisor")
        contact_profile = create_contact_profile(request, db)
        request.contact_id = contact_profile["contact_id"]
    else:
        print("已有的contact supervisor")
        request.contact_id = db_contact_profile.id

    create_supervisor_analysis(request, db)
    return {"message": "Supervisor created successfully"}


@router.get("/get_contact_profile/{contact_id}")
def get_contact_profile(contact_id: int, db: Session = Depends(database.get_db)):
    db_contact = crud.get_contacts_by_contact_id(db, contact_id)

    if db_contact.contact_relationship == "subordinate":
        contact_analysis = crud.get_subordinate_analysis_by_contact_id(db, contact_id)
        profile = {
            "name": db_contact.name,
            "tag": db_contact.tag,
            "relationship_analysis": contact_analysis.relationship_analysis,
            "work_compatibility": contact_analysis.work_compatibility,
            "cunning_index": contact_analysis.cunning_index,
            "work_personality": contact_analysis.work_personality,
            "interests": contact_analysis.interests,
            "bad_colleague_risk": contact_analysis.bad_colleague_risk
        }
    elif db_contact.contact_relationship == "supervisor":
        contact_analysis = crud.get_supervisor_analysis_by_contact_id(db, contact_id)
        profile = {
            "name": db_contact.name,
            "tag": db_contact.tag,
            "relationship_analysis": contact_analysis.relationship_analysis,
            "interaction_suggestions": contact_analysis.interaction_suggestions,
            "leader_opinion_of_me": contact_analysis.leader_opinion_of_me,
            "pua_detection": contact_analysis.pua_detection,
            "preferred_subordinate": contact_analysis.preferred_subordinate,
            "gift_recommendation": contact_analysis.gift_recommendation
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid contact relationship")
    
    return {"contact_profile": profile}


@router.post("/upload_image")
async def upload_image(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid image format. Please upload JPEG or PNG image.")
    
    # generate unique filename
    temp_filename = f"{uuid.uuid4()}.png"
    temp_filepath = os.path.join("temp_images", temp_filename)
    os.makedirs("temp_images", exist_ok=True)

    try:
        # download locally
        with open(temp_filepath, "wb") as f:
            f.write(await file.read())

        chat_history = image2text(image_path=temp_filepath)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {e}")
    finally:
        # delete after process
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
    
    return {"chat_history": chat_history}

    