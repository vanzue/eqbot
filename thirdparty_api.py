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
telegram_Token = os.getenv("TELEGRAM_TOKEN")
processed_update_ids = set()

router = APIRouter()


@router.post("/LINE/webhook")
async def line_webhook(request: Request, db: Session = Depends(database.get_db)):
    print("LINE webhook received")
    body = await request.body()
    try:
        body_json = json.loads(body)
        print(f"message from Line: {body_json}")
    except json.JSONDecodeError as e:
        return JSONResponse(status_code=400, content={"message": "Invalid JSON"})
    for evt in body_json.get('events', []):
        if evt['source']['type'] != 'user':
            continue
        user_id = evt['source']['userId']
        reply_token = evt['replyToken']
        message_id = evt['message']['id']
        if evt['type'] != 'message':
            continue
        if evt['message']['type'] == 'image':
            reply2image("LINE", message_id, user_id, reply_token, db)
        elif evt['message']['type'] == 'text':
            reply2text("LINE", evt['message']['text'],
                       user_id, reply_token, db)
    return JSONResponse(status_code=200, content={"message": "Message received"})


def reply2text(product, message: str, user_id, replyToken: str, db: Session):
    if message.lower() == "eqoach":
        reply_message("Welcome to EQoach! Drop your chat screenshot and I will do analyze for you. \nOr you can type 'new' to start a new chat analysis.",
                      replyToken)
    elif message.lower() == "new":
        state = schemas.ReplyStateCreate(
            product=product,
            userId=str(user_id),
            chat_history="",
            stage2_output="",
            stage_number=1
        )
        crud.replace_reply_state(db, state)
        reply_message(
            "OK, drop another chat to me", replyToken)
    else:
        responses, analyze ,language= generate_auto_reply(
            product, str(user_id), None, message, db)
        response_line_or_telegram(product, responses,analyze, user_id, language)

def response_line_or_telegram(product, responses,analyze, user_id, language: str):
    if(product == "LINE"):
        if language == 'en':
            send_message("Suggested Reply:", user_id)
        else:
            send_message("建议回复:", user_id)
        for response in responses:
            send_message(response, user_id)
        send_message(analyze, user_id)
    else:
        if language == 'en':
            send_telegram_message(user_id,"Suggested Reply:")
        else:
            send_telegram_message(user_id,"建议回复:")
        for response in responses:
            send_telegram_message(user_id, response)
        send_telegram_message(user_id, analyze)

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

    responses, analyze,language = generate_auto_reply(
        product, user_id, chat_history, "", db)
    response_line_or_telegram(product, responses,analyze, user_id, language)



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
    message_url = f"https://api.line.me/v2/bot/message/push"
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
    response, analyse ,language= [], "",""
    if chat_history:
        response, analyse,language = eqmaster.get_response_and_analyze(
            chat_history,"me")

        state = schemas.ReplyStateCreate(
            product=product,
            userId=str(user_id),
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
            response, analyse,language = eqmaster.get_response_and_analyze(
                chat_history=chat_history)
            state = schemas.ReplyStateCreate(
                product=product,
                userId=str(user_id),
                chat_history=json.dumps(chat_history),
                stage2_output=analyse,
                stage_number=3)
        else:
            chat_history = json.loads(retrieved_state.chat_history)
            response ,language= eqmaster.get_response_by_intent(
                chat_history=retrieved_state.chat_history,
                intent=intent,
                analyze=retrieved_state.stage2_output
            )
            state = schemas.ReplyStateBase(
                product=product,
                userId=user_id,
                stage2_output=json.dumps(response),
                chat_history=retrieved_state.chat_history,
                stage_number=3
            )
            crud.replace_reply_state(db, state)

    # here should only be list of responses.
    return response, analyse,language


@router.post("/Telegram/webhook")
async def telegram_webhook(request: Request,db: Session = Depends(database.get_db)):
    print("Telegram webhook received")
    body = await request.body()
    try:
        body_json = json.loads(body)
        print(f"message from Telegram: {body_json}")
    except json.JSONDecodeError as e:
        return JSONResponse(status_code=400, content={"message": "Invalid JSON"})
    message= body_json.get('message', [])
    update_id = body_json['update_id']
    if update_id in processed_update_ids:
        return JSONResponse(status_code=200, content={"message": "Message received"})

    processed_update_ids.add(update_id)
    try:
        if 'photo' in message:
            reply2imageTelegram("Telegram", message['photo'][-1]['file_id'], message['chat']['id'], None, db)
        elif 'text' in message:
            reply2text("Telegram", message['text'],
                        message['chat']['id'], message['message_id'], db)
    except json.JSONDecodeError as e:
        return JSONResponse(status_code=400, content={"message": "An error occurred while processing the message"})
    return JSONResponse(status_code=200, content={"message": "Message received"})

def reply2imageTelegram(product, message_id, user_id, replyToken: str, db: Session):
    try:
        url = f'https://api.telegram.org/bot{telegram_Token}/getFile?file_id={message_id}'

        response = requests.get(url)

        if response.status_code != 200:
            print(f"Failed to get file path:{url}")
            return
        file_path = response.json()['result']['file_path']
        
        # 下载文件
        download_url = f"https://api.telegram.org/file/bot{telegram_Token}/{file_path}"
        image_response = requests.get(download_url)
        if image_response.status_code == 200:
            local_Image(product, image_response.content, user_id, replyToken, db)
        else:
            print(f"Failed to retrieve image. Status code: {image_response.status_code}")
    except requests.RequestException as e:
        print(f"Failed to download image: {e}")

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{telegram_Token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        print(f"Telegram message sent: {response.json()} to {chat_id}")
        return response.json()
    except requests.RequestException as e:
        print(f"Failed to send message: {e}")
        return None