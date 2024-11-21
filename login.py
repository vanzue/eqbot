from fastapi.responses import JSONResponse
import json
import os
import uuid
import requests
from database import crud, schemas, database
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request

weixin_appid = os.getenv('WEIXIN_APPID')
weixin_secret = os.getenv('WEIXIN_APPSECRET')

router = APIRouter()

def create_profile_endpoint(name, unique_id, source, db: Session = Depends(database.get_db)):
    job_level = ""
    gender = ""
    issues = ""

    job_id = str(uuid.uuid4())

    personal_info_data = schemas.PersonalInfoCreate(
                            name=name, 
                            source=source,
                            unique_id=unique_id,
                            gender=gender, 
                            job_level=job_level, 
                            issues=issues, 
                            job_id=job_id)
    db_personal_info = crud.create_personal_info(db, personal_info_data)

    return job_id, db_personal_info.id

# 小程序
@router.post("/wxprogram/login")
async def line_webhook(request: Request, db: Session = Depends(database.get_db)):
    body = await request.body()
    try:
        body_json = json.loads(body)
    except json.JSONDecodeError as e:
        return JSONResponse(status_code=400, content={"message": "Invalid JSON"})
    code =body_json.get('code')
    headers = {
        "Content-Type": "application/json",
    }

    print(weixin_appid)
    print(weixin_secret)

    message_url = f"https://api.weixin.qq.com/sns/jscode2session?appid={weixin_appid}&secret={weixin_secret}&js_code={code}&grant_type=authorization_code"
    response = requests.get(message_url, headers=headers)

    if response.status_code != 200:
        return JSONResponse(status_code=response.status_code, content={"message": "Failed to get session"})
    print(response.json())


    openid = response.json().get('openid')
    personal_info = crud.get_personal_info_by_unqiueid(db, openid)
    

    if personal_info is None:
        # create new user
        print(response)
        name = response.name
        job_id, user_id = create_profile_endpoint(name, openid, "mini_program", db)

        return JSONResponse(status_code=200, content={
            "message": response.json(),
            "isNewUser": True,
            "jobid": job_id,
            "userid": user_id
              })
    else:
        return JSONResponse(status_code=200, content={
            "message": response.json(),
            "isNewUser": False, 
            "jobid":personal_info.job_id,
            "userid":personal_info.id 
            })
    
# app转微信登录
@router.post("/app2wx/login")
async def login_app(request: Request, db: Session = Depends(database.get_db)):
    body = await request.body()
    try:
        body_json = json.loads(body)
    except json.JSONDecodeError as e:
        return JSONResponse(status_code=400, content={"message": "Invalid JSON"})
    code =body_json.get('code')
    headers = {
        "Content-Type": "application/json",
    }

    print(weixin_appid)
    print(weixin_secret)

    message_url = f"https://api.weixin.qq.com/sns/oauth2/access_token?appid={weixin_appid}&secret={weixin_secret}&code={code}&grant_type=authorization_code"
    # message_url = f"https://api.weixin.qq.com/sns/jscode2session?appid={weixin_appid}&secret={weixin_secret}&js_code={code}&grant_type=authorization_code"
    response = requests.get(message_url, headers=headers)

    if response.status_code != 200:
        return JSONResponse(status_code=response.status_code, content={"message": "Failed to get session"})
    print(response.json())


    openid = response.json().get('openid')
    personal_info = crud.get_personal_info_by_unqiueid(db, openid)

    if personal_info is None:
        # create new user
        print(response)
        name = response.name
        job_id, user_id = create_profile_endpoint(name, openid, "wechat", db)

        return JSONResponse(status_code=200, content={
            "message": response.json(),
            "isNewUser": True,
            "jobid": job_id,
            "userid": user_id
              })
    else:
        return JSONResponse(status_code=200, content={
            "message": response.json(),
            "isNewUser": False, 
            "jobid":personal_info.job_id,
            "userid":personal_info.id 
            })

# google登录
@router.post("/google/login")
async def login_google(request: Request, db: Session = Depends(database.get_db)):
    name = request.name
    openid = request.openid
    personal_info = crud.get_personal_info_by_unqiueid(db, openid)

    if personal_info is None:
        job_id, user_id = create_profile_endpoint(name, openid, "google", db)
        return {
            "isNewUser": True,
            "jobid": job_id,
            "userid": user_id
        }
    else:
        {
            "isNewUser": False,
            "jobid": personal_info.job_id,
            "userid": personal_info.user_id
        }
    pass