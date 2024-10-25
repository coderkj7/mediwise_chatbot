from openai import OpenAI
from dotenv import load_dotenv
from tenacity import retry, wait_random_exponential, stop_after_attempt

load_dotenv()
client = OpenAI()

import json

doctors = {
        "dermatologist": ["Calvin Aldrith", "Trudy Ekhart"],
        "otolaryngologist": ["Milford Trinter", "Henry Tallister"],
        "surgeon": ["Travis Redford", "William Kent"],
        "general practitioner": ["Yermol Harrison", "Uncer Patrickson"],
        "radiologist": ["Alfred Renton", "Drew Fanford"],
}

specialties = list(doctors.keys())

availability = {
    "Calvin Aldrith": ["Next Monday at 9am", "Next Wednesday at 2pm"],
    "Trudy Ekhart": ["Next Monday at 9am", "Next Wednesday at 2pm"],
    "Milford Trinter": ["Next Monday at 9am", "Next Wednesday at 2pm"],
    "Henry Tallister": ["Next Monday at 9am", "Next Wednesday at 2pm"],
    "Travis Redford": ["Next Monday at 9am", "Next Wednesday at 2pm"],
    "William Kent": ["Next Monday at 9am", "Next Wednesday at 2pm"],
    "Yermol Harrison": ["Next Monday at 9am", "Next Wednesday at 2pm"],
    "Uncer Patrickson": ["Next Monday at 9am", "Next Wednesday at 2pm"],
    "Alfred Renton": ["Next Monday at 9am", "Next Wednesday at 2pm"],
    "Drew Fanford": ["Next Monday at 9am", "Next Wednesday at 2pm"],
}

availabilities = list(availability.keys())

GPT_MODEL = "gpt-4o-mini"
def chat_complete_messages(messages, temperature):
    # query against the model "gpt-3.5-turbo-1106"
    completion = client.chat.completions.create(
        model=GPT_MODEL,
        messages= messages,
        temperature=temperature, # this is the degree of randomness of the model's output
    )
    return completion.choices[0].message.content

@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, temperature=0, tools=None, tool_choice=None, model=GPT_MODEL):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            tools=tools,
            tool_choice=tool_choice,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

def get_doctors(specialty="general practitioner"):
    """Get the doctors of a certain specialty"""
    return json.dumps(doctors[specialty])

def get_availability(doctor):
    """Get availability of a specific doctor"""
    return json.dumps(availability[doctor])

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_doctors",
            "description": "Get the doctors available based on a specialty",
            "parameters": {
                "type": "object",
                "properties": {
                    "specialty": {
                        "type": "string",
                        "enum": specialties,
                        "description": "The kind of doctor, like a dermatologist",
                    },
                },
                "required": ["specialty"],
            },
        },
        "type": "function",
        "function": {
            "name": "get_availability",
            "description": "Get the availability of a specific doctor",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctor": {
                        "type": "string",
                        "enum": availabilities,
                        "description": "The doctor to check availability with",
                    },
                },
                "required": ["doctor"],
            },
        }
    }
]

available_functions = {
            "get_doctors": get_doctors,
            "get_availability": get_availability,
        }

def tool_call(messages, response_message, tool_calls):
    # Step 2: check if the model wanted to call a function
    if tool_calls:

        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            #print("function name is: ", function_name)
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            #print("function_args:", function_args)
            
            function_response = function_to_call(
                location=function_args.get("location"),
                unit=function_args.get("unit"),
            )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )
            second_response = chat_completion_request(messages, temperature=0, tools=tools, tool_choice="auto")
            messages.append(second_response)
            print(second_response.choices[0].message.content)
        
    return messages
