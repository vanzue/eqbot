import os
import json
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from database import crud, models, schemas
import requests
from azure.storage.blob import BlobClient
import sqlite3
from llm.high_eq_response import EQmaster
import re
from html import unescape
from llm.image2chat import image2text
from fastapi import APIRouter, HTTPException, UploadFile, Depends, File, Form
from sqlalchemy.orm import Session
from database import crud, database, schemas
import uuid
channel_secret = os.getenv("LINE_CHANNEL_SECRET")
channel_access_token = os.getenv("LINE_ACCESS_TOKEN")
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")
SAS_TOKEN=os.getenv("SAS_TOKEN")
router = APIRouter()

@router.post("/LINE/webhook")
async def line_webhook(request: Request,db: Session = Depends(database.get_db)):
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
        get_image_from_LINE(message_id,body_json['destination'],event['replyToken'],db)
      elif event['message']['type'] == 'text':
        message_id = event['message']['id']
        message = event['message']['text']
        if message.isdigit():
          get_response_from_text(body_json['destination'], message, event['replyToken'],db)
        else:
            retrieved_state = crud.get_reply_state_by_product_and_user(
      db, "Line", body_json['destination'])
            if retrieved_state.stage_number==3 :
              crud.update_reply_state(db, schemas.ReplyStateBase(
                product="Line",
                userId=body_json['destination'],
                stage2_output=json.dumps(message),
                stage_number=1
              ))
            return JSONResponse(status_code=200, content={"message": "reply error"})

      print(f"Received message: {message_id}")
      # Here you can add logic to reply to the message
  return JSONResponse(status_code=200, content={"message": "Message received"})


def get_image_from_LINE(message_id: str,user_id: str, replyToken: str,db: Session):
  url = f'https://api-data.line.me/v2/bot/message/{message_id}/content'

  # Set the authorization header
  headers = {
      'Authorization': f'Bearer {channel_access_token}'
  }
  response = requests.get(url, headers=headers)
  print(f"Response status code: {response}")
  # Check if the request was successful
  if response.status_code == 200:
      # upload_image_to_blob(message_id, response.content,user_id,replyToken,db)
      local_Image(response.content,user_id,replyToken,db)
      
  else:
      print(f"Failed to retrieve image. Status code: {response.status_code}")
      print(f"Response: {response.text}")

def upload_image_to_blob(message_id: str, image_data, user_id: str, replyToken: str,db: Session):
    try:
        BLOB_URL = f"{AZURE_STORAGE_CONNECTION_STRING}{CONTAINER_NAME}/{message_id}.png?{SAS_TOKEN}"

        # Create a BlobClient using the SAS token
        blob_client = BlobClient.from_blob_url(BLOB_URL)

        # Upload the image to Azure Blob Storage
        respons=blob_client.upload_blob(image_data, overwrite=True)  # Overwrite if blob already exists
        if respons:
          get_response_from_image(BLOB_URL, user_id, replyToken,db)
        print(f"Image uploaded as '{message_id}' in container '{CONTAINER_NAME}'.")
    except Exception as e:
        print(f"An error occurred while uploading the image: {e}")

# get image from local
def local_Image(imagedate, user_id, replyToken,db: Session):
    
    # generate unique filename
  temp_filename = f"{uuid.uuid4()}.png"
  temp_filepath = os.path.join("temp_images", temp_filename)
  os.makedirs("temp_images", exist_ok=True)

      # download locally
  with open(temp_filepath, "wb") as f:
    f.write(imagedate)
  chat_history = image2text(image_path=temp_filepath)
  get_response_from_image(temp_filepath, user_id, replyToken,db)

# get response from image
def get_response_from_image(BLOB_URL, user_id, replyToken,db: Session):
  #get chat history from image
  chat_history= image2text(image_path=BLOB_URL)
  retrieved_state = crud.get_reply_state_by_product_and_user(
      db, "Line", user_id)
  if retrieved_state==None:
    state = schemas.ReplyStateCreate(
        product="Line",
        userId=user_id,
        stage2_output=json.dumps(chat_history),
        stage_number=1
    )
    crud.create_reply_state(db, state)
  else:
    state = schemas.ReplyStateBase(
        product="Line",
        userId=user_id,
        stage2_output=json.dumps(chat_history),
        stage_number=1
    )
    crud.update_reply_state(db, state)

  retrieved_state = crud.get_reply_state_by_product_and_user(
      db, "Line", user_id)
  eqmaster = EQmaster()
  response = eqmaster.get_response_eqmaster(
        user_nick_name="Bob", chat_history=chat_history)
  state = schemas.ReplyStateBase(
      product="Line",
      userId=user_id,
      stage2_output=json.dumps(chat_history),
      stage_number=eqmaster.current_stage
  )
  crud.update_reply_state(db, state)
  send_message(response,replyToken)
  #get response from eqmaster use query
def get_response_from_text(user_id, message, replyToken,db):
   retrieved_state = crud.get_reply_state_by_product_and_user(
      db, "Line", user_id)
   if retrieved_state.stage_number==3 :
      eqmaster = EQmaster()
      eqmaster.options=retrieved_state.stage2_output
      response = eqmaster.get_response_eqmaster(
        user_nick_name="Bob",query=message )
      send_message(response,replyToken)
        
def send_message(data,replyToken):
# Ensure the access token is valid before sending a message
  headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {channel_access_token}",
  }
  message_url = f"https://api.line.me/v2/bot/message/reply"
  data = {
      "replyToken":replyToken,
      "messages":[
          {
              "type":"text",
              "text":data
          },
      ]
  }
  response = requests.post(message_url, headers=headers, data=json.dumps(data))
  return response.json()


@router.post("/Telegram/webhook")
async def telegram_webhook(request: Request):
  # Read the request body as text for debugging
  body = await request.body()

  try:
    # Parse the JSON
    body_json = json.loads(body)
  except json.JSONDecodeError as e:
    print(f"JSON decode error: {e}")
    return JSONResponse(status_code=400, content={"message": "Invalid JSON"})

  print(f"message from Telegram: {body_json}")
  return JSONResponse(status_code=200, content={"message": "Message received"})


