import re
from dataclasses import dataclass
from typing import List

import pandas as pd

import config


# ─────────────────────────────────────────────────────────────
# Data Model
# ─────────────────────────────────────────────────────────────

@dataclass
class QARecord:
    id: int
    question: str
    answer: str
    content: str
    tokens: List[str]


# ─────────────────────────────────────────────────────────────
# Arabic Cleaning
# ─────────────────────────────────────────────────────────────

ARABIC_DIACRITICS = re.compile("""
                             ّ    | # Tashdid
                             َ    | # Fatha
                             ً    | # Tanwin Fath
                             ُ    | # Damma
                             ٌ    | # Tanwin Damm
                             ِ    | # Kasra
                             ٍ    | # Tanwin Kasr
                             ْ    | # Sukun
                             ـ
                         """, re.VERBOSE)


def normalize_arabic(text):

    text = re.sub(
        "[إأآا]",
        "ا",
        text,
    )

    text = re.sub(
        "ى",
        "ي",
        text,
    )

    text = re.sub(
        "ؤ",
        "و",
        text,
    )

    text = re.sub(
        "ئ",
        "ي",
        text,
    )

    text = re.sub(
        "ة",
        "ه",
        text,
    )

    return text


def strip_diacritics(text):

    return re.sub(
        ARABIC_DIACRITICS,
        "",
        text,
    )


# ─────────────────────────────────────────────────────────────
# Cleaning
# ─────────────────────────────────────────────────────────────

def clean_text(text):

    text = str(text).strip()

    text = strip_diacritics(text)

    text = normalize_arabic(text)

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


# ─────────────────────────────────────────────────────────────
# Tokenization
# ─────────────────────────────────────────────────────────────

def tokenize(text):

    text = clean_text(text)

    text = re.sub(
        r"[^\w\s]",
        " ",
        text,
    )

    tokens = text.split()

    return tokens


# ─────────────────────────────────────────────────────────────
# Load Excel
# ─────────────────────────────────────────────────────────────

def load_excel(
    path,
    question_col=None,
    answer_col=None,
):

    question_col = (
        question_col
        or
        config.QUESTION_COL
    )

    answer_col = (
        answer_col
        or
        config.ANSWER_COL
    )

    df = pd.read_excel(path)

    records = []

    for idx, row in df.iterrows():

        q = clean_text(
            row[question_col]
        )

        a = clean_text(
            row[answer_col]
        )

        # IMPORTANT:
        # index question + answer together

        content = f"""
السؤال:
{q}

الجواب:
{a}
"""

        tokens = tokenize(content)

        records.append(
            QARecord(
                id=idx,
                question=q,
                answer=a,
                content=content,
                tokens=tokens,
            )
        )

    return records