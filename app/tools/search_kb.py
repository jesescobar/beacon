from mcp.server.fastmcp import FastMCP

from app.rag.pipeline import search

mcp = FastMCP("beacon")


@mcp.tool()
async def search_knowledge_base(query: str) -> str:
    """
    Search Plub's knowledge base for FAQs, policies,
    delivery zones, operating hours, and payment methods.
    Returns a formatted answer with source references.

    Use this tool when the user asks informational questions
    that are not about specific products or cart operations.
    Examples: delivery hours, coverage area, return policy,
    accepted payment methods, how to contact support.
    """
    return search(query)
