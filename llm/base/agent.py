import abc
import json
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


class AbstractAgent(abc.ABC):
    def __init__(self, llm, functions=None, tools=None, json_output=True, **kwargs):
        self.llm = llm
        self.json_output = json_output
        self.functions = functions
        self.tools = tools

    def invoke(self, input_dict=None, max_retries=3):
        output = self.invoke_llm(input_dict, max_retries=max_retries)
        if self.json_output:
            return json.dumps(output, indent=2)
        return output

    def invoke_llm(self, input_dict, max_retries=3):
        num_retries = 0
        while num_retries < max_retries:
            try:
                return self.invoke_llm_once(input_dict)
            except Exception as e:
                num_retries += 1
                if num_retries >= max_retries:
                    print(f'Max {max_retries} retries reached: {e}')
                    raise e

    def invoke_llm_once(self, input_dict):
        agent = self.prompt | self.llm
        output = agent.invoke(input_dict)
        if not self.json_output:
            return output
        try:
            output_json = json.loads(output.content)
        except json.JSONDecodeError:
            raise ValueError(f"Output content is not a valid JSON:\n{output.content}")
        return output_json


class Agent(AbstractAgent):

    def __init__(self, name, llm, functions=None, tools=None, json_output=True, **kwargs):
        super().__init__(llm, functions, tools, json_output, **kwargs)
        self.name = name

    def set_prompts(self, system_prompt, task_prompt):
        self.system_prompt = system_prompt
        self.task_prompt = task_prompt
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ('system', self.system_prompt),
                ('human', self.task_prompt),
            ]
        )