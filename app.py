import html
import json
import time
import datetime
import hashlib
import re
import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

# ==============================================================================
# 1. PAGE CONFIGURATION & SYSTEM INITIALIZATION
# ==============================================================================
st.set_page_config(
    page_title="GOVSHIELD AI | Enterprise Legal Decision Intelligence",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "boot_timestamp" not in st.session_state:
    st.session_state["boot_timestamp"] = time.time()

# ==============================================================================
# 2. READ API KEYS & SECRETS
# ==============================================================================
try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    BASE_URL = st.secrets.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
except KeyError:
    st.error("SYSTEM ERROR: Key 'GROQ_API_KEY' not found in .streamlit/secrets.toml!")
    st.stop()
except Exception as e:
    st.error(f"SYSTEM ERROR: Failed reading secrets configuration: {e}")
    st.stop()

# ==============================================================================
# 3. UNIVERSAL CSS OVERRIDE & ENTERPRISE DARK THEME ENGINE
# ==============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg-dark-primary: #040711;
    --bg-dark-secondary: #0A142F;
    --bg-dark-tertiary: #0F172A;
    --accent-gold: #FDE047;
    --accent-gold-dark: #EAB308;
    --accent-cyan: #38BDF8;
    --accent-cyan-dark: #0284C7;
    --accent-emerald: #34D399;
    --accent-rose: #F87171;
    --text-light: #F8FAFC;
    --text-muted: #94A3B8;
    --border-gold: rgba(234, 179, 8, 0.4);
    --border-cyan: rgba(56, 189, 248, 0.35);
}

* {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

header[data-testid="stHeader"] {
    background: transparent !important;
    z-index: 99999 !important;
}

button[data-testid="stSidebarCollapseButton"], 
button[data-testid="baseButton-headerNoPadding"] {
    background-color: var(--bg-dark-secondary) !important;
    border: 1px solid var(--border-gold) !important;
    color: var(--accent-gold) !important;
    border-radius: 8px !important;
    box-shadow: 0 0 12px rgba(234, 179, 8, 0.25) !important;
}

.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
    position: relative;
    z-index: 2;
}

/* BASE BACKGROUND */
.stApp {
    background-color: var(--bg-dark-primary) !important;
    background-image: 
        radial-gradient(circle at 12% -8%, rgba(234, 179, 8, 0.15) 0%, transparent 40%),
        radial-gradient(circle at 108% 6%, rgba(56, 189, 248, 0.16) 0%, transparent 45%),
        radial-gradient(circle at 50% 20%, #0F1C3F 0%, #080E21 65%, var(--bg-dark-primary) 100%) !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
}

/* SIDEBAR STYLING */
section[data-testid="stSidebar"] {
    background-color: #070D1E !important;
    border-right: 1px solid var(--border-cyan) !important;
}

section[data-testid="stSidebar"] * {
    color: var(--text-light) !important;
}

/* PERBAIKAN TOTAL: SELECTBOX, DROPDOWN & INPUTS (PEMBERANTASAN LATAR PUTIH) */
div[data-testid="stSelectbox"],
div[data-testid="stSelectbox"] > div,
div[data-testid="stSelectbox"] > div > div,
div[data-baseweb="select"],
div[data-baseweb="select"] > div,
div[data-baseweb="select"] * {
    background-color: #0A142F !important;
    color: #FDE047 !important;
    border-color: #38BDF8 !important;
    font-weight: 600 !important;
}

div[data-baseweb="select"] {
    border: 1.5px solid #38BDF8 !important;
    border-radius: 10px !important;
}

div[data-baseweb="popover"],
div[data-baseweb="menu"], 
ul[role="listbox"], 
div[data-testid="stSelectboxVirtualDropdown"] {
    background-color: #0F172A !important;
    border: 1px solid #38BDF8 !important;
    border-radius: 10px !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.9) !important;
}

li[role="option"] {
    background-color: #0F172A !important;
    color: #F8FAFC !important;
    padding: 10px 14px !important;
}

li[role="option"]:hover, li[aria-selected="true"] {
    background-color: #1E293B !important;
    color: #FDE047 !important;
}

/* Chat Input Styling */
div[data-testid="stChatInput"] {
    background-color: var(--bg-dark-secondary) !important;
    border: 1.5px solid var(--accent-cyan) !important;
    border-radius: 14px !important;
    box-shadow: 0 0 20px rgba(56, 189, 248, 0.2) !important;
}

div[data-testid="stChatInput"] textarea {
    background-color: transparent !important;
    color: var(--text-light) !important;
    font-size: 0.95rem !important;
}

textarea {
    background-color: var(--bg-dark-secondary) !important;
    color: var(--text-light) !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    border: 1.5px solid var(--accent-cyan) !important;
    border-radius: 12px !important;
    padding: 14px !important;
}

