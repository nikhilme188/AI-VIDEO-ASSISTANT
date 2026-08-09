import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pinecone import Pinecone
load_dotenv()
HUGGINGFACE_API_KEY=os.getenv("HUGGINGFACE_API_KEY")

embedding = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-mpnet-base-v2",
    # model="sentence-transformers/all-MiniLM-L6-v2",
     task="feature-extraction",
    huggingfacehub_api_token=HUGGINGFACE_API_KEY
)


# embeddings = HuggingFaceEndpointEmbeddings(
#     model="sentence-transformers/all-mpnet-base-v2"
# )

def build_vector_store(transcript:str)->str:
    """Returns a Pinecone Vector Store instance"""
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks=splitter.split_text(transcript)

    docs=[Document(
        page_content=chunk,
        metadata={"chunk_index":i}
    )
    for i ,chunk in enumerate(chunks)]


    vector_store = get_vector_store()
    vector_store.add_documents(docs)

    return vector_store

    
def get_vector_store():
    """Returns a Pinecone Vector Store instance"""
    pc = Pinecone(
        api_key=os.getenv("PINECONE_API_KEY")
    )

    index = pc.Index(
        os.getenv("PINECONE_INDEX_NAME")
    )

    vector_store = PineconeVectorStore(
        index=index,
        embedding=embedding
    )

    return vector_store


def get_retriever(vector_store:PineconeVectorStore, k :int = 4):
    return vector_store.as_retriever(
        search_type = 'similarity',
        search_kwargs = {"k":k}
    )

