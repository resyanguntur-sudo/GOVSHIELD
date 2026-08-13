import html
import json
from datetime import datetime

import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

# ---------------------------------------------------------
# 1. PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="GOVSHIELD AI | Legal Decision Intelligence",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# 2. CONSTANTS
# ---------------------------------------------------------
MAX_PDF_MB = 15
MAX_PDF_CHARS = 14000
MAX_QUERY_CHARS = 6000
MAX_CHAT_TURNS_SENT = 8
REQUEST_TIMEOUT_SECS = 60
MODEL_GROQ = "llama-3.3-70b-versatile"
MODEL_OPENAI = "gpt-4o-mini"

# ---------------------------------------------------------
# 3. SECRETS & CLIENT CONFIG
# ---------------------------------------------------------
try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    BASE_URL = st.secrets.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
except KeyError:
    st.error("❌ Key 'GROQ_API_KEY' was not found in .streamlit/secrets.toml!")
    st.stop()
except Exception as e:
    st.error(f"❌ Error reading secrets.toml: {e}")
    st.stop()


def sanitize_error(exc: Exception) -> str:
    msg = str(exc)
    if GROQ_KEY and GROQ_KEY in msg:
        msg = msg.replace(GROQ_KEY, "***")
    if len(msg) > 320:
        msg = msg[:320] + "…"
    return msg


def get_model_name(base_url: str) -> str:
    return MODEL_GROQ if "groq" in base_url.lower() else MODEL_OPENAI


# ---------------------------------------------------------
# 4. CUSTOM CSS STYLES
# ---------------------------------------------------------
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html { scroll-behavior: smooth; }

header[data-testid="stHeader"] {
    background: transparent !important;
    z-index: 99999 !important;
}

button[data-testid="stSidebarCollapseButton"],
button[data-testid="baseButton-headerNoPadding"] {
    background-color: rgba(10, 20, 47, 0.9) !important;
    border: 1px solid rgba(234, 179, 8, 0.6) !important;
    color: #FDE047 !important;
    border-radius: 8px !important;
    box-shadow: 0 0 12px rgba(234, 179, 8, 0.25) !important;
    transition: all 0.2s ease !important;
}

button[data-testid="stSidebarCollapseButton"]:hover,
button[data-testid="baseButton-headerNoPadding"]:hover {
    border-color: #38BDF8 !important;
    background-color: #0D1B3E !important;
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
    position: relative;
    z-index: 2;
}

