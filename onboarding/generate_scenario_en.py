import json
import os
import requests
import base64
from datetime import datetime
import time
import random

from langchain_openai import AzureChatOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain_core.prompts import ChatPromptTemplate

from dotenv import load_dotenv
load_dotenv()
# LLM_API = os.getenv('LLM_API')

# Add these variables at the top of the file, after the imports
SCENARIO_TYPES = [" Workplace difficulties ", "helping others fit in "," Responding to emergencies "]
used_scenarios = set()

# Configuration
# API_KEY = LLM_API
# headers = {
#     "Content-Type": "application/json",
#     "api-key": API_KEY,
# }
# ENDPOINT = "https://peitingaoai.openai.azure.com/openai/deployments/4opeitingus/chat/completions?api-version=2024-02-15-preview"
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_DEPLOYMENT = os.getenv('AZURE_DEPLOYMENT')
AZURE_DEPLOYMENT_API_VERSION = os.getenv('AZURE_DEPLOYMENT_API_VERSION')

# Set up Azure AD Token Provider
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

def escape_braces(template_str):
    return template_str.replace("{", "{{").replace("}", "}}")

# Initial context for the first question
initial_context = ("""
                    ## Emotional Intelligence Scoring Rules ##
                    Based on Self-Analysis Dimensions, here are some popular assessment questions. These questions cover the five core aspects of emotional detection/reading, emotional control, interpersonal balance, communication and expression, and social appropriateness, aiming to assess an individual's emotional intelligence level.
                    
                    ## Perception ##
                    I can quickly notice changes in my own emotions. (1-5 points)
                    I can easily detect subtle changes in other people's emotions. (1-5 points)
                    I am good at analyzing the reasons behind others' emotions. (1-5 points)
                    I can distinguish between different types of emotions, such as anxiety, anger, or sadness. (1-5 points)
                    I can judge others' emotional needs based on the situation. (1-5 points)
                    
                    ## Self Regulation ##
                    I can stay calm and control my reactions when I’m emotionally agitated. (1-5 points)
                    I can quickly stabilize my emotions when facing sudden events. (1-5 points)
                    I can release negative emotions in an effective way without affecting others. (1-5 points)
                    I can effectively adjust my emotions to stay rational when under pressure. (1-5 points)
                    I can adapt to emotional changes and quickly regain emotional stability. (1-5 points)
                    
                    ## Empathy ##
                    I can easily understand and share the feelings of others. (1-5 points)
                    I can put myself in other people's shoes and respond appropriately to their emotions. (1-5 points)
                    I can recognize and validate others' emotional states, even when they are unspoken. (1-5 points)
                    I can offer support and comfort to others during emotional or difficult situations. (1-5 points)
                    I can show compassion and concern for others' well-being in both personal and professional relationships. (1-5 points)
                    
                    ## Social Skill ##
                    I can present myself appropriately in social situations and follow etiquette norms. (1-5 points)
                    I can adjust my words and actions according to the situation and people, maintaining politeness and respect. (1-5 points)
                    When interaction is needed, I can quickly judge how to appropriately engage in conversation. (1-5 points)
                    I can recognize social cues from others, avoiding awkwardness or discomfort. (1-5 points)
                    I am good at maintaining and enhancing my personal image, avoiding making social faux pas. (1-5 points)
                   
                    ## Motivation ##
                    I can maintain a high level of energy and enthusiasm in achieving my goals. (1-5 points)
                    I am proactive in seeking out opportunities for personal or professional growth. (1-5 points)
                    I can stay motivated and focused even when faced with setbacks or challenges. (1-5 points)
                    I can set clear and attainable goals for myself and work persistently towards them. (1-5 points)
                    I can inspire and motivate others to take initiative and contribute to shared goals. (1-5 points)

                    ** Standard Output Format **
                   {{
                        "scenes": {{
                            "background": [based on the previous interactions but keep it shorter than 30 words],
                            "role": "[name]",
                            "location": [location],
                            "description": [someone says something],
                            "options": [
                                {{
                                    "text": [choice1],
                                    "scores": {{"Perception": [integer between 1 to 5],
                                                "Self Regulation": [integer between 1 to 5],
                                                "Empathy": [integer between 1 to 5],
                                                "Social Skill": [integer between 1 to 5],
                                                "Motivation": [integer between 1 to 5]}},
                                    "analysis": [analysis based on choice1]
                                }},
                                {{
                                    "text": [choice2],
                                    "scores": {{"Perception": [integer between 1 to 5],
                                                "Self Regulation": [integer between 1 to 5],
                                                "Empathy": [integer between 1 to 5],
                                                "Social Skill": [integer between 1 to 5],
                                                "Motivation": [integer between 1 to 5]}},
                                    "analysis": [analysis based on choice2]
                                }},
                                {{
                                    "text": [choice3],
                                    "scores": {{"Perception": [integer between 1 to 5],
                                                "Self Regulation": [integer between 1 to 5],
                                                "Empathy": [integer between 1 to 5],
                                                "Social Skill": [integer between 1 to 5],
                                                "Motivation": [integer between 1 to 5]}},
                                    "analysis": [analysis based on choice3]
                                }}
                            ]
                        }}
                    }}
                   
                   ** Output Example **
                    {{
                        "scenes": {{
                            "background": "You served extra food to your colleague [Sarah], and [Sarah] asks:",
                            "role": "[Sarah]",
                            "location": "Cafeteria",
                            "description": "'Are you feeding a pig here?'",
                            "options": [
                                {{
                                    "text": "Haha, I just wanted to make sure you're full.",
                                    "scores": {{"Perception": 4,
                                                "Self Regulation": 3,
                                                "Empathy": 4,
                                                "Social Skill": 3,
                                                "Motivation": 4}},
                                    "analysis": "You used humor to diffuse the awkwardness, showing good emotional detection and interpersonal balance skills."
                                }},
                                {{
                                    "text": "I won't allow you to insult yourself like that.",
                                    "scores": {{"Perception": 2,
                                                "Self Regulation": 3,
                                                "Empathy": 2,
                                                "Social Skill": 3,
                                                "Motivation": 2}},
                                    "analysis": "You used humor to diffuse the situation, but the emotional detection and interpersonal balance could be improved."
                                }},
                                {{
                                    "text": "Sorry, I gave you too much.",
                                    "scores": {{"Perception": 3,
                                                "Self Regulation": 4,
                                                "Empathy": 2,
                                                "Social Skill": 3,
                                                "Motivation": 3}},
                                    "analysis": "You chose to apologize, showing good emotional control, but interpersonal balance was a bit lacking."
                                }}
                            ]
                        }}
                    }}

                    Please generate a json format for questions and answers about [job level][gender] in the [workplace] scenario based on the above format.

                    Both questions and answers are conversational. The ratings can make a little more of a difference.
                    The background should not contain repetitive statements, but should be logically coherent. Please keep it in mind.

                    You are on annual leave, enjoying some well-deserved time off to recharge. However, during your time away, a colleague messages you privately, saying there’s an urgent task that needs immediate attention. The request creates a dilemma as you try to balance respecting your time off while feeling the pressure to help with the urgent task.
                    # The backgrounds of each scenario are high based on the previous interactions but keep it shorter than 30 words.
                    # The character who is going to say something should always change in the adjacent interactions.
                    
                    SCENARIO_TYPES = [" Workplace difficulties ", "helping others fit in "," Responding to emergencies "]
                    used_scenarios = set()
                   
                    ##Additional instructions ##
                    Please generate three answers in the scoring, mainly reflect the three different aspects of high EQ dimensions, but there should be no obvious lack of EQ, that is, for the three choices, the total score of the five dimensions of each choice should be close.
                    The score difference between different choices is widened to encourage low scores. The score values of the five dimensions of the same selection should also be separated, so that the variance is large, the distribution is more uniform, the low segment and the middle segment are more, and the high segment is less.
                    The possibility of each dimension to be the lowest for each path should be almost equal.
                   
                    Make sure to return the JSON data structure (do not start with json letters, do not omit,).
                    Make sure to return the JSON data structure (do not start with json letters, do not omit,).
                    Make sure to return the JSON data structure (do not start with json letters, do not omit,).

        """)

