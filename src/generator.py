from dataclasses import dataclass


@dataclass
class GeneratedAnswer:
    answer: str
    confidence: float
    sources: list


class AnswerGenerator:

    def generate(
        self,
        query,
        hits,
        min_confidence=0.45,
    ):

        if not hits:

            return GeneratedAnswer(
                answer="عذراً، لم أجد فتوى مناسبة.",
                confidence=0.0,
                sources=[],
            )

        best = hits[0]

        if best.score < min_confidence:

            return GeneratedAnswer(
                answer="عذراً، لا توجد إجابة موثوقة كافية.",
                confidence=best.score,
                sources=[],
            )

        return GeneratedAnswer(
            answer=best.answer,
            confidence=best.score,
            sources=[
                {
                    "question": h.question,
                    "answer": h.answer,
                    "score": h.score,
                }
                for h in hits
            ],
        )