.stApp {
    background-color: #040711 !important;
    background-image:
        url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800" viewBox="0 0 24 24" fill="none" stroke="rgba(234,179,8,0.035)" stroke-width="0.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v18"/><path d="M5 7h14"/><path d="M19 7l2 8H17l2-8z"/><path d="M5 7l2 8H3l2-8z"/><path d="M9 21h6"/><path d="M4 21h16"/><line x1="8" y1="3" x2="8" y2="7"/><line x1="16" y1="3" x2="16" y2="7"/></svg>'),
        radial-gradient(circle at 12% -8%, rgba(234, 179, 8, 0.16) 0%, transparent 40%),
        radial-gradient(circle at 108% 6%, rgba(56, 189, 248, 0.18) 0%, transparent 45%),
        radial-gradient(circle at 50% 105%, rgba(56, 189, 248, 0.12) 0%, transparent 60%),
        radial-gradient(circle at 50% 20%, #0F1C3F 0%, #080E21 65%, #040711 100%) !important;
    background-position: center center, 0 0, 0 0, 0 0, 0 0 !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
}

section[data-testid="stSidebar"] {
    background-color: #0A1228 !important;
    border-right: 1px solid rgba(56, 189, 248, 0.25) !important;
}
section[data-testid="stSidebar"] * {
    color: #F1F5F9 !important;
}

.floating-topleft-badge {
    position: fixed;
    top: 50px;
    left: 16px;
    z-index: 9999;
    display: flex;
    align-items: center;
    gap: 9px;
    background: rgba(8, 14, 33, 0.88);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(234, 179, 8, 0.4);
    border-radius: 999px;
    padding: 6px 16px 6px 7px;
    box-shadow: 0 4px 22px rgba(0,0,0,0.4), 0 0 14px rgba(56,189,248,0.14);
}
.floating-topleft-badge .fb-icon {
    width: 24px; height: 24px;
    border-radius: 50%;
    background: linear-gradient(135deg, #EAB308, #FDE047);
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 0 10px rgba(234,179,8,0.5);
}
.floating-topleft-badge .fb-name {
    font-family: 'Playfair Display', serif;
    font-weight: 700;
    font-size: 0.8rem;
    color: #FDE047 !important;
    letter-spacing: 0.3px;
    white-space: nowrap;
}
.floating-topleft-badge .fb-desc {
    font-size: 0.6rem;
    color: #7DD3FC !important;
    font-weight: 600;
    letter-spacing: 0.2px;
    white-space: nowrap;
}

textarea {
    background-color: #0A142F !important;
    color: #FFFFFF !important;
    font-size: 0.98rem !important;
    font-weight: 500 !important;
    border: 1.5px solid #38BDF8 !important;
    border-radius: 12px !important;
    padding: 14px !important;
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.25) !important;
}
textarea:focus {
    border-color: #FDE047 !important;
    box-shadow: 0 0 22px rgba(253, 224, 71, 0.4) !important;
    background-color: #0D1B3E !important;
}

.header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
    padding: 0 0 12px 0;
    width: 100%;
}

.gold-shield-logo {
    background: linear-gradient(135deg, rgba(234, 179, 8, 0.25) 0%, rgba(15, 28, 63, 0.9) 100%);
    padding: 12px;
    border-radius: 16px;
    border: 1.5px solid #FDE047;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 20px rgba(234, 179, 8, 0.4);
}

.lexis-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(1.4rem, 4.2vw, 2.4rem);
    font-weight: 800;
    letter-spacing: 1px;
    background: linear-gradient(120deg, #FFFFFF 0%, #FDE047 42%, #EAB308 55%, #FFFFFF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    text-transform: uppercase;
}

.top-right-badge {
    background: rgba(14, 26, 56, 0.85);
    border: 1px solid rgba(56, 189, 248, 0.4);
    border-radius: 10px;
    padding: 8px 16px;
    text-align: right;
}
.top-right-badge .brand-name { font-size: 0.95rem; font-weight: 800; color: #FDE047 !important; }
.top-right-badge .brand-desc { font-size: 0.75rem; color: #38BDF8 !important; font-weight: 600; }

.letterhead-divider {
    display: flex; align-items: center; gap: 14px; margin: 6px 0 22px 0;
}
.letterhead-divider .lh-line {
    flex: 1; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(234, 179, 8, 0.75), rgba(56, 189, 248, 0.6), transparent);
}

.lexis-divider {
    height: 1px;
    background: linear-gradient(90deg, rgba(56, 189, 248, 0.8) 0%, rgba(234, 179, 8, 0.5) 50%, transparent 100%);
    margin: 8px 0 20px 0;
}

div.stButton > button {
    background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%) !important;
    color: #FFFFFF !important;
    font-weight: 800 !important;
    font-size: 0.95rem !important;
    border: 1px solid #38BDF8 !important;
    border-radius: 10px !important;
    padding: 14px 28px !important;
    box-shadow: 0 0 20px rgba(56, 189, 248, 0.4) !important;
    width: 100% !important;
    text-transform: uppercase;
}
div.stButton > button:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 6px 26px rgba(56, 189, 248, 0.55) !important;
    border-color: #FDE047 !important;
}

