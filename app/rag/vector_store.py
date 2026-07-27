from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import settings

COLLECTION_NAME = "beacon_kb"


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """
    Instancia de embeddings compartida entre ingesta y query.
    Crítico: ambos flujos deben usar el mismo modelo y la misma key
    para que los vectores vivan en el mismo espacio.
    """
    return GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model,
        google_api_key=settings.google_api_key,
    )


def get_vector_store() -> Chroma:
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=settings.chroma_persist_dir,
    )


def get_retriever():
    return get_vector_store().as_retriever(
        search_type="similarity",
        search_kwargs={"k": settings.top_k},
    )
