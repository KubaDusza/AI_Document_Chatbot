from imports import *
from constants import *
from utils.utils import get_uuid


def get_doc_text(doc):
    text = ""
    pdf_reader = PdfReader(doc)
    for page_num, page in enumerate(pdf_reader.pages):
        text += f"\n# page {page_num}#\n"
        text += page.extract_text()

    return text

@st.cache_resource(show_spinner=False)
def get_text_splitter():
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len
    )

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
                    # st.text(st.session_state.document_dict)
                    # st.write("NEW DOCUMENT!", file_name)
                    new_docs.append(Document(page_content=raw_text, metadata=metadata))
                    st.session_state.document_dict[tuple(metadata.values())] = {"active": True, "chunk_ids": []}
                    # st.text(st.session_state.document_dict)

            if new_docs:
                # list_new_docs_names = '\n'.join([doc.metadata["file_name"] for doc in new_docs])
                st.success(f"uploaded documents:", icon='✅')
                for doc in new_docs:
                    st.success(doc.metadata["file_name"])

            if MAX_NUM_DOCUMENTS < len(st.session_state.docs):
                st.error(f"maximum number of unique documents is {MAX_NUM_DOCUMENTS}. Didn't upload docs:", icon="❌")
                for doc in st.session_state.docs[MAX_NUM_DOCUMENTS:]:
                    st.error(doc.name)

                # num_not_uploaded = len(st.session_state.docs) - MAX_NUM_DOCUMENTS
                # list_of_unuploaded_docs = '\n'.join([doc.name for doc in st.session_state.docs[MAX_NUM_DOCUMENTS:]])

            if len(new_docs) > 0:
                doc_start = time.time()

                text_splitter = get_text_splitter()
                metadatas = []
                chunks = []
                for doc in new_docs:
                    new_chunks = text_splitter.split_text(text=doc.page_content)
                    chunks += new_chunks
                    metadatas += [doc.metadata for _ in new_chunks]

                chunking_end = time.time()
                # st.write(f"chunking new docs took {chunking_end - doc_start} seconds")

                if "vectorstore" not in st.session_state:
                    st.session_state.vectorstore = FAISS.from_texts(chunks, metadatas=metadatas,
                                                                    embedding=st.session_state.embeddings)
                else:
                    vectorstore_start = time.time()
                    st.session_state.vectorstore.add_texts(chunks, metadatas=metadatas)
                    vectorstore_end = time.time()
                    # st.write(f"embedding new docs took {vectorstore_end - vectorstore_start} seconds")

                indexing_start = time.time()

                for i, metadata in enumerate(metadatas):
                    index = st.session_state.vectorstore.index.ntotal - i - 1
                    st.session_state.document_dict[tuple(metadata.values())]["chunk_ids"].append(
                        st.session_state.vectorstore.index_to_docstore_id[index])

                indexing_end = time.time()
                # st.write(f"indexing new docs took {indexing_end - indexing_start} seconds")

                doc_end = time.time()
                # st.write(f"processing new docs took {doc_end - doc_start} seconds")

            # st.text("document dict " + str(st.session_state.document_dict))
            # st.write("docs", st.session_state.docs)

        del_start = time.time()
        # st.write(st.session_state.docs)
        # delete_removed_docs()
        del_end = time.time()
        end = time.time()

        # st.write("processing took", end-start, "seconds")
        # st.write("deleting took", del_end - del_start, "seconds")


def docs_uploader(container):
    if st.session_state.first_file_uploaded:
        container = st.sidebar

    with container:

        current_widget_docs = container.file_uploader('Add your Duckuments here!', accept_multiple_files=True,
                                       label_visibility="collapsed", type=ACCEPTED_DOCUMENT_TYPES)

        if current_widget_docs != st.session_state.docs:

            if not st.session_state.first_file_uploaded:
                st.session_state.first_file_uploaded = True
                st.rerun()

            st.session_state.docs = current_widget_docs
            handle_documents()

    return current_widget_docs


def delete_removed_docs(docs):
    doc_metadata = [(get_uuid(get_doc_text(doc)), os.path.splitext(doc.name)[0]) for doc in docs]
    # st.write("deleting unused docs:")
    # st.write("st.session_state.docs:", st.session_state.docs)
    # st.text("document dict: " + str(st.session_state.document_dict))

    docs_to_delete = []
    chunks_to_delete = []

    for metadata, data in st.session_state.document_dict.items():
        if metadata not in doc_metadata:
            docs_to_delete.append(metadata)
            if not data["chunk_ids"]:
                continue
            # st.write("removed doc", metadata)
            chunks_to_delete += data["chunk_ids"]
            # st.session_state.vectorstore.delete(data["chunk_ids"])

    if chunks_to_delete:
        try:
            st.session_state.vectorstore.delete(chunks_to_delete)
        except Exception as e:
            print(f"Error {e}")

    for doc in docs_to_delete:
        del st.session_state.document_dict[doc]

    chunks_to_delete = []

    for id, doc in st.session_state.vectorstore.docstore._dict.items():
        metadata = (doc.metadata["doc_uuid"], doc.metadata["file_name"])

        if not st.session_state.document_dict.get(metadata, False):
            chunks_to_delete.append(id)

    if chunks_to_delete:
        try:
            st.session_state.vectorstore.delete(chunks_to_delete)
        except Exception as e:
            print(f"Error {e}")





