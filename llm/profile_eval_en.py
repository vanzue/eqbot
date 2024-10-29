import os
import requests
import base64
import json


from llm.keyless_setup import creat_llm
from langchain_core.prompts import ChatPromptTemplate


def request_LLM_response(scenario):
    payload_content = """
                    ** Task Description **
                    - You are a highly professional Emotional Intelligence (EQ) assessor. Based on a series of user information provided, you have already scored the user's EQ in five dimensions: Emotion Perception, Self Regulation, Empathy, Social Skill, and Motivation.

                    ** Key Details **
                    The scores for each dimension have already been provided. Please provide a humorous yet concise explanation for each score.
                    Lastly, based on the lowest score among the five dimensions, offer a concise tip in 20 words or fewer, aiming for brevity and precision.
                    Based on the lowest score, provide suggestions for EQ development.


                    ** Refer to the scoring rules **
                    ## Perception ##
                    description: The ostrich reflects avoidance, symbolizing difficulty in recognizing and perceiving emotions.
                    I can quickly notice changes in my own emotions. (1-5 points)
                    I can easily detect subtle changes in other people's emotions. (1-5 points)
                    I am good at analyzing the reasons behind others' emotions. (1-5 points)
                    I can distinguish between different types of emotions, such as anxiety, anger, or sadness. (1-5 points)
                    I can judge others' emotional needs based on the situation. (1-5 points)
                    
                    ## Self Regulation ##
                    description: The monkey represents impulsiveness, symbolizing difficulty in controlling emotions and behaviors
                    I can stay calm and control my reactions when I’m emotionally agitated. (1-5 points)
                    I can quickly stabilize my emotions when facing sudden events. (1-5 points)
                    I can release negative emotions in an effective way without affecting others. (1-5 points)
                    I can effectively adjust my emotions to stay rational when under pressure. (1-5 points)
                    I can adapt to emotional changes and quickly regain emotional stability. (1-5 points)
                    
                    ## Empathy ##
                    description: The hedgehog reflects self-defense, symbolizing difficulty in empathizing with and responding to others' emotions.
                    I can easily understand and share the feelings of others. (1-5 points)
                    I can put myself in other people's shoes and respond appropriately to their emotions. (1-5 points)
                    I can recognize and validate others' emotional states, even when they are unspoken. (1-5 points)
                    I can offer support and comfort to others during emotional or difficult situations. (1-5 points)
                    I can show compassion and concern for others' well-being in both personal and professional relationships. (1-5 points)
                    
                    ## Social Skill ##
                    description: The coyote reflects independence, symbolizing challenges in building social connections and teamwork.
                    I can present myself appropriately in social situations and follow etiquette norms. (1-5 points)
                    I can adjust my words and actions according to the situation and people, maintaining politeness and respect. (1-5 points)
                    When interaction is needed, I can quickly judge how to appropriately engage in conversation. (1-5 points)
                    I can recognize social cues from others, avoiding awkwardness or discomfort. (1-5 points)
                    I am good at maintaining and enhancing my personal image, avoiding making social faux pas. (1-5 points)
                   
                    ## Motivation ##
                    description: The capybara reflects a laid-back nature, symbolizing challenges in maintaining drive and motivation.
                    I can maintain a high level of energy and enthusiasm in achieving my goals. (1-5 points)
                    I am proactive in seeking out opportunities for personal or professional growth. (1-5 points)
                    I can stay motivated and focused even when faced with setbacks or challenges. (1-5 points)
                    I can set clear and attainable goals for myself and work persistently towards them. (1-5 points)
                    I can inspire and motivate others to take initiative and contribute to shared goals. (1-5 points)

                    ** Tone and style **
                    You are young and should maintain a light-hearted, humorous tone while being professional and objective. Be critical yet insightful, with witty and sharp language that hits the nail on the head. Balance the tone so it doesn't come off as offensive.
                    Style inspiration: George Orwell, Kurt Vonnegut, Franz Kafka, Philip Roth

                    ** Structure **
                    - Scoring section:
                        - Score for each dimension and brief explanation of reasons, in the following format:
                            - Dimension name: Score
                            - Cause: Summarize the cause based on the actual conversation content
                    - Tips section:
                        - A quick tip, 20 words or less.
                    - Cultivation Suggestions:
                        - Based on the lowest score dimension, provide EQ training suggestions for that dimension.

                    ** Target Audience **
                    - The target audience is users who wish to improve their emotional intelligence, with above-average comprehension

                    ** Examples or references :**
                    - Example Rating: Perception: 25 Reason: In the workplace, even the sightest setback can disturb your thoughts. You need to be more cautious, or you might easily 'burn' yourself and your colleagues.
                    - Example tip: Impulse is the devil, learn to calm down to control the game.
                    Your emotional stability ability is low, and you need to improve this ability most at present. You are prone to large emotional fluctuations due to small setbacks in work or different opinions of others, which will affect work efficiency and interpersonal relationships. Don't be a hedgehog when someone is talking, listen attentively, don't interrupt, don't contradict, nod your head, and make eye contact to show respect. Deal with conflict calmly and rationally. Listen to the other person before you express yourself. When you stab someone, put painkillers on the blade.


                    ** Additional instructions :**
                    - When providing scores, be fair and constructive. Avoid any negative commentary and ensure that the suggestions for development are practical and can genuinely help the user improve their emotional intelligence.

                    ** User Information: **
                    - Based on the user's provided information and their conversational scenarios, generate the above report. The scores for each dimension have already been provided, so please create the reasoning based on the given scores

                    **Please return the data in the following json format strictly((do not start with json letters, do not omit,))**
                    {{
                        "1. Perception": {{
                            "Score": [Score],
                            "Reason": "[Based on the actual conversation content, briefly explain the reasons, around 50 words]"
                        }},
                        "2. Self Regulation": {{
                            "Score": [Score],
                            "Reason": "[Based on the actual conversation content, briefly explain the reasons, around 50 words]"
                        }},
                        "3. Empathy": {{
                            "Score": [Score],
                            "Reason": "[Based on the actual conversation content, briefly explain the reasons, around 50 words]"
                        }},
                        "4. Social Skill": {{
                            "Score": [Score],
                            "Reason": "[Based on the actual conversation content, briefly explain the reasons, around 50 words]"
                        }},
                        "5. Motivation": {{
                            "Score": [Score],
                            "Reason": "[Based on the actual conversation content, briefly explain the reasons, around 50 words]"
                        }},
                        "6. Tips": {{
                            "Tips": "[Provide a short tip, 20 words or less]
                        }},
                        "7. Cultivation Suggestions": {{
                            "Suggestions": "[Provide detailed analysis by including both pros and cons that show in senes and also consists content in scenes. Please make the suggestions mainly based on the cons!]"
                        }},
                        "8. Summary of Cultivation Suggestions": {{
                            "Summary of Suggestions": "[Summarize the suggestions based on cultivation suggestions into one sentence, like a title]"
                        }},
                        "9. Overall Suggestion": {{
                            "Overall Suggestion": "[According to the user's situation, give a comprehensive evaluation and good wishes to the user, related to the user's cons]"
                        }}
                    }}
                    """
    # return setup_LLM(payload_content=payload_content)
    user_prompt = """
                ** The following is the user's information and his scene conversation **

                {scenario}
                """

    prompt = ChatPromptTemplate.from_messages(
        [
            ('system', payload_content),
            ('user', user_prompt),
        ]
    )
    
    input_dict = {'scenario': scenario}

    llm = creat_llm()
    model = prompt | llm

    analysis_output = model.invoke(input_dict)
    output = analysis_output.content
    print(output)

    return output

