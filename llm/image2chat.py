import os
import requests
import base64
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI


# def image2text(image_path):
#     IMAGE_PATH = image_path
#     # encoded_image = base64.b64encode(open(IMAGE_PATH, 'rb').read()).decode('ascii')

#     reader = easyocr.Reader(['ch_sim', 'en'])  # 支持中文和英文
#     encoded_image = reader.readtext(IMAGE_PATH)

#     system_prompt = """
#         **Task Description**
#         - You're an image recognition expert. You will receive a screenshot of my chat with someone else. You need to extract our conversation.

#         **Main Details**
#         - Message has to inlcude:
#             1. message sender {{user}}
#             2. message content {{message}}

#         **Extra Instructions**
#         The sender of the message on the left is the peer, and the sender of the message on the right is yourself. If the person's name is missing, use "them" instead.
        
#         **Standard Output Format**
#         [
#             {{"user": "me", "message": [message content]}}, 
#             {{"user": [peer name], "message": [message content]}}
#         ]

#         ** Extra Instructions **
#         If the language used in image is chinese, then the output should be chinese.
#         If the language used in image is english, then the output should be english.

#     """

#     user_prompt = """
#                 **The follwoing is a screenshot of the chat history**

#                 {encoded_image}
#                 """

#     prompt = ChatPromptTemplate.from_messages(
#         [
#             ('system', system_prompt),
#             ('user', user_prompt),
#         ]
#     )
    
#     input_dict = {'encoded_image': encoded_image}

#     llm = creat_llm()
#     model = prompt | llm

#     analysis_output = model.invoke(input_dict)
#     output = analysis_output.content
#     print(output)

#     return output



ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT_LONG')
AZURE_DEPLOYMENT = os.getenv('AZURE_DEPLOYMENT')

def image2text(image_path):  
    IMAGE_PATH = image_path     

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )

    client = AzureOpenAI(
        api_version="2024-03-01-preview",
        azure_endpoint=ENDPOINT,
        azure_ad_token_provider=token_provider,
    )

    encoded_image = base64.b64encode(open(IMAGE_PATH, 'rb').read()).decode('ascii')      

    system_prompt = """
        **Task Description**
        - You're an image recognition expert. You will receive a screenshot of my chat with someone else. You need to extract our conversation.

        **Main Details**
        - Message has to inlcude:
            1. message sender {{user}}
            2. message content {{message}}

        **Extra Instructions**
        The sender of the message on the left is the peer, and the sender of the message on the right is yourself. If the person's name is missing, use "them" instead.
        
        **Standard Output Format**
        [
            {{"user": "me", "message": [message content]}}, 
            {{"user": [peer name], "message": [message content]}}
        ]

        ** Extra Instructions **
        If the language used in image is chinese, then the output should be chinese.
        If the language used in image is english, then the output should be english.
    """


    response = client.chat.completions.create(
        # For Azure OpenAI, the model parameter must be set to the deployment name
        model=os.getenv("AZURE_DEPLOYMENT"),
        temperature=0.7,
        n=1,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": 
                                    [{           
                                        "type": "image_url",           
                                        "image_url": {             
                                            "url": f"data:image/jpeg;base64,{encoded_image}"           
                                        }         
                                    }]    
            },
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    current_path = os.getcwd()
    image_path = os.path.join(current_path, "test_image.png")
    image2text(image_path=image_path)