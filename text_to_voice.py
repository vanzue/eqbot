from pydantic import BaseModel
from fastapi import APIRouter, HTTPException,Response
import requests
import os
import json
router = APIRouter()
# Define request model
class TTSRequest(BaseModel):
    text: str
    voice: str
    style: str
 
# Azure TTS function
def call_azure_tts(text, voice, style):
    # Replace with your actual endpoint and key from the screenshot
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
 
    if response.status_code == 200:
        return response.content
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)
 
# FastAPI endpoint
@router.post("/tts")
async def tts_endpoint(request: TTSRequest):
    try:
        audio_content = call_azure_tts(request.text, request.voice, request.style)
        # Return audio content as response
        if audio_content.status_code == 200:
            return Response(content=audio_content, media_type="audio/wav")
        else:
            raise HTTPException(status_code=audio_content.status_code, detail=audio_content.text)
    except HTTPException as e:
            raise HTTPException(status_code=400, detail="Failed to generate audio")
 
