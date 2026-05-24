import re


# ─────────────────────────────────────────────────────────────
# Arabic Diacritics
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


# ─────────────────────────────────────────────────────────────
# Remove Diacritics
# ─────────────────────────────────────────────────────────────

def strip_diacritics(text):

    return re.sub(
        ARABIC_DIACRITICS,
        "",
        text,
    )


# ─────────────────────────────────────────────────────────────
# Normalize Arabic
# ─────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────
# Clean Text
# ─────────────────────────────────────────────────────────────

def clean_text(text):

    text = str(text)

    text = text.strip()

    text = strip_diacritics(text)

    text = normalize_arabic(text)

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


# ─────────────────────────────────────────────────────────────
# Sanitize Query
# ─────────────────────────────────────────────────────────────

def sanitize_query(query):

    query = clean_text(query)

    # remove strange symbols

    query = re.sub(
        r"[^\w\s؟?]",
        " ",
        query,
    )

    query = re.sub(
        r"\s+",
        " ",
        query,
    )

    return query.strip()