#!/usr/bin/env python3
"""
CLI de ingesta — correr una vez después de agregar o modificar docs/.

Uso:
    python scripts/ingest.py
    python scripts/ingest.py --docs-dir /ruta/a/docs
"""

import argparse
import logging
import sys
from pathlib import Path

# Hace que app/ sea importable desde la raíz del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.ingestion import ingest  # noqa: E402

logging.basicConfig(
    level="INFO",
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingesta documentos en el knowledge base de Beacon."
    )
    parser.add_argument(
        "--docs-dir",
        default=None,
        help="Ruta al directorio de documentos (default: DOCS_DIR en .env o ./docs)",
    )
    args = parser.parse_args()

    n = ingest(args.docs_dir)
    if n > 0:
        print(f"\n✓ Ingesta completa: {n} chunks guardados en ChromaDB.")
    else:
        print("\n✗ No se ingirió nada. Verificar que docs/ tenga archivos .md.")
        sys.exit(1)


if __name__ == "__main__":
    main()
