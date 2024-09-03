import os
import requests
import base64
import json

from dotenv import load_dotenv

load_dotenv()

LLM_API = os.getenv('LLM_API')

def request_LLM_response(user_info):
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
                    - 你是一位非常专业的情商评估师。根据提供的一系列用户信息，从以下五个维度对用户的情商进行评估：情绪侦查力、情绪掌控力、人际平衡术、沟通表达力、社交得体度。

                    **关键细节:**
                    - 每个维度需要打分，分数范围为0到100分。
                    - 对每个维度的评分，提供简洁的原因解释。
                    - 最后，根据五个维度中最低的得分，给出一句20字以内的小贴士，力求简洁、精准。
                    - 基于最低得分，提供情商修炼的建议。

                    **语气与风格:**
                    - 专业、客观，同时保持幽默和轻松的语气氛围。注意拿捏冒犯的分寸感。

                    **结构:**
                    - 评分部分：
                        - 每个维度的评分及简短原因解释，按以下格式：
                            - 维度名称: 分数 (0-100)
                            - 原因: 原因简述
                    - 小贴士部分：
                        - 一句简短小贴士，20字以内。
                    - 修炼建议部分：
                        - 根据最低得分维度，提供针对该维度的情商修炼建议。

                    **受众:**
                    - 目标受众为希望提升情商的用户，理解力中等以上。

                    **示例或参考:**
                    - 示例评分：情绪掌控力: 25 原因: 工作中有一点风吹草动，你的小情绪就像火山一样，说爆发就爆发。得悠着点啊，不然很容易把自己和小伙伴都烫伤。
                    - 示例小贴士：冲动是魔鬼，学会冷静才能掌控全场。
                    - 示例提升建议：你的情绪稳定能力偏低，当前你最需要改善这项能力，你容易因为工作中的小挫折或他人的不同意见而产生较大的情绪波动，进而影响工作效率和人际关系。 别人说话时别像刺猬急于扎人，专心听，不打断，不反驳，点头，眼神交流以示尊重。处理冲突要平和理性，先听对方说再表达。别带刺攻击，一起找到双赢办法。


                    **额外指示:**
                    - 提供评分时请保持公正和建设性，避免任何带有负面色彩的评论，确保给出的修炼建议能够切实帮助用户提高情商。

                    **用户信息：**
                    - 请根据以下用户信息生成上述的报告：""" + user_info + """

                    **标准输出格式(不要写上json字母, 也不要漏,)**
                    {
                        "1. 情绪侦查力": {
                            "分数": [分数],
                            "原因": [原因简述]
                        },
                        "2. 情绪掌控力": {
                            "分数": [分数],
                            "原因": [原因简述]
                        },
                        "3. 人际平衡术": {
                            "分数": [分数],
                            "原因": [原因简述]
                        },
                        "4. 沟通表达力": {
                            "分数": [分数],
                            "原因": [原因简述]
                        },
                        "5. 社交得体度": {
                            "分数": [分数],
                            "原因": [原因简述]
                        },
                        "6. 综合小贴士": {
                            "小贴士": [提供一个简短的小贴士，20字以内]
                        },
                        "7. 情商修炼建议": {
                            "建议": [针对最低得分的维度提供详细的修炼建议]
                        },
                        "8. 评估总结": {
                            "总结": [针对用户情况，给出综合评价以及对用户的美好愿望]
                        }
                    }
                    """
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

def parse_LLMresponse(json_data):
    try:
        response = json.loads(json_data)
        print("JSON is valid.")

        dimension1_score = response['1. 情绪侦查力']['分数']
        dimension1_detail = response['1. 情绪侦查力']['原因']

        dimension2_score = response['2. 情绪掌控力']['分数']
        dimension2_detail = response['2. 情绪掌控力']['原因']

        dimension3_score = response['3. 人际平衡术']['分数']
        dimension3_detail = response['3. 人际平衡术']['原因']

        dimension4_score = response['4. 沟通表达力']['分数']
        dimension4_detail = response['4. 沟通表达力']['原因']

        dimension5_score = response['5. 社交得体度']['分数']
        dimension5_detail = response['5. 社交得体度']['原因']

        summary = response['6. 综合小贴士']['小贴士']
        detail = response['7. 情商修炼建议']['建议']
        overall_suggestion = response['8. 评估总结']['总结']

        eq_scores = {
            "dimension1_score": dimension1_score,
            "dimension1_detail": dimension1_detail,
            "dimension2_score": dimension2_score,
            "dimension2_detail": dimension2_detail,
            "dimension3_score": dimension3_score,
            "dimension3_detail": dimension3_detail,
            "dimension4_score": dimension4_score,
            "dimension4_detail": dimension4_detail,
            "dimension5_score": dimension5_score,
            "dimension5_detail": dimension5_detail,
            "summary": summary,
            "detail": detail,
            "overall_suggestion": overall_suggestion
        }
        return eq_scores
    except json.JSONDecodeError as e:
        print("JSON is invalid:", e)
        raise

def retry_parse_LLMresponse(user_info, max_retries=5):
    attempt = 0
    while attempt < max_retries:
        try:
            json_data = request_LLM_response(user_info)
            eq_scores = parse_LLMresponse(json_data)
            return eq_scores
        except json.JSONDecodeError as e:
            attempt += 1
            print(f"Attempt {attempt} failed. Retrying...")
            if attempt == max_retries:
                print("Max retries reached. Giving up.")
                # raise
    return None

if __name__ == "__main__":
    user_info = "该用户是一名女性，她会在开会讨论遇到两个同事意见不合并且其中一个情绪很激动的时候，冷静分析双方意见和优缺点"
    # response = request_LLM_response(user_info)
    # print(response)

    eq_scores = retry_parse_LLMresponse(user_info)
    print(eq_scores)