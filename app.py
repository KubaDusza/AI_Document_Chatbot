import streamlit as st
from dotenv import load_dotenv
from emotion_classification import EmotionClassifier
import openai
import os
from pathlib import Path
import pickle
from uuid import uuid4
import uuid
import time
import concurrent.futures


from langchain.schema import Document
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain

from io import StringIO

# TODO:
todo = '''
add OCR
add different file types
add multipfocessing when vectorizing:



'''

ACCEPTED_DOCUMENT_TYPES = ["pdf"]

MAX_NUM_DOCUMENTS = 5


EMBEDDINGS_FOLDER = Path("embeddings")

openai.api_key = st.secrets["OPENAI_API_KEY"]

ALLOWED_EMAILS = ["jacob.dusza@gmail.com", "test@localhost.com", "test@example.com"]

NAME_OF_THE_SITE = "Ducky Chatbot"
MAIN_ICON = "🐤"

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


def setup():

    EMBEDDINGS_FOLDER.mkdir(parents=True, exist_ok=True)

    st.set_page_config(
        page_title=NAME_OF_THE_SITE,
        page_icon=MAIN_ICON,
        layout="wide",
        initial_sidebar_state="auto",
        menu_items={
            "About": "mailto: jacob.dusza@gmail.com linkedin:https://www.linkedin.com/in/jakub-dusza-041a9023b/",
            "Get help": "https://www.youtube.com/",
            "Report a bug": "https://www.youtube.com/"
        }
    )

    if 'display_clear_button' not in st.session_state:
        st.session_state.display_clear_button = False

    if 'first_file_uploaded' not in st.session_state:
        st.session_state.first_file_uploaded = False

    if "my_avatar" not in st.session_state:
        st.session_state.my_avatar = "🤠"

    if "emotion_classifier" not in st.session_state:
        st.session_state.emotion_classifier = EmotionClassifier()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-3.5-turbo"

    if "llm" not in st.session_state:
        st.session_state.llm = ChatOpenAI()

    if "embeddings" not in st.session_state:
        st.session_state.embeddings = OpenAIEmbeddings()

    if "text_splitter" not in st.session_state:
        st.session_state.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )

    if "memory" not in st.session_state:
        st.session_state.memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)

    if "k" not in st.session_state:
        st.session_state.k = 4

    if "document_dict" not in st.session_state:
        st.session_state.document_dict = {}

    if "docs" not in st.session_state:
        st.session_state.docs = []

    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = FAISS.from_texts([""], OpenAIEmbeddings(), metadatas=[
            {"doc_uuid": None, "file_name": None}])

    if "first_question_asked" not in st.session_state:
        st.session_state.first_question_asked = False

    if "prompt" not in st.session_state:
        st.session_state.prompt = FIRST_MESSAGE

    if "prompts" not in st.session_state:
        st.session_state.prompts = []

    if "regenerate" not in st.session_state:
        st.session_state.regenerate = False

def get_uuid(text):
    return uuid.uuid3(uuid.NAMESPACE_DNS, text)


def get_doc_text(doc):
    text = ""
    pdf_reader = PdfReader(doc)
    for page_num, page in enumerate(pdf_reader.pages):
        text += f"\n# page {page_num}#\n"
        text += page.extract_text()

    return text


def get_text_chunks(text):
    text_splitter = st.session_state.text_splitter
    chunks = text_splitter.split_text(text)
    return chunks


def get_vector_store(chunks):
    embeddings = st.session_state.embeddings
    vectorstore = FAISS.from_texts(chunks, embedding=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = st.session_state.memory
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever,
        memory=memory
    )
    return conversation_chain


def chat():
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=message["avatar"]):
            st.markdown(message["content"])


def get_response(messages):
    return openai.ChatCompletion.create(
        model=st.session_state["openai_model"],
        messages=messages,
        stream=True)


def ai_message(docs):


    relevant_docs_messages = [{"role": "system", "content": doc.page_content} for doc in docs]


    chat_history_header = [{"role": "system", "content": "### end of relevant documents. the next messages contain the chat history ###"}]

    with (st.chat_message("assistant", avatar=MAIN_ICON)):
        message_placeholder = st.empty()
        full_response = ""
        messages = [INSTRUCTION_MESSAGE] + relevant_docs_messages + chat_history_header + [{"role": m["role"], "content": m["content"]} for m in
                                            st.session_state.messages]

        for response in get_response(messages):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response, "avatar": MAIN_ICON})


