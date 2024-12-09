import os
import requests
import json

from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate

from llm.keyless_setup import creat_llm

load_dotenv()

LLM_API = os.getenv('LLM_API')

def escape_braces(template_str):
    return template_str.replace("{", "{{").replace("}", "}}")

def request_LLM_response(user_query, db_prompt):    
    # user_prompt = ""
    # for message in user_query:
    #     if isinstance(message, dict):
    #         user_prompt += escape_braces(json.dumps(message, ensure_ascii=False))
    #     else:
    #         user_prompt += message
    return retry(send_to_LLM, user_query, db_prompt)

    
def chat_eval(user_query, max_retries=5):
    return retry(request_LLM_response_by_eval, user_query, max_retries)


def retry(func, user_prompt, db_prompt=None, max_retries=5):
    attempt = 0
    while attempt < max_retries:
        try:
            json_data = func(user_prompt, db_prompt)
            result = parse_response_to_json(json_data)
            return result
        except json.JSONDecodeError as e:
            attempt += 1
            print(f"Attempt {attempt} failed. Retrying...")
            if attempt == max_retries:
                print("Max retries reached. Giving up.")
                # raise
    return None


def request_LLM_response_by_eval(user_query, db_prompt=None):
    system_prompt = """
                    你是一位情商大师，请根据以下聊天对话，分析对方对我的满意度，并给出提升情商的小技巧。
                    **标准输出格式(不要写上json字母, 也不要漏,)**
                    {{
                        "eval": [
                            {{
                                "role": "领导",
                                "satisfaction": "满意/不满意",
                                "analysis": "根据聊天内容，以领导的第一人称，分析领导对我的感受"
                            }}, {{
                                "role": "同事A",
                                "satisfaction": "满意/不满意",
                                "analysis": "根据聊天内容，以同事A的第一人称，分析同事A对我的感受"
                            }}, {{
                                "role": "同事B",
                                "satisfaction": "满意/不满意",
                                "analysis": "根据聊天内容，以同事B的第一人称，分析同事B对我的感受"
                            }}
                        ],
                        "eq_tips": [
                            "根据实际情况给出建议，不超过二十字",
                            "根据实际情况给出建议，不超过二十字",
                            "根据实际情况给出建议，不超过二十字"
                        ]
                    }}
                """
    user_prompt = """**以下是聊天对话**
                    {user_query}
                """
    input_dict = {'user_query': user_query}


    prompt = ChatPromptTemplate.from_messages(
        [
            ('system', system_prompt),
            ('user', user_prompt),
        ]
    )

    llm = creat_llm()
    model = prompt | llm

    analysis_output = model.invoke(input_dict)
    output = analysis_output.content
    return output



def parse_response_to_json(response):
    try:
        response = json.loads(response)
        print("JSON is valid.")
        return response
    except json.JSONDecodeError as e:
        print("JSON is invalid:", e)
        raise


def send_to_LLM(user_prompt, db_prompt):
    system_prompt = db_prompt+ """
                    对话流程：

                    1. 生成话题：请根据餐厅点菜场景生成一个自然的对话，采用轻松的语气，不使用反问句。输出以下格式，不要有多余的回复， **标准输出格式(不要写上json字母, 也不要漏,)**：
                    {{
                        "dialog": [
                            {{
                                "role": "领导",
                                "words": "xxx"
                            }},
                            {{
                                "role": "同事A",
                                "words": "xxx"
                            }},
                            {{
                                "role": "同事B",
                                "words": "xxx"
                            }}
                        ]
                    }}
                    2. 我会做出回应。
                    3. 根据我的表现进行评估,如果有人的心情值降低，我希望comments能针对性的提出评估,如果没有人心情降低，则给出较好的评价，**标准输出格式(不要写上json字母, 也不要漏,)**：
                    {{
                        "comments": "xxx",
                        "moods": [
                            {{
                                "role": "领导",
                                "mood": "根据情况 +或者- 一定数值"
                            }}, 
                            {{
                                "role": "同事A",
                                "mood": "根据情况 +或者- 一定数值"
                            }}, 
                            {{
                                "role": "同事B",
                                "mood": "根据情况 +或者- 一定数值"
                            }}
                        ]
                    }}

                    4. 等待我发出下一步的指令：
                    1）如果我回答“继续”，则聊天继续。不要有多余的信息。
                    2）**只有在我发出“帮我回答”指令时**，才帮我回答。直接给出最适合的答复，不要有多余的信息。**标准输出格式(不要写上json字母, 也不要漏,)**：
                    {{
                        "responsive": "xxx"
                    }}
                    3）**只有在我发出“给我提示”指令时**，给我提示。只提供提示，不直接给出答案，不要有多余的信息。**标准输出格式(不要写上json字母, 也不要漏,)**
                    {{
                        "tips": "你可以从这个角度出发：xxx"
                    }}

                    5. 每次对话后，只选择随机一位或两位同事参与下一轮对话。

                    请按照这个步骤，请生成第一个话题，并开始对话。
                    """
    messages = [
        ('system', system_prompt)  # Add the system message as a tuple
    ]

    # print("prompt: ", user_prompt)

    for item in user_prompt:
        role = item['role']
        # Join all 'text' values into a single string for the content
        # print('item:', item)

        texts = []
        for text in item['content']: 
            if isinstance(text, dict):
                texts.append(text['text'])
                # text_content.join(text['text'])
            else:
                if isinstance(text, str):
                    texts.append(text)
                    # text_content.join(text)
        text_content = ''.join(texts)
        
        # Append each message as a tuple (role, content)
        messages.append((role, escape_braces(text_content)))
        # print(text_content)

    print(messages)
    prompt = ChatPromptTemplate.from_messages(messages)
    # prompt = ChatPromptTemplate.from_messages(
    #     [
    #         ('system', system_prompt),
    #         ('user', user_prompt),
    #     ]
    # )
    # print(prompt)
    
    llm = creat_llm()
    model = prompt | llm

    input_dict = {}

    analysis_output = model.invoke(input_dict)
    # print(analysis_output.content)
    return analysis_output.content


