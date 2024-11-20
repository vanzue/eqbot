import re
from datetime import datetime
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm.keyless_setup import creat_llm
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from llm.prompt import *
import json

load_dotenv()

class EQmaster:
    def __init__(self):
        self.scene = ""
        self.message = []
        self.chat_history = []
        self.current_stage = 1  # 初始化状态为stage1

    def detect_language(self, text):
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
        print("here is text:", text)
        if isinstance(text, str):
            return chinese_pattern.search(text) and 'zh' or 'en'

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

        for entry in chat_entries:
            message = entry.get('message', '')
            if chinese_pattern.search(message):
                print("Detected Chinese text:")
                return 'zh'
        print("Detected English text:")
        return 'en'


    # do analyze
    def get_response_stage1(self, chat_history,user_nick_name=""):
        self.chat_history = chat_history
        sys_prompt = stage1_prompt.format(
            chat_history=self.chat_history, user_nick_name= user_nick_name)
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
    
    def get_response_stage1_zh(self, chat_history,user_nick_name=""):
        self.chat_history = chat_history
        sys_prompt = stage1_prompt_zh.format(
            chat_history=self.chat_history, user_nick_name= user_nick_name)
        message = [{"role": "system", "content": sys_prompt}]
        self.message = []

        llm = creat_llm()
        response = llm.invoke(message).content
        response_parts = response.split("\n\n")
        if len(response_parts) >= 2:
            self.scene = response_parts[1].replace(
                "推测场景：", "").strip()
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
        sys_prompt += "\nPlease reply in English.\n"


        message = [{"role": "system", "content": sys_prompt}]
        llm = creat_llm()
        response = llm.invoke(message).content

        options = [re.sub(r"^\d+\️⃣", "", line).strip()
                   for line in response.split("\n") if line.strip()]  
        return options

    def get_response_stage2_zh(self, chat_history,
                            userPrefer=None, analyse=None):
        sys_prompt = stage2_prompt1_zh.format(
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
        user_prefer_value = userPrefer if userPrefer else 'none'
        print("user_prefer_value:", user_prefer_value)
        sys_prompt = stage2_prompt2_zh.format(
            chat_history=self.chat_history, user_nick_name="", analyse=analyse,
            userPrefer=user_prefer_value, temp=temp)
        sys_prompt += "\nPlease reply in Chinese.\n"
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

    def get_response_and_analyze(self, chat_history,user_nick_name="", language="en"):
        if(language == 'zh'):
            analyse = self.get_response_stage1_zh(chat_history,user_nick_name)
            response = self.get_response_stage2_zh(chat_history, "",
                                                analyse)
        else:
            analyse = self.get_response_stage1(chat_history,user_nick_name)
            response = self.get_response_stage2(chat_history, "",
                                                analyse)
        return response, analyse

    def get_response_by_intent(self, chat_history, intent, analyze):
        response = self.get_response_stage2(chat_history,
                                            intent, analyze)
        return response
    
    def get_response_by_intent_zh(self, chat_history, intent, analyze):
        response = self.get_response_stage2_zh(chat_history,
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

    chat_history_zh = [
        {"userName": "测试用户", "message": "你好，我需要一些项目上的帮助。"},
        {"userName": "同事", "message": "好的，你需要什么帮助？"},
        {"userName": "测试用户", "message": "我需要帮助准备我们即将召开的会议的演示文稿。"},
        {"userName": "同事", "message": "没问题，我可以帮忙。"}
    ]


    print("Testing get_response_eqmaster with chat history...")
    language = detect_language(chat_history_zh)
    print("Language detected:", language)
    response, analyse = eqmaster.get_response_and_analyze(
        chat_history_zh, "me", language)
    print("response:", response)
    print("analyse:", analyse)
    # if(language == 'en'):
    #     response = eqmaster.get_response_stage1(
    #         user_nick_name="TestUser", chat_history=chat_history)
    # else:
    #     response = eqmaster.get_response_stage1_zh(
    #         user_nick_name="TestUser", chat_history=chat_history_zh)
    # print(response)


if __name__ == "__main__":
    main()
