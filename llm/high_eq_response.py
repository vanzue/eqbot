import re
from html import unescape
from datetime import datetime
from keyless_setup import creat_llm
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from prompt import *

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

    if not isinstance(text, list):
        raise TypeError("Expected a list of dictionaries for text.")

    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')

    for entry in text:
        message = entry['message']
        if chinese_pattern.search(message):
            return 'zh'

    return 'en'


class EQmaster:
    def __init__(self, username=None):
        self.scene = ""
        self.analyse = ""
        self.message = []
        self.chat_history = []
        self.username = username
        self.current_stage = 1  # 初始化状态为stage1
        self.options = []  # 存储stage2的回复选项

    def get_response_stage1(self, chat_history, user_nick_name):
        self.chat_history = chat_history
        sys_prompt = stage1_prompt.format(
            chat_history=self.chat_history, user_nick_name=user_nick_name)
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

    def get_response_stage2(self, userPrefer=None, analyse=None, user_nick_name=None):
        language = detect_language(self.chat_history)
        print("Language detected:", language)
        self.options = []
        sys_prompt = stage2_prompt1.format(
            chat_history=self.chat_history, user_nick_name=user_nick_name,
            analyse=self.analyse)

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
            chat_history=self.chat_history, user_nick_name=user_nick_name, analyse=analyse,
            userPrefer=userPrefer if userPrefer else None, temp=temp)

        if language == 'en':
            sys_prompt += "\nPlease reply in English.\n"

        message = [{"role": "system", "content": sys_prompt}]
        llm = creat_llm()
        response = llm.invoke(message).content

        self.message += [{"role": "assistant", "content": response}]
        self.options = [re.sub(r"^\d+\️⃣", "", line).strip()
                        for line in response.split("\n") if line.strip()]

        if language == 'zh':
            options_prompt = "以下有几种回复参考，请问您倾向选择哪一种回复呢？当然也可以告诉我您有什么回复倾向哦~\n"
        else:
            options_prompt = "There are several possible replies, which one do you prefer? You can also tell me what kind of reply you prefer!\n"

        for i, option in enumerate(self.options, 1):
            options_prompt += f"{i}️⃣ {option.strip()}\n"

        return options_prompt

    def get_response_stage3(self, user_choice):
        return self.options[user_choice - 1]

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

    def get_response_eqmaster(self, user_nick_name=None, chat_history=None, query=None):
        if chat_history:
            analyse = self.get_response_stage1(chat_history, user_nick_name)
            self.current_stage = 2
            response = self.get_response_stage2(analyse, user_nick_name)
            self.current_stage = 3
            return response
        elif query:
            if query.isdigit():
                user_choice = int(query.strip())
                response = self.get_response_stage3(user_choice)
            elif self.current_stage == 2:
                print("current stage is 2, regenerating stage 2 response")
                response = self.get_response_stage2(
                    query, self.analyse, user_nick_name)
            else:
                print("query provided but not a valid stage")
                response = self.get_text_response(query)
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
