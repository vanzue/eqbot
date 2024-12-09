from fastapi.responses import JSONResponse
import json
import os
import uuid
import requests
from database import crud, schemas, database
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request
from datetime import datetime

import data_types
from WXBizDataCrypt_login import WXBizDataCrypt


weixin_appid = os.getenv('WEIXIN_APPID')
weixin_secret = os.getenv('WEIXIN_APPSECRET')
thrid2weixin_appid = os.getenv('THIRD2WEIXIN_APPID')
thrid2weixin_appsecret = os.getenv('THIRD2WEIXIN_APPSECRET')

router = APIRouter()

def create_profile_endpoint(name, auth_provider, union_id, unique_id, gender, age, phone, email, avatar, db: Session = Depends(database.get_db)):
    gender = ""
    issues = ""
    unique_id = auth_provider + ":" + union_id

    job_id = str(uuid.uuid4())

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

    return job_id, db_personal_info.id

# 小程序
@router.post("/wxprogram/login")
async def line_webhook(request: data_types.MiniProgramLogin, db: Session = Depends(database.get_db)):
    code = request.code
    headers = {
        "Content-Type": "application/json",
    }


    message_url = f"https://api.weixin.qq.com/sns/jscode2session?appid={weixin_appid}&secret={weixin_secret}&js_code={code}&grant_type=authorization_code"
    response = requests.get(message_url, headers=headers)

    if response.status_code != 200:
        return JSONResponse(status_code=response.status_code, content={"message": "Failed to get session"})
    print(response.json())

    union_id = response.json().get('unionid')
    open_id = response.json().get('open_id')
    session_key = response.json().get('session_key')
    unique_id = "wechat:" + str(union_id)
    personal_info = crud.get_personal_info_by_unqiueid(db, unique_id)

    # old user
    if personal_info is not None:
        db_eqscore = crud.get_eq_scores_by_job_id(db, personal_info.job_id)
        if db_eqscore is None:
            return JSONResponse(status_code=200, content={
                "isNewUser": True, 
                "name": personal_info.name,
                "jobid":personal_info.job_id,
                "userid":personal_info.id 
            })
        else:
            return JSONResponse(status_code=200, content={
                "isNewUser": False, 
                "name": personal_info.name,
                "jobid":personal_info.job_id,
                "userid":personal_info.id 
            })
    
    # new user
    # create new user
    encryptedData = request.encryptedData
    iv = request.iv
    appId = weixin_appid

    pc = WXBizDataCrypt(appId, session_key)
    info_data = pc.decrypt(encryptedData, iv)

    # create new user
    nickname = info_data['nickName']
    gender = 'male' if info_data['gender'] == 1 else 'female'
    avatar = info_data['avatarUrl']
    union_id = info_data['unionId']
    unique_id = "wechat:" + str(union_id)
    age = ""
    phone = ""
    email = ""
    job_id, user_id = create_profile_endpoint(nickname, "wechat", union_id, unique_id, gender, age, phone, email, avatar, db)

    return JSONResponse(status_code=200, content={
        "isNewUser": True,
        "name": nickname,
        "job_id": job_id,
        "user_id": user_id
    })
    
    