llm = creat_llm()

def generate_next_question(context, branch_number, max_retries=10):
    for attempt in range(max_retries):
        try:
            # response = requests.post(ENDPOINT, headers=headers, json=payload)
            prompt = ChatPromptTemplate.from_messages(
                [
                    ('system', context),
                ]
            )
            input_dict = {}

            model = prompt | llm
            analysis_output = model.invoke(input_dict)
            a = analysis_output.content
            print(a)

            # response.raise_for_status()
            # a = response.json()['choices'][0]['message']['content']
            try:
                output_json = json.loads(a)
                # print(output_json)
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
    scenes_required_keys = ['background', 'role', 'location', 'description', 'options']
    option_required_keys = ['text', 'scores', 'analysis']
    # emotion perception, emotion perception, interpersonal balance, communication skills, and social skills
    ability_keys = ["Perception", "Self Regulation", "Empathy", "Social Skill", "Motivation"]

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

        new_scenario = escape_braces(json.dumps(next_question, ensure_ascii=False))

        new_context = context + f"""
                                The system generates a question and options in the same format:
                                {new_scenario}
                                User chooses {i}. The new question should follow the previous scenario and choice, paying attention to the context transition, but please don't use the same content. 
                                If changing the scene, there should be a transition. The scenario involves two NPCs, [Monica] and [Bob], along with you. The NPCs' names appear in brackets only in the background. 
                                A conversation or story occurs between the three of you. 
                                
                                The dialogue, scenario and background should not be repeated. There should be conflict in the situation and dialogue, preferably with some passive-aggressiveness or an element of {scenario_type}.
                                Provide one abstract, unclear response, one answer that leans toward agreement, and one answer that leans toward disagreement, possibly with passive-aggressive undertones. All three options should make sense in their own way, creating a dilemma when choosing. Keep it conversational and natural.
                                
                                Don't repeat the tedious background each time and the backgrounds of each scenario are high based on the previous interactions but keep it shorter than 30 words.
                                Don't ask the same persion to say in the adjacent scenes and keep the output format. Make sure to return the given Standard Output Format and do not generate inside other containers like ```json```!
                                """
        new_context += "\nPlease avoid repeating previous scenarios or answers and the background shoule keep going with the new interations, and it can be more varied, combined with the last round of dialogue, add some body movements but don't include the original background. The description includes the words that role says and following the movements described in background. Make sure to return the JSON data structure (do not start with json letters, do not omit,) and take it easy.\n"
        # print(new_context)

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