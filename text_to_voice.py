from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException,Response
from azure.storage.blob import BlobClient
from fastapi.responses import JSONResponse
import requests
import os
import json
import uuid

from tts_sample import synthesize_speech

router = APIRouter()
# Define request model
class TTSRequest(BaseModel):
    text: str
    voice: str
    style: str
    rate: Optional[str] = "0%"
AZURE_STORAGE_CONNECTION_STRING = os.getenv("BLOB_ADRESS")
CONTAINER_NAME = os.getenv("CONTAINER_AUDIONAME")
SAS_TOKEN=os.getenv("AUDIO_TOEKN")
SAS_TOKEN_READ=os.getenv("AUDIO_TOEKN_READ")
# Azure TTS function

def azure_openai_tts(text, voice, style):
    endpoint =os.getenv("TTS_ENDPOINT")
    api_key = os.getenv("TTS_KEY")
 
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
 
    payload = {
        "model": "tts",  # Replace with your model ID
        "input": text,
        "voice": voice,
        "style": style
    }
    response = requests.post(endpoint, headers=headers, json=payload)
    return response

def call_azure_tts(text, voice, style, rate="0%"):
    """
    调用Azure TTS服务合成语音并上传到Blob存储。

    参数：
    - text (str): 要合成的文本。
    - voice (str): 使用的语音名称。
    - style (str): 语音风格。

    返回：
    - str: 上传后可读取的Blob URL。
    """
    # 调用语音合成功能
    response = synthesize_speech(text, voice, style, rate)
    if response is not None:
        # 上传音频到Blob存储
        blob_url = upload_audio_to_blob(response)
        return blob_url
    else:
        print("语音合成时发生错误。")
        return None

def upload_audio_to_blob(audio_data):
    try:
        job_id = str(uuid.uuid4())
        BLOB_URL = f"{AZURE_STORAGE_CONNECTION_STRING}{CONTAINER_NAME}/{job_id}.wav?{SAS_TOKEN}"
        BLOB_URL_READ = f"{AZURE_STORAGE_CONNECTION_STRING}{CONTAINER_NAME}/{job_id}.wav?{SAS_TOKEN_READ}"
        # 创建BlobClient
        blob_client = BlobClient.from_blob_url(BLOB_URL)

        # 上传音频数据到Blob存储
        response = blob_client.upload_blob(audio_data, overwrite=True)
        if response:
            print("音频已成功上传到Blob存储。")
            return BLOB_URL_READ
    except Exception as e:
        print(f"上传音频时发生错误: {e}")
        return None

# FastAPI endpoint
@router.post("/tts")
async def tts_endpoint(request: TTSRequest):
    try:
        audio_content = azure_openai_tts(request.text, request.voice, request.style)
        # Return audio content as response
        return JSONResponse(status_code=200, content={"message": audio_content})
    except HTTPException as e:
            raise HTTPException(status_code=400, detail="Failed to generate audio")

@router.post("/ttsaz")
async def tts_endpoint_az(request: TTSRequest):
    try:
        audio_content = call_azure_tts(request.text, request.voice, request.style, request.rate)
        return JSONResponse(status_code=200, content={"message": audio_content})
    except HTTPException as e:
            raise HTTPException(status_code=400, detail="Failed to generate audio") 
