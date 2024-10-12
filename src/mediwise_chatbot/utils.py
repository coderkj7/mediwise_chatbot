from openai import OpenAI

client = OpenAI()

def chat_complete_messages(messages, temperature):
    # query against the model "gpt-3.5-turbo-1106"
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages= messages,
        temperature=temperature, # this is the degree of randomness of the model's output
    )
    return completion.choices[0].message.content
