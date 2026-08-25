# step 1 Load raw PDF

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

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


if __name__ == "__main__":
    documents = load_pdf_files(DATA_PATH)
    text_chunks = create_chunks(documents)
    print("Length of Text Chunks: ", len(text_chunks))

    # step 3 create vector embeddings
    
    
    
    
    # step 4 store embeddings