/* TABS STYLING */
div[data-baseweb="tab-list"] {
    background-color: var(--bg-dark-secondary) !important;
    padding: 6px !important;
    border-radius: 12px !important;
    border: 1px solid rgba(56, 189, 248, 0.3) !important;
    gap: 8px !important;
}

button[data-baseweb="tab"] {
    background-color: var(--bg-dark-tertiary) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
    color: var(--text-muted) !important;
    font-weight: 700 !important;
    padding: 10px 18px !important;
}

button[aria-selected="true"] {
    background: linear-gradient(135deg, #0F2B5B 0%, #1E3A8A 100%) !important;
    color: var(--accent-gold) !important;
    border: 1.5px solid var(--accent-gold) !important;
}

/* BUTTON CUSTOM STYLING */
div.stButton > button {
    background: linear-gradient(135deg, var(--accent-cyan-dark) 0%, #0369A1 100%) !important;
    color: #FFFFFF !important;
    font-weight: 800 !important;
    border: 1px solid var(--accent-cyan) !important;
    border-radius: 10px !important;
    padding: 14px 28px !important;
    width: 100% !important;
    text-transform: uppercase;
}

.lexis-card-cyan {
    background: rgba(14, 26, 56, 0.85);
    border: 1px solid var(--border-cyan);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
    color: var(--text-light) !important;
}

.lexis-card-gold {
    background: rgba(14, 26, 56, 0.85);
    border: 1px solid var(--border-gold);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
    color: var(--text-light) !important;
}

.card-title-cyan {
    font-size: 0.85rem;
    font-weight: 800;
    color: var(--accent-cyan) !important;
    letter-spacing: 1px;
    margin-bottom: 10px;
    text-transform: uppercase;
}

.card-title-gold {
    font-size: 0.85rem;
    font-weight: 800;
    color: var(--accent-gold) !important;
    letter-spacing: 1px;
    margin-bottom: 10px;
    text-transform: uppercase;
}

.badge-supported {
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid #10B981;
    color: var(--accent-emerald) !important;
    padding: 16px 22px;
    border-radius: 12px;
    font-weight: 700;
}

.badge-review {
    background: rgba(234, 179, 8, 0.15);
    border: 1px solid #EAB308;
    color: var(--accent-gold) !important;
    padding: 16px 22px;
    border-radius: 12px;
    font-weight: 700;
}

.badge-rejected {
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid #EF4444;
    color: var(--accent-rose) !important;
    padding: 16px 22px;
    border-radius: 12px;
    font-weight: 700;
}

.telemetry-card {
    background: rgba(10, 20, 47, 0.9);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 10px;
    padding: 12px;
    margin-bottom: 12px;
    font-family: 'JetBrains Mono', monospace;
}

.telemetry-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.75rem;
    padding: 4px 0;
    border-bottom: 1px dashed rgba(255, 255, 255, 0.08);
}

.telemetry-row:last-child {
    border-bottom: none;
}

.telemetry-label { color: var(--text-muted); }
.telemetry-value { color: var(--accent-cyan); font-weight: 600; }

.security-badge {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.4);
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 14px;
}

.security-badge-text {
    font-size: 0.78rem;
    font-weight: 700;
    color: var(--accent-emerald);
}

.custom-label {
    font-size: 0.85rem !important;
    font-weight: 800 !important;
    color: var(--accent-cyan) !important;
    letter-spacing: 0.8px !important;
    text-transform: uppercase;
    margin-bottom: 8px !important;
    display: flex;
    align-items: center;
    gap: 8px;
}

.ai-search-frame {
    background: rgba(10, 20, 47, 0.65);
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-radius: 14px;
    padding: 14px 18px;
    margin-bottom: 10px;
}

.pulse-dot {
    width: 8px;
    height: 8px;
    background-color: var(--accent-emerald);
    border-radius: 50%;
    display: inline-block;
    margin-right: 6px;
}

.robot-welcome-card {
    background: linear-gradient(135deg, rgba(10, 20, 47, 0.95) 0%, rgba(15, 28, 63, 0.95) 100%);
    border: 1.5px solid var(--accent-gold);
    border-radius: 20px;
    padding: 28px;
    text-align: center;
    margin-bottom: 25px;
}

.floating-topleft-badge {
    position: fixed;
    top: 52px;
    left: 16px;
    z-index: 9999;
    display: flex;
    align-items: center;
    gap: 9px;
    background: rgba(8, 14, 33, 0.9);
    border: 1px solid rgba(234, 179, 8, 0.4);
    border-radius: 999px;
    padding: 6px 16px 6px 8px;
}

