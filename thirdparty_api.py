import os
import json
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import requests
from azure.storage.blob import BlobClient

channel_secret = os.getenv("LINE_CHANNEL_SECRET")
channel_access_token = os.getenv("LINE_ACCESS_TOKEN")
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")
SAS_TOKEN=os.getenv("SAS_TOKEN")

router = APIRouter()

@router.post("/LINE/webhook")
async def line_webhook(request: Request):
  # Read the request body as text for debugging
  body = await request.body()

  try:
    # Parse the JSON
    body_json = json.loads(body)
  except json.JSONDecodeError as e:
    print(f"JSON decode error: {e}")
    return JSONResponse(status_code=400, content={"message": "Invalid JSON"})

  print(f"message from LINE: {body_json}")
  # Pocess the incoming message
  for event in body_json.get('events', []):
    if event['type'] == 'message':
      if event['message']['type'] == 'image':
        message_id = event['message']['id']
        get_image_from_LINE(message_id)
      reply_token = event['replyToken']
      print(f"Received message: {message_id}")
      # Here you can add logic to reply to the message
  return JSONResponse(status_code=200, content={"message": "Message received"})

def get_image_from_LINE(message_id: str):
  url = f'https://api-data.line.me/v2/bot/message/{message_id}/content'

  # Set the authorization header
  headers = {
      'Authorization': f'Bearer {channel_access_token}'
  }
  response = requests.get(url, headers=headers)
  print(f"Response status code: {response}")
  # Check if the request was successful
  if response.status_code == 200:
      upload_image_to_blob(message_id, response.content)
  else:
      print(f"Failed to retrieve image. Status code: {response.status_code}")
      print(f"Response: {response.text}")

def upload_image_to_blob(message_id: str, image_data):
    try:
        BLOB_URL = f"{AZURE_STORAGE_CONNECTION_STRING}/{CONTAINER_NAME}/{message_id}.png?{SAS_TOKEN}"

        # Create a BlobClient using the SAS token
        blob_client = BlobClient.from_blob_url(BLOB_URL)

        # Upload the image to Azure Blob Storage
        blob_client.upload_blob(image_data, overwrite=True)  # Overwrite if blob already exists
        print(f"Image uploaded as '{message_id}' in container '{CONTAINER_NAME}'.")
    except Exception as e:
        print(f"An error occurred while uploading the image: {e}")
