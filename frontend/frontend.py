import html
import requests
import pandas as pd
import gradio as gr

# ─────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────

API_URL = "http://127.0.0.1:8000/query"
DATA_PATH = "data/qa_data.xlsx"


# ─────────────────────────────────────────────────────────────
# Suggested Questions
# ─────────────────────────────────────────────────────────────

try:
    df = pd.read_excel(DATA_PATH)
    suggested_questions = (
        df["Question"]
        .dropna()
        .astype(str)
        .sample(min(12, len(df)))
        .tolist()
    )
except Exception:
    suggested_questions = [
        "ما حكم إخراج زكاة الفطر نقداً؟",
        "ما هي شروط المسح على الخفين؟",
        "ما حكم صلاة الجماعة في المسجد؟",
        "هل يجوز تقسيط زكاة المال؟",
    ]


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def to_html(text: str) -> str:
    return html.escape(str(text or "")).replace("\n", "<br>")


# ─────────────────────────────────────────────────────────────
# Ask Backend
# ─────────────────────────────────────────────────────────────

def ask_question(question):
    try:
        if not question or not question.strip():
            return (
                "<div class='warning-box'>⚠️ الرجاء إدخال سؤال شرعي للبحث عنه.</div>",
                "<div class='warning-box'>لا توجد مصادر لعرضها.</div>",
            )

        response = requests.post(
            API_URL,
            json={"question": question.strip()},
            timeout=120,
        )

        try:
            data = response.json()
        except Exception:
            return (
                f"<div class='error-box'>❌ تعذر قراءة رد الخادم.<br>HTTP {response.status_code}</div>",
                "",
            )

        if response.status_code != 200:
            detail = data.get("detail", "حدث خطأ غير متوقع من الخادم.")
            return (
                f"<div class='error-box'>❌ {to_html(detail)}</div>",
                "",
            )

        answer = data.get("answer", "لم يتم العثور على إجابة مفصلة في قاعدة البيانات.")
        confidence = data.get("confidence", 0)
        sources = data.get("sources", [])

        confidence_percent = round(confidence * 100, 2)
        bar_color = (
            "var(--success-color)"
            if confidence_percent > 75
            else ("var(--warning-color)" if confidence_percent > 50 else "var(--danger-color)")
        )

        # ─────────────────────────────────────────
        # Answer HTML
        # ─────────────────────────────────────────

        answer_html = f"""
        <div class="answer-card fade-in">
            <div class="answer-header">
                <span class="icon">✨</span>
                <span>الخلاصة الفقهية</span>
            </div>
            <div class="answer-text">
                {to_html(answer)}
            </div>

            <div class="confidence-wrapper">
                <div class="confidence-label">
                    <span>مستوى دقة الإجابة (استناداً للمصادر)</span>
                    <span>{confidence_percent}%</span>
                </div>
                <div class="confidence-track">
                    <div class="confidence-fill" style="width: {confidence_percent}%; background-color: {bar_color};"></div>
                </div>
            </div>
        </div>
        """

        # ─────────────────────────────────────────
        # Sources HTML
        # ─────────────────────────────────────────

        if not sources:
            sources_html = "<div class='warning-box'>لم يتم العثور على مصادر مطابقة.</div>"
        else:
            sources_html = "<div class='sources-container'>"
            for i, s in enumerate(sources, start=1):
                score = round(s.get("score", 0) * 100, 2)
                sources_html += f"""
                <div class="source-card fade-in" style="animation-delay: {i * 0.08}s">
                    <div class="source-header">
                        <span class="source-badge">📚 المصدر {i}</span>
                        <span class="source-score">التطابق: {score}%</span>
                    </div>
                    <div class="source-content">
                        <div class="source-block">
                            <div class="source-label">السؤال المرجعي:</div>
                            <p>{to_html(s.get('question', 'غير متوفر'))}</p>
                        </div>
                        <div class="source-block">
                            <div class="source-label">نص الفتوى:</div>
                            <p class="source-answer-text">{to_html(s.get('answer', 'غير متوفر'))}</p>
                        </div>
                    </div>
                </div>
                """
            sources_html += "</div>"

        return answer_html, sources_html

    except Exception as e:
        error_html = f"<div class='error-box'>❌ حدث خطأ في الاتصال بالخادم:<br>{to_html(str(e))}</div>"
        return error_html, ""


