import os
import requests
import json

from langchain_core.prompts import ChatPromptTemplate
from llm.keyless_setup import creat_llm

# from llm.llm_setup import setup_LLM


def autoreply_eval(chat_history, analysis, suggest_response):
    # TODO: reduce dimension, polish dimension description and add one shot
    # TODO: set up pipeline in github repo priority: 0
    system_prompt = """
                    **任务描述**
                    - 你是一位高情商评估专家。你将接收一段我与我的一个联系人的聊天记录，以及我的回复。你需要根据以下几个维度对我的回复内容进行评估打分，每个维度的满分是100分。

                    **关键细节**
                    - 维度包括：
                    1. {{语义理解能力}}
                    2. {{语言风格适宜度}}
                    3. {{心眼子指数}}
                    4. {{回复策略有效程度}}
                    5. {{情绪感知与表达能力}}
                    6. {{同理心}}

                    **语气与风格**
                    - 专业且客观，同时保持礼貌和中立的语气。

                    **标准输出格式(不要写上json字母, 也不要漏)**
                    分数：
                    {{
                        "语义理解能力": [分数（0 - 100）],
                        "语言风格适宜度": [分数（0 - 100）],
                        "心眼子指数": [分数（0 - 100）],
                        "回复策略有效程度": [分数（0 - 100）],
                        "情绪感知与表达能力": [分数（0 - 100）],
                        "同理心": [分数（0 - 100）]
                    }}
                    评分依据：
                    {{
                        "语义理解能力": [原因],
                        "语言风格适宜度": [原因],
                        "心眼子指数": [原因],
                        "回复策略有效程度": [原因],
                        "情绪感知与表达能力": [原因],
                        "同理心": [原因]
                    }}


                    **输出示例**
                    分数：
                    {{
                        "语义理解能力": [80],
                        "语言风格适宜度": [90],
                        "心眼子指数": [80],
                        "回复策略有效程度": [70],
                        "情绪感知与表达能力": [85],
                        "同理心": [90]
                    }}
                    评分依据：
                    {{
                        "语义理解能力": ["能够准确理解问题中的细微差异，例如识别用户问题中的多重含义并予以有效解答。"],
                        "语言风格适宜度": ["根据对话环境调整语言风格，例如在正式场合使用得体的措辞，在轻松场合保持自然随意。"],
                        "心眼子指数": ["巧妙地避开潜在敏感话题，例如在讨论中避免对方不想触及的个人隐私问题。"],
                        "回复策略有效程度": ["提供的建议具有可操作性，例如在问题中用户表达焦虑时，直接提供可行的解决方案。"],
                        "情绪感知与表达能力": ["能够通过用户的语气识别情绪，例如在用户语气中听出焦虑并及时给予安慰。"],
                        "同理心": ["展现出对用户感受的深刻理解，例如在用户表达失落时，用贴心的语言表示支持和鼓励。"]
                    }}


                    **额外指示**
                    - 确保分析客观、公正，避免任何过度主观或带有偏见的推测，提供的建议应有助于用户提高情商。
                    """
    user_prompt = """

                **以下是聊天记录**

                {chat_history}

                **以下是我的回复**
                {suggest_response}
                """

    prompt = ChatPromptTemplate.from_messages(
        [
            ('system', system_prompt),
            ('user', user_prompt),
        ]
    )
    
    input_dict = {'chat_history': chat_history, 'suggest_response': suggest_response}

    llm = creat_llm()
    model = prompt | llm

    analysis_output = model.invoke(input_dict)
    output = analysis_output.content
    return output