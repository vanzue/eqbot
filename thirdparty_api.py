import os
import json
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

channel_secret = os.getenv("LINE_CHANNEL_SECRET")

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
      message = event['message']['text']
      reply_token = event['replyToken']
      print(f"Received message: {message}")
      # Here you can add logic to reply to the message
  return JSONResponse(status_code=200, content={"message": "Message received"})