from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # LLM providers
    google_api_key: str
    anthropic_api_key: str = ""  # opcional, para fallback

    # RAG
    chroma_persist_dir: str = "./chroma_db"
    docs_dir: str = "./docs"
    top_k: int = 4
    chunk_size: int = 500
    chunk_overlap: int = 50
    embedding_model: str = "models/gemini-embedding-001"

    # Server
    port: int = 8000  # Render inyecta PORT automáticamente
    log_level: str = "INFO"

    # URL que usa el demo agent para conectarse a Beacon
    mcp_server_url: str = "http://localhost:8000/sse"


settings = Settings()
