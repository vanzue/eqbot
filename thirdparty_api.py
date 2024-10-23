import os
import json
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import requests
from azure.storage.blob import BlobClient
import sqlite3
from ai_line_bot.response_openai import get_response
from ai_line_bot.AiChatbot import AiChatbot
from ai_line_bot.EQmaster import EQmaster

import re
from html import unescape
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

def create_eqmaster(username, verbose=False):
    """
    创建角色chatbot
    """
    # 自定义角色的载入
    chatbot = EQmaster(
        username=username,
        llm = get_response,
        verbose=verbose,
        )

    return chatbot

def GetEqBotResponse(history, username,replyToken=None):
   if __name__ == "__main__":   
    ai_chatbot = create_eqmaster(username=username, verbose=True)
    #   while True:
    response = ai_chatbot.get_response_eqmaster(chat_history=history,user_nick_name=username)
    if response != None:
        send_message(response,replyToken)
    else:
       print("最后结果：\n"+response)

def get_id(rolename, username):
    # 默认数据,用于新用户  
    default_relationship = "陌生人"  
    default_intimacy = 0
    default_userinfo = "未知"

    # 获取userid，若不存在则新建用户信息   
    conn = sqlite3.connect('./database/mydata.db')
    cur = conn.cursor()

    roleid = cur.execute("SELECT roleid FROM role_info WHERE rolename = ?", (rolename,)).fetchone()[0]
    userid = cur.execute("SELECT userid FROM user WHERE username = ?", (username,)).fetchone()
    if not userid:
        max_rowid = cur.execute(f"SELECT MAX(rowid) FROM user").fetchone()[0]
        cur.execute("INSERT INTO user (userinfo, username) VALUES (?, ?)", (default_userinfo, username))
        cur.execute("INSERT INTO relationship (userid, roleid, relationship, intimacy) VALUES (?, ?, ?, ?)", (int(max_rowid)+1, roleid, default_relationship, default_intimacy))
        userid = int(max_rowid)+1
    else:
        userid = userid[0]
    
    conn.commit() 
    conn.close()
    return roleid, userid


def create_chatbot(rolename, username, verbose=False):
    """
    创建角色chatbot
    """
    roleid, userid = get_id(rolename, username)
    
    # 从数据库中读取数据
    conn = sqlite3.connect('./database/mydata.db')
    cur = conn.cursor()
    
    persona = cur.execute("SELECT persona FROM role_info WHERE roleid = ?", (roleid,)).fetchone()[0]


    stories = cur.execute("SELECT story, story_vec FROM memories WHERE roleid = ? and userid = ?", (roleid, userid)).fetchall()
    if stories:
        stories, story_vecs = zip(*stories)
        story_vecs = [eval(i)[0] if i else None for i in story_vecs]
    else:
        stories, story_vecs = None, None

    relationship, intimacy = cur.execute("SELECT relationship, intimacy FROM relationship WHERE roleid = ? and userid = ?", (roleid, userid)).fetchone()
    context = cur.execute("SELECT plot FROM plots WHERE roleid = 1 ORDER BY rowid DESC LIMIT 1").fetchone()[0]
    userinfo = cur.execute("SELECT userinfo FROM user WHERE userid = ?", (userid,)).fetchone()[0]
    conn.close()

    # 自定义角色的载入
    chatbot = AiChatbot(
        roleid = roleid,
        userid= userid,
        rolename = rolename,
        username= username,
        userinfo = userinfo,
        persona=persona,
        stories=stories, 
        story_vecs=story_vecs,
        llm = get_response,
        verbose=verbose,
        max_input_token = 1800,
        max_len_story = 600,
        max_story_n = 3,
        intimacy = intimacy,
        context = context,
        relationship = relationship,
        )

    return chatbot


# if __name__ == "__main__":   
username="me"
#   ai_chatbot = create_eqmaster(username=username, verbose=True)
#   while True:
message = '''[
    {
        "userName": "me",
        "message": "Hey Bob, how's it going?"
    },
    {
        "userName": "Bob",
        "message": "Hey! I'm doing well, thanks. How about you?"
    },
    {
        "userName": "me",
        "message": "I'm good too, just a bit busy with some work."
    },
    {
        "userName": "Bob",
        "message": "I hear you. Let me know if you need any help."
    }
]'''
# print()
# # if message[:5] == "对话记录：":
# response = ai_chatbot.get_response_eqmaster(user_nick_name=username,chat_history=message)
# # 获取用户选择的回应选项
# choice = input("\n请选择回应选项（1-4）：")

# # 根据选择生成最终回复
# if choice.isdigit() and 1 <= int(choice) <= 4:
#     ai_chatbot.verbose=False
#     response = ai_chatbot.get_response_eqmaster( query=choice)
#     print("\nEQmaster：", response)
# else:
#     print("\n无效输入，请选择1到4之间的数字。")

GetEqBotResponse(message,username)