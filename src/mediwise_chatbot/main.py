import os
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from mediwise_chatbot.utils import chat_complete_messages, chat_completion_request, tool_call, tools,\
    build_kb, retrive_from_pinecone, build_prompt, build_context_query_knowledge, index_name,\
    get_input_embedding, pc
from mediwise_chatbot import constants as C

app = FastAPI()
templates = Jinja2Templates(directory="templates")

chatHistory = []
chatResponses = []
chatHistory.append(C.chatContext[0])
kbstate = None
if kbstate == None:
    kbstate = build_kb(index_name)

@app.get('/', response_class=HTMLResponse)
async def page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.post("/", response_class=HTMLResponse)
async def entry(request: Request, user_input: Annotated[str, Form()]):
    # chatHistory.append({'role':'user', 'content':f"{user_input}"})
    chatResponses.append(f'User: {user_input}')
    ### RAG
    # global kbstate
    # if kbstate == None:
    #     kbstate = build_kb(index_name)
    input_embed = get_input_embedding(user_input)
    context_from_vecdb = retrive_from_pinecone(input_embed, pc.Index(index_name))
    prompt = build_prompt(context_from_vecdb)
    context_query_knowledge = build_context_query_knowledge(user_input, prompt, chatHistory)
    
    response = chat_completion_request(context_query_knowledge, temperature=0.2, tools=tools, tool_choice="auto")
    response_message = response.choices[0].message
    response_message_content = response_message.content
    tool_calls = response_message.tool_calls
    if tool_calls:
        response_message_content = tool_call(context_query_knowledge, response_message, tool_calls)
    chatHistory.append({'role': 'assistant', 'content': f"{response_message_content}"})
    chatResponses.append(f'ChatBot: {response_message_content}')
    return templates.TemplateResponse("home.html", {"request": request, "chatresponses": chatResponses[::-1]})


def entry_local():
    chatHistory = []
    chatHistory.append(C.chatContext[0])
    context_query_knowledge = chatHistory
    while True:
        ### RAG
        # global kbstate
        # if kbstate == None:
        #     print('Building KnowledgeBase!!!')
        #     # kbstate = build_kb(index_name)
        #     context_query_knowledge = chatHistory

        response = chat_completion_request(context_query_knowledge, temperature=0.2, tools=tools, tool_choice="auto")
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        if tool_calls:
            response_message_content = tool_call(context_query_knowledge, response_message, tool_calls)
        else:
            response_message_content = response.choices[0].message.content
        print("ChatBot: ", response_message_content)
        chatHistory.append({'role': 'assistant', 'content': f"{response_message_content}"})

        if chatHistory[-1]['content'].endswith('day!') or\
            chatHistory[-1]['content'].lower() == 'stop':
            break

        user_input = input("User Input:")
        input_embed = get_input_embedding(user_input)
        context_from_vecdb = retrive_from_pinecone(input_embed, pc.Index(index_name))
        prompt = build_prompt(context_from_vecdb)
        context_query_knowledge = build_context_query_knowledge(user_input, prompt, chatHistory)

        # chatHistory.append({'role':'user', 'content':f"{user_input}"})
