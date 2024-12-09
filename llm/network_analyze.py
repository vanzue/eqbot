import os
import requests
import json

from langchain_core.prompts import ChatPromptTemplate
from llm.keyless_setup import creat_llm


def request_LLM_response(chat_history):
    system_prompt = """
                    ** Task Description **
                    You are a relationship analysis expert. You will receive a chat histry between me and a peer. You are required to analyze the chat content from the input screenshot and provide an emotional intelligence improvement suggestion tailored to the conversation. Your response should include: 

                    ** Tone and Style **
                    - Professional and objective, while maintaining a polite and neutral tone.

                    Your response should include:
                    title: A concise phrase summarizing the key emotional intelligence aspect of the chat (e.g., "Responsiveness and Proactive Communication"), please includes emoji(eg. U+1F604, U+1F31F) in the front.
                    summary: One sentence describing the current issue
                    You can: 
                    [First actionable suggestion based on the current context] 
                    [Second actionable suggestion based on the analysis of the other person's perspective of you] 
                    [Third actionable suggestion for self-improvement] 
                    [Fourth actionable suggestion for a recommended response the user can give]

                    ** Standard Output Format (Do not include the word "json", and do not omit anything.) **
                    {{
                        "title": [
                            {{
                                "title: [A concise phrase summarizing the key emotional intelligence aspect of the chat, please includes emoji(eg. U+1F604, U+1F31F) in the front]
                            }}
                        ], 
                        "summary": [
                            {{
                                "summary: [One sentence describing the current issue]
                            }}
                        ],
                        "suggestions": [
                            {{
                            "point": [First actionable suggestion based on the current context. If possible, please include the name mentioned in chat history]
                            }},
                            {{
                            "point": [Second actionable suggestion based on the analysis of the other person's perspective of you. If possible, please include the name mentioned in chat history]
                            }},
                            {{
                            "point": [Third actionable suggestion for self-improvement. If possible, please include the name mentioned in chat history]
                            }},
                            {{
                            "point": [Fourth actionable suggestion for a recommended response the user can give. If possible, please include the name mentioned in chat history]
                            }}
                        ]                        
                    }}

                    ** Audience **
                    - The target audience is those who wish to understand how the other person perceives them.

                    ** Output Example **
                    {{      
                        "title": [
                            {{
                                "title: "U+1F31F Clarity and Timely Communication"
                            }}
                        ], 
                        "summary": [
                            {{
                                "summary: "This issue is that while tasks are agreed upon, there's littlw proactive communication on progress or delays causing missed calls and potential misunderstandings."
                            }}
                        ],
                        "suggestions": [
                            {{
                            "point": "Provide status updates regularly, even if incomplete, to manage expections."
                            }},
                            {{
                            "point": "Address missed calls promptly to avoid the other party feeling ignored or anxious."
                            }},
                            {{
                            "point": "This is the third actionable suggestion."
                            }},
                            {{
                            "point": "This is the fourth actionable suggestion."
                            }}
                        ]
                    }}

                    """
    user_prompt = """
                **The following is the chat history**

                {chat_history}
                """

    prompt = ChatPromptTemplate.from_messages(
        [
            ('system', system_prompt),
            ('user', user_prompt),
        ]
    )
    
    input_dict = {'chat_history': chat_history}

    llm = creat_llm()
    model = prompt | llm

    analysis_output = model.invoke(input_dict)
    output = analysis_output.content
    return output


