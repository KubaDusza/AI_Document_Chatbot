from imports import *
from modules.setup import setup, grant_access
from modules.page import sticky_header, display_chat_buttons, display_relevant_fragments
from modules.chat import display_chat, ask_question
from modules.file_handling import docs_uploader, delete_removed_docs
from modules.page import display_pdfs



def main():


    uploader_placeholder = st.empty()

    display_chat()




    current_widget_docs = docs_uploader(uploader_placeholder)
    delete_removed_docs(current_widget_docs)



    ask_question()


    display_chat_buttons()

    #with st.sidebar:
        #display_pdfs()

if __name__ == '__main__':
    load_dotenv()
    setup()

    sticky_header()

    # st.write(st.session_state.access_key in allowed_access_keys)
    # st.write("allowed access keys:", allowed_access_keys)
    # st.write("access key:", st.session_state.access_key)

    if grant_access():
        main()
