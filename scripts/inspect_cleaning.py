"""Inspect how the Arabic cleaning transforms the dataset."""

from __future__ import annotations

import os
import sys

import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT)

import config
from src.data_loader import clean_question, clean_answer
from src.utils import simple_tokenize


def main():
    df = pd.read_excel(config.DATA_PATH)
    df.columns = [str(c).strip() for c in df.columns]
    q_col = config.QUESTION_COL
    a_col = config.ANSWER_COL

    print(f"Loaded {len(df)} rows from {config.DATA_PATH}\n")

    for i, row in df.head(8).iterrows():
        q = str(row[q_col])
        a = str(row[a_col])
        print("=" * 80)
        print(f"ROW {i}")
        print("Q raw   :", q[:200])
        print("Q clean :", clean_question(q)[:200])
        print("Q toks  :", simple_tokenize(clean_question(q))[:12])
        print("A raw   :", a[:200])
        print("A clean :", clean_answer(a)[:200])
        print("A toks  :", simple_tokenize(clean_answer(a))[:12])


if __name__ == "__main__":
    main()