def request_LLM_response_zh(chat_history):
    system_prompt = """
                    ** 任务描述 **
                    你是关系分析专家。你会收到我和一个同伴的聊天记录。您需要从输入的截图中分析聊天内容，并根据对话提供量身定制的情商提升建议。你的回答应该包括：

                    ** 语气风格 **
                    - 专业和客观，同时保持礼貌和中立的语气。

                    你的回答应该包括：
                    title：一个简洁的短语，概括了聊天中关键的情商方面（例如，“反应能力和主动沟通”），并包含一个emoji表情在最前方(eg. U+1F604, U+1F31F)。
                    summary：用一句话描述当前问题
                    您可以:
                    [基于当前背景的第一个可操作建议]
                    [基于分析对方对你的看法而提出的第二个可行建议]
                    [自我提升的第三个可行建议]
                    [用户可以给出的第四个可操作的建议]

                    ** 标准输出格式（开头不要写上json字母，不要漏,） **
                    {{
                        "title": [
                            {{
                                "title: [一个简洁的短语，概括了聊天中关键的情商方面（例如，“反应能力和主动沟通”），并包含一个emoji表情在最前方(eg. U+1F604, U+1F31F)]
                            }}
                        ], 
                        "summary": [
                            {{
                                "summary: [用一句话描述当前问题]
                            }}
                        ],
                        "suggestions": [
                            {{
                            "point": [基于当前背景的第一个可操作建议]
                            }},
                            {{
                            "point": [基于分析对方对你的看法而提出的第二个可行建议]
                            }},
                            {{
                            "point": [自我提升的第三个可行建议]
                            }},
                            {{
                            "point": [用户可以给出的第四个可操作的建议]
                            }}
                        ]                        
                    }}

                    ** 目标受众 **
                    - 目标受众是那些希望了解他人如何看待他们的人。

                    ** 输出样例 **
                    {{      
                        "title": [
                            {{
                                "title: "U+1F31F 清晰和及时的沟通" 
                            }}
                        ], 
                        "summary": [
                            {{
                                "summary: "问题在于，尽管任务已经达成共识，但缺乏主动的进度或延误沟通，导致错过电话和潜在的误解。"
                            }}
                        ],
                        "suggestions": [
                            {{
                            "point": "即使进展不完全，也要定期提供状态更新，以便管理预期"
                            }},
                            {{
                            "point": "及时处理未接来电，以避免对方感到被忽视或焦"
                            }},
                            {{
                            "point": "这是第三个可行的建议"
                            }},
                            {{
                            "point": "这是第四个可行的建议"
                            }}
                        ]
                    }}

                    """
    user_prompt = """
                **以下是给出的聊天记录**

                {chat_history}
                """

    prompt = ChatPromptTemplate.from_messages(
        [
            ('system', system_prompt),
            ('user', user_prompt),
        ]
    )
    
    input_dict = {'chat_history': chat_history}

    llm = creat_llm()
    model = prompt | llm

    analysis_output = model.invoke(input_dict)
    output = analysis_output.content
    return output

def parse_LLMresponse(json_data):
    try:
        response = json.loads(json_data)
        print("JSON is valid.")

        title = response['title'][0]
        summary = response['summary'][0]
        suggestions = response['suggestions']

        analysis = {
            "title": title,
            "summary": summary,
            "suggestions": suggestions
        }
        return analysis
    except json.JSONDecodeError as e:
        print("JSON is invalid:", e)
        raise

def retry_parse_LLMresponse(chat_history, locale=None, max_retries=5):
    attempt = 0
    # while attempt < max_retries:
    while 1:
        try:
            if locale == "en":
                json_data = request_LLM_response(chat_history)
            else:
                json_data = request_LLM_response_zh(chat_history)
            analysis = parse_LLMresponse(json_data)
            return analysis
        except json.JSONDecodeError as e:
            attempt += 1
            print(f"Attempt {attempt} failed. Retrying... for analysis")
            if attempt == max_retries:
                print("Max retries reached. Giving up.")
                # raise
    return None



if __name__ == "__main__":
    chat_history1 = "[{\"role\": \"user\", \"content\": \"姐，麻烦看下邮件呢，那个资料今天必须要了，都是星期五了\"}, {\"role\": \"colleague\", \"content\": \"那个不是我负责的\"}, {\"role\": \"user\", \"content\": \"不是一直都是你负责的吗\"}, {\"role\": \"user\", \"content\": \"以前每个月都是你发给我们的啊\"}, {\"role\": \"user\", \"content\": \"是业务交给别人了吗\"}, {\"role\": \"colleague\", \"content\": \"不知道 反正不是我负责的\"}]"
    chat_history2 = [{"role": "colleague", "content": "亲爱的你干什么去了？"}, {"role": "user", "content": "在处理点事情。"}, {"role": "colleague", "content": "说嘛，咋俩谁跟谁。"}, {"role": "user", "content": "在忙，待会儿聊。"}, {"role": "colleague", "content": "你不会是去面试了吧？"}]

    # response = retry_parse_LLMresponse_with_subordinate(personal_name="test", contact_name="test_contact", chat_history=chat_history1)
    analysis = retry_parse_LLMresponse(chat_history=chat_history2, locale = "en")
    print(analysis)

    # response = parse_LLMresponse_from_supervisor(response)
    # print(response)

    # response = retry_parse_LLMresponse_with_supervisor(chat_history=chat_history2)
    # print(response)
