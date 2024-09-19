import os
import requests
from bs4 import BeautifulSoup
from openai import AzureOpenAI
from langchain_openai import AzureChatOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider


"""Configure the Azure OpenAI client."""
# os.environ["AZURE_OPENAI_ENDPOINT"] = "https://nft2b-gpt4.openai.azure.com/"
# azure_deployment = "dmigpt4o"
# api_version = "2024-02-01"
# token_provider = get_bearer_token_provider(
#     DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
# )

os.environ["AZURE_CLIENT_ID"] = "ae21e6cf-ba89-410a-b52a-684bbb686343"
os.environ["AZURE_TENANT_ID"] = "8fb0df59-77b9-421c-94a0-10688a6e7c22"
os.environ["AZURE_CLIENT_SECRET"] = "lsQ8Q~mNnSiEtqd18rQVYeni8UVQLEeVhio51dg7"

os.environ["AZURE_OPENAI_ENDPOINT"] = "https://peitingaoai.openai.azure.com/"
azure_deployment = "4opeitingus"
api_version = "2024-02-15-preview"

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)

def creat_llm():
    llm = AzureChatOpenAI(
        azure_ad_token_provider=token_provider,
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_version=api_version,
        azure_deployment=azure_deployment,
    )
    return llm




def bing_search(query, offset=0, count=50, safeSearch="Strict"):
    subscription_key = "ec52313cf176406186f4274facaae8a3"
    search_url = "https://api.bing.microsoft.com/v7.0/search"

    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    params = {
        "q": query, 
        "textDecorations": False, 
        "textFormat": "Raw", 
        "count": count, 
        "safeSearch": safeSearch,
        "offset": offset
    }
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()
    return search_results

def browse_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.body.get_text(separator='\n', strip=True)
        return text
    return None


if __name__ == "__main__":
    import os
    import json
    import requests
    import datetime
    from bs4 import BeautifulSoup
    from openai import AzureOpenAI
    from langchain_openai import AzureChatOpenAI
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

    from chat_llms import *
    from utils import *

    import importlib
    import prompts
    importlib.reload(prompts)
    from prompts import *

    llm = creat_llm()
    input_dict = {'user_info': 1, 'num_scenarios': 4}
    original_prompt = scenario_library_creation_original_system_prompt
    slc_prompt = ChatPromptTemplate.from_messages(
        [
            ('system', original_prompt),
            ('human', scenario_library_creation_task_prompt),
        ]
    )
    slc_model = slc_prompt | llm
    scenario_library_output = slc_model.invoke(input_dict)
    pass
