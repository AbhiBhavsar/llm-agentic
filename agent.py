from openai import OpenAI
from dotenv import load_dotenv
import requests
import json
import os

load_dotenv()
client = OpenAI()
SYSTEM_PROMPT = f"""
    You are an helpfull AI Assistant who is specialized in resolving user query.
    You work on start, plan, action, and observe mode.

    For the given user query and available tools, plan the step by step execution, based on the planning,
    select the relevant tool from the available tool, and based on the tool selection you perform an action to call the tool.

    Wait for the observation and based on the observation from the tool call resolve the user query.

    Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query

    Output JSON Format:
    {{
        "step": "string",
        "content": "string",
        "tool": "The name of function if the step is action",
        "input": "The input parameter for the function",
    }}

    Available Tools:
    - "get_weather": Takes a city name as an input and returns the current weather for the city
    - "run_cli_cmd": takes a terminal command and execute it

    Example:
    User Query: What is the weather of new york?
    Output: {{ "step": "plan", "content": "The user is interseted in weather data of new york" }}
    Output: {{ "step": "plan", "content": "From the available tools I should call get_weather" }}
    Output: {{ "step": "tool", "tool": "get_weather", "input": "new york" }}
    Output: {{ "step": "observe", "output": "12 Degree Cel" }}
    Output: {{ "step": "output", "content": "The weather for new york seems to be 12 degrees." }}
"""
def get_weather(city: str):
    url = f"https://wttr.in/{city.lower()}?format=%C+%t"
    resp = requests.get(url)
    if resp.status_code == 200:
        return f"The weather in {city} is {resp.text}"
    else:
        return "Something went wrong"
    
def run_cli_cmd(cmd: str):
    cmd_response = os.system(cmd)
    return cmd_response

message_history=[{
    'role':'system',
    'content':SYSTEM_PROMPT
}]
user_query = input('⌨️: ')
message_history.append({'role':'assistant', 'content':user_query})
available_tools={
    'get_weather': get_weather,
    'run_cli_cmd': run_cli_cmd
}

while True:
    response = client.chat.completions.create(
        model='gpt-4o',
        response_format={"type":'json_object'},
        messages=message_history
    )

    raw_result = response.choices[0].message.content
    message_history.append({'role':'assistant', 'content':raw_result})
    parsed_result = json.loads(raw_result)

    if parsed_result.get('step')=='plan':
        print(f"⚙️ {parsed_result.get('content')}")
        continue

    if parsed_result.get('step')=='tool':
        tool_to_use=parsed_result.get('tool')
        tool_input=parsed_result.get('input')
        print(f"🔧 used {tool_to_use} tool with i/p {tool_input}")
        tool_response = available_tools[tool_to_use](tool_input)
        message_history.append({'role':'developer','content':json.dumps({"step":"observe","tool":tool_to_use,'input':tool_input,
                                                                         'output':tool_response})})
        continue

    if parsed_result.get('step')=='output':
        print(f"🤖 {parsed_result.get('content')}")
        break

print('\n\n\n')


