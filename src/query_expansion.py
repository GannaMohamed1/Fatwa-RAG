from groq import Groq

import config


client = Groq(
    api_key=config.GROQ_API_KEY
)


def expand_query(query):

    try:

        prompt = f"""
قم بإعادة صياغة السؤال التالي بثلاث صيغ مختلفة
لتحسين البحث في الفتاوى الإسلامية.

السؤال:
{query}

أعد فقط الأسئلة.
"""

        response = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.2,
        )

        text = response.choices[0].message.content

        queries = []

        for line in text.split("\n"):

            line = line.strip(
                "-•123456789. "
            )

            if line:
                queries.append(line)

        return [query] + queries[:3]

    except Exception:

        return [query]