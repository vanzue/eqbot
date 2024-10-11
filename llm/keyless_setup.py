import os
from langchain_openai import AzureChatOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from dotenv import load_dotenv
load_dotenv()



"""Configure the Azure OpenAI client."""

AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_DEPLOYMENT = os.getenv('AZURE_DEPLOYMENT')
AZURE_DEPLOYMENT_API_VERSION = os.getenv('AZURE_DEPLOYMENT_API_VERSION')

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)

def creat_llm():
    llm = AzureChatOpenAI(
        azure_ad_token_provider=token_provider,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version=AZURE_DEPLOYMENT_API_VERSION,
        azure_deployment=AZURE_DEPLOYMENT,
    )
    return llm

if __name__ == "__main__":
    from langchain_core.prompts import ChatPromptTemplate

    system_prompt = """
                    **任务描述**
                    - 你是一位关系分析专家。你将接收一段我与同级同事的聊天记录。你需要根据以下几个维度对聊天记录进行分析。

                    **关键细节**
                    - 维度包括：
                    1. {{关系分析}}
                    2. {{共事契合度}}
                    3. {{心眼子指数}}
                    4. {{职场性格}}
                    5. {{感兴趣的话题}}
                    6. {{鉴别坏同事}}

                    **语气与风格**
                    - 专业且客观，同时保持礼貌和中立的语气。

                    **标准输出格式(不要写上json字母, 也不要漏,)**
                    {{
                        "关系分析": [对你与同级同事之间关系的简短分析，注意分析边界感],
                        "共事契合度": [分析你们在工作中的配合程度，契合度高低及原因],
                        "心眼子指数": [推测同事的心机程度，0到100分，说明原因，需要关注是否存在窥探个人隐私的情况],
                        "职场性格": [根据聊天记录，分析同事的职场性格特征，如外向、谨慎、独立等],
                        "感兴趣的话题": [基于聊天内容，分析同事对哪些话题感兴趣],
                        "鉴别坏同事": [判断该同事是否有潜在的负面影响或坏同事行为，并说明理由]
                    }}

                    **受众**
                    - 目标受众为希望了解与同级同事关系，并提升共事能力的用户，具有基本的职场经验。

                    **输出示例**
                    {{
                        "关系分析": "你与这位同事的关系看似不太紧密，沟通中缺乏一定的理解和包容，表现出一定的紧张和争执。",
                        "共事契合度": "你们的共事契合度较低，沟通中存在信息不对称和职责分工不明确的问题，需要加强沟通与协调。",
                        "心眼子指数": “75, 同事在对话中表现出一定的防备和推诿责任的倾向，可能会在特定情况下保护自己的利益。",
                        "职场性格": "同事表现出较为谨慎和防御的性格特征，倾向于明确职责范围，不愿多承担额外的责任。",
                        "感兴趣的话题": "从聊天记录来看，没有明确显示同事对特定话题的兴趣，更多的是关注工作职责分工。",
                        "鉴别坏同事": "同事表现出一定的推诿责任的行为，但没有明显的恶意或破坏性行为迹象，需进一步观察其在团队中的表现。"
                    }}

                    **额外指示**
                    - 确保分析客观、公正，避免任何过度主观或带有偏见的推测，提供的建议应有助于用户改善职场关系，但也要谨防他人对于个人隐私的追问。
                    """
    user_prompt = """
                我的名字是{personal_name}, 同事的名字是{contact_name}。

                **以下是聊天记录**

                {chat_history}
                """

    prompt = ChatPromptTemplate.from_messages(
        [
            ('system', system_prompt),
            ('user', user_prompt),
        ]
    )
    
    personal_name = 'ultraseven'
    contact_name = 'ultraman'
    chat_history = 'ultraseven：把方案交一下ultraman：你说公主请交方案ultraseven：不想干明天可以不用来了。ultraman：好的后天见ultraseven：你后天也不用来了"'
    input_dict = {'personal_name': personal_name, 'contact_name': contact_name, 'chat_history': chat_history}

    llm = creat_llm()
    model = prompt | llm

    analysis_output = model.invoke(input_dict)
    output = analysis_output.content
    print(output)