"""CLI tester for the pipeline without the web UI."""

from __future__ import annotations

import argparse
import os
import sys
import time

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT)

from src.pipeline import RAGPipeline


BENCHMARK = [
    "ما حكم أكل الضفدع؟",
    "هل يكفي عن يوم عاشوراء أن أصوم معه التاسع أم لابد من الحادي عشر؟",
    "ما حكم من صلى صلاة بلا وضوء متعمدا وهو يعلم أنه لا يجوز ذلك؟",
    "ما حكم البيع بالتقسيط والإيجار المنتهي بالتمليك؟",
    "ما علاج الحسد؟",
    "ما حكم الأخذ بالبيعة للجماعات؟",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", default=None)
    parser.add_argument("--benchmark", action="store_true")
    args = parser.parse_args()

    pipeline = RAGPipeline()
    pipeline.load_index()

    questions = BENCHMARK if args.benchmark else [args.question or BENCHMARK[0]]

    for q in questions:
        t0 = time.perf_counter()
        result = pipeline.answer(q)
        elapsed = round((time.perf_counter() - t0) * 1000, 1)

        print("\n" + "=" * 80)
        print("Q:", q)
        print("Topic:", result.topic)
        print("Mode :", result.mode)
        print("Conf :", result.confidence)
        print("Latency:", elapsed, "ms")
        print("Answer:\n", result.answer)
        print("Sources:")
        for s in result.sources:
            print(f"  - [{s['score']:.3f}] {s['question']}")


if __name__ == "__main__":
    main()
