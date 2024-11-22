from fastapi.responses import JSONResponse
import json
import os
import uuid
import requests
from database import crud, schemas, database
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request

import data_types
from WXBizDataCrypt_login import WXBizDataCrypt


weixin_appid = os.getenv('WEIXIN_APPID')
weixin_secret = os.getenv('WEIXIN_APPSECRET')

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
                            job_id=job_id)
    db_personal_info = crud.create_personal_info(db, personal_info_data)

    return job_id, db_personal_info.id

# 小程序
@router.post("/wxprogram/login")
async def line_webhook(request: data_types.MiniProgramLogin, db: Session = Depends(database.get_db)):
    # body = await request.body()
    # try:
    #     body_json = json.loads(body)
    # except json.JSONDecodeError as e:
    #     return JSONResponse(status_code=400, content={"message": "Invalid JSON"})
    code = request.code
    headers = {
        "Content-Type": "application/json",
    }

    # print(weixin_appid)
    # print(weixin_secret)

    message_url = f"https://api.weixin.qq.com/sns/jscode2session?appid={weixin_appid}&secret={weixin_secret}&js_code={code}&grant_type=authorization_code"
    response = requests.get(message_url, headers=headers)

    if response.status_code != 200:
        return JSONResponse(status_code=response.status_code, content={"message": "Failed to get session"})
    print(response.json())
    # {'session_key': 'kxZmRzab5re+UlT9/XVAkg==', 'openid': 'obhRt7R4GThypSkeNpmc3TqFSy1M', 'unionid': 'oZL-Y6qZ4U9UZcdI42IYMNRPhbX0'}
    
    # test
    # session_key = "kxZmRzab5re+UlT9/XVAkg=="
    # open_id = "obhRt7R4GThypSkeNpmc3TqFSy1M"
    # union_id = "oZL-Y6qZ4U9UZcdI42IYMNRPhbX0"
    union_id = response.json().get('unionid')
    open_id = response.json().get('open_id')
    session_key = response.json().get('session_key')
    unique_id = "wechat:" + str(union_id)
    personal_info = crud.get_personal_info_by_unqiueid(db, unique_id)

    # old user
    if personal_info is not None:
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
    # print(pc.decrypt(encryptedData, iv))
    # {'openId': 'oGZUI0egBJY1zhBYw2KhdUfwVJJE', 'nickName': 'Band', 'gender': 1, 'language': 'zh_CN', 'city': 'Guangzhou', 'province': 'Guangdong', 'country': 'CN', 'avatarUrl': 'http://wx.qlogo.cn/mmopen/vi_32/aSKcBBPpibyKNicHNTMM0qJVh8Kjgiak2AHWr8MHM4WgMEm7GFhsf8OYrySdbvAMvTsw3mo8ibKicsnfN5pRjl1p8HQ/0', 'unionId': 'ocMvos6NjeKLIBqg5Mr9QjxrP1FA', 'watermark': {'timestamp': 1477314187, 'appid': 'wx4f4bc4dec97d474b'}}

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


# # only for new user
# @router.post("/wxprogram/login/encrypte")
# async def encrypte_miniProgram(request: Request,  db: Session = Depends(database.get_db)):
#     sessionKey = request.sessionKey
#     encryptedData = request.encryptedData
#     iv = request.iv
#     appId = weixin_appid

