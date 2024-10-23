import json
import requests
import os

from dotenv import load_dotenv
load_dotenv()
#get tolen from env
botToken = os.getenv("LINE_ACCESS_TOKEN")
class ReceiveSendMessage:
    def send_message(data,replyToken):
# Ensure the access token is valid before sending a message
        print(botToken)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {botToken}",
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

# recieve_send_message = ReceiveSendMessage()
# reply= recieve_send_message.send_message("Hello", "e400c4af5aa44ad3b835521743788d50")
# print(reply)