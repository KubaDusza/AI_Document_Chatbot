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


def pdf_display(pdf_binary, width="100%", height="600px"):
    pdf_file = utils.get_base64_of_bin_file(pdf_binary)
    pdf_embed = f"""
    <iframe
        src="data:application/pdf;base64,{pdf_file}"
        width="{width}"
        height="{height}"
        type="application/pdf"
        style="position:relative;width:{width};height:{height};overflow:auto;"
        frameborder="0"
    >
    </iframe>
    """
    return pdf_embed

"""def pdf_display(pdf_binary, width = 1000, height = 600):
    
    pdf_display = f'''
    <iframe src="data:application/pdf;base64,{pdf_file}" width="{width}" height="{height}" type="application/pdf">
    </iframe>
    '''
    return pdf_display
"""



def display_relevant_fragments(docs):

    if docs is None:
        return


    num_of_fragments = len(docs)


    if num_of_fragments != 0:
        with st.expander(f"relevant fragments", expanded=False):

            columns = st.columns(num_of_fragments)
            for column, doc in zip(columns, docs):

                    column.text(doc.page_content)

def display_pdfs():
    if st.session_state.docs:
        for uploaded_file in st.session_state.docs:
            with st.expander(f"View PDF: {uploaded_file.name}", expanded=False):
                st.markdown(
                    pdf_display(uploaded_file.getbuffer(), width="100%", height="400px"),
                    unsafe_allow_html=True
                )
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
