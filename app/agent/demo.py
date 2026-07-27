"""
Demo ReAct agent para el Desafío Alura Agentes.

Usa search_knowledge_base directamente (sin MCP) para funcionar standalone
y ser inspeccionable en LangGraph Studio con `langgraph dev`.

Para el flujo MCP completo (Beacon como server externo), ver scripts/ingest.py
y el README.
"""

from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from app.config import settings
from app.rag.pipeline import search


@tool
def search_knowledge_base(query: str) -> str:
    """
    Search Plub's knowledge base for FAQs, policies,
    delivery zones, operating hours, and payment methods.
    Returns a formatted answer with source references.

    Use this for informational questions, not product queries.
    """
    return search(query)


llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=settings.google_api_key,
    temperature=0,
)

# Graph expuesto a LangGraph Studio via langgraph.json
agent = create_react_agent(llm, [search_knowledge_base])


if __name__ == "__main__":
    """Corre el demo directamente: python -m app.agent.demo"""
    queries = [
        "¿Cuáles son los horarios de entrega?",
        "¿Qué pasa si me falta un producto en el pedido?",
        "¿Qué medios de pago aceptan?",
        "¿Cómo sé si mi dirección tiene cobertura?",
        "¿Puedo usar dos cupones en el mismo pedido?",
    ]

    for q in queries:
        print(f"\n{'='*60}")
        print(f"Query: {q}")
        print("=" * 60)
        result = agent.invoke({"messages": [{"role": "user", "content": q}]})
        print(f"Answer: {result['messages'][-1].content}")
