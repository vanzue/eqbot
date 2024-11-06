import os
import requests
import base64
import json

from keyless_setup import creat_llm
from langchain_core.prompts import ChatPromptTemplate


def request_LLM_response(scenario):
    payload_content = """
                    **任务描述:**
                    - 你是一位非常专业的情商评估师。根据提供的一系列用户信息，你已经从以下五个维度对用户的情商进行打分：情绪侦查力、情绪掌控力、人际平衡术、沟通表达力、社交得体度。

                    **关键细节:**
                    - 每个维度的打分已给出，请根据每个维度的评分，提供幽默但简洁的原因解释。
                    - 最后，根据五个维度中最低的得分，给出一句20字以内的小贴士，力求简洁、精准。
                    - 基于最低得分，提供情商修炼的建议。

                    **参考打分细则**
                    1. 感知力
                    我能够迅速察觉到自己情绪的变化。（1-5分）
                    我能够轻易辨别他人情绪的微妙变化。（1-5分）
                    我擅长分析他人情绪背后的原因。（1-5分）
                    我能够区分不同类型的情绪，如焦虑、愤怒或悲伤。（1-5分）
                    我能根据情境判断他人的情感需求。（1-5分）
                    2. 掌控力
                    我能在情绪激动时保持冷静并控制自己的反应。（1-5分）
                    我在面对突发事件时，能够快速稳定自己的情绪。（1-5分）
                    我能通过有效的方式宣泄负面情绪，而不影响他人。（1-5分）
                    在面对压力时，我能有效调节自己的情绪以保持理性。（1-5分）
                    我能适应情绪上的变化，并迅速恢复情绪稳定。（1-5分）
                    3. 共情力
                    我很容易理解和分享别人的感受。(1 - 5分)
                    我可以设身处地地为别人着想，对他们的情绪做出适当的反应。(1 - 5分)
                    我能识别并认同他人的情绪状态，即使他们没有说出来。(1 - 5分)
                    我可以在情绪激动或困难的情况下为他人提供支持和安慰。(1 - 5分)
                    我可以在个人和工作关系中对他人的幸福表现出同情和关心。(1 - 5分)
                    4. 社交力
                    我能在社交场合得体地表现自己，遵守礼仪规范。(1 - 5分)
                    我可以根据情况和人调整自己的言行，保持礼貌和尊重。(1 - 5分)
                    当需要互动时，我能很快判断出如何适当地参与对话。(1 - 5分)
                    我能识别他人的社交暗示，避免尴尬或不适。(1 - 5分)
                    善于维护和提升个人形象，避免在社交场合失礼。(1 - 5分)
                    5. 驱动力
                    我能保持高度的精力和热情来实现我的目标。(1 - 5分)
                    我积极主动地寻找个人或职业发展的机会。(1 - 5分)
                    即使面对挫折或挑战，我也能保持动力和专注。(1 - 5分)
                    我能为自己设定明确的、可实现的目标，并为之不懈努力。(1 - 5分)
                    我能激励他人主动为共同的目标做出贡献。(1 - 5分)

                    **语气与风格:**
                    - 你是年轻人，请在专业、客观的同时，保持幽默和轻松的语气氛围。批判现实，思考深刻，语言风趣，擅长一针见血地抓住本质，注意拿捏冒犯的分寸感。
                    - 风格：鲁迅，王朔，刘震云，王小波

                    **结构:**
                    - 评分部分：
                        - 每个维度的评分及简短原因解释，按以下格式：
                            - 维度名称: 分数
                            - 原因: 结合实际对话内容，简述原因
                    - 小贴士部分：
                        - 一句简短小贴士，20字以内。
                    - 修炼建议部分：
                        - 根据最低得分维度，提供针对该维度的情商修炼建议。

                    **受众:**
                    - 目标受众为希望提升情商的用户，理解力中等以上。

                    **示例或参考:**
                    - 示例评分：情绪掌控力: 25 原因: 工作中有一点风吹草动，你的小情绪就像火山一样，说爆发就爆发。得悠着点啊，比如在对方反驳你的时候，可以缓和一点回答，不然很容易把自己和小伙伴都烫伤。
                    - 示例小贴士：冲动是魔鬼，学会冷静才能掌控全场。
                    - 示例提升建议：你的情绪稳定能力偏低，当前你最需要改善这项能力，你容易因为工作中的小挫折或他人的不同意见而产生较大的情绪波动，进而影响工作效率和人际关系。 别人说话时别像刺猬急于扎人，专心听，不打断，不反驳，点头，眼神交流以示尊重。处理冲突要平和理性，先听对方说再表达。刺向他人时，记得在剑刃上撒上止痛药。


                    **额外指示:**
                    - 提供评分时请保持公正和建设性，避免任何带有负面色彩的评论，确保给出的修炼建议能够切实帮助用户提高情商。

                    **用户信息：**
                    - 请根据输入的用户信息及他的场景对话生成上述的报告，并且不同维度的打分已给出，请根据打分生成原因解释。

                    **标准输出格式(不要写上json字母, 也不要漏,)**
                    {{
                        "1. 感知力": {{
                            "分数": [分数],
                            "原因": [结合实际对话内容，简述原因]
                        }},
                        "2. 掌控力": {{
                            "分数": [分数],
                            "原因": [结合实际对话内容，简述原因]
                        }},
                        "3. 共情力": {{
                            "分数": [分数],
                            "原因": [结合实际对话内容，简述原因]
                        }},
                        "4. 社交力": {{
                            "分数": [分数],
                            "原因": [结合实际对话内容，简述原因]
                        }},
                        "5. 驱动力": {{
                            "分数": [分数],
                            "原因": [结合实际对话内容，简述原因]
                        }},
                        "6. 综合小贴士": {{
                            "小贴士": [提供一个简短的小贴士，20字以内]
                        }},
                        "7. 情商修炼建议": {{
                            "建议": [针对最低得分的维度提供详细的修炼建议]
                        }},
                        "8. 情商修炼建议总结": {{
                            "建议总结": [基于情商修炼建议总结成一句话，类似于一个标题]
                        }},
                        "9. 总结建议": {{
                            "总结": [根据用户的情况，给用户一个综合的评价和良好的祝愿，涉及到用户的优点与缺点]
                        }}
                    }}
                    """
    # return setup_LLM(payload_content=payload_content)
    user_prompt = """
                **以下是用户信息及他的场景对话**

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

        dimension1_score = response['1. 感知力']['分数']
        dimension1_detail = response['1. 感知力']['原因']

        dimension2_score = response['2. 掌控力']['分数']
        dimension2_detail = response['2. 掌控力']['原因']

        dimension3_score = response['3. 共情力']['分数']
        dimension3_detail = response['3. 共情力']['原因']

        dimension4_score = response['4. 社交力']['分数']
        dimension4_detail = response['4. 社交力']['原因']

        dimension5_score = response['5. 驱动力']['分数']
        dimension5_detail = response['5. 驱动力']['原因']

        summary = response['6. 综合小贴士']['小贴士']
        detail = response['7. 情商修炼建议']['建议']
        detail_summary = response['8. 情商修炼建议总结']['建议总结']
        overall_suggestion = response['9. 总结建议']['总结']

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
    while True:
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


async def process_with_llm(scores, analysis_data):
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
    # scenario += analysis_data

    return retry_parse_LLMresponse(scenario)

async def process_with_llm_new(scores, analysis_data):
    scenario = ""
    scenario += "各维度得分:\n"
    for dimension, score in scores.items():
        scenario += f"- {dimension}: {score}\n"

    scenario += "\n对话分析:\n"
    for i, analysis in enumerate(analysis_data, 1):
        scenario += f"\n场景 {i}:\n"
        scenario += f"背景: {analysis.background}\n"
        scenario += f"描述: {analysis.description}\n"
        scenario += f"选择: {analysis.choice}\n"
        scenario += f"分析: {analysis.analysis}\n"

    return retry_parse_LLMresponse(scenario)

    
if __name__ == "__main__":
    # import asynicio
    from example_debug import analysis_data, scores

    # res = asyncio.run(process_with_llm_new(scores, analysis_data))
    # print(res)

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
    
    eq_scores = retry_parse_LLMresponse(scenario)
    print(eq_scores)
    # # await process_with_llm(scores, analysis_data)