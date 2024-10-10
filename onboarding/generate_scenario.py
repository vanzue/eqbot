import json
import os
import requests
import base64
from datetime import datetime
import time
import random

from dotenv import load_dotenv

load_dotenv()
LLM_API = os.getenv('LLM_API')

# Add these variables at the top of the file, after the imports
SCENARIO_TYPES = ["职场刁难", "帮助别人融入", "应对突发状况"]
used_scenarios = set()

# Configuration
API_KEY = LLM_API
headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY,
}
ENDPOINT = "https://peitingaoai.openai.azure.com/openai/deployments/4opeitingus/chat/completions?api-version=2024-02-15-preview"

# Initial context for the first question
initial_context = ("""
        情商评分规则：基于自我分析维度，以下是一些流行的评估题目。这些题目涵盖了情绪侦查/阅读力、情绪掌控力、人际平衡术、沟通表达力和社交得体度五个核心方面，旨在评估个人的情商水平。

        1. 情绪侦查/阅读力（情绪感知与理解）
        我能够迅速察觉到自己情绪的变化。（1-5分）
        我能够轻易辨别他人情绪的微妙变化。（1-5分）
        我擅长分析他人情绪背后的原因。（1-5分）
        我能够区分不同类型的情绪，如焦虑、愤怒或悲伤。（1-5分）
        我能根据情境判断他人的情感需求。（1-5分）
        2. 情绪掌控力（情绪控制与管理）
        我能在情绪激动时保持冷静并控制自己的反应。（1-5分）
        我在面对突发事件时，能够快速稳定自己的情绪。（1-5分）
        我能通过有效的方式宣泄负面情绪，而不影响他人。（1-5分）
        在面对压力时，我能有效调节自己的情绪以保持理性。（1-5分）
        我能适应情绪上的变化，并迅速恢复情绪稳定。（1-5分）
        3. 人际平衡术（关系管理）
        我能够在团队中有效地处理人际关系。（1-5分）
        当出现矛盾时，我能够通过妥协和沟通解决问题。（1-5分）
        我能够在不同背景和性格的人之间找到平衡点。（1-5分）
        我能够敏锐地捕捉团队中的紧张情绪，并采取行动化解。（1-5分）
        我能够建立长期的、稳定的关系，无论是在个人生活中还是在工作中。（1-5分）
        4. 沟通表达力（沟通与表达）
        我能够清晰地表达自己的想法和需求。（1-5分）
        在沟通过程中，我能保持开放的态度，倾听他人意见。（1-5分）
        我善于在不同场合选择合适的沟通方式。（1-5分）
        我能通过非语言的方式（如面部表情、肢体语言）有效传达信息。（1-5分）
        我能够在复杂的对话中避免误解和冲突。（1-5分）
        5. 社交得体度（社交礼仪与技巧）
        我能在社交场合中得体地表现自己，遵守礼仪规范。（1-5分）
        我能根据场合和对象调整自己的言行，保持礼貌和尊重。（1-5分）
        在需要互动时，我能迅速判断该如何得体地介入对话。（1-5分）
        我能够识别他人的社交暗示，避免尴尬或不适。（1-5分）
        我擅长维护和提升个人形象，避免在社交中犯下失礼行为。（1-5分）

        请返回的 JSON 数据结构如下：
        {
          "scenes": {
            "background": 你帮同事[小王]盛饭，盛得比较多，同事[小王]问：,
            "role": "小王",
            "location": "食堂",
            "description": "你这是在喂猪呢？",
            "options": [  
                {  
                    "text": "1.哈哈，只是想让你吃饱嘛。",  
                    "scores": {"情绪侦查力": 4, "情绪掌控力": 3, "人际平衡术": 4, "沟通表达力": 3, "社交得体度": 4},  
                    "analysis": "你用幽默化解了尴尬，表现了较好的情绪侦查力和人际平衡术。",  
                },  
                {  
                    "text": "2.我不允许你这样子骂自己。",  
                    "scores": {"情绪侦查力": 2, "情绪掌控力": 3, "人际平衡术": 2, "沟通表达力": 3, "社交得体度": 2},  
                    "analysis": "你用幽默化解了尴尬，表现了较好的情绪侦查力和人际平衡术。",  
                },  
                {  
                    "text": "3.不好意思，我盛多了。",  
                    "scores": {"情绪侦查力": 3, "情绪掌控力": 4, "人际平衡术": 2, "沟通表达力": 3, "社交得体度": 3},  
                    "analysis": "你选择了道歉，表现了较好的情绪掌控力，但在人际平衡术上稍显欠缺。",  
                }  
            ]  
          }
        }
        请根据以上格式生成一个关于[职位等级][性别]在[职场场合]场景会遇到的提问和回答选项json格式。
        问题和回答都是对话的形式。打分可以区分度稍微大一点。

        职场场合：公司食堂
        性别：女性
        职位等级：新人
        前置背景：你在向大家敬酒时，不小心把酒洒到了桌子上，主管笑着说：“看来你还得多练练敬酒啊！”

        # Add these variables at the top of the file, after the imports
        SCENARIO_TYPES = ["职场刁难", "帮助别人融入", "应对突发状况"]
        used_scenarios = set()
                   
        **额外指示**
        请在打分时生成的三个回答，主要体现三个不同方面较高的情商维度，但也不能有明显的情商不足，即对于三个选择，每个选择的五个维度的总分应当接近。
        不同选择间分差拉开，鼓励低分出现。同一个选择的五个维度分值也要拉开，使得方差较大，分布较为均匀，低分段与中间段较多，高分段较少。


        请确保返回的 JSON 数据结构（开头不要写上json字母，不要漏,）
        请确保返回的 JSON 数据结构（开头不要写上json字母，不要漏,）
        请确保返回的 JSON 数据结构（开头不要写上json字母，不要漏,）
        
        """)