def clear_regenerate_button_callback():
    st.session_state.messages = []
    st.session_state.display_clear_button = False

def regenerate_callback():
    st.session_state.messages = st.session_state.messages[:-2]
    st.session_state.display_clear_button = False
    st.session_state.regenerate = True


def upload_first_doc_callback():
    st.session_state.first_file_uploaded = True

    #handle_documents()


def handle_documents():

    if st.session_state.first_file_uploaded:
        start = time.time()
        with st.spinner("Processing files"):

            new_docs = []
            for i, doc in enumerate(st.session_state.docs):

                if i >= MAX_NUM_DOCUMENTS:
                    st.write("stopped at file", doc.name)
                    break

                file_name, extension = os.path.splitext(doc.name)

                raw_text = get_doc_text(doc)

                doc_uuid = get_uuid(raw_text)
                metadata = {"doc_uuid": doc_uuid, "file_name": file_name}


                if not st.session_state.document_dict.get(tuple(metadata.values()), False):
                    #st.text(st.session_state.document_dict)
                    #st.write("NEW DOCUMENT!", file_name)
                    new_docs.append(Document(page_content=raw_text, metadata=metadata))
                    st.session_state.document_dict[tuple(metadata.values())] = {"active": True, "chunk_ids": []}
                    #st.text(st.session_state.document_dict)

            if new_docs:
                #list_new_docs_names = '\n'.join([doc.metadata["file_name"] for doc in new_docs])
                st.success(f"uploaded documents:", icon='✅')
                for doc in new_docs:
                    st.success(doc.metadata["file_name"])

            if MAX_NUM_DOCUMENTS < len(st.session_state.docs):
                st.error(f"maximum number of unique documents is {MAX_NUM_DOCUMENTS}. Didn't upload docs:", icon="❌")
                for doc in st.session_state.docs[MAX_NUM_DOCUMENTS:]:
                    st.error(doc.name)


                #num_not_uploaded = len(st.session_state.docs) - MAX_NUM_DOCUMENTS
                #list_of_unuploaded_docs = '\n'.join([doc.name for doc in st.session_state.docs[MAX_NUM_DOCUMENTS:]])


            if len(new_docs) > 0:
                doc_start = time.time()

                text_splitter = st.session_state.text_splitter
                metadatas = []
                chunks = []
                for doc in new_docs:
                    new_chunks = text_splitter.split_text(text=doc.page_content)
                    chunks += new_chunks
                    metadatas += [doc.metadata for _ in new_chunks]



                chunking_end = time.time()
                #st.write(f"chunking new docs took {chunking_end - doc_start} seconds")

                if "vectorstore" not in st.session_state:
                    st.session_state.vectorstore = FAISS.from_texts(chunks, metadatas=metadatas, embedding=st.session_state.embeddings)
                else:
                    vectorstore_start = time.time()
                    st.session_state.vectorstore.add_texts(chunks, metadatas=metadatas)
                    vectorstore_end = time.time()
                    #st.write(f"embedding new docs took {vectorstore_end - vectorstore_start} seconds")

                indexing_start = time.time()

                for i, metadata in enumerate(metadatas):
                    index = st.session_state.vectorstore.index.ntotal - i - 1
                    st.session_state.document_dict[tuple(metadata.values())]["chunk_ids"].append(st.session_state.vectorstore.index_to_docstore_id[index])

                indexing_end = time.time()
                #st.write(f"indexing new docs took {indexing_end - indexing_start} seconds")

                doc_end = time.time()
                #st.write(f"processing new docs took {doc_end - doc_start} seconds")

            #st.text("document dict " + str(st.session_state.document_dict))
            #st.write("docs", st.session_state.docs)


        del_start = time.time()
        #st.write(st.session_state.docs)
        #delete_removed_docs()
        del_end = time.time()
        end = time.time()

        #st.write("processing took", end-start, "seconds")
        #st.write("deleting took", del_end - del_start, "seconds")


def docs_uploader(container):

    with container:
        if st.session_state.first_file_uploaded:
            docs = st.sidebar.file_uploader('Add your Duckuments here!', accept_multiple_files=True,
                                   label_visibility="collapsed", type=ACCEPTED_DOCUMENT_TYPES)
            if docs != st.session_state.docs:
                # st.session_state.first_file_uploaded = True
                st.session_state.docs = docs
                with st.sidebar:
                    handle_documents()


        else:

            docs = st.file_uploader('Add your Duckuments here!', accept_multiple_files=True,
                                       label_visibility="collapsed", on_change=upload_first_doc_callback,
                                    type = ACCEPTED_DOCUMENT_TYPES)

            if docs != st.session_state.docs:
                # st.session_state.first_file_uploaded = True
                st.session_state.docs = docs
                with st.sidebar:
                    handle_documents()

    delete_removed_docs(docs)