# app转微信登录
@router.post("/app2wx/login")
async def login_app(request: Request, db: Session = Depends(database.get_db)):
    body = await request.body()
    try:
        body_json = json.loads(body)
    except json.JSONDecodeError as e:
        return JSONResponse(status_code=400, content={"message": "Invalid JSON"})
    code = body_json.get('code')
    headers = {
        "Content-Type": "application/json",
    }

    print(thrid2weixin_appid)
    print(thrid2weixin_appsecret)

    message_url = f"https://api.weixin.qq.com/sns/oauth2/access_token?appid={thrid2weixin_appid}&secret={thrid2weixin_appsecret}&code={code}&grant_type=authorization_code"
    response = requests.get(message_url, headers=headers)

    if response.status_code != 200:
        return JSONResponse(status_code=response.status_code, content={"message": "Failed to get session"})

    union_id = response.json().get('unionid')
    open_id = response.json().get('openid')
    refresh_token = response.json().get('refresh_token')
    unique_id = "wechat:" + str(union_id)
    personal_info = crud.get_personal_info_by_unqiueid(db, unique_id)

    # old user
    if personal_info is not None:
        db_eqscore = crud.get_eq_scores_by_job_id(db, personal_info.job_id)
        if db_eqscore is None:
            return JSONResponse(status_code=200, content={
                "isNewUser": True, 
                "name": personal_info.name,
                "jobid":personal_info.job_id,
                "userid":personal_info.id 
            })
        else:
            return JSONResponse(status_code=200, content={
                "isNewUser": False, 
                "name": personal_info.name,
                "jobid":personal_info.job_id,
                "userid":personal_info.id 
            })

    # new user
    # send request
    # refresh
    refresh_url = f"https://api.weixin.qq.com/sns/oauth2/refresh_token?appid={thrid2weixin_appid}&grant_type=refresh_token&refresh_token={refresh_token}"
    refresh_res = requests.get(url=refresh_url, headers=headers)
    access_token = refresh_res.json().get('access_token')

    # get user info
    info_url = f"https://api.weixin.qq.com/sns/userinfo?access_token={access_token}&openid={open_id}"
    info_res = requests.get(url=info_url, headers=headers)
    info_data = info_res.json()
    print(info_data)
    nickname = info_data['nickname']
    gender = 'male' if info_data['sex'] == 1 else 'female'
    avatar = info_data['headimgurl']
    # placeholder
    age = ""
    phone = ""
    email = ""
    # {'openid': 'oft6z6TTPMwcpL_Dyg0C_Yr2zPRQ', 'nickname': 'Elijah Lin', 'sex': 0, 'language': '', 'city': '', 'province': '', 'country': '', 'headimgurl': 'https://thirdwx.qlogo.cn/mmopen/vi_32/yaywFdfM3rQw5fjfTJuXOrFVdbXDWSBz3YYuwUSeo30oCbBAmwc3HkQZ7Xn3vN1ZZ3gMfxRMHTRFKIqibpQRl1ddciaViblY443rOWceowv3Zc/132', 'privilege': [], 'unionid': 'oZL-Y6jIyyC2iRPYAkO7UImdKGTs'}

    # create new user
    job_id, user_id = create_profile_endpoint(nickname, "wechat", union_id, unique_id, gender, age, phone, email, avatar, db)

    return JSONResponse(status_code=200, content={
        "isNewUser": True,
        "name": nickname,
        "jobid": job_id,
        "userid": user_id
    })
        

# google登录
@router.post("/google/login")
async def login_google(request: data_types.GoogleLogin, db: Session = Depends(database.get_db)):
    name = request.nickname
    avatar = request.headimgurl
    email = request.email

    union_id = request.unionid
    unique_id = "google:" + str(union_id)
    personal_info = crud.get_personal_info_by_unqiueid(db, unique_id)
    gender = ""
    age = ""
    phone = ""

    if personal_info is None:
        job_id, user_id = create_profile_endpoint(name, "google", union_id, unique_id, gender, age, phone, email, avatar, db)
        return {
            "isNewUser": True,
            "name": name,
            "jobid": job_id,
            "userid": user_id
        }
    else:
        db_eqscore = crud.get_eq_scores_by_job_id(db, personal_info.job_id)
        if db_eqscore is None:
            return JSONResponse(status_code=200, content={
                "isNewUser": True, 
                "name": personal_info.name,
                "jobid":personal_info.job_id,
                "userid":personal_info.id 
            })
        else:
            return {
                "isNewUser": False,
                "name": personal_info.name,
                "jobid": personal_info.job_id,
                "userid": personal_info.id
            }
    
