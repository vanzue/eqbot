import os
import requests
import json

from dotenv import load_dotenv

load_dotenv()

LLM_API = os.getenv('LLM_API')

def request_LLM_response_with_subordinate(chat_history):
    # Configuration
    API_KEY = LLM_API
    # IMAGE_PATH = "YOUR_IMAGE_PATH"
    # encoded_image = base64.b64encode(open(IMAGE_PATH, 'rb').read()).decode('ascii')
    headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY,
    }

    # Payload for the request
    payload = {
    "messages": [
        {
        "role": "system",
        "content": [
            {
            "type": "text",
            "text": """
                    **任务描述**
                    - 你是一位关系分析专家。你将接收一段我与同级同事的聊天记录。你需要根据以下几个维度对聊天记录进行分析。

                    **关键细节**
                    - 维度包括：
                    1. 关系分析
                    2. 共事契合度
                    3. 心眼子指数
                    4. 职场性格
                    5. 感兴趣的话题
                    6. 鉴别坏同事

                    **语气与风格**
                    - 专业且客观，同时保持礼貌和中立的语气。

                    **标准输出格式(不要写上json字母, 也不要漏,)**
                    {
                        "关系分析": [对你与同级同事之间关系的简短分析],
                        "共事契合度": [分析你们在工作中的配合程度，契合度高低及原因],
                        "心眼子指数": [推测同事的心机程度，0到100分，说明原因],
                        "职场性格": [根据聊天记录，分析同事的职场性格特征，如外向、谨慎、独立等],
                        "感兴趣的话题": [基于聊天内容，分析同事对哪些话题感兴趣],
                        "鉴别坏同事": [判断该同事是否有潜在的负面影响或坏同事行为，并说明理由]
                    }

                    **受众**
                    - 目标受众为希望了解与同级同事关系，并提升共事能力的用户，具有基本的职场经验。

                    **输出示例**
                    {
                        "关系分析": "你与这位同事的关系看似不太紧密，沟通中缺乏一定的理解和包容，表现出一定的紧张和争执。",
                        "共事契合度": "你们的共事契合度较低，沟通中存在信息不对称和职责分工不明确的问题，需要加强沟通与协调。",
                        "心眼子指数": “75, 同事在对话中表现出一定的防备和推诿责任的倾向，可能会在特定情况下保护自己的利益。",
                        "职场性格": "同事表现出较为谨慎和防御的性格特征，倾向于明确职责范围，不愿多承担额外的责任。",
                        "感兴趣的话题": "从聊天记录来看，没有明确显示同事对特定话题的兴趣，更多的是关注工作职责分工。",
                        "鉴别坏同事": "同事表现出一定的推诿责任的行为，但没有明显的恶意或破坏性行为迹象，需进一步观察其在团队中的表现。"
                    }

                    **额外指示**
                    - 确保分析客观、公正，避免任何过度主观或带有偏见的推测，提供的建议应有助于用户改善职场关系。

                    **以下是聊天记录**

                    """ + chat_history
            }
        ]
        }
    ],
    "temperature": 0.7,
    "top_p": 0.95,
    "max_tokens": 800
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

    return response.json()['choices'][0]['message']['content']


def parse_LLMresponse_from_subordinate(json_data):
    try:
        response = json.loads(json_data)
        print("JSON is valid.")

        relationship_analysis = response['关系分析']
        work_compatibility = response['共事契合度']
        cunning_index = response['心眼子指数']
        work_personality = response['职场性格']
        interests = response['感兴趣的话题']
        bad_colleague_risk = response['鉴别坏同事']


        analysis = {
            "relationship_analysis": relationship_analysis,
            "work_compatibility": work_compatibility,
            "cunning_index": cunning_index,
            "work_personality": work_personality,
            "interests": interests,
            "bad_colleague_risk": bad_colleague_risk
        }
        return analysis
    except json.JSONDecodeError as e:
        print("JSON is invalid:", e)
        raise


def request_LLM_response_with_supervisor(chat_history):
    # Configuration
    API_KEY = LLM_API
    # IMAGE_PATH = "YOUR_IMAGE_PATH"
    # encoded_image = base64.b64encode(open(IMAGE_PATH, 'rb').read()).decode('ascii')
    headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY,
    }

    # Payload for the request
    payload = {
    "messages": [
        {
        "role": "system",
        "content": [
            {
            "type": "text",
            "text": """
                    **任务描述:**
                    - 你是一位关系分析专家。你将接收一段聊天记录，其中包含我与对方的对话内容。对方的身份是我职场上的领导。你需要根据以下几个维度对聊天记录进行分析。

                    **关键细节:**
                    - 维度包括：
                    1. 关系分析
                    2. 相处建议
                    3. 对我的看法
                    4. PUA鉴别
                    5. 对方喜欢什么样的下属
                    6. 礼物推荐

                    **语气与风格:**
                    - 专业且客观，同时保持礼貌和中立的语气。

                    **结构:**
                    - 每个维度的分析及建议，按以下格式：
                    - 关系分析: [对你与领导之间关系的简短分析]
                    - 相处建议: [提供关于如何更好与领导相处的建议]
                    - 对我的看法: [根据聊天记录，推测领导对你的看法]
                    - PUA鉴别: [判断是否有职场PUA倾向，并说明理由]
                    - 喜欢什么样的下属: [分析领导可能喜欢什么样的下属]
                    - 礼物推荐: [基于聊天记录中的信息，推荐合适的礼物]

                    **受众:**
                    - 目标受众为希望了解与上司关系，并改进职场表现的用户，具有基本的职场经验。

                    **标准输出格式(不要写上json字母, 也不要漏,)**
                    {
                        "关系分析": "领导与您保持着较为正式的职场关系，对方似乎欣赏您的工作能力，但还没有表现出深层次的信任。",
                        "相处建议": "多关注领导的沟通风格，适当增加沟通的主动性，显示出您的责任感和团队协作能力。",
                        "对我的看法": "领导认为您是一个努力且有潜力的员工，但在一些决策时可能显得犹豫不决。",
                        "PUA鉴别": "没有明显的PUA行为迹象，领导的要求和建议大多合情合理，具有建设性。",
                        "喜欢什么样的下属": "领导可能更喜欢能够独立解决问题，并在关键时刻表现出主动性和领导力的下属。",
                        "礼物推荐": "选择实用且不过于私人化的礼物，如高档钢笔、工作相关的实用工具，或是领导喜欢的品牌咖啡。"
                    }

                    **额外指示:**
                    - 确保分析客观、公正，避免任何过度主观或带有偏见的推测。

                    **以下是聊天记录：**
                    """ + chat_history
            }
        ]
        }
    ],
    "temperature": 0.7,
    "top_p": 0.95,
    "max_tokens": 800
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

    return response.json()['choices'][0]['message']['content']


def parse_LLMresponse_from_supervisor(json_data):
    try:
        response = json.loads(json_data)
        print("JSON is valid.")

        relationship_analysis = response['关系分析']
        interaction_suggestions = response['相处建议']

        leader_opinion_of_me = response['对我的看法']
        pua_detection = response['PUA鉴别']

        preferred_subordinate = response['喜欢什么样的下属']
        gift_recommendation = response['礼物推荐']

        analysis = {
            "relationship_analysis": relationship_analysis,
            "interaction_suggestions": interaction_suggestions,
            "leader_opinion_of_me": leader_opinion_of_me,
            "pua_detection": pua_detection,
            "preferred_subordinate": preferred_subordinate,
            "gift_recommendation": gift_recommendation
        }
        return analysis
    except json.JSONDecodeError as e:
        print("JSON is invalid:", e)
        raise


def retry_parse_LLMresponse_with_subordinate(chat_history, max_retries=5):
    attempt = 0
    while attempt < max_retries:
        try:
            json_data = request_LLM_response_with_subordinate(chat_history)
            eq_scores = parse_LLMresponse_from_subordinate(json_data)
            return eq_scores
        except json.JSONDecodeError as e:
            attempt += 1
            print(f"Attempt {attempt} failed. Retrying...")
            if attempt == max_retries:
                print("Max retries reached. Giving up.")
                # raise
    return None


def retry_parse_LLMresponse_with_supervisor(chat_history, max_retries=5):
    attempt = 0
    while attempt < max_retries:
        try:
            json_data = request_LLM_response_with_supervisor(chat_history)
            eq_scores = parse_LLMresponse_from_supervisor(json_data)
            return eq_scores
        except json.JSONDecodeError as e:
            attempt += 1
            print(f"Attempt {attempt} failed. Retrying...")
            if attempt == max_retries:
                print("Max retries reached. Giving up.")
                # raise
    return None


if __name__ == "__main__":
    chat_history = "[{\"role\": \"user\", \"content\": \"姐，麻烦看下邮件呢，那个资料今天必须要了，都是星期五了\"}, {\"role\": \"colleague\", \"content\": \"那个不是我负责的\"}, {\"role\": \"user\", \"content\": \"不是一直都是你负责的吗\"}, {\"role\": \"user\", \"content\": \"以前每个月都是你发给我们的啊\"}, {\"role\": \"user\", \"content\": \"是业务交给别人了吗\"}, {\"role\": \"colleague\", \"content\": \"不知道 反正不是我负责的\"}]"
    # response = retry_parse_LLMresponse_with_subordinate(chat_history=chat_history)
    # response = request_LLM_response_with_supervisor(chat_history=chat_history)
    # print(response)

    # response = parse_LLMresponse_from_supervisor(response)
    # print(response)

    response = retry_parse_LLMresponse_with_supervisor(chat_history=chat_history)
    print(response)