.stDownloadButton > button {
    background: linear-gradient(135deg, #EAB308 0%, #CA8A04 100%) !important;
    color: #0A1228 !important;
    font-weight: 800 !important;
    border: none !important;
    border-radius: 10px !important;
}

.lexis-card-cyan {
    background: rgba(14, 26, 56, 0.85);
    border: 1px solid rgba(56, 189, 248, 0.4);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
    color: #F1F5F9 !important;
}

.lexis-card-gold {
    background: rgba(14, 26, 56, 0.85);
    border: 1px solid rgba(234, 179, 8, 0.4);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
    color: #F1F5F9 !important;
}

.card-title-cyan { font-size: 0.85rem; font-weight: 800; color: #38BDF8 !important; margin-bottom: 10px; }
.card-title-gold { font-size: 0.85rem; font-weight: 800; color: #FDE047 !important; margin-bottom: 10px; }

.badge-supported { background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; color: #34D399 !important; padding: 14px 20px; border-radius: 10px; font-weight: 700; }
.badge-review { background: rgba(234, 179, 8, 0.15); border: 1px solid #EAB308; color: #FDE047 !important; padding: 14px 20px; border-radius: 10px; font-weight: 700; }
.badge-rejected { background: rgba(239, 68, 68, 0.15); border: 1px solid #EF4444; color: #F87171 !important; padding: 14px 20px; border-radius: 10px; font-weight: 700; }

.robot-welcome-card {
    background: linear-gradient(135deg, rgba(10, 20, 47, 0.95) 0%, rgba(15, 28, 63, 0.95) 100%);
    border: 1.5px solid #FDE047;
    border-radius: 20px;
    padding: 30px;
    text-align: center;
    box-shadow: 0 0 35px rgba(234, 179, 8, 0.25);
    margin-bottom: 25px;
}
</style>
""", unsafe_allow_html=True)

# FLOATING BADGE
st.markdown("""<div class="floating-topleft-badge">
    <div class="fb-icon">⚖️</div>
    <div class="fb-text">
        <div class="fb-name">GovShield AI</div>
        <div class="fb-desc">Evidence-First Legal Intelligence</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. HEADER
# ---------------------------------------------------------
st.markdown("""<div class="header-container">
<div style="display: flex; align-items: center; gap: 16px;">
<div class="gold-shield-logo">⚖️</div>
<div>
<h1 class="lexis-title">GOVSHIELD AI</h1>
<div style="color: #94A3B8; font-size: 0.85rem;">Evidence-First Legal &amp; Regulatory Intelligence Engine</div>
</div>
</div>
<div class="top-right-badge">
<div class="brand-name">🛡️ GOVSHIELD AI v3.1</div>
<div class="brand-desc">Global Legal Analysis System</div>
</div>
</div>
<div class="letterhead-divider"><span class="lh-line"></span></div>""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. GROUNDED KNOWLEDGE BASE
# ---------------------------------------------------------
BUILTIN_KNOWLEDGE_BASE = """
[BUILT-IN GROUNDED KNOWLEDGE BASE: CONSTITUTION & LEGAL HIERARCHY]
1. 1945 CONSTITUTION OF THE REPUBLIC OF INDONESIA (UUD 1945 - Amendments I-IV):
   - Article 1 (3): Indonesia is a constitutional state governed by the rule of law.
   - Article 28D (1): Guarantee of fair legal certainty and equal treatment before the law.
   - Article 31: Human Rights & Right to Education.
2. STATUTORY HIERARCHY (Act No. 12/2011 & Act No. 13/2022):
   - 1945 Constitution (UUD 1945) > TAP MPR > Acts/Laws (UU) / Perppu > Government Regulations (PP) > Presidential Regulations (Perpres) > Regional Decrees.
3. FUNDAMENTAL LEGAL PRINCIPLES:
   - Lex Specialis Derogat Legi Generali: Specific laws override general laws.
   - Lex Superior Derogat Legi Inferiori: Higher ranking laws override lower ranking laws.
"""

# ---------------------------------------------------------
# 7. INITIALIZE SESSION STATE
# ---------------------------------------------------------
_defaults = {
    "pdf_text": "",
    "pdf_name": "",
    "pdf_signature": "",
    "robot_dismissed": False,
    "analysis_result": None,
    "chat_history": [],
    "uploader_key": 0,
    "processing": False,
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ---------------------------------------------------------
# 8. SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""<div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; padding: 12px; border-radius: 10px; margin-bottom: 16px;">
<b style="color:#34D399; font-size:0.88rem;">⚡ SECRETS CONNECTED</b><br>
<span style="font-size:0.75rem; color:#94A3B8;">GROQ API Key Authenticated</span>
</div>""", unsafe_allow_html=True)

    reg_scope = st.selectbox(
        "Choose Analysis Scope",
        [
            "🏛️ Macro (National Level - UUD 1945 & Acts)",
            "🎓 Meso (Institutional / Campus Policy)",
            "⚖️ Harmonization (National vs Local Alignment)"
        ],
        index=2
    )

    st.markdown('<div class="lexis-divider"></div>', unsafe_allow_html=True)

    if st.button("🗑️ RESET WORKSPACE DATA", disabled=st.session_state["processing"]):
        st.session_state["pdf_text"] = ""
        st.session_state["pdf_name"] = ""
        st.session_state["pdf_signature"] = ""
        st.session_state["analysis_result"] = None
        st.session_state["chat_history"] = []
        st.session_state["robot_dismissed"] = False
        st.session_state["uploader_key"] += 1
        st.rerun()

    st.caption("🛡️ **GovShield Intelligence Engine v3.1**")

# ---------------------------------------------------------
# 9. WELCOME OVERLAY
# ---------------------------------------------------------
if not st.session_state["robot_dismissed"]:
    st.markdown("""
    <div class="robot-welcome-card">
        <h2 style="font-family:'Playfair Display', serif; color:#FDE047; margin:0 0 8px 0;">Welcome to GovShield AI Legal Assistant</h2>
        <p style="color:#CBD5E1; font-size:0.95rem; max-width:650px; margin:0 auto 18px auto;">
            Automated Legal & Policy Intelligence Assistant using evidence-first grounded reasoning.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 LAUNCH LEGAL ANALYSIS WORKSPACE"):
        st.session_state["robot_dismissed"] = True
        st.rerun()

# ---------------------------------------------------------
# 10. FORM INPUTS
# ---------------------------------------------------------
st.markdown(f"📄 **OPTIONAL: SPECIFIC POLICY / PDF DOCUMENT ATTACHMENT (max {MAX_PDF_MB}MB)**")

uploaded_file = st.file_uploader(
    "Upload Policy or Contract PDF",
    type=["pdf"],
    label_visibility="collapsed",
    key=f"pdf_uploader_{st.session_state['uploader_key']}",
)

if uploaded_file is not None:
    st.session_state["robot_dismissed"] = True
    file_signature = f"{uploaded_file.name}:{uploaded_file.size}"

    if st.session_state["pdf_signature"] != file_signature:
        if uploaded_file.size > MAX_PDF_MB * 1024 * 1024:
            st.error(f"❌ File size exceeds {MAX_PDF_MB}MB limit.")
        else:
            with st.spinner("Extracting PDF document..."):
                try:
                    reader = PdfReader(uploaded_file)
                    if reader.is_encrypted:
                        st.error("❌ PDF is encrypted.")
                    else:
                        extracted_text = ""
                        for page in reader.pages:
                            text = page.extract_text()
                            if text:
                                extracted_text += text + "\n"

                        if not extracted_text.strip():
                            st.warning("⚠️ No extractable text found in PDF.")

                        st.session_state["pdf_text"] = extracted_text
                        st.session_state["pdf_name"] = uploaded_file.name
                        st.session_state["pdf_signature"] = file_signature
                except Exception:
                    st.error("❌ Failed to process PDF.")

    if st.session_state["pdf_name"]:
        st.success(f"✓ Active Document: {st.session_state['pdf_name']}")
else:
    st.session_state["pdf_text"] = ""
    st.session_state["pdf_name"] = ""
    st.session_state["pdf_signature"] = ""

st.markdown("❓ **POLICY INQUIRY / CASE SCENARIO / LEGAL QUERY (REQUIRED)**")

user_query = st.text_area(
    "Type your legal inquiry",
    placeholder="Type your policy scenario or regulatory questions here...",
    height=140,
    label_visibility="collapsed",
    key=f"query_input_{st.session_state['uploader_key']}"
)

if user_query.strip():
    st.session_state["robot_dismissed"] = True

_char_count = len(user_query)
st.caption(f"{_char_count:,}/{MAX_QUERY_CHARS:,} characters")

# ---------------------------------------------------------
# 11. REASONING ENGINE EXECUTION
# ---------------------------------------------------------
run_clicked = st.button("RUN GOVSHIELD LEGAL INTELLIGENCE ANALYSIS", disabled=st.session_state["processing"])

if run_clicked:
    st.session_state["robot_dismissed"] = True
    query_clean = user_query.strip()

    if not query_clean:
        st.warning("⚠️ Please enter a legal inquiry before proceeding.")
    elif len(query_clean) > MAX_QUERY_CHARS:
        st.warning(f"⚠️ Your inquiry is too long ({len(query_clean):,}/{MAX_QUERY_CHARS:,} characters).")
    else:
        st.session_state["processing"] = True
        try:
            with st.spinner("Analyzing legal hierarchy & cross-referencing provisions..."):
                combined_context = f"{BUILTIN_KNOWLEDGE_BASE}\n[SELECTED REGULATORY SCOPE]: {reg_scope}\n"

                # PARAGRAPH-SAFE TRUNCATION
                if st.session_state["pdf_text"]:
                    pdf_full = st.session_state["pdf_text"]
                    if len(pdf_full) > MAX_PDF_CHARS:
                        truncated_text = pdf_full[:MAX_PDF_CHARS].rsplit('\n', 1)[0]
                        combined_context += f"\n[ATTACHED USER DOCUMENT / PDF]:\n{truncated_text}\n"
                        st.info(f"ℹ️ Attached PDF truncated neatly at paragraph boundary ({len(truncated_text):,} chars).")
                    else:
                        combined_context += f"\n[ATTACHED USER DOCUMENT / PDF]:\n{pdf_full}\n"

                client = OpenAI(
                    api_key=GROQ_KEY,
                    base_url=BASE_URL,
                    timeout=REQUEST_TIMEOUT_SECS,
                    max_retries=2,
                )

                system_prompt = """
You are GOVSHIELD AI, an evidence-first enterprise Legal & Regulatory Intelligence Assistant.

CORE MANDATES:
1. Analyze legal hierarchy based on user scope.
2. Apply Lex Specialis Derogat Legi Generali and Lex Superior Derogat Legi Inferiori.
3. Distinguish between General Provisions and Exceptions.
4. Provide direct EVIDENCE quotes from UUD 1945 or uploaded PDF.
5. IF NO EVIDENCE EXISTS, SET STATUS AS "REQUIRES HUMAN REVIEW". DO NOT HALLUCINATE.
6. RESPOND ENTIRELY IN ENGLISH.

OUTPUT FORMAT (JSON ONLY):
{
  "recommendation_status": "SUPPORTED" | "NOT SUPPORTED" | "REQUIRES HUMAN REVIEW",
  "recommendation_summary": "Executive summary in English",
  "applicable_rule": "The final governing legal rule or supreme principle",
  "evidence": "Direct textual quote or clause citation",
  "rule_analysis": {
    "general_provision": "General rule identified",
    "specific_provision": "Specific rule or exception identified",
    "exception_detected": true | false,
    "unresolved_conflict": true | false
  },
  "reasoning_conclusion": "Detailed step-by-step legal reasoning",
  "review_note": "Critical analysis note for legal counsel"
}
"""

                user_prompt = f"GROUNDED KNOWLEDGE & DOCUMENTS:\n---\n{combined_context}\n---\nINQUIRY:\n{query_clean}"
                model_name = get_model_name(BASE_URL)

                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"},
                )

                if response and response.choices and response.choices[0].message.content:
                    content = response.choices[0].message.content
                    st.session_state["analysis_result"] = json.loads(content)
                else:
                    st.error("❌ Model returned an empty analysis.")
        except json.JSONDecodeError:
            st.error("❌ Invalid JSON response format from AI.")
        except Exception as e:
            st.error(f"❌ Technical error: {sanitize_error(e)}")
        finally:
            st.session_state["processing"] = False

# ---------------------------------------------------------
# 12. RESULTS WORKSPACE
# ---------------------------------------------------------
if st.session_state["analysis_result"]:
    result = st.session_state["analysis_result"]
    ra = result.get("rule_analysis") or {}

    st.markdown('<div class="lexis-divider"></div>', unsafe_allow_html=True)
    st.markdown("### ⚖️ GOVSHIELD INTELLIGENCE ANALYSIS DASHBOARD")

    status = str(result.get("recommendation_status", "REQUIRES HUMAN REVIEW"))
    summary = html.escape(str(result.get("recommendation_summary", "")))

    if status == "SUPPORTED":
        st.markdown(f'<div class="badge-supported">✅ RECOMMENDATION: SUPPORTED — {summary}</div>', unsafe_allow_html=True)
    elif status == "NOT SUPPORTED":
        st.markdown(f'<div class="badge-rejected">❌ RECOMMENDATION: NOT SUPPORTED — {summary}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="badge-review">⚠️ STATUS: REQUIRES HUMAN REVIEW — Insufficient Direct Evidence</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Executive Summary & Evidence",
        "⚖️ Statutory Structure & Legal Reasoning",
        "💬 Interactive Follow-up Q&A Assistant",
        "📥 Export Executive Legal Brief"
    ])

    applicable_rule = html.escape(str(result.get('applicable_rule', '-')))
    evidence_text = html.escape(str(result.get('evidence', 'No direct text excerpt available')))
    reasoning = html.escape(str(result.get('reasoning_conclusion', '-')))
    review_note = html.escape(str(result.get('review_note', 'N/A')))
    gen_prov = html.escape(str(ra.get('general_provision', '-')))
    spec_prov = html.escape(str(ra.get('specific_provision', '-')))

    with tab1:
        r_col1, r_col2 = st.columns(2, gap="medium")
        with r_col1:
            st.markdown(f"""
            <div class="lexis-card-gold">
                <div class="card-title-gold">⚖️ GOVERNING / APPLICABLE RULE</div>
                <div style="font-size:0.95rem; line-height:1.6; color:#F1F5F9;">{applicable_rule}</div>
            </div>
            """, unsafe_allow_html=True)
        with r_col2:
            st.markdown(f"""
            <div class="lexis-card-cyan">
                <div class="card-title-cyan">📌 CITATION & DIRECT LEGAL EVIDENCE EXCERPT</div>
                <div style="font-size:0.95rem; line-height:1.6; color:#F1F5F9;">{evidence_text}</div>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        exc_str = 'YES' if ra.get('exception_detected') else 'NO'
        conf_str = 'YES' if ra.get('unresolved_conflict') else 'NO'

        st.markdown(f"""
        <div class="lexis-card-cyan">
            <div class="card-title-cyan">📊 REGULATORY HIERARCHY & NORMA ANALYSIS</div>
            <div style="font-size:0.95rem; line-height:1.6; color:#F1F5F9;">
                <b>General Provision:</b> {gen_prov}<br>
                <b>Specific Exception:</b> {spec_prov}<br>
                <b>Exception Detected:</b> {exc_str}<br>
                <b>Normative Conflict:</b> {conf_str}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="lexis-card-gold">
            <div class="card-title-gold">📝 DETAILED LEGAL RATIONALE & CONCLUSION</div>
            <div style="font-size:0.95rem; line-height:1.6; color:#F1F5F9;">
                {reasoning}<br><br>
                💡 <b>Counsel Advisory Note:</b> {review_note}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        st.markdown("### 💬 Interactive Legal Q&A Assistant")

        for msg in st.session_state["chat_history"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        chat_input = st.chat_input("Ask a follow-up question regarding this case...")
        if chat_input:
            chat_input = chat_input.strip()[:MAX_QUERY_CHARS]
            st.session_state["chat_history"].append({"role": "user", "content": chat_input})
            with st.chat_message("user"):
                st.markdown(chat_input)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing follow-up..."):
                    try:
                        chat_client = OpenAI(
                            api_key=GROQ_KEY,
                            base_url=BASE_URL,
                            timeout=REQUEST_TIMEOUT_SECS,
                            max_retries=2,
                        )

                        # TRIM HISTORIES FOR SAFETY
                        followup_messages = [
                            {"role": "system", "content": f"You are GovShield AI Legal Assistant. Answer strictly based on this context: {json.dumps(result)}"},
                        ] + st.session_state["chat_history"][-MAX_CHAT_TURNS_SENT:]

                        chat_res = chat_client.chat.completions.create(
                            model=get_model_name(BASE_URL),
                            messages=followup_messages,
                            temperature=0.1,
                        )

                        if chat_res and chat_res.choices and chat_res.choices[0].message.content:
                            chat_ans = chat_res.choices[0].message.content
                            st.markdown(chat_ans)
                            st.session_state["chat_history"].append({"role": "assistant", "content": chat_ans})
                        else:
                            st.error("❌ Empty response received from assistant.")
                    except Exception as err:
                        st.error(f"❌ Chat error: {sanitize_error(err)}")

    with tab4:
        st.markdown("### 📥 Download Formal Legal Determination Brief")
        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_text = f"""================================================================================
GOVSHIELD AI - FORMAL LEGAL & REGULATORY DETERMINATION REPORT
================================================================================
Generated: {generated_at}
Status: {status}
Regulatory Scope: {reg_scope}
Attached Document: {st.session_state['pdf_name'] or 'None'}

EXECUTIVE SUMMARY:
{result.get('recommendation_summary') or '-'}

GOVERNING / APPLICABLE LEGAL RULE:
{result.get('applicable_rule') or '-'}

DIRECT LEGAL EVIDENCE & CITATION:
{result.get('evidence') or '-'}

REGULATORY NORMA ANALYSIS:
- General Provision: {ra.get('general_provision') or '-'}
- Specific Provision / Exception: {ra.get('specific_provision') or '-'}
- Exception Detected: {ra.get('exception_detected')}
- Conflict Detected: {ra.get('unresolved_conflict')}

DETAILED LEGAL RATIONALE:
{result.get('reasoning_conclusion') or '-'}

LEGAL COUNSEL ADVISORY NOTE:
{result.get('review_note') or '-'}
================================================================================
"""
        st.download_button(
            label="📄 DOWNLOAD FORMAL LEGAL REPORT (.TXT)",
            data=report_text,
            file_name="GovShield_Executive_Legal_Brief.txt",
            mime="text/plain"
        )

# ---------------------------------------------------------
# 13. FOOTER
# ---------------------------------------------------------
st.markdown('<div class="lexis-divider"></div>', unsafe_allow_html=True)
st.caption("⚖️ GovShield AI provides AI-generated legal analysis for informational purposes only. Session data stays in memory.")