def parse_LLMresponse(json_data):
    try:
        response = json.loads(json_data)
        print("JSON is valid.")

        dimension1_score = response['1. Perception']['Score']
        dimension1_detail = response['1. Perception']['Reason']

        dimension2_score = response['2. Self Regulation']['Score']
        dimension2_detail = response['2. Self Regulation']['Reason']

        dimension3_score = response['3. Empathy']['Score']
        dimension3_detail = response['3. Empathy']['Reason']

        dimension4_score = response['4. Social Skill']['Score']
        dimension4_detail = response['4. Social Skill']['Reason']

        dimension5_score = response['5. Motivation']['Score']
        dimension5_detail = response['5. Motivation']['Reason']

        summary = response['6. Tips']['Tips']
        detail = response['7. Cultivation Suggestions']['Suggestions']
        detail_summary = response['8. Summary of Cultivation Suggestions']['Summary of Suggestions']
        overall_suggestion = response['9. Overall Suggestion']['Overall Suggestion']

        eq_scores = {
            "dimension1_score": dimension1_score,
            "dimension1_detail": dimension1_detail,
            "dimension2_score": dimension2_score,
            "dimension2_detail": dimension2_detail,
            "dimension3_score": dimension3_score,
            "dimension3_detail": dimension3_detail,
            "dimension4_score": dimension4_score,
            "dimension4_detail": dimension4_detail,
            "dimension5_score": dimension5_score,
            "dimension5_detail": dimension5_detail,
            "summary": summary,
            "detail": detail,
            "detail_summary": detail_summary,
            "overall_suggestion": overall_suggestion
        }
        return eq_scores
    except json.JSONDecodeError as e:
        print("JSON is invalid:", e)
        raise

