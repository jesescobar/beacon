import logging
from pathlib import Path

from langchain_core.documents import Document

from app.rag.vector_store import get_retriever

logger = logging.getLogger(__name__)

_FALLBACK = (
    "No encontré información sobre ese tema en la base de conocimiento. "
    "Para más ayuda, contactanos por WhatsApp al 0971 444 600 "
    "o por email a info@plub.com."
)


def format_response(docs: list[Document]) -> str:
    """
    Formatea los chunks recuperados en un string con referencias de fuente.
    El agente recibe este string y lo usa para construir su respuesta final.
    """
    if not docs:
        return _FALLBACK

    parts = []
    for doc in docs:
        source_path = doc.metadata.get("source", "")
        source_name = Path(source_path).stem if source_path else "desconocida"
        parts.append(f"{doc.page_content.strip()}\n[Fuente: {source_name}]")

    return "\n\n---\n\n".join(parts)


def search(query: str) -> str:
    """Embedea la query, recupera los top-k chunks y retorna la respuesta formateada."""
    logger.info("Buscando en knowledge base | query=%r", query)
    retriever = get_retriever()
    docs = retriever.invoke(query)
    response = format_response(docs)
    logger.info("Retornando %d chunks", len(docs))
    return response
