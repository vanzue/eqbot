import os
import requests
import base64
import json


from llm.keyless_setup import creat_llm
from langchain_core.prompts import ChatPromptTemplate


def request_LLM_response(scenario):
    payload_content = """
                    ** Mission Description **
                    - You're a very professional emotional intelligence evaluator. Based on a range of user information, you have scored the user's emotional intelligence on five dimensions: emotional detection, emotional mastery, interpersonal balance, communication, and social appropriateness.

                    ** Key Details **
                    - The score for each dimension has been given, please provide a humorous but concise explanation of the reason according to the score for each dimension.
                    - Finally, according to the lowest score of the five dimensions, give a tip of 20 words or less, and strive to be concise and precise.
                    - Provide advice on EQ cultivation based on the lowest score.

                    ** Refer to the scoring rules **
                    ## Emotion Perception ##
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

                    ** Tone and style **
                    - You are a young person, please maintain a humorous and relaxed tone while being professional and objective. Critical reality, deep thinking, funny language, good at grasping the essence of the point, pay attention to the sense of proportion of offense.
                    - Style: George Orwell, Kurt Vonnegut, Franz Kafka, Jean-Paul Sartre


                    ** Structure **
                    - Scoring section:
                        - Score for each dimension and brief explanation of reasons, in the following format:
                            - Dimension name: Score
                            - Cause: Summarize the cause based on the actual conversation content
                    - Tips section:
                        - A quick tip, 20 words or less.
                    - Cultivation Suggestions:
                        - Based on the lowest score dimension, provide EQ training suggestions for that dimension.

                    ** Custmers **
                    - The target custmers are users who want to improve their emotional intelligence, and have an average understanding.

                    ** Examples or references :**
                    - Example Rating: Emotion Perception: 25 Reason: There is a little wind and wind at work, your little emotions are like a volcano, it will explode. Take it easy, for example, when the other party refutes you, you can ease up on your answer, otherwise it is easy to burn yourself and your partners.
                    - Example tip: Impulse is the devil, learn to calm down to control the game.
                    Your emotional stability ability is low, and you need to improve this ability most at present. You are prone to large emotional fluctuations due to small setbacks in work or different opinions of others, which will affect work efficiency and interpersonal relationships. Don't be a hedgehog when someone is talking, listen attentively, don't interrupt, don't contradict, nod your head, and make eye contact to show respect. Deal with conflict calmly and rationally. Listen to the other person before you express yourself. When you stab someone, put painkillers on the blade.


                    ** Additional instructions :**
                    - Be fair and constructive when providing ratings, avoid any negative comments, and ensure that the cultivation suggestions given can actually help users improve their emotional intelligence.

                    ** User Information: **
                    - Please generate the above report according to the input user information and his scene dialogue, and the scores of different dimensions have been given, please explain the reasons for generating the scores.

                    **Please return the data in the following json format strictly((do not start with json letters, do not omit,))**
                    {{
                        "1. Emotion Perception": {{
                            "Score": [Score],
                            "Reason": [Based on the actual conversation content, briefly explain the reasons]
                        }},
                        "2. Self Regulation": {{
                            "Score": [Score],
                            "Reason": [Based on the actual conversation content, briefly explain the reasons]
                        }},
                        "3. Empathy": {{
                            "Score": [Score],
                            "Reason": [Based on the actual conversation content, briefly explain the reasons]
                        }},
                        "4. Social Skill": {{
                            "Score": [Score],
                            "Reason": [Based on the actual conversation content, briefly explain the reasons]
                        }},
                        "5. Motivation": {{
                            "Score": [Score],
                            "Reason": [Based on the actual conversation content, briefly explain the reasons]
                        }},
                        "6. Tips": {{
                            "Tips": [Provide a short tip, 20 words or less]
                        }},
                        "7. Cultivation Suggestions": {{
                            "Suggestions": [Provide detailed practice suggestions for the lowest scoring dimensions]
                        }},
                        "8. Summary of Cultivation Suggestions": {{
                            "Summary of Suggestions": [Summarize the suggestions based on cultivation suggestions into one sentence, within 20 words]
                        }},
                        "9. Overall Suggestion": {{
                            "Overall Suggestion": [According to the user's situation, give a comprehensive evaluation and good wishes to the user]
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

        dimension1_score = response['1. Emotion Perception']['Score']
        dimension1_detail = response['1. Emotion Perception']['Reason']

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