import io
import re
import math
import html
from collections import Counter

import streamlit as st
from pypdf import PdfReader

st.set_page_config(page_title="Suma — AI Text Summarizer", page_icon="✦", layout="wide")

STOP_WORDS = set("""a an the and or but if then else when at by for from in into of on onto to up with is am are was were be been being have has had do does did can could should would will may might must this that these those it its as not no so than too very also about after again all any because before between both each few more most other some such only own same until while what which who whom why how i me my we our you your he she they them their his her there here over under out off""".split())

def split_sentences(text):
    text = re.sub(r"\\s+", " ", text).strip()
    if not text:
        return []
    return [s.strip() for s in re.split(r"(?<=[.!?])\\s+(?=[A-Z0-9“\"'])", text) if s.strip()]

def summarize(text, amount="Balanced", bullets=5):
    sentences = split_sentences(text)
    if len(sentences) <= 1:
        return sentences
    words = re.findall(r"\\b[a-zA-Z][a-zA-Z'-]{2,}\\b", text.lower())
    freq = Counter(w for w in words if w not in STOP_WORDS)
    if not freq:
        return sentences[:bullets]
    max_freq = max(freq.values())
    weights = {w: n / max_freq for w, n in freq.items()}
    scored = []
    for i, sentence in enumerate(sentences):
        tokens = re.findall(r"\\b[a-zA-Z][a-zA-Z'-]{2,}\\b", sentence.lower())
        content = [w for w in tokens if w not in STOP_WORDS]
        score = sum(weights.get(w, 0) for w in content) / max(1, math.sqrt(len(tokens)))
        score += max(0, 0.08 - i * 0.003)
        scored.append((score, i, sentence))
    ratio = {"Short": 0.18, "Balanced": 0.32, "Detailed": 0.55}.get(amount, 0.32)
    count = min(bullets, max(1 if amount == "Short" else 2, round(len(sentences) * ratio)))
    chosen = sorted(scored, reverse=True)[:count]
    return [s for _, _, s in sorted(chosen, key=lambda item: item[1])]

