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
                    title: A concise phrase summarizing the key emotional intelligence aspect of the chat (e.g., "Responsiveness and Proactive Communication"). 
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
                                "title: [A concise phrase summarizing the key emotional intelligence aspect of the chat. ]
                            }}
                        ], 
                        "summary": [
                            {{
                                "summary: [One sentence describing the current issue]
                            }}
                        ],
                        "suggestions": [
                            {{
                            "point": [First actionable suggestion based on the current context]
                            }},
                            {{
                            "point": [Second actionable suggestion based on the analysis of the other person's perspective of you]
                            }},
                            {{
                            "point": [Third actionable suggestion for self-improvement]
                            }},
                            {{
                            "point": [[Fourth actionable suggestion for a recommended response the user can give]]
                            }}
                        ]                        
                    }}

                    ** Audience **
                    - The target audience is those who wish to understand how the other person perceives them.

                    ** Output Example **
                    {{      
                        "title": [
                            {{
                                "title: "Responsiveness and Proactive Communication" ]
                            }}
                        ], 
                        "summary": [
                            {{
                                "summary: "You should listen more abot others' opinions."
                            }}
                        ],
                        "suggestions": [
                            {{
                            "point": "This is the first actionable suggestion."
                            }},
                            {{
                            "point": "This is the second actionable suggestion."
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
                **Rhe following is the chat history**

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

def retry_parse_LLMresponse(chat_history, max_retries=5):
    attempt = 0
    while attempt < max_retries:
        try:
            json_data = request_LLM_response(chat_history)
            analysis = parse_LLMresponse(json_data)
            return analysis
        except json.JSONDecodeError as e:
            attempt += 1
            print(f"Attempt {attempt} failed. Retrying...")
            if attempt == max_retries:
                print("Max retries reached. Giving up.")
                # raise
    return None



if __name__ == "__main__":
    chat_history1 = "[{\"role\": \"user\", \"content\": \"姐，麻烦看下邮件呢，那个资料今天必须要了，都是星期五了\"}, {\"role\": \"colleague\", \"content\": \"那个不是我负责的\"}, {\"role\": \"user\", \"content\": \"不是一直都是你负责的吗\"}, {\"role\": \"user\", \"content\": \"以前每个月都是你发给我们的啊\"}, {\"role\": \"user\", \"content\": \"是业务交给别人了吗\"}, {\"role\": \"colleague\", \"content\": \"不知道 反正不是我负责的\"}]"
    chat_history2 = [{"role": "colleague", "content": "亲爱的你干什么去了？"}, {"role": "user", "content": "在处理点事情。"}, {"role": "colleague", "content": "说嘛，咋俩谁跟谁。"}, {"role": "user", "content": "在忙，待会儿聊。"}, {"role": "colleague", "content": "你不会是去面试了吧？"}]

    # response = retry_parse_LLMresponse_with_subordinate(personal_name="test", contact_name="test_contact", chat_history=chat_history1)
    analysis = retry_parse_LLMresponse(chat_history=chat_history2)
    print(analysis)

    # response = parse_LLMresponse_from_supervisor(response)
    # print(response)

    # response = retry_parse_LLMresponse_with_supervisor(chat_history=chat_history2)
    # print(response)
