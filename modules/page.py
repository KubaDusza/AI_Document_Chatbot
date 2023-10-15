from utils import utils
from constants import *
from imports import *


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



def display_pdfs():
    if st.session_state.docs:
        for uploaded_file in st.session_state.docs:
            try:
                pages = convert_from_bytes(uploaded_file.read(), fmt="png", dpi=200)
                st.write(f"{len(pages)} page(s) loaded!")

                # Display images
                for i, page in enumerate(pages):
                    bio = io.BytesIO()  # Create a BytesIO object
                    page.save(bio, format="PNG")  # Save image to BytesIO object
                    st.image(bio, caption=f"Page {i + 1}", use_column_width=True)  # Display image
            except Exception as e:
                st.write("Error processing PDF: ", str(e))

def display_relevant_fragments(docs):

    if docs is None:
        return


    num_of_fragments = len(docs)


    if num_of_fragments != 0:
        with st.expander(f"relevant fragments", expanded=False):

            columns = st.columns(num_of_fragments)
            for column, doc in zip(columns, docs):

                    column.text(doc.page_content)


def clear_regenerate_button_callback():
    st.session_state.messages = []
    st.session_state.display_clear_button = False


def regenerate_callback():
    st.session_state.messages = st.session_state.messages[:-2]
    st.session_state.display_clear_button = False
    st.session_state.regenerate = True


def display_chat_buttons():


    if st.session_state.messages:
        st.session_state.display_clear_button = True


    if st.session_state.display_clear_button:
        button1, button2 = st.columns(2)

        button1.button('clear', use_container_width=True, on_click=clear_regenerate_button_callback)
        button2.button('regenerate', use_container_width=True, on_click=regenerate_callback)
