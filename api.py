import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_classic.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import ChatHuggingFace, HuggingFaceEmbeddings, HuggingFaceEndpoint
from pydantic import BaseModel

load_dotenv(".env")

DB_FAISS_PATH = "vectorstore/db_faiss"
CUSTOM_PROMPT_TEMPLATE = """
Use the pieces of information provided in the context to answer the user's question.
If you do not know the answer, say that you do not know. Do not make up an answer.
Answer only from the provided context.

Context: {context}
Question: {question}

Start the answer directly. No small talk.
"""

app = FastAPI(title="Medical Chatbot API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


def build_qa_chain():
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        raise RuntimeError("HF_TOKEN is missing from the .env file.")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vectorstore = FAISS.load_local(
        DB_FAISS_PATH,
        embeddings,
        allow_dangerous_deserialization=True,
    )
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
    return RetrievalQA.from_chain_type(
        llm=ChatHuggingFace(llm=endpoint),
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True,
        chain_type_kwargs={
            "prompt": PromptTemplate(
                template=CUSTOM_PROMPT_TEMPLATE,
                input_variables=["context", "question"],
            )
        },
    )


qa_chain = None


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat")
def chat(request: ChatRequest):
    global qa_chain
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        if qa_chain is None:
            qa_chain = build_qa_chain()
        response = qa_chain.invoke({"query": question})
        sources = [
            {
                "page": document.metadata.get("page_label"),
                "source": os.path.basename(document.metadata.get("source", "")),
            }
            for document in response.get("source_documents", [])
        ]
        return {"answer": response["result"], "sources": sources}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