def retry_parse_LLMresponse(scenario, max_retries=5):
    attempt = 0
    while attempt < max_retries:
        try:
            json_data = request_LLM_response(scenario)
            eq_scores = parse_LLMresponse(json_data)
            return eq_scores
        except json.JSONDecodeError as e:
            attempt += 1
            print(f"Attempt {attempt} failed. Retrying...")
            if attempt == max_retries:
                print("Max retries reached. Giving up.")
                # raise
    return None


async def process_with_llm_en(scores, analysis_data):
    scenario = ""
    scenario += "Score by dimension:\n"
    for dimension, score in scores.items():
        scenario += f"- {dimension}: {score}\n"
    print(scenario)

    scenario += "\nAnalyze the scenario:\n"
    for i, analysis in enumerate(analysis_data, 1):
        scenario += f"\nScenario {i}:\n"
        scenario += f"Background: {analysis['background']}\n"
        scenario += f"Descriptiom: {analysis['description']}\n"
        scenario += f"Choice: {analysis['choice']}\n"
        scenario += f"Analysis: {analysis['analysis']}\n"
    # scenario += analysis_data

    return retry_parse_LLMresponse(scenario)

async def process_with_llm_en_new(scores, analysis_data):
    scenario = ""
    scenario += "Score by dimension:\n"
    for dimension, score in scores.items():
        scenario += f"- {dimension}: {score}\n"
    print(scenario)

    scenario += "\nAnalyze the scenario:\n"
    for i, analysis in enumerate(analysis_data, 1):
        scenario += f"\nScenario {i}:\n"
        scenario += f"Background: {analysis.background}\n"
        scenario += f"Descriptiom: {analysis.description}\n"
        scenario += f"Choice: {analysis.choice}\n"
        scenario += f"Analysis: {analysis.analysis}\n"

    return retry_parse_LLMresponse(scenario)

    
if __name__ == "__main__":
        
    from example_debug import analysis_data, scores

    scenario = ""

    scenario += "各维度得分:\n"
    for dimension, score in scores.items():
        scenario += f"- {dimension}: {score}\n"

    scenario += "\n对话分析:\n"
    for i, analysis in enumerate(analysis_data, 1):
        scenario += f"\n场景 {i}:\n"
        scenario += f"背景: {analysis['background']}\n"
        scenario += f"描述: {analysis['description']}\n"
        scenario += f"选择: {analysis['choice']}\n"
        scenario += f"分析: {analysis['analysis']}\n"
    # print(scenario)
    
    # response = request_LLM_response(scenario)
    # print(response)

    eq_scores = retry_parse_LLMresponse(scenario)
    print(eq_scores)
    # await process_with_llm(scores, analysis_data)