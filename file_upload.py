from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import aiofiles
import requests
import os
from fastapi import APIRouter

file_router = APIRouter()

# 替换为你的 Azure 订阅密钥和区域
AZURE_SUBSCRIPTION_KEY = os.getenv('AZURE_SUBSCRIPTION_KEY')
AZURE_REGION =  os.getenv('SPEECH_REGION')

# 定义路由来处理文件上传
@file_router.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    # 保存上传的文件
    file_path = f"/tmp/{file.filename}"
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()  # 读取上传的文件内容
            await out_file.write(content)  # 保存文件到本地
        
        # 发送文件到 Azure Speech-to-Text 服务
        transcript = await send_to_azure_speech(file_path)

        # 返回解析后的文本
        return JSONResponse(content={"transcript": transcript})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")
    finally:
        # 删除临时文件
        if os.path.exists(file_path):
            os.remove(file_path)

# 发送音频文件到 Azure Speech-to-Text API 并获取识别结果
async def send_to_azure_speech(file_path: str) -> str:
    headers = {
        'Ocp-Apim-Subscription-Key': AZURE_SUBSCRIPTION_KEY,
        'Content-Type': 'audio/wav'
    }
    url = f'https://{AZURE_REGION}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=zh-CN&format=detailed'

    with open(file_path, 'rb') as audio_file:
        response = requests.post(url, headers=headers, data=audio_file)

    if response.status_code == 200:
        result = response.json()
        transcript = result.get('DisplayText', '')
        return transcript
    else:
        raise HTTPException(status_code=response.status_code, detail=f"Azure 语音识别失败: {response.text}")