# ─────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

:root {
    --brand-primary: #0f766e;
    --brand-hover: #115e59;
    --brand-glow: rgba(15, 118, 110, 0.4);

    --card-bg: #ffffff;
    --card-border: #e2e8f0;
    --text-title: #0f172a;
    --text-body: #334155;
    --text-muted: #64748b;
    --bg-light: #f8fafc;
    --badge-bg: #f1f5f9;

    --success-color: #0d9488;
    --warning-color: #d97706;
    --danger-color: #dc2626;
}

body, .gradio-container {
    font-family: 'Cairo', sans-serif !important;
    direction: rtl;
    text-align: right;
}

.gradio-container {
    max-width: 1100px !important;
    margin: auto !important;
    padding-top: 20px !important;
}

.hero-box {
    background: linear-gradient(135deg, var(--brand-primary) 0%, var(--brand-hover) 100%);
    border-radius: 20px;
    padding: 35px 20px;
    text-align: center;
    color: white;
    box-shadow: 0 10px 30px -5px var(--brand-glow);
    margin-bottom: 30px;
    border: 1px solid rgba(255,255,255,0.1);
}
.hero-title { font-size: 38px; font-weight: 800; margin-bottom: 12px; text-shadow: 0 2px 4px rgba(0,0,0,0.2); }
.hero-subtitle { font-size: 19px; opacity: 0.95; font-weight: 400; }

.answer-card {
    background: var(--card-bg);
    border-radius: 16px;
    padding: 30px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    border: 1px solid var(--card-border);
    transition: all 0.3s ease;
}
.answer-header {
    font-size: 24px;
    font-weight: 700;
    color: var(--text-title);
    border-bottom: 2px solid var(--bg-light);
    padding-bottom: 15px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.answer-text { font-size: 19px; line-height: 1.8; color: var(--text-body); }

.confidence-wrapper {
    margin-top: 30px;
    background: var(--bg-light);
    padding: 15px 20px;
    border-radius: 12px;
    border: 1px solid var(--card-border);
}
.confidence-label {
    display: flex;
    justify-content: space-between;
    font-size: 15px;
    font-weight: 700;
    color: var(--text-muted);
    margin-bottom: 10px;
}
.confidence-track {
    height: 8px;
    background: var(--card-border);
    border-radius: 10px;
    overflow: hidden;
}
.confidence-fill {
    height: 100%;
    border-radius: 10px;
    transition: width 1.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.sources-container { display: flex; flex-direction: column; gap: 20px; }
.source-card {
    background: var(--card-bg);
    border-radius: 16px;
    padding: 25px;
    border: 1px solid var(--card-border);
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}
.source-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 20px -8px var(--brand-glow);
    border-color: var(--brand-primary);
}
.source-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}
.source-badge { background: var(--badge-bg); color: var(--text-body); padding: 6px 12px; border-radius: 8px; font-weight: 700; font-size: 14px;}
.source-score { color: var(--brand-primary); font-weight: 700; font-size: 15px; background: var(--bg-light); padding: 4px 10px; border-radius: 6px;}
.source-label { font-size: 14px; color: var(--text-muted); font-weight: 700; margin-bottom: 5px; }
.source-block p { margin: 0 0 15px 0; font-size: 16px; line-height: 1.7; color: var(--text-title); }
.source-answer-text { background: var(--bg-light); padding: 15px; border-radius: 10px; border-right: 4px solid var(--brand-primary); }