#     # appId = 'wx4f4bc4dec97d474b'
#     # sessionKey = 'tiihtNczf5v6AKRyjwEUhQ=='
#     # encryptedData = 'CiyLU1Aw2KjvrjMdj8YKliAjtP4gsMZMQmRzooG2xrDcvSnxIMXFufNstNGTyaGS9uT5geRa0W4oTOb1WT7fJlAC+oNPdbB+3hVbJSRgv+4lGOETKUQz6OYStslQ142dNCuabNPGBzlooOmB231qMM85d2/fV6ChevvXvQP8Hkue1poOFtnEtpyxVLW1zAo6/1Xx1COxFvrc2d7UL/lmHInNlxuacJXwu0fjpXfz/YqYzBIBzD6WUfTIF9GRHpOn/Hz7saL8xz+W//FRAUid1OksQaQx4CMs8LOddcQhULW4ucetDf96JcR3g0gfRK4PC7E/r7Z6xNrXd2UIeorGj5Ef7b1pJAYB6Y5anaHqZ9J6nKEBvB4DnNLIVWSgARns/8wR2SiRS7MNACwTyrGvt9ts8p12PKFdlqYTopNHR1Vf7XjfhQlVsAJdNiKdYmYVoKlaRv85IfVunYzO0IKXsyl7JCUjCpoG20f0a04COwfneQAGGwd5oa+T8yO5hzuyDb/XcxxmK01EpqOyuxINew=='
#     # iv = 'r7BXXKkLb8qrSNn05n0qiA=='

#     pc = WXBizDataCrypt(appId, sessionKey)
#     info_data = pc.decrypt(encryptedData, iv)
#     # print(pc.decrypt(encryptedData, iv))
#     # {'openId': 'oGZUI0egBJY1zhBYw2KhdUfwVJJE', 'nickName': 'Band', 'gender': 1, 'language': 'zh_CN', 'city': 'Guangzhou', 'province': 'Guangdong', 'country': 'CN', 'avatarUrl': 'http://wx.qlogo.cn/mmopen/vi_32/aSKcBBPpibyKNicHNTMM0qJVh8Kjgiak2AHWr8MHM4WgMEm7GFhsf8OYrySdbvAMvTsw3mo8ibKicsnfN5pRjl1p8HQ/0', 'unionId': 'ocMvos6NjeKLIBqg5Mr9QjxrP1FA', 'watermark': {'timestamp': 1477314187, 'appid': 'wx4f4bc4dec97d474b'}}

#     # create new user
#     nickname = info_data['nickName']
#     gender = 'male' if info_data['gender'] == 1 else 'female'
#     avatar = info_data['avatarUrl']
#     union_id = info_data['unionId']
#     unique_id = "wechat:" + str(union_id)
#     age = ""
#     phone = ""
#     email = ""
#     job_id, user_id = create_profile_endpoint(nickname, "wechat", union_id, unique_id, gender, age, phone, email, avatar, db)
    
#     return {"job_id": job_id, "user_id": user_id}
    
    
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

    print(weixin_appid)
    print(weixin_secret)

    message_url = f"https://api.weixin.qq.com/sns/oauth2/access_token?appid={weixin_appid}&secret={weixin_secret}&code={code}&grant_type=authorization_code"
    response = requests.get(message_url, headers=headers)

    if response.status_code != 200:
        return JSONResponse(status_code=response.status_code, content={"message": "Failed to get session"})
    print(response.json())


    union_id = response.json().get('unionid')
    refresh_token = response.json.get('refresh_token')
    unique_id = "wechat:" + str(union_id)
    personal_info = crud.get_personal_info_by_unqiueid(db, unique_id)

    # old user
    if personal_info is not None:
        return JSONResponse(status_code=200, content={
            "isNewUser": False, 
            "name": personal_info.name,
            "jobid":personal_info.job_id,
            "userid":personal_info.id 
        })

    # new user
    # send request
    # refresh
    refresh_url = f"https://api.weixin.qq.com/sns/oauth2/refresh_token?appid={weixin_appid}&grant_type=refresh_token&refresh_token={refresh_token}"
    refresh_res = request.get(url=refresh_url, headers=headers)
    access_token = refresh_res.json().get('access_token')

    # get user info
    info_url = f"https://api.weixin.qq.com/sns/userinfo?access_token={access_token}&openid={weixin_appid}"
    info_res = request.get(url=info_url, headers=headers)
    info_data = info_res.json()
    nickname = info_data['nickname']
    gender = 'male' if info_data['sex'] == 1 else 'female'
    avatar = info_data['headimgurl']
    # placeholder
    age = ""
    phone = ""
    email = ""

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
        return {
            "isNewUser": False,
            "name": personal_info.name,
            "jobid": personal_info.job_id,
            "userid": personal_info.id
        }
    