def delete_removed_docs(docs):
    doc_metadata = [(get_uuid(get_doc_text(doc)), os.path.splitext(doc.name)[0]) for doc in docs]
    #st.write("deleting unused docs:")
    #st.write("st.session_state.docs:", st.session_state.docs)
    #st.text("document dict: " + str(st.session_state.document_dict))

    docs_to_delete = []

    for metadata, data in st.session_state.document_dict.items():
        if metadata not in doc_metadata:
            docs_to_delete.append(metadata)
            if not data["chunk_ids"]:
                continue
            #st.write("removed doc", metadata)
            st.session_state.vectorstore.delete(data["chunk_ids"])

    for doc in docs_to_delete:
        del st.session_state.document_dict[doc]

    chunks_to_delete = []

    for id, doc in st.session_state.vectorstore.docstore._dict.items():
        metadata = (doc.metadata["doc_uuid"], doc.metadata["file_name"])

        if not st.session_state.document_dict.get(metadata, False):
            chunks_to_delete.append(id)

    if chunks_to_delete:
        st.session_state.vectorstore.delete(chunks_to_delete)








def sticky_header():
    header = st.container()
    header.header(NAME_OF_THE_SITE + "  " + MAIN_ICON)
    header.write("""<div class='fixed-header'/>""", unsafe_allow_html=True)

    # Custom CSS for the sticky header
    st.markdown(
        """
    <style>
        div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
            position: sticky;
            background: #0E1117;
            top: 2rem;
            z-index: 999;
        }
        .fixed-header {
            border-bottom: 4px solid #262730;
        }
    </style>
        """,
        unsafe_allow_html=True
    )


def write_atsize(text, size):
    st.write(f'<span style="font-size: {size}px;">{text}</span>', unsafe_allow_html=True)



def ask_question():

    #prompt = st.session_state.prompt

    prompt = st.chat_input("What is up?")#, key="prompt")

    st.session_state.prompts.append(prompt)

    if st.session_state.regenerate:
        last_non_null_text = next((text for text in reversed(st.session_state.prompts) if text is not None), None)

        prompt = last_non_null_text
        st.session_state.regenerate = False

    if prompt:
        avatar = st.session_state.emotion_classifier.classify(prompt)

        with st.chat_message("user", avatar=avatar):
            st.markdown(prompt)

        st.session_state.messages.append({"role": "user", "content": prompt, "avatar": avatar})

        docs = st.session_state.vectorstore.similarity_search(prompt, k=st.session_state.k)

        # st.write(docs)

        ai_message(docs)

        columns = st.columns(st.session_state.k)

        x = '''any_expanded = False
        for i, column in enumerate(columns):
            if not any_expanded:
                with column:
                    with st.expander(docs[i].page_content[:10] + "..."):
                        any_expanded = True
                        write_atsize(docs[i].page_content, 12)'''


def log():
    st.write("current state of docs and document dict:")
    st.write("st.session_state.docs:", st.session_state.docs)
    st.text("document dict: " + str(st.session_state.document_dict))
    st.write("vector store:", st.session_state.vectorstore.docstore._dict)

def main():

    load_dotenv()

    sticky_header()

    uploader_placeholder = st.empty()



    #if st.session_state.first_file_uploaded:
    chat()

    ask_question()

    docs_uploader(uploader_placeholder)

    #st.write(st.session_state.docs)
    #st.text(st.session_state.document_dict)

        #st.write("chat history:", st.session_state.messages[1:])
    #log()

    if st.session_state.messages:
        st.session_state.display_clear_button = True


    # fytst.write(st.session_state.prompts)

    if st.session_state.display_clear_button:

        button1, button2 = st.columns(2)

        button1.button('clear', use_container_width=True, on_click=clear_regenerate_button_callback)
        button2.button('regenerate', use_container_width=True, on_click=regenerate_callback)



if __name__ == '__main__':
    setup()

    #if st.experimental_user.email in ALLOWED_EMAILS:
        #write_atsize(f"email: {st.experimental_user.email}", 10)
    main()
    #else:
    #    st.write(f"sorry, email {st.experimental_user.email} has no access")
