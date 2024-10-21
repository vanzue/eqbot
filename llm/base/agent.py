import abc
import json
from langchain_core.prompts import ChatPromptTemplate


class AbstractAgent(abc.ABC):
    def __init__(self, llm, functions=None, tools=None, json_output=True, **kwargs):
        self.llm = llm
        self.json_output = json_output
        self.functions = functions
        self.tools = tools
        self.prompt = None

    def act(self, input_dict=None, max_retries=3):
        for attempt in range(max_retries):
            try:
                output = self.invoke_llm_once(input_dict)
                return json.loads(output.content) if self.json_output else output
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f'Max {max_retries} retries reached: {e}')
                    raise

    def invoke_llm_once(self, input_dict):
        if self.prompt is None:
            raise ValueError("Prompt is not set. Please set the prompt before invoking the LLM.")
        output = (self.prompt | self.llm).invoke(input_dict)
        if not self.json_output:
            try:
                json.loads(output.content)
            except json.JSONDecodeError:
                raise ValueError(f"Output content is not a valid JSON:\n{output.content}")
        return output

class Agent(AbstractAgent):
    def __init__(self, name, llm, functions=None, tools=None, json_output=True, **kwargs):
        super().__init__(llm, functions, tools, json_output, **kwargs)
        self.name = name

    def set_prompts(self, system_prompt, task_prompt):
        if not system_prompt or not task_prompt:
            raise ValueError("Both system_prompt and task_prompt must be provided.")
        self.prompt = ChatPromptTemplate.from_messages([
            ('system', system_prompt),
            ('human', task_prompt),
        ])
