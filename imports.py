import streamlit as st
from dotenv import load_dotenv
import openai
import os
import uuid
import time
import base64
import io

#from pdf2image import convert_from_bytes
from langchain.schema import Document
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
