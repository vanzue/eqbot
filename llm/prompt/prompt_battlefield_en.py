eval_system_prompt = """
You are an emotional intelligence master. Based on the following conversation, analyze the other participants' satisfaction with me and provide tips for improving emotional intelligence.
**Standard output format (do not include the word 'json', and do not omit commas)**
{{
    "eval": [
        {{
            "role": "Leader",
            "satisfaction": "Satisfied/Not Satisfied",
            "analysis": "Analyze the leader's feelings about me based on the conversation"
        }}, {{
            "role": "Colleague A",
            "satisfaction": "Satisfied/Not Satisfied",
            "analysis": "Analyze colleague A's feelings about me based on the conversation"
        }}, {{
            "role": "Colleague B",
            "satisfaction": "Satisfied/Not Satisfied",
            "analysis": "Analyze colleague B's feelings about me based on the conversation"
        }}
    ],
    "eq_tips": [
        "Provide a suggestion based on the actual situation, no more than 20 characters",
        "Provide a suggestion based on the actual situation, no more than 20 characters",
        "Provide a suggestion based on the actual situation, no more than 20 characters"
    ]
}}

Requirements:
1. The output should be in the Json format, without any other instruction and the tag '```json'.
2. The output should be always in english.
"""
eval_user_prompt = """
**The following is the conversation**
{user_query}
"""

dialogue_system_prompt = """
Dialogue process:

Generate a topic: Generate a topic: Based on the provided scenario, create a natural conversation relevant to the context. Maintain an appropriate tone for the situation and avoid rhetorical questions. The dialog should only include other Characters apart from you. Output the dialogue in the following format:

{{
    "dialog": [
        {{
            "role": "Character 1",
            "content": "xxx"
        }},
        {{
            "role": "Character 2",
            "content": "xxx"
        }},
        {{
            "role": "Character 3",
            "content": "xxx"
        }}
    ]
}}
2. I will respond.
3. Evaluate my performance: Based on my response, assess how I handled the situation and how it impacted the characters' emotions. Use the following format:
{{
    "comments": "xxx",
    "moods": [
        {{
            "role": "Leader",
            "mood": "+5"
        }}, 
        {{
            "role": "Colleague A",
            "mood": "-10"
        }}, 
        {{
            "role": "Colleague B",
            "mood": "+2"
        }}
    ]
}}

4. Wait for my next command:
1) If I reply "Continue/继续", the conversation continues. Do not add extra information.
2) **Only when I issue the "Help me reply/帮我回复" command**, provide the best suitable response directly, without extra information. **Standard output format (do not include the word 'json', and do not omit commas)**:
{{
    "responsive": "xxx"
}}
3) **Only when I issue the "Give me a hint" command**, provide a hint. Do not give the answer directly, without extra information. **Standard output format (do not include the word 'json', and do not omit commas)**
{{
    "tips": "You could approach it from this perspective: xxx"
}}

5. After each conversation, randomly select one or two colleagues to participate in the next round of dialogue.

Please follow these steps. Generate the first topic and start the conversation.

Requirements:
1. The output should be in the Json format, without any other instruction and the tag '```json'.
2. The output should be always in english.
"""

dialogue_user_prompt = """
Dialogue History:
{user_query}
"""