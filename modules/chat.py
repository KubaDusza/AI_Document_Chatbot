import streamlit

from imports import *
from constants import *
from utils.emotion_classification import EmotionClassifier

openai.api_key = st.secrets["OPENAI_API_KEY"]


@st.cache_resource(show_spinner=False)
def get_emotion_classifier():
    return EmotionClassifier()


def get_response(messages):
    return openai.ChatCompletion.create(
        model=st.session_state["openai_model"],
        messages=messages,
        stream=True)


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


def ai_message(docs):

    if docs:
        relevant_docs_messages = [{"role": "system", "content": doc.page_content} for doc in docs]
    else:
        relevant_docs_messages = [{"role": "system", "content": "there are no available documents from the user"}]

    chat_history_header = [
        {"role": "system", "content": "### end of relevant documents. the next messages contain the chat history ###"}]

    with (st.chat_message("assistant", avatar=MAIN_ICON)):
        message_placeholder = st.empty()
        full_response = ""
        messages = [INSTRUCTION_MESSAGE] + relevant_docs_messages + chat_history_header + [
            {"role": m["role"], "content": m["content"]} for m in
            st.session_state.messages]

        for response in get_response(messages):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response, "avatar": MAIN_ICON})
