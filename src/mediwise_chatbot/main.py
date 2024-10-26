import os
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from mediwise_chatbot.utils import chat_complete_messages
from mediwise_chatbot import constants as C

app = FastAPI()
templates = Jinja2Templates(directory="templates")

chatHistory = []
chatResponses = []
chatHistory.append(C.chatContext[0])


@app.get('/', response_class=HTMLResponse)
async def page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.post("/", response_class=HTMLResponse)
async def entry(request: Request, user_input: Annotated[str, Form()]):

    chatHistory.append({'role':'user', 'content':f"{user_input}"})
    chatResponses.append(user_input)
    response_message_content = chat_complete_messages(chatHistory, 0.2)
    chatHistory.append({'role': 'assistant', 'content': f"{response_message_content}"})
    chatResponses.append(response_message_content)
    return templates.TemplateResponse("home.html", {"request": request, "chatresponses": chatResponses})


def entry_local():
    chatHistory = []
    chatHistory.append(C.chatContext[0])
    while True:
        response_message_content = chat_complete_messages(chatHistory, 0.2)
        print("ChatBot: ", response_message_content)
        chatHistory.append({'role': 'assistant', 'content': f"{response_message_content}"})
    
        if chatHistory[-1]['content'].endswith('day!') or\
            chatHistory[-1]['content'].lower() == 'stop':
            break
    
        user_input = input("User Input:")
        print("User: ", user_input)
        chatHistory.append({'role':'user', 'content':f"{user_input}"})
