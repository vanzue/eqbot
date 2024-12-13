import os
from dotenv import load_dotenv

from llm.keyless_setup import creat_llm
from llm.base.agent import Agent

from llm.prompt import prompt_battlefield_multilingual_library

load_dotenv()

def escape_braces(template_str):
    return template_str.replace("{", "{{").replace("}", "}}")

def request_LLM_response_by_eval(user_query, db_prompt=None, lang='zh'):
    assert lang in prompt_battlefield_multilingual_library, f"Language {lang} not supported"
    prompt_battlefield = prompt_battlefield_multilingual_library[lang]

    eval_agent = Agent(name="eval", llm=creat_llm())
    system_prompt = prompt_battlefield.eval_system_prompt
    user_prompt = prompt_battlefield.eval_user_prompt
    eval_agent.set_prompts(system_prompt, user_prompt)
    input_dict = {'user_query': user_query}
    analysis_output = eval_agent.act(input_dict)
    return analysis_output

def request_LLM_response(user_query, db_prompt, lang='zh'):
    assert lang in prompt_battlefield_multilingual_library, f"Language {lang} not supported"
    prompt_battlefield = prompt_battlefield_multilingual_library[lang]

    # user_prompt = escape_braces(user_prompt)
    system_prompt = db_prompt + prompt_battlefield.dialogue_system_prompt
    user_prompt = prompt_battlefield.dialogue_user_prompt
    dialog_agent = Agent(name="dialog", llm=creat_llm())
    dialog_agent.set_prompts(system_prompt, user_prompt)
    input_dict = {'user_query': user_query}
    analysis_output = dialog_agent.act(input_dict)
    return analysis_output

def send_to_LLM_multiagent(user_query, db_prompt, lang='zh'):
    assert lang in prompt_battlefield_multilingual_library, f"Language {lang} not supported"

    prompt_battlefield = prompt_battlefield_multilingual_library[lang]
    system_prompt = db_prompt+prompt_battlefield.dialogue_system_prompt
    user_prompt = prompt_battlefield.dialogue_user_prompt
    dialog_agent = Agent(name="dialog", llm=creat_llm())
    dialog_agent.set_prompts(system_prompt, user_prompt)
    input_dict = {'user_query': user_query}
    analysis_output = dialog_agent.act(input_dict)
    return analysis_output


if __name__ == "__main__":
    user_query = ["开始"]
    user_chat = "{'dialog': [{'role': '领导', 'content': '这家餐厅的菜品看起来不错，大家有什么推荐的吗？'}, {'role': '同事A', 'content': '领导，您喜欢吃什么，我们就点什么。您的口味肯定不会错。'}, {'role': '同事B', 'content': '哎呀，领导的口味当然是最好的。我们就跟着领导点吧，不会有错的。'}]}"
    try:
        res = request_LLM_response_by_eval(user_chat)
        print(res)
    except Exception as e:
        print(f"An error occurred: {e}")
    # [x] 1. Multiagent -> API (Single/ Multi-agent)
    # [1] 2. EN prompt + Senario (PM)
    # [x] 3. EN RAG dataset
    # [x] 4. t2s / s2t
