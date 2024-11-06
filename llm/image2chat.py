import os
import json
import requests
import base64
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI


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
        - You're also an expert of summary. Please summurize the given chat history by less than 10 words and give out the most uegent dimension that need to be improved among five dimensions.
        - If the language used in image is chinese, then the dimension are 感知力, 掌控力, 共情力,驱动力,社交力".
        - If the language used in image is english, then the dimension are Perception, Self Regulation, Empathy, Social Skill and Motivation.

        **Main Details**
        - Message has to inlcude:
            1. message sender {{user}}
            2. message content {{message}}

        **Extra Instructions**
        The sender of the message on the left is the peer, and the sender of the message on the right is yourself. If the person's name is missing, use "them" instead.
        
        **Standard Output Format(Do not include the word "json", and do not omit anything.)**
        {{
            "chat":[
                {{"user": "me", "message": [message content]}}, 
                {{"user": [peer name], "message": [message content]}}
            ],
            "summary": [summary of the chat above],
            "low_dim" : [the most uegent dimension that need to be improved]
        }}    

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
    # print(response.choices[0].message.content)
    return response.choices[0].message.content

def parse_chatHistory(json_data):
    try:
        response = json.loads(json_data)
        print("JSON is valid.")

        chat_history = response['chat']
        summary = response['summary']
        low_dim = response['low_dim']

        analysis = {
            "chat_history": chat_history,
            "summary": summary,
            "low_dim": low_dim
        }
        # print(analysis)
        return analysis
    except json.JSONDecodeError as e:
        print("JSON is invalid:", e)
        raise

def get_image2text(image_path, max_retries=5):
    attempt = 0
    while attempt < max_retries:
        try:
            json_data = image2text(image_path)
            analysis = parse_chatHistory(json_data)
            return analysis
        except json.JSONDecodeError as e:
            attempt += 1
            print(f"Attempt {attempt} failed. Retrying...")
            if attempt == max_retries:
                print("Max retries reached. Giving up.")
                # raise
    return None

if __name__ == "__main__":
    current_path = os.getcwd()
    image_path = os.path.join(current_path, "test_image.png")
    res = get_image2text(image_path=image_path)
    print(res)
    # parse_chatHistory(res)
    