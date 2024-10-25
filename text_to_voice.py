from pydantic import BaseModel
from fastapi import APIRouter, HTTPException,Response
from azure.storage.blob import BlobClient
from fastapi.responses import JSONResponse
import requests
import os
import json
import uuid

router = APIRouter()
# Define request model
class TTSRequest(BaseModel):
    text: str
    voice: str
    style: str
AZURE_STORAGE_CONNECTION_STRING = os.getenv("BLOB_ADRESS")
CONTAINER_NAME = os.getenv("CONTAINER_AUDIONAME")
SAS_TOKEN=os.getenv("AUDIO_TOEKN")
SAS_TOKEN_READ=os.getenv("AUDIO_TOEKN_READ")
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
        return  upload_image_to_blob(response)
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)
def upload_image_to_blob( audio_data):
    try:
        job_id = str(uuid.uuid4())
        BLOB_URL = f"{AZURE_STORAGE_CONNECTION_STRING}{CONTAINER_NAME}/{job_id}.wav?{SAS_TOKEN}"
        BLOB_URLRead = f"{AZURE_STORAGE_CONNECTION_STRING}{CONTAINER_NAME}/{job_id}.wav?{SAS_TOKEN_READ}"
        # Create a BlobClient using the SAS token
        blob_client = BlobClient.from_blob_url(BLOB_URL)

        # Upload the image to Azure Blob Storage
        response= blob_client.upload_blob(audio_data, overwrite=True)  # Overwrite if blob already exists
        print(response)
        if response:
            return BLOB_URLRead
    except Exception as e:
        print(f"An error occurred while uploading the audio: {e}")

# FastAPI endpoint
@router.post("/tts")
async def tts_endpoint(request: TTSRequest):
    try:
        audio_content = call_azure_tts(request.text, request.voice, request.style)
        # Return audio content as response
        return JSONResponse(status_code=200, content={"message": audio_content})
    except HTTPException as e:
            raise HTTPException(status_code=400, detail="Failed to generate audio")
 
