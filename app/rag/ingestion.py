import logging
from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.rag.vector_store import get_vector_store

logger = logging.getLogger(__name__)


def load_documents(docs_dir: str | None = None) -> list:
    """Carga todos los archivos .md del directorio docs/."""
    path = Path(docs_dir or settings.docs_dir)
    if not path.exists():
        raise FileNotFoundError(f"docs_dir no existe: {path}")

    loader = DirectoryLoader(
        str(path),
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=True,
    )
    docs = loader.load()
    logger.info("Cargados %d documentos desde %s", len(docs), path)
    return docs


def chunk_documents(docs: list) -> list:
    """
    Fragmenta los documentos en chunks con overlap.

    Los separadores están ordenados de mayor a menor unidad semántica:
    primero por heading de Markdown, después por párrafo, línea y palabra.
    Así el splitter respeta las secciones del documento antes de romper
    por cualquier salto de línea.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "],
    )
    chunks = splitter.split_documents(docs)
    logger.info("Fragmentados en %d chunks", len(chunks))
    return chunks


def ingest(docs_dir: str | None = None) -> int:
    """Pipeline completo: load → chunk → embed → persist en ChromaDB."""
    docs = load_documents(docs_dir)
    if not docs:
        logger.warning("No se encontraron documentos. Verificar docs_dir.")
        return 0

    chunks = chunk_documents(docs)
    vs = get_vector_store()
    vs.add_documents(chunks)
    logger.info(
        "Persistidos %d chunks en ChromaDB (%s)",
        len(chunks),
        settings.chroma_persist_dir,
    )
    return len(chunks)