.error-box { background: rgba(220, 38, 38, 0.1); color: #ef4444; padding: 20px; border-radius: 12px; border: 1px solid #fecaca; font-weight: 600; }
.warning-box { background: rgba(217, 119, 6, 0.1); color: #f59e0b; padding: 20px; border-radius: 12px; border: 1px solid #fcd34d; font-weight: 600; }

button.primary {
    background: var(--brand-primary) !important;
    font-weight: 700 !important;
    border: none !important;
    transition: all 0.2s !important;
}
button.primary:hover {
    background: var(--brand-hover) !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px var(--brand-glow) !important;
}
button.secondary {
    background: transparent !important;
    border: 2px solid var(--card-border) !important;
    color: var(--text-title) !important;
    font-weight: 700 !important;
    transition: all 0.2s !important;
}
button.secondary:hover {
    background: var(--bg-light) !important;
    border-color: var(--brand-primary) !important;
    color: var(--brand-primary) !important;
}

textarea {
    font-size: 18px !important;
    border-radius: 12px !important;
    background: var(--card-bg) !important;
    color: var(--text-title) !important;
    border-color: var(--card-border) !important;
}
textarea:focus {
    border-color: var(--brand-primary) !important;
    box-shadow: 0 0 0 1px var(--brand-primary) !important;
}

.fade-in { animation: fadeIn 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards; opacity: 0; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }

footer { display: none !important; }
"""


# ─────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────

with gr.Blocks(css=CUSTOM_CSS, theme=gr.themes.Default()) as demo:

    gr.HTML(
        """
        <div class="hero-box">
            <div class="hero-title">🕌 بوابة الفتاوى الذكية</div>
            <div class="hero-subtitle">محرك بحث عربي مدعوم بالذكاء الاصطناعي لاسترجاع الفتاوى من المصادر الموثوقة</div>
        </div>
        """
    )

    with gr.Row():
        with gr.Column(scale=7):
            question_input = gr.Textbox(
                label="",
                show_label=False,
                placeholder="اكتب سؤالك الفقهي أو الشرعي هنا...",
                lines=3,
                elem_id="target_q_input"
            )

            with gr.Row():
                submit_btn = gr.Button("🔍 ابحث عن الفتوى", variant="primary", elem_id="submit_btn_id")
                voice_btn = gr.Button("🎤 تحدث بالسؤال", variant="secondary", elem_id="voice_btn_id")

            gr.Examples(
                examples=[[q] for q in suggested_questions],
                inputs=question_input,
                label="💡 أسئلة شائعة للتجربة",
            )

    with gr.Row():
        with gr.Column():
            with gr.Tabs():
                with gr.TabItem("📖 الإجابة والفتوى"):
                    answer_output = gr.HTML()
                with gr.TabItem("📚 المصادر والأدلة المسترجعة"):
                    sources_output = gr.HTML()

    submit_btn.click(
        fn=ask_question,
        inputs=question_input,
        outputs=[answer_output, sources_output],
        api_name="query_fatwa"
    )

    voice_btn.click(
        fn=None,
        inputs=None,
        outputs=None,
        js="""
        () => {
            if (!('webkitSpeechRecognition' in window)) {
                alert('عذراً، متصفحك لا يدعم التعرف الصوتي.');
                return;
            }

            const recognition = new webkitSpeechRecognition();
            recognition.lang = 'ar-SA';
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            const textarea = document.querySelector('#target_q_input textarea');
            const submit = document.querySelector('#submit_btn_id button');

            if (!textarea) {
                alert('لم يتم العثور على مربع السؤال.');
                return;
            }

            recognition.onstart = () => {
                const btn = document.querySelector('#voice_btn_id button');
                if (btn) {
                    btn.textContent = '🔴 جارٍ الاستماع...';
                }
            };

            recognition.onresult = (event) => {
                const text = event.results[0][0].transcript;
                textarea.value = text;
                textarea.dispatchEvent(new Event('input', { bubbles: true }));

                setTimeout(() => {
                    if (submit) submit.click();
                }, 400);
            };

            recognition.onerror = (event) => {
                console.error(event);
                alert('حدث خطأ في التعرف الصوتي.');
            };

            recognition.onend = () => {
                const btn = document.querySelector('#voice_btn_id button');
                if (btn) {
                    btn.textContent = '🎤 تحدث بالسؤال';
                }
            };

            recognition.start();
        }
        """
    )

if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7861,
        share=False,
    )