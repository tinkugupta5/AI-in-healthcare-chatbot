# step 1 Load raw PDF

import os

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

DATA_PATH = "data/"

def load_pdf_files(data):
    loader = DirectoryLoader(
        data,
        glob="*.pdf",
        loader_cls=PyPDFLoader
    )

    documents = loader.load()
    print("Length of PDF pages : ", len(documents))
    return documents


def create_chunks(extracted_data):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )
    return text_splitter.split_documents(extracted_data)


def get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


if __name__ == "__main__":
     # step 1
    documents = load_pdf_files(DATA_PATH)
    text_chunks = create_chunks(documents)
    print("Length of Text Chunks: ", len(text_chunks))

    # step 3 create vector embeddings
    embedding_model = get_embedding_model()
    print("Embedding model loaded")

    # step 4 store embeddings
    
    DB_FAISS_PATH = "vectorstore/db_faiss"
    os.makedirs(os.path.dirname(DB_FAISS_PATH), exist_ok=True)

    db = FAISS.from_documents(text_chunks, embedding_model)
    db.save_local(DB_FAISS_PATH)
    print("FAISS vector store saved to:", DB_FAISS_PATH)