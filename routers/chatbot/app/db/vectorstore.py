from config import Config
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_astradb import AstraDBVectorStore

def get_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    return AstraDBVectorStore(
        embedding=embeddings,
        collection_name=Config.ASTRA_COLLECTION,
        api_endpoint=Config.ASTRA_DB_ENDPOINT,
        token=Config.ASTRA_DB_API_KEY,
    )

# ✅ For Chat Cache Collection
def get_chat_cache_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    return AstraDBVectorStore(
        embedding=embeddings,
        collection_name="chat_cache",  # fixed collection for all cached chats
        api_endpoint=Config.ASTRA_DB_ENDPOINT,
        token=Config.ASTRA_DB_API_KEY,
    )