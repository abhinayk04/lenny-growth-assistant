#!/usr/bin/env python3
"""
CLI entrypoint script to run transcript ingestion pipeline.
"""
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.ingestion.ingest import ingest_corpus

if __name__ == "__main__":
    print("Starting transcript ingestion into PostgreSQL + pgvector...")
    ingest_corpus()
