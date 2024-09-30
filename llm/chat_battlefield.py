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
                    "text": "你是一位情绪掌控大师。今晚，我和三位同事——我的领导、同事A和同事B——在餐厅聚餐。通过轻松的日常对话，他们会考察我的情绪掌控力。请根据以下人物性格生成对话：\n\n领导：擅长PUA，脾气很大。\n同事A：阿谀奉承，讨好领导。\n同事B：尖酸刻薄。\n\n对话流程：\n1. 生成话题：你将根据餐厅点菜场景生成一个自然的对话，采用轻松的语气，不使用反问句。输出以下格式，不要有多余的回复：\n领导：xxx\n同事A：xxx\n同事B：xxx\n\n2. 我会做出回应。\n3. 根据我的表现进行评估：\n如果回答恰当，回应：“做得好，xxx（简短评价）”。不要有多余的信息。\n如果回答不够好，回应：“继续努力，xxx（简短评价）”。不要有多余的信息。\n等待我发出下一步的指示：\n如果我回答“继续”，则聊天继续。不要有多余的信息。\n如果我回答“帮我回答”或“给我提示”，帮我回答时的答复格式为“xxx”，直接给出最适合的答复，不要有多余的信息。\n给我提示的答复格式为\"你可以从这个角度出发：xxx\"，只提供提示，不直接给出答案，不要有多余的信息。\n\n请生成第一个话题，并开始对话。"
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
    return send_to_LLM(payload)

    
def chat_eval(chat_history, max_retries=5):
    attempt = 0
    while attempt < max_retries:
        try:
            json_data = request_LLM_response_by_eval(chat_history)
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
            "领导": {  
                "满意度": "满意/不满意",  
                "分析": "根据聊天内容，分析领导对我的感受"  
            },  
            "同事A": {  
                "满意度": "满意/不满意",  
                "分析": "根据聊天内容，分析同事A对我的感受"  
            },  
            "同事B": {  
                "满意度": "满意/不满意",  
                "分析": "根据聊天内容，分析同事B对我的感受"  
            },  
            "情商技巧": [  
                {  
                    "建议": "根据实际情况给出建议，不超过二十字"  
                },  
                {  
                    "建议": "根据实际情况给出建议，不超过二十字"  
                },  
                {  
                    "建议": "根据实际情况给出建议，不超过二十字"  
                }  
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