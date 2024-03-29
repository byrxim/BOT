import streamlit as st
from langchain import PromptTemplate
from langchain_community.llms import HuggingFaceHub
import textwrap
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from PyPDF2 import PdfReader
import os
import textwrap
from langchain.chains.question_answering import load_qa_chain
from langchain.chains.summarize import load_summarize_chain
document = PdfReader("48lawsofpower.pdf")

os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"

def load_LLM():
    """Logic for loading the chain you want to use should go here."""
    # Make sure your openai_api_key is set as an environment variable
    llm = HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs={"temperature":0.8,"max_length":512})
    return llm

st.set_page_config(page_title="PDF ChatBot")
st.header("PDF CHATTER BY BRIYASH")

st.markdown("## Enter Your Query")


def get_text():
    input_text = st.text_area(label="Email Input", label_visibility='collapsed', placeholder="Your query", key="email_input")
    return input_text

email_input = get_text()

if len(email_input.split(" ")) > 700:
    st.write("Please enter a shorter Query. The maximum length is 700 words.")
    st.stop()

st.markdown("### Your Converted Email:")

if email_input:

    llm = load_LLM()

    raw_text=''

    for i, page in enumerate(document.pages):
        text=page.extract_text()
        if text:
            raw_text += text

    from langchain.text_splitter import RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 0)
    docs = text_splitter.split_text(raw_text)

    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    embeddings = HuggingFaceEmbeddings()
    db = FAISS.from_texts(docs, embeddings)

    query=email_input

    docRes=db.similarity_search(query)
    chain = load_summarize_chain(llm, chain_type="map_reduce")
    chain(docRes)
    chain2 = load_qa_chain(llm, chain_type="refine")
    ada = chain2.run(input_documents=docRes, question=query)
    st.write(ada)