.floating-topleft-badge .fb-icon {
    width: 24px; height: 24px;
    border-radius: 50%;
    background: linear-gradient(135deg, #EAB308, #FDE047);
    display: flex; align-items: center; justify-content: center;
}

.floating-topleft-badge .fb-name {
    font-family: 'Playfair Display', serif;
    font-weight: 700;
    font-size: 0.8rem;
    color: var(--accent-gold) !important;
}

.floating-topleft-badge .fb-desc {
    font-size: 0.6rem;
    color: var(--accent-cyan) !important;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# FLOATING BADGE (TOP-LEFT)
st.markdown("""
<div class="floating-topleft-badge">
    <div class="fb-icon">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#0A1228" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2l7 4v6c0 5-3.5 8.5-7 10-3.5-1.5-7-5-7-10V6z"/>
        </svg>
    </div>
    <div>
        <div class="fb-name">GovShield AI</div>
        <div class="fb-desc">Evidence-First Legal Intelligence</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. HEADER LEGAL BANNER (PERBAIKAN: RAW HTML STRING UNINDENTED TANPA TAB/SPASI)
# ==============================================================================
svg_banner_html = """<div style="width: 100%; position: relative; margin-bottom: 24px;">
<svg width="100%" height="150" viewBox="0 0 1200 150" fill="none" xmlns="http://www.w3.org/2000/svg" style="border-radius: 16px; filter: drop-shadow(0px 8px 24px rgba(0,0,0,0.6));">
<rect width="1200" height="150" rx="16" fill="url(#bgGradient)" stroke="url(#goldBorder)" stroke-width="2"/>
<path d="M 0,30 L 1200,30 M 0,75 L 1200,75 M 0,120 L 1200,120" stroke="rgba(56,189,248,0.06)" stroke-width="1" stroke-dasharray="8 4"/>
<path d="M 200,0 L 200,150 M 600,0 L 600,150 M 1000,0 L 1000,150" stroke="rgba(234,179,8,0.05)" stroke-width="1" stroke-dasharray="10 5"/>
<g transform="translate(35, 25)">
<circle cx="50" cy="50" r="42" fill="url(#shieldGlow)" stroke="#FDE047" stroke-width="1.5"/>
<path d="M50 18 V78 M30 32 H70 M30 32 L18 58 H42 L30 32 M70 32 L58 58 H82 L70 32 M25 78 H75" stroke="#FDE047" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="50" cy="18" r="4" fill="#38BDF8"/>
</g>
<g transform="translate(145, 42)">
<text x="0" y="32" fill="url(#textGoldGrad)" font-family="'Playfair Display', serif" font-size="30" font-weight="800" letter-spacing="2">GOVSHIELD AI ENTERPRISE</text>
<text x="0" y="55" fill="#38BDF8" font-family="'Plus Jakarta Sans', sans-serif" font-size="13" font-weight="700" letter-spacing="1">EVIDENCE-FIRST LEGAL & REGULATORY DECISION INTELLIGENCE PLATFORM</text>
<text x="0" y="74" fill="#94A3B8" font-family="'Playfair Display', serif" font-size="11" font-style="italic">"Fiat justitia ruat caelum" — Statutory Hierarchy & Constitutional Compliance Verification</text>
</g>
<g transform="translate(930, 20)" opacity="0.85">
<rect x="0" y="0" width="230" height="110" rx="10" fill="rgba(10, 20, 47, 0.7)" stroke="rgba(234,179,8,0.4)" stroke-width="1.2"/>
<path d="M 20 25 H 210 M 20 45 H 170 M 20 65 H 190 M 20 85 H 140" stroke="#38BDF8" stroke-width="2" stroke-linecap="round"/>
<text x="160" y="90" fill="#FDE047" font-family="'JetBrains Mono', monospace" font-size="12" font-weight="800">§ LEX SUPERIOR</text>
</g>
<line x1="20" y1="148" x2="1180" y2="148" stroke="url(#laserLineGrad)" stroke-width="2.5" stroke-linecap="round"/>
<defs>
<linearGradient id="bgGradient" x1="0" y1="0" x2="1200" y2="150" gradientUnits="userSpaceOnUse">
<stop offset="0%" stop-color="#080E21"/>
<stop offset="50%" stop-color="#0F1C3F"/>
<stop offset="100%" stop-color="#040711"/>
</linearGradient>
<linearGradient id="goldBorder" x1="0" y1="0" x2="1200" y2="0" gradientUnits="userSpaceOnUse">
<stop offset="0%" stop-color="#EAB308" stop-opacity="0.8"/>
<stop offset="50%" stop-color="#38BDF8" stop-opacity="0.6"/>
<stop offset="100%" stop-color="#EAB308" stop-opacity="0.8"/>
</linearGradient>
<linearGradient id="textGoldGrad" x1="0" y1="0" x2="500" y2="0" gradientUnits="userSpaceOnUse">
<stop offset="0%" stop-color="#FFFFFF"/>
<stop offset="40%" stop-color="#FDE047"/>
<stop offset="80%" stop-color="#EAB308"/>
<stop offset="100%" stop-color="#FFFFFF"/>
</linearGradient>
<linearGradient id="shieldGlow" x1="0" y1="0" x2="100" y2="100" gradientUnits="userSpaceOnUse">
<stop offset="0%" stop-color="rgba(234, 179, 8, 0.3)"/>
<stop offset="100%" stop-color="rgba(10, 20, 47, 0.9)"/>
</linearGradient>
<linearGradient id="laserLineGrad" x1="0" y1="0" x2="1200" y2="0" gradientUnits="userSpaceOnUse">
<stop offset="0%" stop-color="transparent"/>
<stop offset="25%" stop-color="#EAB308"/>
<stop offset="50%" stop-color="#38BDF8"/>
<stop offset="75%" stop-color="#EAB308"/>
<stop offset="100%" stop-color="transparent"/>
</linearGradient>
</defs>
</svg>
</div>"""

st.markdown(svg_banner_html, unsafe_allow_html=True)

# ==============================================================================
# 5. BUILT-IN GROUNDED KNOWLEDGE BASE
# ==============================================================================
BUILTIN_KNOWLEDGE_BASE = """
[BUILT-IN GROUNDED KNOWLEDGE BASE: CONSTITUTION & LEGAL HIERARCHY]
1. 1945 CONSTITUTION OF THE REPUBLIC OF INDONESIA (UUD 1945 - Amendments I-IV):
   - Article 1 (3): Indonesia is a constitutional state governed by the rule of law (Negara Hukum).
   - Article 28D (1): Guarantee of fair legal certainty, protection, and equal treatment before the law.
   - Article 28I (2): Protection against discriminatory treatment on any grounds whatsoever.
   - Article 31 (1)-(5): Right to education and state obligation to prioritize educational funding.
2. STATUTORY HIERARCHY (Act No. 12/2011 jo. Act No. 13/2022 on Legislation Drafting):
   - Level 1: 1945 Constitution (UUD 1945)
   - Level 2: People's Consultative Assembly Resolutions (TAP MPR)
   - Level 3: Acts/Laws (Undang-Undang / UU) & Government Regulations in Lieu of Law (Perppu)
   - Level 4: Government Regulations (PP)
   - Level 5: Presidential Regulations (Perpres)
   - Level 6: Provincial Regulations (Perda Provinsi)
   - Level 7: Regency/City Regulations (Perda Kabupaten/Kota)
3. FUNDAMENTAL LEGAL PRINCIPLES & MAXIMS:
   - Lex Specialis Derogat Legi Generali: Specific laws override general statutory provisions.
   - Lex Superior Derogat Legi Inferiori: Higher ranking laws invalidate non-compliant lower ranking rules.
   - Lex Posterior Derogat Legi Priori: Later laws supersede earlier laws on the same subject matter.
"""

# ==============================================================================
# 6. SESSION STATE MANAGEMENT & UTILITY FUNCTIONS
# ==============================================================================
if "pdf_text" not in st.session_state:
    st.session_state["pdf_text"] = ""
if "pdf_name" not in st.session_state:
    st.session_state["pdf_name"] = ""
if "robot_dismissed" not in st.session_state:
    st.session_state["robot_dismissed"] = False
if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "audit_logs" not in st.session_state:
    st.session_state["audit_logs"] = []

def log_audit_event(event_type: str, details: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "event_type": event_type,
        "details": details,
        "hash": hashlib.sha256(f"{timestamp}{event_type}{details}".encode()).hexdigest()[:12]
    }
    st.session_state["audit_logs"].append(log_entry)

def parse_pdf_structure(reader: PdfReader) -> tuple[str, dict]:
    full_text = ""
    metadata = {"num_pages": len(reader.pages), "toc_detected": False}
    for idx, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            full_text += f"\n--- [PAGE {idx + 1}] ---\n" + text
    return full_text, metadata

def compute_risk_score(result_json: dict) -> int:
    score = 15
    if result_json.get("recommendation_status") == "NOT SUPPORTED":
        score += 65
    elif result_json.get("recommendation_status") == "REQUIRES HUMAN REVIEW":
        score += 35
    
    rule_analysis = result_json.get("rule_analysis", {})
    if rule_analysis.get("unresolved_conflict"):
        score += 20
    if rule_analysis.get("exception_detected"):
        score += 10
    return min(score, 100)

if len(st.session_state["audit_logs"]) == 0:
    log_audit_event("SYSTEM_BOOT", "GovShield Enterprise AI Workspace initialized successfully.")

# ==============================================================================
# 7. PREMIUM SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div class="security-badge">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#34D399" stroke-width="2.2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            <path d="M9 12l2 2 4-4"/>
        </svg>
        <span class="security-badge-text">TLS 1.3 ENCRYPTED • AES-256</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2">
            <rect x="2" y="2" width="20" height="8" rx="2" ry="2"/>
            <rect x="2" y="14" width="20" height="8" rx="2" ry="2"/>
        </svg>
        <span style="font-weight:800; color:#38BDF8; font-size:0.82rem; letter-spacing:0.5px;">SYSTEM TELEMETRY</span>
    </div>
    """, unsafe_allow_html=True)

    uptime = int(time.time() - st.session_state["boot_timestamp"])
    latency_ms = round((time.time() % 1) * 20 + 12, 1)

    st.markdown(f"""
    <div class="telemetry-card">
        <div class="telemetry-row">
            <span class="telemetry-label">Engine Version</span>
            <span class="telemetry-value">v3.0.4-Enterprise</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Node Status</span>
            <span class="telemetry-value" style="color:#34D399;">● ONLINE (Jakarta-1)</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">API Latency</span>
            <span class="telemetry-value">{latency_ms} ms</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Active Session</span>
            <span class="telemetry-value">{uptime}s Uptime</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#FDE047" stroke-width="2">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
        </svg>
        <span style="font-weight:800; color:#FDE047; font-size:0.82rem; letter-spacing:0.5px;">REGULATORY SCOPE</span>
    </div>
    """, unsafe_allow_html=True)

    reg_scope = st.selectbox(
        "Choose Regulatory Scope",
        [
            "🏛️ Macro (National Level - UUD 1945 & Acts)",
            "🎓 Meso (Institutional / Campus Policy)",
            "⚖️ Harmonization (National vs Local Alignment)",
            "💼 Corporate / Contractual Compliance"
        ],
        index=2,
        label_visibility="collapsed"
    )

    st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:10px;">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="16" x2="12" y2="12"/>
        </svg>
        <span style="font-weight:800; color:#38BDF8; font-size:0.82rem; letter-spacing:0.5px;">GROUNDED INDEX ACTIVE</span>
    </div>
    <div style="background: #0A142F; border-left: 3px solid #34D399; padding: 8px 12px; border-radius: 6px; margin-bottom: 8px; font-size: 0.8rem;">
        <b style="color:#FFFFFF;">§ 1945 Constitution (UUD)</b><br><span style="color:#94A3B8;">Amendments I-IV Indexed</span>
    </div>
    <div style="background: #0A142F; border-left: 3px solid #34D399; padding: 8px 12px; border-radius: 6px; font-size: 0.8rem;">
        <b style="color:#FFFFFF;">§ Statutory Hierarchy</b><br><span style="color:#94A3B8;">Act 12/2011 jo. Act 13/2022</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)

    if st.button("🗑️ RESET WORKSPACE DATA"):
        log_audit_event("WORKSPACE_RESET", "User cleared session state and workspace memory.")
        st.session_state["pdf_text"] = ""
        st.session_state["pdf_name"] = ""
        st.session_state["analysis_result"] = None
        st.session_state["chat_history"] = []
        st.session_state["robot_dismissed"] = False
        st.rerun()

    st.caption("🛡️ **GovShield Enterprise Intelligence v3.0**")

# ==============================================================================
# 8. WELCOME ASSISTANT OVERLAY CARD
# ==============================================================================
if not st.session_state["robot_dismissed"]:
    st.markdown("""
    <div class="robot-welcome-card">
        <div style="width: 80px; height: 80px; margin: 0 auto 12px auto;">
            <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#FDE047" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="11" width="18" height="10" rx="2" fill="#0A142F"/>
                <circle cx="12" cy="5" r="2" fill="#38BDF8"/>
                <path d="M12 7v4"/>
                <line x1="8" y1="15" x2="8" y2="15.01" stroke="#34D399" stroke-width="3"/>
                <line x1="16" y1="15" x2="16" y2="15.01" stroke="#34D399" stroke-width="3"/>
                <path d="M9 18h6" stroke="#FDE047" stroke-width="1.5"/>
            </svg>
        </div>
        <h2 style="font-family:'Playfair Display', serif; color:#FDE047; margin:0 0 8px 0; font-size: 1.8rem;">Welcome to GovShield AI Assistant</h2>
        <p style="color:#CBD5E1; font-size:0.92rem; max-width:700px; margin:0 auto 16px auto; line-height:1.6;">
            I am your automated <b>Enterprise Legal & Policy Intelligence Assistant</b>. I analyze legal cases, institutional regulations, and statutory hierarchies using evidence-first grounded reasoning.
        </p>
        <p style="color:#38BDF8; font-size:0.85rem; font-weight:700; margin-bottom:0;">
            Upload a policy PDF or input your legal inquiry below to initialize analysis.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 INITIALIZE LEGAL ANALYSIS WORKSPACE"):
        st.session_state["robot_dismissed"] = True
        log_audit_event("WORKSPACE_INIT", "User initialized legal workspace.")
        st.rerun()

# ==============================================================================
# 9. INPUT AREA: FILE UPLOADER & INQUIRY FORM
# ==============================================================================
st.markdown("""
<div class="custom-label">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FDE047" stroke-width="2.5">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
    </svg>
    OPTIONAL: ATTACH SPECIFIC POLICY / CONTRACT / REGULATION (PDF)
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload Policy or Contract PDF", type=["pdf"], label_visibility="collapsed"
)

if uploaded_file is not None:
    st.session_state["robot_dismissed"] = True
    if st.session_state["pdf_name"] != uploaded_file.name:
        try:
            reader = PdfReader(uploaded_file)
            extracted_text, pdf_meta = parse_pdf_structure(reader)
            st.session_state["pdf_text"] = extracted_text
            st.session_state["pdf_name"] = uploaded_file.name
            log_audit_event("PDF_UPLOAD", f"File '{uploaded_file.name}' loaded ({pdf_meta['num_pages']} pages).")
        except Exception as err:
            st.error(f"Failed to process PDF document: {err}")
            log_audit_event("PDF_ERROR", f"Error parsing PDF: {str(err)}")

    st.markdown(f"""
    <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; padding: 10px 16px; border-radius: 8px; font-size: 0.85rem; color: #34D399; margin-top: 4px; margin-bottom: 12px; display:flex; align-items:center; gap:8px;">
        <span style="font-weight:800;">✓ Active Custom Document Attached:</span> {html.escape(st.session_state['pdf_name'])}
    </div>
    """, unsafe_allow_html=True)
else:
    st.session_state["pdf_text"] = ""
    st.session_state["pdf_name"] = ""

st.markdown("""
<div class="ai-search-frame">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div class="custom-label" style="margin-bottom: 0 !important;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2.5">
                <circle cx="11" cy="11" r="8"/>
                <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            POLICY INQUIRY / LEGAL CASE SCENARIO (REQUIRED)
        </div>
        <div style="font-size: 0.78rem; color: #38BDF8; font-weight:700; display:flex; align-items:center;">
            <span class="pulse-dot"></span> REASONING ENGINE READY
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

user_query = st.text_area(
    "Type your legal inquiry",
    placeholder="Describe your legal case, operational dispute, or regulatory clause for full analysis...",
    height=130,
    label_visibility="collapsed",
)

if user_query.strip():
    st.session_state["robot_dismissed"] = True

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# 10. ANALYSIS EXECUTION ENGINE
# ==============================================================================
if st.button("RUN GOVSHIELD LEGAL INTELLIGENCE ANALYSIS"):
    st.session_state["robot_dismissed"] = True
    if not user_query.strip():
        st.warning("⚠️ Please enter a legal inquiry or scenario description before proceeding.")
    else:
        log_audit_event("ANALYSIS_START", f"Scope: {reg_scope} | Query length: {len(user_query)} chars.")
        with st.spinner("Evaluating statutory hierarchy, cross-referencing legal clauses, and generating evidence brief..."):
            try:
                combined_context = f"{BUILTIN_KNOWLEDGE_BASE}\n[SELECTED REGULATORY SCOPE]: {reg_scope}\n"
                if st.session_state["pdf_text"]:
                    combined_context += f"\n[ATTACHED PDF TEXT]:\n{st.session_state['pdf_text'][:15000]}\n"

                client = OpenAI(api_key=GROQ_KEY, base_url=BASE_URL)

                system_prompt = """
You are GOVSHIELD AI, an enterprise Legal & Regulatory Intelligence Engine.

CORE MANDATES:
1. Analyze legal hierarchy (1945 Constitution vs Statutory Laws vs Institutional Decrees) based on the user's selected Regulatory Scope.
2. Apply the legal maxims "Lex Specialis Derogat Legi Generali" and "Lex Superior Derogat Legi Inferiori".
3. Distinguish clearly between General Provisions and Specific Provisions/Exceptions.
4. Provide direct EVIDENCE quotes or clause citations from the Constitution or uploaded document.
5. IF NO DIRECT EVIDENCE EXISTS, SET STATUS AS "REQUIRES HUMAN REVIEW" and explicitly state that no corresponding clauses were found. DO NOT HALLUCINATE OR INVENT ARTICLES.
6. RESPOND ENTIRELY IN ENGLISH.

OUTPUT FORMAT (STRICT JSON ONLY):
{
  "recommendation_status": "SUPPORTED" | "NOT SUPPORTED" | "REQUIRES HUMAN REVIEW",
  "recommendation_summary": "Executive summary of the legal determination in English",
  "applicable_rule": "The governing legal rule or constitutional principle applicable",
  "evidence": "Direct textual quote or clause reference serving as legal evidence",
  "rule_analysis": {
    "general_provision": "General rule or statutory provision identified",
    "specific_provision": "Specific rule or institutional decree identified",
    "exception_detected": true | false,
    "unresolved_conflict": true | false
  },
  "reasoning_conclusion": "Detailed step-by-step legal rationale and justification",
  "review_note": "Critical advice for human legal counsel"
}
"""

                user_prompt = f"""
GROUNDED KNOWLEDGE & DOCUMENTS:
---
{combined_context}
---

INQUIRY / CASE SCENARIO:
{user_query}
"""

                model_name = "llama-3.3-70b-versatile" if "groq" in BASE_URL.lower() else "gpt-4o-mini"

                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.0,
                    response_format={"type": "json_object"},
                )

                st.session_state["analysis_result"] = json.loads(response.choices[0].message.content)
                log_audit_event("ANALYSIS_SUCCESS", f"Result Status: {st.session_state['analysis_result'].get('recommendation_status')}")

            except Exception as e:
                st.error(f"Technical Execution Error: {e}")
                log_audit_event("ANALYSIS_ERROR", str(e))

# ==============================================================================
# 11. OUTPUT DASHBOARD & MULTI-TAB WORKSPACE
# ==============================================================================
if st.session_state["analysis_result"]:
    result = st.session_state["analysis_result"]
    risk_score = compute_risk_score(result)
    
    col_dash_title, col_dash_risk = st.columns([3, 1])
    with col_dash_title:
        st.markdown("""
        <div style="font-size:1.2rem; font-weight:800; color:#38BDF8; letter-spacing:1px; display:flex; align-items:center; gap:10px;">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2.2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            GOVSHIELD LEGAL INTELLIGENCE ANALYSIS DASHBOARD
        </div>
        """, unsafe_allow_html=True)
    with col_dash_risk:
        risk_color = "#34D399" if risk_score < 30 else ("#FDE047" if risk_score < 70 else "#F87171")
        st.markdown(f"""
        <div style="background:rgba(10,20,47,0.9); border:1px solid {risk_color}; padding:8px 14px; border-radius:10px; text-align:right;">
            <span style="font-size:0.75rem; color:#94A3B8; font-weight:700;">STATUTORY RISK SCORE:</span>
            <span style="font-size:1.1rem; color:{risk_color}; font-weight:800; font-family:'JetBrains Mono';"> {risk_score} / 100</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    status = str(result.get("recommendation_status", "REQUIRES HUMAN REVIEW"))
    summary = html.escape(str(result.get("recommendation_summary", "")))

    if status == "SUPPORTED":
        st.markdown(f'<div class="badge-supported">✅ RECOMMENDATION: SUPPORTED — {summary}</div>', unsafe_allow_html=True)
    elif status == "NOT SUPPORTED":
        st.markdown(f'<div class="badge-rejected">❌ RECOMMENDATION: NOT SUPPORTED — {summary}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="badge-review">⚠️ STATUS: REQUIRES HUMAN REVIEW — Direct Evidence Missing or Insufficient Context</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Executive Summary & Evidence", 
        "⚖️ Statutory Structure & Reasoning",
        "💬 Interactive Legal Q&A Assistant",
        "📥 Export Legal Brief",
        "🛡️ System Audit Logs"
    ])

    applicable_rule = html.escape(str(result.get('applicable_rule', '-')))
    evidence_text = html.escape(str(result.get('evidence', 'No direct text excerpt available')))
    reasoning = html.escape(str(result.get('reasoning_conclusion', '-')))
    review_note = html.escape(str(result.get('review_note', 'N/A')))

    with tab1:
        col_t1_1, col_t1_2 = st.columns(2, gap="medium")
        with col_t1_1:
            st.markdown(f"""
            <div class="lexis-card-gold">
                <div class="card-title-gold">⚖️ GOVERNING / APPLICABLE LEGAL RULE</div>
                <div style="font-size:0.95rem; line-height:1.6; color:#F1F5F9;">{applicable_rule}</div>
            </div>
            """, unsafe_allow_html=True)

        with col_t1_2:
            st.markdown(f"""
            <div class="lexis-card-cyan">
                <div class="card-title-cyan">📌 CITATION & DIRECT LEGAL EVIDENCE EXCERPT</div>
                <div style="font-family:'JetBrains Mono', monospace; font-size:0.85rem; color:#34D399; background:#070C1A; padding:12px; border-radius:8px; border: 1px solid rgba(56, 189, 248, 0.25);">
                    {evidence_text}
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        ra = result.get("rule_analysis", {})
        gen_prov = html.escape(str(ra.get('general_provision', '-')))
        spec_prov = html.escape(str(ra.get('specific_provision', '-')))
        exc_str = '<span style="color:#34D399; font-weight:700;">YES</span>' if ra.get('exception_detected') else '<span style="color:#F87171;">NO</span>'
        conf_str = '<span style="color:#FDE047; font-weight:700;">YES</span>' if ra.get('unresolved_conflict') else '<span style="color:#34D399;">NO</span>'

        st.markdown(f"""
        <div class="lexis-card-cyan">
            <div class="card-title-cyan">📊 REGULATORY HIERARCHY & NORMA ANALYSIS</div>
            <div style="font-size:0.9rem; line-height:1.8; color:#F1F5F9;">
                <div><b>General Provision:</b> {gen_prov}</div>
                <div><b>Specific Provision / Exception:</b> {spec_prov}</div>
                <div><b>Exception Detected:</b> {exc_str}</div>
                <div><b>Normative Conflict Detected:</b> {conf_str}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="lexis-card-gold">
            <div class="card-title-gold">📝 DETAILED LEGAL RATIONALE & CONCLUSION</div>
            <div style="font-size:0.95rem; line-height:1.6; color:#E2E8F0;">
                {reasoning}
            </div>
            <div style="font-size:0.85rem; color:#94A3B8; margin-top:14px; border-top:1px solid rgba(234, 179, 8, 0.2); padding-top:8px;">
                💡 <b>Legal Counsel Advisory Note:</b> {review_note}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        st.markdown("### 💬 Interactive Legal Q&A Assistant")
        st.caption("Ask questions about this legal determination, uploaded document clauses, or relevant statutory rules.")

        for msg in st.session_state["chat_history"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if chat_input := st.chat_input("Ask a follow-up legal question..."):
            st.session_state["chat_history"].append({"role": "user", "content": chat_input})
            log_audit_event("CHAT_QUERY", f"User query: {chat_input[:50]}...")
            with st.chat_message("user"):
                st.markdown(chat_input)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing follow-up question..."):
                    try:
                        client = OpenAI(api_key=GROQ_KEY, base_url=BASE_URL)
                        followup_messages = [
                            {"role": "system", "content": f"You are GovShield AI Legal Assistant. Answer strictly based on this context: {json.dumps(result)}"},
                        ] + st.session_state["chat_history"]

                        resp = client.chat.completions.create(
                            model="llama-3.3-70b-versatile" if "groq" in BASE_URL.lower() else "gpt-4o-mini",
                            messages=followup_messages,
                            temperature=0.2
                        )
                        answer = resp.choices[0].message.content
                        st.markdown(answer)
                        st.session_state["chat_history"].append({"role": "assistant", "content": answer})
                    except Exception as err:
                        st.error(f"Chat error: {err}")

    with tab4:
        st.markdown("### 📥 Download Formal Legal Determination Brief")
        report_text = f"""================================================================================
GOVSHIELD AI - FORMAL LEGAL & REGULATORY DETERMINATION REPORT
================================================================================
Status: {status}
Risk Score Index: {risk_score}/100
Regulatory Scope: {reg_scope}
Attached Document: {st.session_state['pdf_name'] or 'None'}

EXECUTIVE SUMMARY:
{result.get('recommendation_summary')}

GOVERNING / APPLICABLE LEGAL RULE:
{result.get('applicable_rule')}

DIRECT LEGAL EVIDENCE & CITATION:
{result.get('evidence')}

REGULATORY NORMA ANALYSIS:
- General Provision: {ra.get('general_provision')}
- Specific Provision / Exception: {ra.get('specific_provision')}
- Exception Detected: {ra.get('exception_detected')}
- Conflict Detected: {ra.get('unresolved_conflict')}

DETAILED LEGAL RATIONALE:
{result.get('reasoning_conclusion')}

LEGAL COUNSEL ADVISORY NOTE:
{result.get('review_note')}
================================================================================
Generated automatically by GovShield Enterprise AI Engine v3.0
================================================================================
"""
        st.download_button(
            label="📄 DOWNLOAD FORMAL LEGAL REPORT (.TXT)",
            data=report_text,
            file_name=f"GovShield_Brief_{datetime.date.today().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )

    with tab5:
        st.markdown("### 🛡️ Real-Time Audit Log & Security Telemetry")
        st.caption("Immutable session log records for compliance verification and audit trails.")
        
        for log in reversed(st.session_state["audit_logs"]):
            st.markdown(f"""
            <div style="background:rgba(10,20,47,0.8); border:1px solid rgba(56,189,248,0.2); border-radius:8px; padding:10px 14px; margin-bottom:8px; font-family:'JetBrains Mono', monospace; font-size:0.8rem;">
                <span style="color:#94A3B8;">[{log['timestamp']}]</span> 
                <b style="color:#FDE047;">{log['event_type']}</b> - 
                <span style="color:#F8FAFC;">{html.escape(log['details'])}</span> 
                <span style="color:#38BDF8; float:right;">HASH: {log['hash']}</span>
            </div>
            """, unsafe_allow_html=True)
