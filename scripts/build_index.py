"""Build the FAISS + BM25 indexes from the Excel dataset."""

from __future__ import annotations

import argparse
import os
import sys
import time

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT)

import config
from src.pipeline import RAGPipeline


def parse_args():
    parser = argparse.ArgumentParser(description="Build hybrid indices from Excel.")
    parser.add_argument("--data", default=config.DATA_PATH, help="Path to qa_data.xlsx")
    return parser.parse_args()


def main():
    args = parse_args()

    if not os.path.exists(args.data):
        print(f"Data file not found: {args.data}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print(" Fatwa RAG — Index Builder")
    print("=" * 60)
    print(f" Data file      : {args.data}")
    print(f" Embedding model: {config.EMBEDDING_MODEL}")
    print(f" Groq model     : {config.GROQ_MODEL}")
    print(f" Index dir      : {config.INDEX_DIR}")
    print("=" * 60 + "\n")

    t0 = time.time()
    pipeline = RAGPipeline()
    pipeline.build_index(args.data)
    elapsed = time.time() - t0

    print(f"\nDone in {elapsed:.1f}s")
    print(f"Saved FAISS   -> {config.FAISS_INDEX}")
    print(f"Saved BM25    -> {config.BM25_PATH}")
    print(f"Saved metadata-> {config.METADATA_PATH}")


if __name__ == "__main__":
    main()
