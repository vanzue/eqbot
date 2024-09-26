import os
import requests
import json

from dotenv import load_dotenv

load_dotenv()

LLM_API = os.getenv('LLM_API')

payload = {
    "messages": [
        {
        "role": "system",
        "content": [
            {
            "type": "text",
            "text": """
                    情绪掌控测试\n\n你是一位情绪掌控大师。今晚，我和公司里的三位同事——我的领导、同事A以及同事B——参加了一次聚餐。在聚餐过程中，领导和同事A会主动向我发起话题，希望通过我的回答来考察我的情绪掌控力。\n\n请按照以下步骤进行：\n\n生成领导的问题：生成一个领导可能会在聚餐中提问的问题。\n评估回答：等待我给出回答后，根据我的表现进行评估。\n如果我的回答恰当，请回应“做得好”，并给出简短的评价。不要有多余的消息\n如果我的回答不够好，请回应“继续努力”，并给出简短的评价。不要有多余的消息\n提示和帮助：在得到回应之后，请等待我的回应做出响应的问题，如果我发出指令“继续“，则生成下一个对象的话题。如果得到的评级是”继续努力“，请等待我发出指令”帮我回答“或者”给我提示“或者”继续“。在提示中，请不要直接生成示例，只有我回复“帮我回答”后，才给我生成合适的回答。\n对话场景：他们的提问应尽量符合日常对话场景，例如：“我最近有点上火，医生建议我清淡饮食。这些重口味的菜我可真不敢吃了，不然怕是吃完嘴上火气就更旺了。”\n回答机会：请注意，只有在我要求的时候，才给我重新作答的机会，否则继续进行下一个问题。在我需要再回答一次的时候，我会说“给我点提示吧”或者“帮我回答”。此时给我提示或者帮助我直接回答。\n回答格式: 在提问时，以xx的问题：...的格式提问，\n\n请生成领导的第一个问题。
                    """
            }
        ]
        }
    ],
    "temperature": 0.7,
    "top_p": 0.95,
    "max_tokens": 800
    }

def request_LLM_response(user_info):
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
        response = requests.post(ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.RequestException as e:
        raise SystemExit(f"Failed to make the request. Error: {e}")

    # Handle the response as needed (e.g., print or process)
    # print(response.json())
    # print(type(response))
    print(response.json()['choices'][0]['message']['content'])
    return response.json()['choices'][0]['message']['content']