import streamlit

from imports import *
from constants import *
from utils.emotion_classification import EmotionClassifier
from modules.page import display_relevant_fragments
openai.api_key = st.secrets["OPENAI_API_KEY"]


@st.cache_resource(show_spinner=False)
def get_emotion_classifier():
    return EmotionClassifier()


def get_response(messages, model = None, stream = True, temperature = 1.0):
    if model is None:
        model = st.session_state["openai_model"]

    return openai.ChatCompletion.create(
        model=model,
        messages=messages,
        stream=stream,
        temperature=temperature)


def display_chat():

    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=message["avatar"]):
            st.markdown(message["content"])


def ask_question():
    # prompt = st.session_state.prompt

    prompt = st.chat_input("What is up?")  # , key="prompt")

    st.session_state.prompts.append(prompt)

    if st.session_state.regenerate:
        last_non_null_text = next((text for text in reversed(st.session_state.prompts) if text is not None), None)

        prompt = last_non_null_text
        st.session_state.regenerate = False

    if prompt:
        avatar = get_emotion_classifier().classify(prompt)

        with st.chat_message("user", avatar=avatar):
            st.markdown(prompt)

        st.session_state.messages.append({"role": "user", "content": prompt, "avatar": avatar})

        rephrased_prompt = rephrase_question()

        docs = st.session_state.vectorstore.similarity_search(rephrased_prompt, k=K)

        #display_relevant_fragments(docs)

        # st.write(docs)

        ai_message(docs)

        columns = st.columns(K)

        x = '''any_expanded = False
        for i, column in enumerate(columns):
            if not any_expanded:
                with column:
                    with st.expander(docs[i].page_content[:10] + "..."):
                        any_expanded = True
                        write_atsize(docs[i].page_content, 12)'''


def ai_message(docs):

    if docs:
        relevant_docs_messages = [{"role": "assistant", "content": "content of document fragment:\n" + doc.page_content} for doc in docs]
    else:
        relevant_docs_messages = [{"role": "system", "content": "there are no available documents from the user"}]

    chat_history_header = [
        {"role": "system", "content": "### end of relevant documents. the next messages contain the chat history ###"}]

    with (st.chat_message("assistant", avatar=MAIN_ICON)):
        message_placeholder = st.empty()
        full_response = ""
        messages = [INSTRUCTION_MESSAGE] + relevant_docs_messages + chat_history_header + [
            {"role": m["role"], "content": m["content"]} for m in
            st.session_state.messages[-SLIDING_CHAT_WINDOW_SIZE:]]

        for response in get_response(messages):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response, "avatar": MAIN_ICON})




REPHRASE_QUESTION_INSTRUCTION_TEXT = """###INSTRUCTIONS: Construct a query from the last question in the provided chat history, suitable for a similarity search in a vector store, using keywords and context from the history.You can also add other keywords you think will help. Respond only with the query, without any additional prefixes or labels.###"""

def rephrase_question():
    REPHRASE_MESSAGE = {
        "role": "system",
        "content": REPHRASE_QUESTION_INSTRUCTION_TEXT + f"avaliable file names: " + ", ".join([doc.name for doc in st.session_state.docs])
    }

    m = st.session_state.messages[-1]

    last_prompt = "\nTHE QUESTION: " + m["content"] + " Query:"

    messages = "Chat hostory:\n" +", ".join(
        [m["role"] + ": " + m["content"] for m in
        st.session_state.messages[-SLIDING_CHAT_WINDOW_SIZE:-1]]) + last_prompt


    #st.text(REPHRASE_MESSAGE)
    #st.text(messages)

    response = get_response([REPHRASE_MESSAGE] + [{"role": "user", "content": messages}], stream=False, temperature=0.2).choices[0].message.get("content", "")
    #response = st.session_state.messages[-1]["content"]
    #st.write(response)
    return response
