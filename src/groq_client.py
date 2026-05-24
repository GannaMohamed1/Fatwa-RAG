"""Groq API wrapper for Arabic query rewriting, expansion, and answer generation."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any

from groq import Groq


_JSON_RE = re.compile(r"\{.*\}", re.S)


def _safe_json(text: str, default: dict[str, Any]) -> dict[str, Any]:
    try:
        return json.loads(text)
    except Exception:
        match = _JSON_RE.search(text or "")
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
    return default


@dataclass
class GroqOutputs:
    msa_query: str
    expanded_queries: list[str]
    topic: str


class GroqArabicHelper:
    """Keeps Groq usage small, cheap, and Arabic-friendly."""

    def __init__(self, model: str, api_key: str | None = None, max_tokens: int = 900, temperature: float = 0.1):
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.client = Groq(api_key=self.api_key) if self.api_key else None

    @property
    def available(self) -> bool:
        return self.client is not None

    def _chat(self, system: str, user: str, max_tokens: int | None = None, temperature: float | None = None) -> str:
        if not self.client:
            return ""
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature if temperature is not None else self.temperature,
            max_tokens=max_tokens if max_tokens is not None else self.max_tokens,
        )
        return (resp.choices[0].message.content or "").strip()

    def rewrite_to_msa(self, query: str) -> str:
        if not self.available:
            return query.strip()

        system = (
            "أنت خبير في العربية. "
            "حوّل السؤال إلى العربية الفصحى مع الحفاظ على المعنى الدقيق والمصطلحات الشرعية. "
            "أعد نصاً واحداً فقط دون شرح."
        )
        return self._chat(system, query, max_tokens=120).strip() or query.strip()

    def classify_topic(self, query: str) -> str:
        if not self.available:
            return "عام"

        system = (
            "أنت مصنّف موضوعات للفتاوى الإسلامية. "
            "أعد فقط أحد هذه التصنيفات: "
            "طهارة، صلاة، صيام، زكاة، حج وعمرة، عقيدة، معاملات، أسرة، فتن وسياسة، أذكار ودعاء، عام. "
            "أعد كلمة واحدة فقط."
        )
        topic = self._chat(system, query, max_tokens=20).strip()
        topic = topic.replace("،", "").replace(".", "").strip()
        allowed = {"طهارة", "صلاة", "صيام", "زكاة", "حج وعمرة", "عقيدة", "معاملات", "أسرة", "فتن وسياسة", "أذكار ودعاء", "عام"}
        return topic if topic in allowed else "عام"

    def expand_queries(self, query: str, n: int = 3) -> list[str]:
        if not self.available or n <= 0:
            return []

        system = (
            "أنت مساعد بحث عربي. "
            "حوّل السؤال إلى ثلاث صيغ بحثية قصيرة ومختلفة مع الحفاظ على المعنى. "
            "أعد JSON فقط بهذه الصيغة: {\"queries\": [\"...\", \"...\", \"...\"]}. "
            "لا تضع شرحاً إضافياً."
        )
        raw = self._chat(system, query, max_tokens=180)
        data = _safe_json(raw, {"queries": []})
        queries = [str(q).strip() for q in data.get("queries", []) if str(q).strip()]
        # Deduplicate and cap
        out = []
        for q in queries:
            if q not in out and q != query:
                out.append(q)
        return out[:n]

    def answer_from_context(self, question: str, context: str) -> str:
        if not self.available:
            return ""

        system = """
أنت نظام استرجاع فتاوى إسلامية.

مهمتك:

الإجابة فقط من النصوص المسترجعة
عدم اختراع أي معلومة
عدم إصدار فتوى جديدة
عدم الاستنتاج من نفسك
إذا كانت المعلومات غير كافية قل:
"لم أجد فتوى موثوقة كافية للإجابة"

استخدم فقط المعلومات الموجودة في المصادر.
"""
        user = f"السياق:\n{context}\n\nالسؤال:\n{question}"
        return self._chat(system, user, max_tokens=450, temperature=0.05)

    def summarize_related(self, question: str, context: str) -> str:
        if not self.available:
            return ""
        system = (
            "لخّص الجواب في فقرة عربية فصيحة قصيرة جداً، "
            "من دون تغيير المعنى أو إضافة استنتاجات جديدة."
        )
        user = f"السياق:\n{context}\n\nالسؤال:\n{question}"
        return self._chat(system, user, max_tokens=220, temperature=0.05)
