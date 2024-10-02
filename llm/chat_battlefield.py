import os
import requests
import json

from dotenv import load_dotenv
from llm.llm_setup import setup_LLM

load_dotenv()

LLM_API = os.getenv('LLM_API')

def request_LLM_response(chat_history):
    payload = {
        "messages": [
            {
                "role": "system",
                "content": [
                    {
                    "type": "text",
                    "text": """
                    你是一位情绪掌控大师。今晚，我和三位同事——我的领导、同事A和同事B——在餐厅聚餐。通过轻松的日常对话，他们会考察我的情绪掌控力。每位同事初始都有一个心情值，每次对话都会使他们的心情加或减。请根据以下人物性格生成对话：请根据以下人物性格生成对话：

                        领导：擅长PUA，脾气很大。
                        同事A：阿谀奉承，讨好领导。
                        同事B：尖酸刻薄。

                    对话流程：

                    1. 生成话题：请根据餐厅点菜场景生成一个自然的对话，采用轻松的语气，不使用反问句。输出以下格式，不要有多余的回复， **标准输出格式(不要写上json字母, 也不要漏,)**：
                    {
                        "dialog": [
                            {
                                "role": "领导",
                                "content": "xxx"
                            },{
                                "role": "同事A",
                                "content": "xxx"
                            },{
                                "role": "同事B",
                                "content": "xxx"
                            }
                        ]
                    }
                    2. 我会做出回应。
                    3. 根据我的表现进行评估，**标准输出格式(不要写上json字母, 也不要漏,)**：
                    {
                        "comments": "xxx",
                        "moods": [
                            {
                                "role": "领导",
                                "mood": "根据情况 +或者- 一定数值"
                            }, {
                                "role": "同事A",
                                "mood": "根据情况 +或者- 一定数值"
                            }, {
                                "role": "同事B",
                                "mood": "根据情况 +或者- 一定数值"
                            }
                        ]
                    }

                    4. 等待我发出下一步的指令：
                    1）如果我回答“继续”，则聊天继续。不要有多余的信息。
                    2）**只有在我发出“帮我回答”指令时**，才帮我回答。直接给出最适合的答复，不要有多余的信息。**标准输出格式(不要写上json字母, 也不要漏,)**：
                    {
                    "responsive": "xxx"
                    }
                    3）**只有在我发出“给我提示”指令时**，给我提示。只提供提示，不直接给出答案，不要有多余的信息。**标准输出格式(不要写上json字母, 也不要漏,)**
                    {
                    "tips": "你可以从这个角度出发：xxx"
                    }

                    5. 每次对话后，只选择随机一位同事参与下一轮对话。

                    请按照这个步骤，请生成第一个话题，并开始对话。
                    """
                    }
                ]
            },
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 800,
    }
    for message in chat_history:
        payload['messages'].append(message)
    return retry(send_to_LLM, payload)

    
def chat_eval(chat_history, max_retries=5):
    return retry(request_LLM_response_by_eval, chat_history, max_retries)

def retry(func, chat_message, max_retries=5):
    attempt = 0
    while attempt < max_retries:
        try:
            json_data = func(chat_message)
            result = parse_response_to_json(json_data)
            return result
        except json.JSONDecodeError as e:
            attempt += 1
            print(f"Attempt {attempt} failed. Retrying...")
            if attempt == max_retries:
                print("Max retries reached. Giving up.")
                # raise
    return None

def request_LLM_response_by_eval(chat_history):
    payload = """
        你是一位情商大师，请根据以下聊天对话，分析对方对我的满意度，并给出提升情商的小技巧。
        **标准输出格式(不要写上json字母, 也不要漏,)**
        {
            "eval": [
                {
                    "role": "领导",
                    "satisfaction": "满意/不满意",
                    "analysis": "根据聊天内容，分析领导对我的感受"
                }, {
                    "role": "同事A",
                    "satisfaction": "满意/不满意",
                    "analysis": "根据聊天内容，分析同事A对我的感受"
                }, {
                    "role": "同事B",
                    "satisfaction": "满意/不满意",
                    "analysis": "根据聊天内容，分析同事B对我的感受"
                }
            ],
            "eq_tips": [
                "根据实际情况给出建议，不超过二十字",
                "根据实际情况给出建议，不超过二十字",
                "根据实际情况给出建议，不超过二十字"
            ]
        }

        以下是聊天记录：
    """ + chat_history
    return setup_LLM(payload_content=payload)

def parse_response_to_json(response):
    try:
        response = json.loads(response)
        print("JSON is valid.")
        return response
    except json.JSONDecodeError as e:
        print("JSON is invalid:", e)
        raise


def send_to_LLM(messages):
    # Configuration
    API_KEY = LLM_API
    # IMAGE_PATH = "YOUR_IMAGE_PATH"
    # encoded_image = base64.b64encode(open(IMAGE_PATH, 'rb').read()).decode('ascii')
    headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY,
    }

    ENDPOINT = "https://peitingaoai.openai.azure.com/openai/deployments/4opeitingus/chat/completions?api-version=2024-02-15-preview"

    # Send request
    try:
        response = requests.post(ENDPOINT, headers=headers, json=messages)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.RequestException as e:
        raise SystemExit(f"Failed to make the request. Error: {e}")

    return response.json()['choices'][0]['message']['content']