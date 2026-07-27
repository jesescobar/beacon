import logging

from app.config import settings
from app.tools.search_kb import mcp  # noqa: F401 — importar registra la tool en FastMCP

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

if __name__ == "__main__":
    # SSE transport: expone GET /sse y POST /messages
    # El agente se conecta a http://host:port/sse
    mcp.run(transport="sse", host="0.0.0.0", port=settings.port)
