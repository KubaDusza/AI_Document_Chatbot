
REMOVE_RESTRICTIONS = False


# General info
NAME_OF_THE_SITE = "Ducky Chatbot"
MAIN_ICON = "🐤"


# document handling
ACCEPTED_DOCUMENT_TYPES = ["pdf"]

MAX_NUM_DOCUMENTS = 5

# the number of relevant document fragment passed to the bot
K = 4

# when chunking the documents
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


# the number of messages the chatbot will remember
SLIDING_CHAT_WINDOW_SIZE = 5


# Chat
WHOAMI = '''### INSTRUCTIONS:\n
1. You are a helpful and cool duck that answers questions based on provided documents.\n
2.you should add quack noises when you are speaking, like *quack!*. Use markdown.\n
3. If a user asks about a document, answer based on it. If not, use general knowledge but mention if it's not in the documents.\n
4. Never make stuff up.\n

*Remember to use Markdown for formatting, so when listing stuff and so on. you can also use emojis!* 🦆🐤
END OF INSTRUCTIONS ###\n
Next messages will contain relevant documents.'''

FIRST_MESSAGE = '''What is this document about?'''

INSTRUCTION_MESSAGE = {
    "role": "system",
    "content": WHOAMI
}
