import requests
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

corpid = os.getenv("CORPID")
corpsecret = os.getenv("CORPSECRET")
agentid = os.getenv("AGENTID")

import requests
import json

class WeChatAPI:
    def __init__(self, corpid, corpsecret):
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.access_token = None
        self.token_expiration_time = 0
        self.get_access_token()

    def get_access_token(self):
        # Check if the current token is still valid
        if time.time() < self.token_expiration_time:
            return self.access_token

        # If the token is expired or doesn't exist, request a new one
        token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.corpid}&corpsecret={self.corpsecret}"
        response = requests.get(token_url)
        response_data = response.json()

        if response_data.get("errcode") == 0:
            self.access_token = response_data.get("access_token")
            expires_in = response_data.get("expires_in", 7200)  # Default is 7200 seconds
            self.token_expiration_time = time.time() + expires_in - 300  # Subtract 300s to refresh slightly before expiry
        else:
            raise Exception(f"Failed to get access token: {response_data.get('errmsg')}")

    def send_message(self, agentid, touser_list, content):
        # Ensure the access token is valid before sending a message
        self.get_access_token()

        message_url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.access_token}"
        data = {
            "touser": "|".join(touser_list),
            "msgtype": "text",
            "agentid": agentid,
            "text": {
                "content": content
            },
            "safe": 0
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(message_url, headers=headers, data=json.dumps(data))
        return response.json()

# Example usage
corpid = "your_corpid"
corpsecret = "your_corpsecret"
wechat_api = WeChatAPI(corpid, corpsecret)

touser_list = ["UserID1", "UserID2", "UserID3"]
content = "你好，这是一条来自企业微信的文本消息。"

result = wechat_api.send_message(agentid, touser_list, content)
print(result)
