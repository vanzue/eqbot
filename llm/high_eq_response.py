import re
from datetime import datetime
from llm.keyless_setup import creat_llm
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from llm.prompt import *
import json

load_dotenv()


def detect_language(text):
    print("here is text:", text)
    if isinstance(text, str):
        try:
            text = json.loads(text)
        except json.JSONDecodeError:
            raise ValueError(
                "Invalid format: text is a string but cannot be parsed as JSON.")

    # Check if text is a dictionary with 'chat' field or a list
    if isinstance(text, dict) and 'chat' in text:
        chat_entries = text['chat']
    elif isinstance(text, list):
        chat_entries = text
    else:
        raise TypeError(
            "Expected either a dictionary with a 'chat' field or a list of dictionaries.")

    if not isinstance(chat_entries, list):
        raise TypeError("The 'chat' field should be a list of dictionaries.")

    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')

    for entry in chat_entries:
        message = entry.get('message', '')
        if chinese_pattern.search(message):
            return 'zh'

    return 'en'


class EQmaster:
    def __init__(self):
        self.scene = ""
        self.message = []
        self.chat_history = []
        self.current_stage = 1  # 初始化状态为stage1

    # do analyze
    def get_response_stage1(self, chat_history):
        self.chat_history = chat_history
        sys_prompt = stage1_prompt.format(
            chat_history=self.chat_history, user_nick_name="")
        message = [{"role": "system", "content": sys_prompt}]
        self.message = []

        llm = creat_llm()
        response = llm.invoke(message).content
        response_parts = response.split("\n\n")
        if len(response_parts) >= 2:
            self.scene = response_parts[1].replace(
                "Inferred Scene:：", "").strip()
        else:
            self.scene = response_parts
            print(
                "Warning: response does not contain enough parts. Using default scene.")
        self.analyse = response

        self.options = response_parts[3].split(
            '\n') if len(response_parts) > 3 else []

        return response

    # do response
    def get_response_stage2(self, chat_history,
                            userPrefer=None, analyse=None):
        language = detect_language(chat_history)
        print("Language detected:", language)
        sys_prompt = stage2_prompt1.format(
            chat_history=chat_history, user_nick_name="",
            analyse=analyse)

        message = [{"role": "system", "content": sys_prompt}]
        keys = []
        temp = ""

        llm = creat_llm()
        response = llm.invoke(message).content
        keys = [i.replace("\"", "").strip() for i in response.split("\n")]
        for scene in keys:
            if scene in scene_data.keys():
                temp += scene_data[scene] + "\n"

        sys_prompt = stage2_prompt2.format(
            chat_history=self.chat_history, user_nick_name="", analyse=analyse,
            userPrefer=userPrefer if userPrefer else None, temp=temp)

        if language == 'en':
            sys_prompt += "\nPlease reply in English.\n"

        message = [{"role": "system", "content": sys_prompt}]
        llm = creat_llm()
        response = llm.invoke(message).content

        options = [re.sub(r"^\d+\️⃣", "", line).strip()
                   for line in response.split("\n") if line.strip()]

        return options

    def get_text_response(self, query):
        sys_prompt = f"""
            You are an emotional intelligence response assistant, skilled at providing thoughtful and empathetic replies to user inquiries. Your task is to understand the context of the user’s question and suggest responses that resonate with American cultural values, such as individualism, openness, and collaboration. Aim to foster a supportive dialogue that encourages trust and connection.
        """
        message = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": query}
        ]

        llm = creat_llm()
        response = llm.invoke(message).content
        return response

    def get_response_and_analyze(self, chat_history):
        analyse = self.get_response_stage1(chat_history,)
        response = self.get_response_stage2(chat_history, "",
                                            analyse)
        return response, analyse

    def get_response_by_intent(self, chat_history, intent, analyze):
        response = self.get_response_stage2(chat_history,
                                            intent, analyze)
        return response


def main():
    eqmaster = EQmaster()
    chat_history = [
        {"userName": "TestUser", "message": "Hi, I need some help with a project."},
        {"userName": "Colleague", "message": "Sure, what do you need help with?"},
        {"userName": "TestUser",
            "message": "I need assistance preparing a presentation for our upcoming meeting."},
        {"userName": "Colleague", "message": "No problem, I can help with that."}
    ]

    print("Testing get_response_eqmaster with chat history...")
    response = eqmaster.get_response_eqmaster(
        user_nick_name="TestUser", chat_history=chat_history)
    print(response)


if __name__ == "__main__":
    main()
