import streamlit as st

ALLOWED_EMAILS = ["jacob.dusza@gmail.com", "test@localhost.com"]

NAME_OF_THE_SITE = "File Chatbot"
PAGE_ICON = "💬"


def setup():
    st.set_page_config(
        page_title=NAME_OF_THE_SITE,
        page_icon=PAGE_ICON,
        layout="wide",
        initial_sidebar_state="auto",
        menu_items={
            "About":        "mailto: jacob.dusza@gmail.com linkedin:https://www.linkedin.com/in/jakub-dusza-041a9023b/",
            "Get help":     "https://www.youtube.com/",
            "Report a bug": "https://www.youtube.com/"
        }
    )


if "assistant_avatar" not in st.session_state:
    st.session_state.assistant_avatar = "🤠"

if "show_assistant_avatar_radio" not in st.session_state:
    st.session_state.show_assistant_avatar_radio = False

def side_bar(show):

    if not show:
        return


    with st.sidebar:
        #st.toggle("show assistant avatars", key="show_assistant_avatar_radio", value=st.session_state.show_assistant_avatar_radio)
        if st.toggle("first toggle", value=st.session_state.show_assistant_avatar_radio):
            st.session_state.show_assistant_avatar_radio = not st.session_state.show_assistant_avatar_radio



        if st.session_state.show_assistant_avatar_radio:
            st.session_state.assistant_avatar = st.radio(
                label="choose assistant's avatar",
                label_visibility="collapsed",
                index=0,
                options=["🤠", "🤖", "😺"]
            )

        if st.toggle("second toggle", value=st.session_state.show_assistant_avatar_radio):
            st.session_state.show_assistant_avatar_radio = not st.session_state.show_assistant_avatar_radio



messages = ["hi", "hello", "how are you?", "good, thanks"]


def main():
    setup()
    side_bar(True)
    st.header(NAME_OF_THE_SITE + PAGE_ICON)
    st.write(st.session_state)

    for k, v in st.session_state.items():
        st.write(f"{k}: {v}")


    for i, message in enumerate(messages):
        name = "ai" if i%2 == 0 else "user"
        avatar = st.session_state.assistant_avatar if i % 2 == 0 else "🤠"
        with st.chat_message(name=name, avatar=avatar):
            st.write(message)


if __name__ == '__main__':
    if st.experimental_user.email in ALLOWED_EMAILS:
        main()
    else:
        st.write(f"sorry, email {st.experimental_user.email} has no access")

