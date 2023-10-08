
# 🦆 Ducky Chatbot 🐤
[ducky chatbot]( https://duckyai.streamlit.app/)

An AI assistant created to be helpful, harmless, and honest. Just like a friendly duck! *quack!*

This chatbot allows users to upload documents and chat with the bot to get information from the documents. The bot will search the uploaded documents and use relevant excerpts to answer your questions.

## How it works *quack!*

1. Upload PDF documents using the file uploader button
2. Type a question in the chat interface
3. The bot will search the documents and try to find the best answer
4. If relevant text is found, it will be displayed for you!

## What can it do?
- Answer general and detailed questions to the best of its duck abilities.
- Provide context and excerpts from uploaded documents
- Summarize and classify short passages
- Give friendly reminders to be excellent to each other 🦆

## Technologies used
This chatbot is built using:

- Streamlit for the web interface
- Langchain for NLP models and features
- Transformers and Huggingface API for model backends
- OpenAI API for embeddings and the LLM

## TODOs
- Add OCR support
- Support additional file formats like docx, txt etc
- Add multiprocessing when vectorizing document text
- Save user messages and session state per user
- Improve information extraction

##Installation
you can also host it by yourself! it's so easy!

1. Clone the repo
2. Create a virtualenv and activate
3. Install dependencies - pip install -r requirements.txt
4. Create a credentials file in the .streamlit directory and add OpenAI API key
5. change the REMOVE_RESTRICTIONS flag to True
6. Run the app - streamlit run app.py

So come on and give it a quack! The friendliest chatbot around won't quack you up but will do its best to help out. Just be nice and have fun! 🦆🐤
