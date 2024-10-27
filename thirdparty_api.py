from fastapi.responses import JSONResponse
import json
import os
import requests
import uuid
from database import crud, schemas, database
from azure.storage.blob import BlobClient
from llm.high_eq_response import EQmaster
from llm.image2chat import image2text
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request

channel_secret = os.getenv("LINE_CHANNEL_SECRET")
channel_access_token = os.getenv("LINE_ACCESS_TOKEN")
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")
SAS_TOKEN = os.getenv("SAS_TOKEN")


router = APIRouter()


@router.post("/LINE/webhook")
async def line_webhook(request: Request, db: Session = Depends(database.get_db)):
    body = await request.body()
    try:
        body_json = json.loads(body)
        print(f"message from Line: {body_json}")
    except json.JSONDecodeError as e:
        return JSONResponse(status_code=400, content={"message": "Invalid JSON"})
    user_id = body_json['destination']
    for evt in body_json.get('events', []):
        reply_token = evt['replyToken']
        message_id = evt['message']['id']
        if evt['type'] != 'message':
            continue
        if evt['message']['type'] == 'image':
            reply2image("LINE", message_id, user_id, reply_token, db)
            reply_message("processing...", reply_token)
        elif evt['message']['type'] == 'text':
            reply2text("LINE", evt['message']['text'],
                       user_id, reply_token, db)
    return JSONResponse(status_code=200, content={"message": "Message received"})


def reply2text(product, message: str, user_id, replyToken: str, db: Session):
    if message == "eqoach":
        reply_message("Welcome to EQoach! Drop your chat screenshot and I will do analyze for you. \nOr you can type 'new' to start a new chat analysis.",
                      replyToken)
    elif message == "new":
        state = schemas.ReplyStateCreate(
            product=product,
            userId=user_id,
            chat_history="",
            stage2_output="",
            stage_number=1
        )
        crud.replace_reply_state(db, state)
        reply_message(
            "OK, drop another chat to me", replyToken)
    else:
        responses, analyze = generate_auto_reply(
            product, user_id, None, message, db)

        send_message(analyze, user_id)
        for response in responses:
            send_message(response, user_id)


def reply2image(product, message_id, user_id, replyToken: str, db: Session):
    url = f'https://api-data.line.me/v2/bot/message/{message_id}/content'
    headers = {'Authorization': f'Bearer {channel_access_token}'}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        local_Image(product, response.content, user_id, replyToken, db)
    else:
        print(f"Failed to retrieve image. Status code: {response.status_code}")


def local_Image(product, imagedate, user_id, replyToken, db: Session):
    temp_filename = f"{uuid.uuid4()}.png"
    temp_filepath = os.path.join("temp_images", temp_filename)
    os.makedirs("temp_images", exist_ok=True)

    with open(temp_filepath, "wb") as f:
        f.write(imagedate)
    get_response_from_image(product, temp_filepath, user_id, replyToken, db)


def get_response_from_image(product, IMAGE_PATH, user_id, replyToken, db: Session):
    chat_history = image2text(image_path=IMAGE_PATH)
    try:
        os.remove(IMAGE_PATH)
        print(f"Deleted local image file: {IMAGE_PATH}")
    except Exception as e:
        print(f"An error occurred while deleting the image file: {e}")

    responses, analyze = generate_auto_reply(
        product, user_id, chat_history, "", db)
    send_message(analyze, user_id)
    for response in responses:
        send_message(response, user_id)


def reply_message(data, replyToken):
    # Ensure the access token is valid before sending a message
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {channel_access_token}",
    }
    message_url = f"https://api.line.me/v2/bot/message/reply"
    data = {
        "replyToken": replyToken,
        "messages": [
            {
                "type": "text",
                "text": data
            },
        ]
    }
    response = requests.post(
        message_url, headers=headers, data=json.dumps(data))
    return response.json()


def send_message(data, to):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {channel_access_token}",
    }
    message_url = f"https://api.line.me/v2/bot/message/reply"
    data = {
        "to": to,
        "messages": [
            {
                "type": "text",
                "text": data
            },
        ]
    }
    response = requests.post(
        message_url, headers=headers, data=json.dumps(data))
    return response.json()


def generate_auto_reply(product: str, user_id: str, chat_history, intent,
                        db: Session):
    retrieved_state = crud.get_reply_state_by_product_and_user(
        db, product, user_id)
    eqmaster = EQmaster()
    response, analyse = [], ""
    if chat_history:
        response, analyse = eqmaster.get_response_and_analyze(
            chat_history)

        state = schemas.ReplyStateCreate(
            product=product,
            userId=user_id,
            chat_history=json.dumps(chat_history),
            stage2_output=analyse,
            stage_number=3)
        crud.replace_reply_state(db, state)
    else:
        # no chat history
        # new chat:
        if not retrieved_state or not retrieved_state.chat_history:
            chat_history = [{
                "userName": "other",
                "message": intent
            }]
            response, analyse = eqmaster.get_response_and_analyze(
                chat_history=chat_history)
            state = schemas.ReplyStateCreate(
                product=product,
                userId=user_id,
                chat_history=json.dumps(chat_history),
                stage2_output=analyse,
                stage_number=3)
        else:
            chat_history = json.loads(retrieved_state.chat_history)
            response = eqmaster.get_response_by_intent(
                chat_history=retrieved_state.chat_history,
                intent=intent,
                analyze=retrieved_state.stage2_output
            )
            state = schemas.ReplyStateBase(
                product=product,
                userId=user_id,
                stage2_output=response,
                chat_history=retrieved_state.chat_history,
                stage_number=3
            )
            crud.replace_reply_state(db, state)

    # here should only be list of responses.
    return response, analyse


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
