# %%
import os 
import dotenv

from langchain_chroma import Chroma

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders.text import TextLoader

from langchain_nomic.embeddings import NomicEmbeddings
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)

from langchain_text_splitters import CharacterTextSplitter

dotenv.load_dotenv()

root = os.getcwd()

embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

POLITICAL_P = os.getenv("POLITICAL_PARTI")
TXT_ROOT = os.getenv("TXT_ROOT")
txt_root = f"{root}{TXT_ROOT}{POLITICAL_P}/{POLITICAL_P}.txt"
root = os.getcwd()
PDF_ROOT = os.getenv("PDF_ROOT")

def load_chunk_persist_pdf(POLITICAL_PARTI) -> Chroma : 

    pdf_root = f"{root}/{PDF_ROOT}{POLITICAL_PARTI}/"

    print("#######################")
    print(f"Initialize the vector DB  {POLITICAL_PARTI}")
    print("#######################")

    if os.path.exists(f"{root}/chroma_db_{POLITICAL_PARTI}") :
         print("load the vector db...")
         vectorstore = Chroma(persist_directory=f"{root}/chroma_db_{POLITICAL_PARTI}", embedding_function=embedding_function)
    else:
        documents = []
        for file in os.listdir(pdf_root):
                if file.endswith('.pdf'):
                    pdf_path = os.path.join(pdf_root+file)
                    loader = PyPDFLoader(pdf_path)
                    documents.extend(loader.load())
        text_splitter = CharacterTextSplitter(chunk_size=50, chunk_overlap=10)
        # split it into chunks
        docs = text_splitter.split_documents(documents)
        print("create the vector db...")
        vectorstore = Chroma.from_documents(documents =docs,
                                    persist_directory=f"{root}/chroma_db_{POLITICAL_PARTI}",
                                    collection_name="rag-chroma",
                                    embedding=embedding_function,
                                    )
        #vectorstore = Chroma(persist_directory=f"{root}/chroma_db_{POLITICAL_PARTI}", embedding_function=embedding_function)
    
    retriever = vectorstore.as_retriever()
    
    print("...vector db loaded")

    return retriever
# %%
def txt_loader_db(root=txt_root) -> Chroma:
    loader = TextLoader(root)
    documents = loader.load()

    # split it into chunks
    text_splitter = CharacterTextSplitter(chunk_size=20, chunk_overlap=5)
    docs = text_splitter.split_documents(documents)

    # load it into Chroma
    vectorstore = Chroma.from_documents(documents =docs,
                                collection_name="rag-chroma",
                                embedding=NomicEmbeddings(model="nomic-embed-text-v1.5",
                                inference_mode='local'),
                                )
    retriever = vectorstore.as_retriever()

    return retriever