"""
Evaluación del pipeline RAG de Beacon.

Métricas:
- keyword_hit_rate por query: fracción de keywords esperados presentes en la respuesta
- avg_hit_rate: promedio general — calidad de retrieval
- empty_rate: fracción de queries que no devolvieron resultados

Uso:
    python evals/eval.py

Target: avg_hit_rate >= 0.80
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.pipeline import search  # noqa: E402


def evaluate() -> None:
    qa_path = Path(__file__).parent / "qa_pairs.json"
    pairs = json.loads(qa_path.read_text(encoding="utf-8"))

    results = []
    for pair in pairs:
        response = search(pair["question"])
        response_lower = response.lower()

        hits = [kw for kw in pair["expected_keywords"] if kw.lower() in response_lower]
        missed = [kw for kw in pair["expected_keywords"] if kw.lower() not in response_lower]
        hit_rate = len(hits) / len(pair["expected_keywords"]) if pair["expected_keywords"] else 1.0
        empty = "No encontré información" in response

        results.append({"hit_rate": hit_rate, "empty": empty})

        icon = "✓" if hit_rate >= 0.8 else "✗"
        print(f"{icon} [{hit_rate:.0%}] {pair['question']}")
        if missed:
            print(f"      missed: {missed}")
        if empty:
            print("      ⚠ respuesta vacía")

    avg = sum(r["hit_rate"] for r in results) / len(results)
    empty_rate = sum(1 for r in results if r["empty"]) / len(results)

    print(f"\n{'='*50}")
    print(f"Avg keyword hit rate : {avg:.1%}  (target ≥ 80%)")
    print(f"Empty response rate  : {empty_rate:.1%}")
    print(f"Total queries        : {len(results)}")
    print("=" * 50)

    if avg < 0.8:
        print("\n⚠  Hit rate por debajo del target. Revisar chunk_size, top_k o calidad de docs.")
        sys.exit(1)
    else:
        print("\n✓  Pipeline dentro del target.")


if __name__ == "__main__":
    evaluate()
