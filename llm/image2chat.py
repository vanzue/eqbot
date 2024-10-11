import os
import requests
import base64
from langchain_core.prompts import ChatPromptTemplate

from llm.keyless_setup import creat_llm

def image2text(image_path):
    IMAGE_PATH = image_path
    encoded_image = base64.b64encode(open(IMAGE_PATH, 'rb').read()).decode('ascii')

    system_prompt = """
        **任务描述**
        - 你是一位图像识别专家。你将接收一段含有我与他人的聊天记录的截图。你需要提取出我们的对话内容。

        **关键细节**
        - 维度包括：
            1. 对话时间 {{time}}
            2. 消息发送方 {{sender}}
            3. 消息内容 {{message}}

        **额外指示**
        左侧消息发送方为对方，右侧消息发送方为自己。如若缺少自身名字，则用“我”来代替。
        
        **标准输出格式**
        [
            {{"time": [对话时间], "sender": "我", "message": [消息内容]}}, 
            {{"time": [对话时间], "sender": [对方名字], "message": [消息内容]}}
        ]

        **输出样例**
        [
            {{"time": "2024-9-4 11:47", "sender": "WHISKYpop 🍭", "message": "姐，麻烦看下邮件呢，那个资料必须今天要了，都是星期五了"}}, 
            {{"time": "2024-9-4 11:49", "sender": "c.llm.high 公羽", "message": "那个不是我负责的"}}, 
            {{"time": "2024-9-4 13:01", "sender": "WHISKYpop 🍭", "message": "不是一直都是 你负责的吗"}}, 
            {{"time": "2024-9-4 13:01", "sender": "WHISKYpop 🍭", "message": "以前每个月都是你发给我们的啊"}}, 
            {{"time": "2024-9-4 13:02", "sender": "WHISKYpop 🍭", "message": "是业务交给别人了吗"}}, 
            {{"time": "2024-9-4 13:02", "sender": "c.llm.high 公羽", "message": "不知道 反正不是我负责的"}}
        ]
    """
    user_prompt = """
                **以下是聊天记录截图**

                {encoded_image}
                """

    prompt = ChatPromptTemplate.from_messages(
        [
            ('system', system_prompt),
            ('user', user_prompt),
        ]
    )
    
    input_dict = {'encoded_image': encoded_image}

    llm = creat_llm()
    model = prompt | llm

    analysis_output = model.invoke(input_dict)
    output = analysis_output.content
    print(output)

    return output




    # # Configuration
    # API_KEY = LLM_API
    # IMAGE_PATH = image_path
    # encoded_image = base64.b64encode(open(IMAGE_PATH, 'rb').read()).decode('ascii')
    # headers = {
    #     "Content-Type": "application/json",
    #     "api-key": API_KEY,
    # }

    # # Payload for the request
    # payload = {
    # "messages": [
    #     {
    #     "role": "system",
    #     "content": [
    #         {
    #         "type": "text",
    #         "text": """
    #                     **任务描述**
    #                     - 你是一位图像识别专家。你将接收一段含有我与他人的聊天记录的截图。你需要提取出我们的对话内容。

    #                     **关键细节**
    #                     - 维度包括：
    #                     1. 对话时间time
    #                     2. 消息发送方sender
    #                     3. 消息内容message

    #                     **额外指示**
    #                     左侧消息发送方为对方，右侧消息发送方为自己。如若缺少自身名字，则用“我”来代替。
                        
    #                     **标准输出格式**
    #                     [{"time": [对话时间], "sender": "我", "message": [消息内容]}, 
    #                     {"time": [对话时间], "sender": [对方名字], "message": [消息内容]}, 


    #                     **输出样例**
    #                     [{"time": "2024-9-4 11:47", "sender": "WHISKYpop 🍭", "message": "姐，麻烦看下邮件呢，那个资料必须今天要了，都是星期五了"}, 
    #                     {"time": "2024-9-4 11:49", "sender": "c.llm.high 公羽", "message": "那个不是我负责的"}, 
    #                     {"time": "2024-9-4 13:01", "sender": "WHISKYpop 🍭", "message": "不是一直都是 你负责的吗"}, 
    #                     {"time": "2024-9-4 13:01", "sender": "WHISKYpop 🍭", "message": "以前每个月都是你发给我们的啊"}, 
    #                     {"time": "2024-9-4 13:02", "sender": "WHISKYpop 🍭", "message": "是业务交给别人了吗"}, 
    #                     {"time": "2024-9-4 13:02", "sender": "c.llm.high  公羽", "message": "不知道 反正不是我负责的"}]
    #                 """
    #         }
    #     ]
    #     },
    #     {
    #         "role": "user",
    #         "content": [
    #             {
    #                 "type": "image",
    #                 "image": encoded_image
    #             }
    #         ]
    #     }
    # ],
    # "temperature": 0.7,
    # "top_p": 0.95,
    # "max_tokens": 800
    # }

    # ENDPOINT = "https://peitingaoai.openai.azure.com/openai/deployments/4opeitingus/chat/completions?api-version=2024-02-15-preview"

    # # Send request
    # try:
    #     response = requests.post(ENDPOINT, headers=headers, json=payload)
    #     response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
    # except requests.RequestException as e:
    #     raise SystemExit(f"Failed to make the request. Error: {e}")

    # # Handle the response as needed (e.g., print or process)
    # print(response.json()['choices'][0]['message']['content'])

    # return response.json()['choices'][0]['message']['content']

if __name__ == "__main__":
    current_path = os.getcwd()
    image_path = os.path.join(current_path, "test_image.png")
    image2text(image_path=image_path)