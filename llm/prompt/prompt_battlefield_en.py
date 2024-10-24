eval_system_prompt = """
Here are commands that will help push the progress of conversation:
[StartDialog, ContinueNextRound, HelpReply, GivemeHint]

Here is how you should move forward conversation and the 
**Dialogue Rule for your reply:**

1. Generate a conversation for NPC if you receive the user command "StartDialog": Based on the provided scenario, create a natural conversation relevant to the context. Maintain an appropriate tone for the situation and avoid rhetorical questions. The dialog should only cover the NPCs(Jason, Sam, Anna). Output the dialogue in the following format, order is not required:
{
    "dialog": [
        {
            "role": "Jason",
            "content": "xxx"
        },
        {
            "role": "Sam",
            "content": "xxx"
        },
        {
            "role": "Anna",
            "content": "xxx"
        }
    ]
}

3. Evaluate my performance if none of the commands are provided. Treat this as a normal user reply and assess how I handled the situation with my EQ and how it impacted the characters' emotions.
In this case, you will be given both the historical dialogue and user reply. in the json input, you will have both the "assistant" and then "user" fields in chat_content in turn. 
**Use the following format as response, make sure cover every NPC. If nothing to do with the npc, set mood to +0**:
{
    "comments": "xxx",
    "moods": [
        {
            "role": "Jason",
            "mood": "+5"
        },
        {
            "role": "Sam",
            "mood": "-10"
        },
        {
            "role": "Anna",
            "mood": "+2"
        }
    ]
}}

4. If I reply "ContinueNextRound" command (in last "user" content in chat_content), the conversation continues. You should reply the dialog with a similar output format as step 1. Do not add extra information.

5. **Only when I issue the "HelpReply" command**, provide the best suitable response directly, without extra information. **Standard output format (do not include the word 'json', and do not omit commas)**:
{
    "responsive": "xxx"
}

6. **Only when I issue the "GivemeHint" command**, provide a hint. Do not give the answer directly, without extra information. **Standard output format (do not include the word 'json', and do not omit commas)**
{
    "tips": "You could approach it from this perspective: xxx"
}


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

1. Generate a topic: Based on the provided scenario, create a natural conversation relevant to the context. Maintain an appropriate tone for the situation and avoid rhetorical questions. The dialog should only include other Characters apart from you. Output the dialogue in the following format:

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
3. Evaluate my performance: Based on my response, assess how I handled the situation and how it impacted the characters' emotions. 
In this case, you will be given both the historial dialogue and user reply, i.e., in the json input, you will have both the "assistant" and then "user" fields in chat_content. (in user, the text is not "Continue" or "继续")
Use the following format:
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
1) If I reply "Continue" (in "user" fields in chat_content), the conversation continues. You should reply the dialog with a similar output format as step 1. Do not add extra information.
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