def generate_next_question(context, branch_number, max_retries=3):
    payload = {
        "messages": [
            {
                "role": "system",
                "content": context
            }
        ],
        "temperature": 1,
        "top_p": 0.95,
        "max_tokens": 4000
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(ENDPOINT, headers=headers, json=payload)
            response.raise_for_status()
            a = response.json()['choices'][0]['message']['content']
            try:
                output_json = json.loads(a)
                if validate_json_structure(output_json):
                    return output_json
                else:
                    print(f"Branch {branch_number}: JSON 结构无效，重试中...")
            except json.JSONDecodeError:
                print(f"Branch {branch_number}: API 返回的内容不是 JSON 格式，重试中...")
        except requests.RequestException as e:
            print(f"API request failed: {e}")

        if attempt < max_retries - 1:
            time.sleep(2)  # 等待2秒后重试

    raise SystemExit(f"生成对话失败，已重试 {max_retries} 次")


def validate_json_structure(json_data):
    required_keys = ['scenes']
    scenes_required_keys = ['background', 'description', 'options']
    option_required_keys = ['text', 'scores', 'analysis']
    ability_keys = ["情绪侦查力", "情绪掌控力", "人际平衡术", "沟通表达力", "社交得体度"]

    if not all(key in json_data for key in required_keys):
        return False

    scenes = json_data['scenes']
    if not all(key in scenes for key in scenes_required_keys):
        return False

    options = scenes['options']
    if not isinstance(options, list) or len(options) != 3:
        return False

    for option in options:
        if not all(key in option for key in option_required_keys):
            return False
        if not all(key in option['scores'] for key in ability_keys):
            return False

    return True


def create_scenario_folder():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"scenario_{timestamp}"

    current_path = os.getcwd()
    folder_path = os.path.join(current_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    return folder_name


def save_json(data, folder, filename):
    filepath = os.path.join(folder, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_to_file(content, filename="dialogue_log.txt"):
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(content + "\n\n")


def calculate_average_score(option_scores_list):
    average_scores = {key: sum(d[key] for d in option_scores_list) / len(option_scores_list) for key in
                      option_scores_list[0]}
    return average_scores


def recursive_dialogue(context, folder, depth=0, max_depth=5, branch_path=""):
    global used_scenarios
    if depth >= max_depth:
        return []

    # Select a scenario type
    available_scenarios = list(set(SCENARIO_TYPES) - used_scenarios)
    if not available_scenarios:
        available_scenarios = SCENARIO_TYPES
        used_scenarios.clear()

    scenario_type = random.choice(available_scenarios)
    used_scenarios.add(scenario_type)

    next_question = generate_next_question(context, depth)

    # Save the JSON for this branch
    save_json(next_question, folder, f"branch_{branch_path}.json")

    print(f"\n深度 {depth} 的对话 (分支路径: {branch_path}):")
    print(next_question['scenes']['background'])
    print(next_question['scenes']['description'])

    for i, option in enumerate(next_question['scenes']['options'], 1):
        print(f"{i}. {option['text']}")

    all_scores = []
    for i, option in enumerate(next_question['scenes']['options'], 1):
        print(f"\n-----------------------------------执行分支 {i}:")
        print(f"分支 {i} - 选项 {i} 分析: {option['analysis']}")

        new_context = context + f"\n系统生成一样格式的问题和选项:\n{json.dumps(next_question, ensure_ascii=False)}\n用户选择: {i}。新的问题要接着上一个场景和选择，注意上下文过渡，换情境的话要有过渡，情境有两个NPC[小王]和[小李]和你。NPC的[]的符号只会出现在background中。你们三个人发生对话和故事。对话和情境不要重复。每过三轮对话可以换个去到新的场景来展开话题。情境和会话要有冲突。最好阴阳怪气一下。或者有{scenario_type}。回答给一个意图不明的抽象回答，给一个赞同倾向的回答，给一个反驳倾向的回答，可以阴阳。但是三个选项都各有道理。大家选的时候会纠结。口语化一点。"

        new_branch_path = f"{branch_path}{i}"
        sub_scores = recursive_dialogue(new_context, folder, depth + 1, max_depth, new_branch_path)
        all_scores.extend(sub_scores)

    current_scores = [option['scores'] for option in next_question['scenes']['options']]
    all_scores.extend(current_scores)

    # save_to_file(f"深度 {depth} 分支路径 {branch_path} 的对话:\n{json.dumps(next_question, ensure_ascii=False)}")

    return all_scores


def interactive_dialogue():
    folder = create_scenario_folder()
    all_scores = recursive_dialogue(initial_context, folder)
    average_scores = calculate_average_score(all_scores)
    print("\n-------------------------------")
    print(f"总体平均分: {average_scores}")
    print(f"对话树已保存到文件夹: {folder}")


# 启动互动对话
interactive_dialogue()