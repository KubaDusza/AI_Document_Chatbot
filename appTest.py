import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import pickle
from dotenv import load_dotenv
import os
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
from io import BytesIO
import fitz
from PIL import Image
import base64
from pathlib import Path
from langchain.memory import ConversationBufferMemory


EMBEDDINGS_FOLDER = Path("embeddings")


def displayPDF(pdf):
    pdf.seek(0)
    pdf_bytes = pdf.read()
    pdf.seek(0)

    stream = BytesIO(pdf_bytes)
    base64_pdf = base64.b64encode(stream.read()).decode('utf-8')

    # Embedding PDF in HTML
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="500" height="1100" type="application/pdf"></iframe>'
    return pdf_display


def main():
    load_dotenv()
    st.header("Chat with PDF 💬")

    # upload a PDF file

    pdf = st.file_uploader("upload your pdf", type = "pdf")

    if pdf:
        pdf_reader = PdfReader(pdf)

        pdf_bytes = pdf.read()

        stream = BytesIO(pdf_bytes)
        pdf_display = displayPDF(pdf)

        st.sidebar.markdown(pdf_display, unsafe_allow_html=True)

        text = ""
        for i, page in enumerate(pdf_reader.pages):
            text += f"\n\n###PAGE {i+1}###\n\n{page.extract_text()}"

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=400,
            length_function=len
        )
        chunks = text_splitter.split_text(text=text)

        store_name = pdf.name[:-4]
        path = os.path.join(EMBEDDINGS_FOLDER, f"{store_name}.pkl")
        st.write(path)

        if os.path.exists(path):
            with open(path, "rb") as f:
                vectorStore = pickle.load(f)
                st.write("embeddings loaded from a file")
        else:
            embeddings = OpenAIEmbeddings()
            vectorStore = FAISS.from_texts(chunks, embedding=embeddings)

            with open(path, "wb") as f:
                pickle.dump(vectorStore, f)
            st.write("embeddings computation completed")

        # accept user questions
        k = st.slider(label = "number of relevant chunks you want", min_value=1, max_value=10 ,value=6)

        query = st.text_input("ask questions about your PDF file:")





        if query:
            docs = vectorStore.similarity_search(query, k=k)

            llm = OpenAI(temperature=1, model_name="gpt-3.5-turbo", )
            chain = load_qa_chain(llm=llm, chain_type="stuff")
            with get_openai_callback() as cb:
                response = chain.run(input_documents=docs, question=query)
                st.write(cb)
            st.write(response)





if __name__ == "__main__":
    EMBEDDINGS_FOLDER.mkdir(parents=True, exist_ok=True)
    main()