def extract_pdf(uploaded):
    reader = PdfReader(io.BytesIO(uploaded.getvalue()))
    return "\\n".join(page.extract_text() or "" for page in reader.pages).strip()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root{--ink:#f5f5ff;--muted:#a6abc5;--line:rgba(255,255,255,.11)}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
.stApp{color:var(--ink);background:radial-gradient(ellipse at 8% 0%,rgba(99,102,241,.23),transparent 35%),radial-gradient(ellipse at 90% 16%,rgba(20,184,166,.13),transparent 31%),linear-gradient(135deg,#090b18,#101329 52%,#0b1020)}
.stApp:before{content:"";position:fixed;inset:0;pointer-events:none;opacity:.16;background-image:radial-gradient(rgba(255,255,255,.38) .7px,transparent .7px);background-size:24px 24px}
.block-container{max-width:1180px;padding-top:2rem;padding-bottom:4rem;position:relative}
header,footer,#MainMenu{visibility:hidden}
.brand{display:flex;align-items:center;gap:11px;font-family:'Space Grotesk',sans-serif;font-weight:700;letter-spacing:-.04em;font-size:1.28rem}
.brand-icon{width:38px;height:38px;display:grid;place-items:center;border-radius:13px;background:linear-gradient(135deg,#8b5cf6,#4f46e5 55%,#06b6d4);box-shadow:0 8px 28px #635bdf45}
.pill{display:inline-flex;gap:7px;border:1px solid #4f46e54d;background:#4f46e51a;color:#c7c5ff;padding:7px 12px;border-radius:999px;font-size:.78rem;font-weight:600}
.pulse{width:7px;height:7px;border-radius:50%;background:#34d399;display:inline-block;box-shadow:0 0 0 5px #34d39918}
.hero{padding:58px 0 35px;animation:rise .75s cubic-bezier(.2,.8,.2,1) both}
.eyebrow{color:#a5a2ff;text-transform:uppercase;letter-spacing:.18em;font-size:.72rem;font-weight:700;margin-bottom:17px}
h1{font-family:'Space Grotesk',sans-serif!important;font-size:clamp(2.7rem,6vw,4.8rem)!important;line-height:1.04!important;letter-spacing:-.065em!important;margin:0 0 18px!important;color:#fff!important}
.gradient-text{background:linear-gradient(100deg,#c4b5fd,#818cf8 43%,#67e8f9);-webkit-background-clip:text;background-clip:text;color:transparent}
.hero-copy{color:#b5bad1;max-width:660px;font-size:1.05rem;line-height:1.8}
.panel{background:linear-gradient(145deg,rgba(25,29,55,.92),rgba(17,21,41,.82));border:1px solid var(--line);border-radius:23px;padding:24px;box-shadow:0 24px 80px #00000024;backdrop-filter:blur(18px)}
.panel-title{font-family:'Space Grotesk',sans-serif;font-size:1.05rem;font-weight:700;color:#f6f6ff;margin-bottom:5px}
.panel-sub{color:#9da4c1;font-size:.84rem;line-height:1.6;margin-bottom:20px}
.stat{border:1px solid var(--line);background:#ffffff06;border-radius:16px;padding:15px 17px;transition:transform .2s,border-color .2s}
.stat:hover{transform:translateY(-3px);border-color:#818cf866}
.stat-label{font-size:.75rem;color:#9da4c1;margin-bottom:8px}
.stat-value{font-family:'Space Grotesk',sans-serif;font-size:1.4rem;font-weight:700;color:#fff}
.section-kicker{color:#9da4c1;font-size:.76rem;text-transform:uppercase;letter-spacing:.15em;font-weight:700;margin:28px 0 13px}
.result-card{border:1px solid var(--line);border-radius:17px;padding:17px 18px;background:#ffffff05;margin:10px 0;animation:rise .45s ease both}
.result-num{display:inline-grid;place-items:center;flex-shrink:0;width:27px;height:27px;border-radius:9px;background:#8176ff20;color:#bcb5ff;font-size:.78rem;font-weight:700}
.result-text{color:#e7e9f8;line-height:1.7}
.stTextArea textarea{background:#0c1022!important;color:#f2f3ff!important;border:1px solid #ffffff20!important;border-radius:15px!important;line-height:1.7!important}
.stTextArea textarea:focus{border-color:#8b7dff!important;box-shadow:0 0 0 3px #8b7dff20!important}
.stSelectbox div[data-baseweb="select"]>div{background:#0c1022;color:#f2f3ff;border-color:#ffffff20;border-radius:12px}
.stButton button{border-radius:12px;border:1px solid #ffffff18;background:linear-gradient(110deg,#7868f5,#4f46e5);color:white;font-weight:700;padding:.68rem 1rem;transition:transform .18s,box-shadow .18s}
.stButton button:hover{transform:translateY(-2px);box-shadow:0 10px 25px #6559e645;border-color:#a5a0ff}
div[data-testid="stFileUploader"] section{background:#0c1022;border:1px dashed #7c7af866;border-radius:15px}
hr{border-color:#ffffff15!important}
.footer{color:#777f9f;font-size:.78rem;text-align:center;padding-top:32px}
@keyframes rise{from{opacity:0;transform:translateY(15px)}to{opacity:1;transform:translateY(0)}}
@media(max-width:700px){.hero{padding:38px 0 25px}.panel{padding:17px;border-radius:18px}h1{font-size:2.7rem!important}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important}}
</style>
""", unsafe_allow_html=True)

a, b = st.columns([3, 1])
with a:
    st.markdown('<div class="brand"><span class="brand-icon">✦</span> suma <span style="color:#9ba0bd;font-weight:500">/ text intelligence</span></div>', unsafe_allow_html=True)
with b:
    st.markdown('<div style="text-align:right;padding-top:8px"><span class="pill"><span class="pulse"></span> Offline-ready</span></div>', unsafe_allow_html=True)

st.markdown('<div class="hero"><div class="eyebrow">✦ Less reading. More understanding.</div><h1>Big ideas, <span class="gradient-text">beautifully brief.</span></h1><div class="hero-copy">Turn long articles, class notes, reports, and PDFs into clear takeaways in seconds. A focused workspace for the information that matters.</div></div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
for col, label, value, desc in [
    (c1, "01 · INPUT", "Text + PDF", "Paste or upload a document"),
    (c2, "02 · CONTROL", "Your length", "Short, balanced, or detailed"),
    (c3, "03 · PRIVACY", "No API key", "Runs without an AI API"),
]:
    with col:
        st.markdown(f'<div class="stat"><div class="stat-label">{label}</div><div class="stat-value">{value}</div><div style="color:#8e96b7;font-size:.78rem;margin-top:5px">{desc}</div></div>', unsafe_allow_html=True)

st.markdown('<div class="section-kicker">Your workspace</div>', unsafe_allow_html=True)
left, right = st.columns([1.05, .95], gap="large")
with left:
    st.markdown('<div class="panel"><div class="panel-title">✍️ Bring your content</div><div class="panel-sub">Paste text below, or upload a text-based PDF.</div></div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload a PDF", type=["pdf"], help="Scanned image-only PDFs may need OCR.")
    pasted = st.text_area("Or paste your text", height=260, placeholder="Paste an article, essay, lecture notes, or report here…")
    if st.button("Try a sample text", use_container_width=True):
        st.session_state["sample_text"] = """Artificial intelligence is changing how people work, learn, and communicate. Modern AI tools can help teams analyze large amounts of information, automate repetitive tasks, and make knowledge easier to access. However, useful AI systems need clear goals, reliable data, and thoughtful human oversight.

One practical application is automatic text summarization. Students can turn lengthy reading materials into revision notes, while professionals can extract key decisions from reports and meeting documents. Summaries can save time, but they should preserve the original meaning and avoid leaving out important qualifications.

Privacy and accuracy remain essential. Users should understand where their documents are processed and verify important facts against the source. A good summarization workflow combines speed with careful review, making it easier to focus on the ideas that matter most."""
        st.rerun()
    if "sample_text" in st.session_state and not pasted and not uploaded:
        st.caption("Sample loaded — click Generate summary to use it.")
    length = st.selectbox("Summary style", ["Balanced", "Short", "Detailed"], index=0)
    bullets = st.slider("Maximum bullet points", 2, 10, 5)
    run = st.button("✦  Generate summary", use_container_width=True, type="primary")

with right:
    st.markdown('<div class="panel"><div class="panel-title">✨ Summary studio</div><div class="panel-sub">Your key points appear here, ready to use.</div>', unsafe_allow_html=True)
    if run:
        try:
            if uploaded:
                source = extract_pdf(uploaded)
            elif pasted.strip():
                source = pasted.strip()
            else:
                source = st.session_state.get("sample_text", "")
            if not source:
                st.warning("Add text or upload a PDF to get started.")
            elif len(source.split()) < 12:
                st.info("Add a little more content for a useful summary (around 12 words or more).")
                st.write(source)
            else:
                with st.spinner("Finding the key ideas…"):
                    st.session_state["last_summary"] = summarize(source, length, bullets)
                st.session_state["last_source_words"] = len(source.split())
        except Exception as exc:
            st.error(f"Could not read this file. Please try another text-based PDF. Details: {exc}")
    if st.session_state.get("last_summary"):
        points = st.session_state["last_summary"]
        for i, point in enumerate(points, 1):
            safe_point = html.escape(point)
            st.markdown(f'<div class="result-card" style="animation-delay:{i*70}ms"><div style="display:flex;gap:12px;align-items:flex-start"><span class="result-num">{i:02}</span><div class="result-text">{safe_point}</div></div></div>', unsafe_allow_html=True)
        summary_text = "\n".join(f"• {point}" for point in points)
        st.download_button("↓  Download summary (.txt)", summary_text, file_name="suma-summary.txt", mime="text/plain", use_container_width=True)
        original_words = st.session_state.get("last_source_words", 0)
        summary_words = len(summary_text.split())
        st.markdown("<hr/>", unsafe_allow_html=True)
        x, y = st.columns(2)
        with x:
            st.markdown(f'<div class="stat"><div class="stat-label">SOURCE WORDS</div><div class="stat-value">{original_words:,}</div></div>', unsafe_allow_html=True)
        with y:
            st.markdown(f'<div class="stat"><div class="stat-label">SUMMARY WORDS</div><div class="stat-value">{summary_words:,}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="border:1px dashed #7777a64d;border-radius:17px;padding:44px 22px;text-align:center;margin-top:18px;background:#ffffff03"><div style="font-size:2.4rem;margin-bottom:15px">✧</div><div style="color:#e8e9fa;font-weight:700;margin-bottom:8px">Your clarity is loading</div><div style="color:#8e96b7;font-size:.86rem;line-height:1.7">Add content on the left and generate your first summary. Key ideas will show up here.</div></div><div style="margin-top:18px;color:#8e96b7;font-size:.82rem;line-height:1.8"><div>✦ &nbsp; Extractive, offline summarization</div><div>✦ &nbsp; No account or API key required</div><div>✦ &nbsp; Export as a text file</div></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="footer">Made for focused minds · Suma Text Summarizer · No API key required</div>', unsafe_allow_html=True)
