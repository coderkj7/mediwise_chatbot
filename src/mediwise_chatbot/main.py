import os
from dotenv import load_dotenv
from mediwise_chatbot.utils import chat_complete_messages
from mediwise_chatbot import constants as C


def entry():
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