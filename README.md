# MediWise Chatbot
Medical Chat Assistant.

Built using:

`OpenAI` - LLM

`Fastapi` - framework for building API's.

`Jinja2` - templating for creating HTML.

`Bootstrap 5` - html, css and javascript toolkit for developing UI.

# How to Use the Bot from Browser
- Clone the repo to your machine
- Open terminal and then `cd` into the repo.
- From the terminal execute `python -m pip install -e .` to install the package on your machine.
- Create a .env file in the root directory of the repo
- In the first line of the .env file, put put your API key insteadf of `{your_key}` in `OPENAI_API_KEY={your_key}`
- execute `uvicorn mediwise_chatbot.main:app --host 127.0.0.1 --port 8001 --reload`
- uvicorn will host the application at `http://127.0.0.1:8001`

# How to Use the Bot from Terminal
- Clone the repo to your machine
- Open terminal and then `cd` into the repo.
- From the terminal execute `python -m pip install -e .` to install the package on your machine.
- Create a .env file in the root directory of the repo
- In the first line of the .env file, put put your API key insteadf of `{your_key}` in `OPENAI_API_KEY={your_key}`
- execute `chatbot`
  
# How to Contribute

- Create a `feature` branch from `main` .
- Make your changes in the `feature` branch.
- Push the `feature` to github.
- Create a Pull Request to the `main` from the `feature` branch.

# Note

Do not commit your api keys or any personal details.

# Resources
- [Planning and User Stories](https://lucid.app/lucidspark/40dc780b-0a4b-4243-ae61-28290dc36111/edit?invitationId=inv_a7c6313a-3322-4a40-92af-773b961cd35c&page=0_0#)