def send_to_LLM_v2(user_prompt, db_prompt):
    system_prompt = db_prompt+ """
                    对话流程：

                    1. 生成话题：请根据给定场景生成一个自然的对话，采用轻松的语气，不使用反问句。输出以下格式，不要有多余的回复， **标准输出格式(不要写上json字母, 也不要漏,)**：
                    {{
                        "dialog": [
                            {{
                                "role": "领导",
                                "content": "xxx"
                            }},
                            {{
                                "role": "同事A",
                                "content": "xxx"
                            }},
                            {{
                                "role": "同事B",
                                "content": "xxx"
                            }}
                        ]
                    }}
                    2. 我会做出回应。
                    3. 根据我的表现进行评估，**标准输出格式(不要写上json字母, 也不要漏,)**：
                    {{
                        "comments": "xxx",
                        "moods": [
                            {{
                                "role": "领导",
                                "mood": "根据情况 +或者- 一定数值"
                            }}, 
                            {{
                                "role": "同事A",
                                "mood": "根据情况 +或者- 一定数值"
                            }}, 
                            {{
                                "role": "同事B",
                                "mood": "根据情况 +或者- 一定数值"
                            }}
                        ]
                    }}

                    4. 等待我发出下一步的指令：
                    1）如果我回答“继续”，则聊天继续。不要有多余的信息。
                    2）**只有在我发出“帮我回答”指令时**，才帮我回答。直接给出最适合的答复，不要有多余的信息。**标准输出格式(不要写上json字母, 也不要漏,)**：
                    {{
                        "responsive": "xxx"
                    }}
                    3）**只有在我发出“给我提示”指令时**，给我提示。只提供提示，不直接给出答案，不要有多余的信息。**标准输出格式(不要写上json字母, 也不要漏,)**
                    {{
                        "tips": "你可以从这个角度出发：xxx"
                    }}

                    5. 每次对话后，只选择随机一位或两位同事参与下一轮对话。

                    请按照这个步骤，请生成第一个话题，并开始对话。
                    """
    messages = [
        ('system', system_prompt)  # Add the system message as a tuple
    ]


    for item in user_prompt:
        role = item['role']
        # Join all 'text' values into a single string for the content
        text_content = ''.join(content['text'] for content in item['content'] if content['type'] == 'text')
        # Append each message as a tuple (role, content)
        messages.append((role, escape_braces(text_content)))

    prompt = ChatPromptTemplate.from_messages(messages)
    # prompt = ChatPromptTemplate.from_messages(
    #     [
    #         ('system', system_prompt),
    #         ('user', user_prompt),
    #     ]
    # )
    
    llm = creat_llm()
    model = prompt | llm

    input_dict = {}

    analysis_output = model.invoke(input_dict)
    # print(analysis_output.content)
    return analysis_output.content


def request_LLM_response_v2(user_query, db_prompt):    
    user_prompt = ""
    for message in user_query:
        if isinstance(message, dict):
            user_prompt += escape_braces(json.dumps(message))
        else:
            user_prompt += message
    return retry(send_to_LLM_v2, user_prompt, db_prompt)

if __name__ == "__main__":
    user_query = ["开始"]

    # res = request_LLM_response(user_query)
    # print(res)

    user_chat = "{'dialog': [{'role': '领导', 'content': '这家餐厅的菜品看起来不错，大家有什么推荐的吗？'}, {'role': '同事A', 'content': '领导，您喜欢吃什么，我们就点什么。您的口味肯定不会错。'}, {'role': '同事B', 'content': '哎呀，领导的口味当然是最好的。我们就跟着领导点吧，不会有错的。'}]}"
    res = chat_eval(user_chat)
    print(res)

    
