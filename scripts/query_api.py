"""Simple command-line client for testing the API."""

from __future__ import annotations

import argparse
import os
import sys

import requests

DEFAULT_ENDPOINT = "http://127.0.0.1:8000"


def ask(endpoint: str, question: str) -> dict:
    r = requests.post(f"{endpoint}/query", json={"question": question}, timeout=120)
    r.raise_for_status()
    return r.json()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--question", default=None)
    args = parser.parse_args()

    if args.question:
        questions = [args.question]
    else:
        questions = [
            "ما حكم أكل الضفدع؟",
            "كيف أصوم يوم عاشوراء؟",
            "هل يجوز أخذ أجر على تحصيل الفواتير؟",
        ]

    for q in questions:
        try:
            res = ask(args.endpoint, q)
            print("\n" + "=" * 80)
            print("Question:", res["question_original"])
            print("Topic   :", res["topic"])
            print("Mode    :", res["mode"])
            print("Conf    :", res["confidence"])
            print("Answer  :")
            print(res["answer"])
            print("Sources :")
            for s in res["sources"]:
                print(f"  - [{s['score']:.3f}] {s['question']}")
        except Exception as exc:
            print("Error:", exc)


if __name__ == "__main__":
    main()
