
from opendevin.llm.llm import LLM
from opendevin.exceptions import AgentEventTypeError
import agenthub.monologue_agent.utils.json as json
import agenthub.monologue_agent.utils.prompts as prompts
from opendevin.logger import opendevin_logger as logger

import time


class Monologue:
    """
    The monologue is a representation for the agent's internal monologue where it can think.
    The agent has the capability of using this monologue for whatever it wants.
    """

    def __init__(self):
        """
        Initialize the empty list of thoughts
        """
        self.thoughts = []
        self.organized_thoughts = []

    def add_event(self, t: dict):
        """
        Adds an event to memory if it is a valid event.

        Parameters:
        - t (dict): The thought that we want to add to memory

        Raises:
        - AgentEventTypeError: If t is not a dict
        """
        if not isinstance(t, dict):
            raise AgentEventTypeError()
        self.thoughts.append(t)
        self.organized_thoughts.append(t)

    def get_thoughts(self, task: str, iteration: int):
        """
        Get the current thoughts of the agent.

        Returns:
        - List: The list of thoughts that the agent has.
        """
        if iteration != 0:
            # for thought in self.thoughts:
            #     print(thought)
            return self.thoughts
        else:
            self.thoughts.append(prompts.start_task(task))
            for thought in self.thoughts:
                print(thought)
            return self.thoughts
    
    def get_relevant(self, task, history, llm: LLM):
        """reiterate users request before it is ingested by the agent"""

        instruction = """
        Your job is to determine whether the task and the history are relevant.
        The task is a user request, while the history is history log of a coding agent.
        If the two strings are relevant in some extent, return RELEVANT.
        If they are irrelevant, return IRRELEVANT.
        If the history is about finalizing and confirming tasks, you MUST return IRRELEVANT.
        You must return and only return what required above.

        Example 1:

        Input: **task**: describe about calculator.py. **history**: {'observation': 'recall', 'content': "Here's what I want to do: Write a python file to convert temperature in Celsius to Fahrenheit.", 'extras': {'memories': [], 'role': 'assistant'}}
        
        Output: IRRELEVANT

        Example 2: 

        Input: **task**: describe about calculator.py. **history**: {'action': 'think', 'args': {'thought': 'I need to begin by planning the basic structure of a Python calculator. It will require a simple interface to take input and functions for basic arithmetic operations like addition, subtraction, multiplication, and division. An exception handling system will also be crucial to manage any input errors or arithmetic issues like division by zero.'}}

        Output: RELEVANT

        Example 3: 

        Input: **task**: describe about calculator.py. **history**: {'action': 'think', 'args': {'thought': 'The tests for the calculator function passed successfully, which confirms that the basic functionality and error handling are working as expected. My task to implement a basic calculator in Python is now complete and fully tested. I should finalize my task and confirm completion.'}}

        Output: IRRELEVANT
        """
        prompt = f"**task**{task} **history**{history}"
        messages = [
                {"role": "system", "content": instruction},
                {"role": "user", "content": prompt}
                ]
        resp = llm.completion(messages=messages)
        return resp['choices'][0]['message']['content']

    def get_organized_thoughts(self, task, iteration, llm: LLM):
        """
            Filters histories based on their relevance to the given task.

            Args:
            - task (str): The task string to compare the history against.
            - histories (list of dict): A list of dictionaries, each representing a history.

            Returns:
            - list of dict: A list of dictionaries that are relevant to the task.
            """
        if iteration != 0:
            for thought in self.organized_thoughts:
                print(thought)
            return self.organized_thoughts
        else:
            start_time = time.time()

            relevant_histories = []
            for thought in self.thoughts:
                if self.get_relevant(task, thought, llm) != "IRRELEVANT":
                    relevant_histories.append(thought)
            self.organized_thoughts = relevant_histories

            end_time = time.time()
            # print(f'\nIt taks {end_time - start_time} seconds to organize memory.')

            relevant_histories.append(prompts.start_task(task))
            self.organized_thoughts = relevant_histories
            self.thoughts.append(prompts.start_task(task))
            for thought in relevant_histories:
                print(thought)

        return relevant_histories

    def get_total_length(self):
        """
        Gives the total number of characters in all thoughts

        Returns:
        - Int: Total number of chars in thoughts.
        """
        total_length = 0
        for t in self.thoughts:
            try:
                total_length += len(json.dumps(t))
            except TypeError as e:
                logger.error('Error serializing thought: %s', str(e), exc_info=False)
        return total_length

    def condense(self, llm: LLM):
        """
        Attempts to condense the monologue by using the llm

        Parameters:
        - llm (LLM): llm to be used for summarization

        Raises:
        - Exception: the same exception as it got from the llm or processing the response
        """

        try:
            prompt = prompts.get_summarize_monologue_prompt(self.thoughts)
            messages = [{'content': prompt, 'role': 'user'}]
            resp = llm.completion(messages=messages)
            summary_resp = resp['choices'][0]['message']['content']
            self.thoughts = prompts.parse_summary_response(summary_resp)
        except Exception as e:
            logger.error('Error condensing thoughts: %s', str(e), exc_info=False)

            # TODO If the llm fails with ContextWindowExceededError, we can try to condense the monologue chunk by chunk
            raise
