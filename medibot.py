import os

import streamlit as st
from dotenv import load_dotenv
from langchain_classic.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import (
    ChatHuggingFace,
    HuggingFaceEmbeddings,
    HuggingFaceEndpoint,
)

load_dotenv(".env")

DB_FAISS_PATH = "vectorstore/db_faiss"


@st.cache_resource
def get_vectorstore():
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return FAISS.load_local(
        DB_FAISS_PATH,
        embedding_model,
        allow_dangerous_deserialization=True,
    )


def set_custom_prompt(custom_prompt_template):
    return PromptTemplate(
        template=custom_prompt_template,
        input_variables=["context", "question"],
    )


CUSTOM_PROMPT_TEMPLATE = """
Use the pieces of information provided in the context to answer the user's question.
If you do not know the answer, say that you do not know. Do not make up an answer.
Answer only from the provided context.

Context: {context}
Question: {question}

Start the answer directly. No small talk.
"""


@st.cache_resource
def get_qa_chain():
    vectorstore = get_vectorstore()
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        raise RuntimeError("HF_TOKEN is missing from the .env file.")

    endpoint = HuggingFaceEndpoint(
        repo_id=os.environ.get(
            "HUGGINGFACE_REPO_ID",
            "meta-llama/Llama-3.1-8B-Instruct",
        ),
        task="conversational",
        huggingfacehub_api_token=hf_token,
        temperature=0.0,
        max_new_tokens=512,
    )
    llm = ChatHuggingFace(llm=endpoint)
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True,
        chain_type_kwargs={
            "prompt": set_custom_prompt(CUSTOM_PROMPT_TEMPLATE),
        },
    )


def main():
    st.title("Ask Chatbot!")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Pass your prompt here")
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Searching the medical reference..."):
                response = get_qa_chain().invoke({"query": prompt})
            st.markdown(response["result"])
            st.session_state.messages.append(
                {"role": "assistant", "content": response["result"]}
            )
        except Exception as error:
            st.error(f"Error: {error}")

if __name__ == "__main__":
    main()