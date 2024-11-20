from fastapi.responses import JSONResponse
import json
import os
import requests
from database import crud, schemas, database
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request

weixin_appid = os.getenv('WEIXIN_APPID')
weixin_secret = os.getenv('WEIXIN_APPSECRET')

router = APIRouter()

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
    personal_info = crud.get_personal_info_by_name(db, openid)
    if personal_info is None:
        return JSONResponse(status_code=200, content={
            "message": response.json(),
            "isNewUser": True,
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
    pass

# google登录
@router.post("/google/login")
async def login_google(request: Request, db: Session = Depends(database.get_db)):
    pass