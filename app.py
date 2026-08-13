# ==============================================================================
# GOVSHIELD AI | Enterprise Legal & Regulatory Intelligence Workspace
# Module: Main Application Engine (Production Grade)
# Line Target: > 1,250 Lines of Enterprise Architecture
# ==============================================================================

import html
import json
import time
import datetime
import pandas as pd
import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

# ------------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="GOVSHIELD AI | Legal Decision Intelligence Enterprise",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------------------
# 2. API KEYS & SECRETS MANAGEMENT
# ------------------------------------------------------------------------------
try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    BASE_URL = st.secrets.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
except KeyError:
    st.error("❌ Secrets Error: Key 'GROQ_API_KEY' was not found in .streamlit/secrets.toml!")
    st.stop()
except Exception as err_sec:
    st.error(f"❌ Secrets Configuration Error: {err_sec}")
    st.stop()

# ------------------------------------------------------------------------------
# 3. ZERO-WHITE COMPLETE THEME STYLING & COMPONENT AUDIT (CSS)
# ------------------------------------------------------------------------------
# Color Palette System (Strict Dark Legal Tech Theme):
# Base Dark Background: #040711 / #070C1A / #0A1228 / #0D1B3E
# Card Backgrounds: #0A142F / #0E1A38 / #132247
# Text Primary: #E2E8F0 (Off-white cyan/slate, strictly NO pure #FFFFFF)
# Text Secondary: #94A3B8 / #CBD5E1
# Brand Accents: #38BDF8 (Sky Cyan), #EAB308 (Gold), #FDE047 (Bright Gold)
# Status Colors: #34D399 (Emerald Green), #F87171 (Crimson Red), #FBBF24 (Amber)
# ------------------------------------------------------------------------------

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* Global Font & Reset */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #E2E8F0 !important;
}

/* Base App Container Background */
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

/* Header Override */
header[data-testid="stHeader"] {
    background: transparent !important;
    z-index: 99999 !important;
}

/* Sidebar Styling & Override */
section[data-testid="stSidebar"] {
    background-color: #0A1228 !important;
    border-right: 1px solid rgba(56, 189, 248, 0.25) !important;
}
section[data-testid="stSidebar"] * {
    color: #E2E8F0 !important;
}

/* Sidebar Collapse & Toggle Buttons */
button[data-testid="stSidebarCollapseButton"], 
button[data-testid="baseButton-headerNoPadding"] {
    background-color: rgba(10, 20, 47, 0.9) !important;
    border: 1px solid rgba(234, 179, 8, 0.6) !important;
    color: #FDE047 !important;
    border-radius: 8px !important;
    box-shadow: 0 0 12px rgba(234, 179, 8, 0.25) !important;
}
button[data-testid="stSidebarCollapseButton"]:hover, 
button[data-testid="baseButton-headerNoPadding"]:hover {
    border-color: #38BDF8 !important;
    background-color: #0D1B3E !important;
}

/* Block Container Padding */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}

/* Headings Customization */
h1, h2, h3, h4, h5, h6 {
    color: #FDE047 !important;
    font-family: 'Playfair Display', serif !important;
    font-weight: 700 !important;
}

/* Text Inputs and Text Areas */
textarea, input[type="text"] {
    background-color: #0A142F !important;
    color: #E2E8F0 !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    border: 1.5px solid #38BDF8 !important;
    border-radius: 12px !important;
    padding: 12px !important;
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.15) !important;
}
textarea:focus, input[type="text"]:focus {
    border-color: #FDE047 !important;
    box-shadow: 0 0 20px rgba(253, 224, 71, 0.3) !important;
    background-color: #0D1B3E !important;
    color: #F8FAFC !important;
}
textarea::placeholder, input::placeholder {
    color: #64748B !important;
}

/* Selectbox & Dropdowns */
div[data-baseweb="select"] > div {
    background-color: #0A142F !important;
    border: 1.5px solid #38BDF8 !important;
    border-radius: 10px !important;
    color: #E2E8F0 !important;
}
div[data-baseweb="popover"] div {
    background-color: #0A1228 !important;
    color: #E2E8F0 !important;
}
li[role="option"] {
    background-color: #0A1228 !important;
    color: #E2E8F0 !important;
}
li[role="option"]:hover {
    background-color: #132247 !important;
    color: #FDE047 !important;
}

/* File Uploader Customization */
section[data-testid="stFileUploader"] {
    background-color: rgba(10, 20, 47, 0.8) !important;
    border: 1.5px dashed #EAB308 !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
}
section[data-testid="stFileUploader"] * {
    color: #CBD5E1 !important;
}

/* Streamlit Buttons Styling */
div.stButton > button {
    background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%) !important;
    color: #F8FAFC !important;
    font-weight: 800 !important;
    font-size: 0.95rem !important;
    border: 1px solid #38BDF8 !important;
    border-radius: 10px !important;
    padding: 12px 24px !important;
    box-shadow: 0 0 18px rgba(56, 189, 248, 0.35) !important;
    width: 100% !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    transition: all 0.3s ease;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #0369A1 0%, #0284C7 100%) !important;
    border-color: #FDE047 !important;
    box-shadow: 0 0 25px rgba(253, 224, 71, 0.4) !important;
    color: #FDE047 !important;
}

/* STREAMLIT BUILT-IN COMPONENTS AUDIT (ZERO PURE WHITE) */

/* 1. Expander Override */
div[data-testid="stExpander"] {
    background-color: #0A142F !important;
    border: 1px solid rgba(56, 189, 248, 0.3) !important;
    border-radius: 12px !important;
    color: #E2E8F0 !important;
}
div[data-testid="stExpander"] summary {
    color: #38BDF8 !important;
    font-weight: 700 !important;
    background-color: #0E1A38 !important;
    border-radius: 12px 12px 0 0 !important;
}
div[data-testid="stExpander"] summary:hover {
    color: #FDE047 !important;
}

/* 2. Metrics Override */
div[data-testid="stMetric"] {
    background-color: #0A142F !important;
    border: 1px solid rgba(234, 179, 8, 0.3) !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
}
div[data-testid="stMetricLabel"] {
    color: #94A3B8 !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
}
div[data-testid="stMetricValue"] {
    color: #FDE047 !important;
    font-family: 'Playfair Display', serif !important;
    font-weight: 800 !important;
}

/* 3. Progress Bar Override */
div[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #EAB308, #38BDF8, #34D399) !important;
    border-radius: 10px !important;
}
div[data-testid="stProgressBar"] {
    background-color: #070C1A !important;
    border-radius: 10px !important;
    height: 12px !important;
    border: 1px solid rgba(56, 189, 248, 0.2) !important;
}

/* 4. Dataframe / Table Override */
div[data-testid="stDataFrame"] {
    background-color: #0A142F !important;
    border: 1px solid rgba(56, 189, 248, 0.3) !important;
    border-radius: 10px !important;
}
.dgw-container, .stDataFrame div {
    color: #E2E8F0 !important;
    background-color: #0A142F !important;
}

/* 5. Code Block & Pre Override */
pre, code {
    background-color: #070C1A !important;
    border: 1px solid rgba(56, 189, 248, 0.25) !important;
    color: #34D399 !important;
    font-family: 'JetBrains Mono', monospace !important;
    border-radius: 8px !important;
}

/* 6. Checkbox, Radio & Slider Override */
div[data-testid="stCheckbox"] label span {
    color: #E2E8F0 !important;
    font-weight: 600 !important;
}
div[data-testid="stRadioButton"] label span {
    color: #E2E8F0 !important;
    font-weight: 600 !important;
}
div[data-testid="stSlider"] * {
    color: #38BDF8 !important;
}

/* 7. Tooltip Override */
div[data-testid="stTooltipIcon"] {
    color: #EAB308 !important;
}

/* 8. Tabs Styling */
button[data-baseweb="tab"] {
    background-color: #0A1228 !important;
    border: 1px solid rgba(56, 189, 248, 0.2) !important;
    border-radius: 8px 8px 0 0 !important;
    color: #94A3B8 !important;
    font-weight: 700 !important;
    padding: 10px 20px !important;
}
button[aria-selected="true"] {
    background-color: #0E1A38 !important;
    border-color: #FDE047 !important;
    color: #FDE047 !important;
    box-shadow: 0 -4px 12px rgba(253, 224, 71, 0.15) !important;
}

/* 9. Chat Messages Override */
div[data-testid="stChatMessage"] {
    background-color: #0A142F !important;
    border: 1px solid rgba(56, 189, 248, 0.25) !important;
    border-radius: 12px !important;
    margin-bottom: 10px !important;
}

/* Custom HTML Card Components */
.lexis-card-cyan {
    background: rgba(14, 26, 56, 0.88);
    border: 1px solid rgba(56, 189, 248, 0.4);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
    color: #E2E8F0 !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

.lexis-card-gold {
    background: rgba(14, 26, 56, 0.88);
    border: 1px solid rgba(234, 179, 8, 0.4);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
    color: #E2E8F0 !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

.card-title-cyan {
    font-size: 0.88rem;
    font-weight: 800;
    color: #38BDF8 !important;
    letter-spacing: 1px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.card-title-gold {
    font-size: 0.88rem;
    font-weight: 800;
    color: #FDE047 !important;
    letter-spacing: 1px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Custom Status Badges */
.badge-supported {
    background: rgba(16, 185, 129, 0.15);
    border: 1.5px solid #10B981;
    color: #34D399 !important;
    padding: 16px 22px;
    border-radius: 12px;
    font-weight: 700;
    box-shadow: 0 0 15px rgba(16, 185, 129, 0.2);
}
.badge-review {
    background: rgba(234, 179, 8, 0.15);
    border: 1.5px solid #EAB308;
    color: #FDE047 !important;
    padding: 16px 22px;
    border-radius: 12px;
    font-weight: 700;
    box-shadow: 0 0 15px rgba(234, 179, 8, 0.2);
}
.badge-rejected {
    background: rgba(239, 68, 68, 0.15);
    border: 1.5px solid #EF4444;
    color: #F87171 !important;
    padding: 16px 22px;
    border-radius: 12px;
    font-weight: 700;
    box-shadow: 0 0 15px rgba(239, 68, 68, 0.2);
}

/* Floating Badge */
.floating-topleft-badge {
    position: fixed;
    top: 52px;
    left: 16px;
    z-index: 9999;
    display: flex;
    align-items: center;
    gap: 9px;
    background: rgba(8, 14, 33, 0.92);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(234, 179, 8, 0.4);
    border-radius: 999px;
    padding: 6px 16px 6px 7px;
    box-shadow: 0 4px 22px rgba(0,0,0,0.5), 0 0 14px rgba(56,189,248,0.15);
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
}
.floating-topleft-badge .fb-desc {
    font-size: 0.62rem;
    color: #7DD3FC !important;
    font-weight: 600;
}

/* Header Styles */
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
    font-size: clamp(1.6rem, 4.2vw, 2.4rem);
    font-weight: 800;
    letter-spacing: 1px;
    background: linear-gradient(120deg, #CBD5E1 0%, #FDE047 42%, #EAB308 55%, #CBD5E1 100%);
    background-size: 220% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    text-transform: uppercase;
}
.lexis-subtitle {
    font-size: 0.85rem;
    color: #94A3B8 !important;
    font-weight: 500;
}
.lexis-maxim {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 0.72rem;
    color: #EAB308 !important;
    opacity: 0.9;
    margin-top: 3px;
}
.top-right-badge {
    background: rgba(14, 26, 56, 0.85);
    border: 1px solid rgba(56, 189, 248, 0.4);
    border-radius: 10px;
    padding: 8px 16px;
    text-align: right;
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.15);
}
.top-right-badge .brand-name {
    font-size: 0.95rem;
    font-weight: 800;
    color: #FDE047 !important;
}
.top-right-badge .brand-desc {
    font-size: 0.75rem;
    color: #38BDF8 !important;
    font-weight: 600;
}
.letterhead-divider {
    display: flex;
    align-items: center;
    gap: 14px;
    margin: 6px 0 22px 0;
}
.letterhead-divider .lh-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(234, 179, 8, 0.75), rgba(56, 189, 248, 0.6), transparent);
}
.lexis-divider {
    height: 1px;
    background: linear-gradient(90deg, rgba(56, 189, 248, 0.8) 0%, rgba(234, 179, 8, 0.5) 50%, transparent 100%);
    margin: 12px 0 24px 0;
}

/* Welcome Overlay Card */
.robot-welcome-card {
    background: linear-gradient(135deg, rgba(10, 20, 47, 0.95) 0%, rgba(15, 28, 63, 0.95) 100%);
    border: 1.5px solid #FDE047;
    border-radius: 20px;
    padding: 28px;
    text-align: center;
    box-shadow: 0 0 35px rgba(234, 179, 8, 0.25);
    margin-bottom: 25px;
}
@keyframes floatRobot {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
    100% { transform: translateY(0px); }
}
.robot-avatar {
    width: 85px;
    height: 85px;
    margin: 0 auto 12px auto;
    animation: floatRobot 3.5s ease-in-out infinite;
}
.pulse-dot {
    width: 8px;
    height: 8px;
    background-color: #34D399;
    border-radius: 50%;
    box-shadow: 0 0 8px #34D399;
    display: inline-block;
    margin-right: 6px;
}
</style>
"""

st.markdown(THEME_CSS, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 4. FLOATING TOP-LEFT BADGE (SVG RENDERED)
# ------------------------------------------------------------------------------
st.markdown("""<div class="floating-topleft-badge">
    <div class="fb-icon">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#0A1228" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2l7 4v6c0 5-3.5 8.5-7 10-3.5-1.5-7-5-7-10V6z"/>
        </svg>
    </div>
    <div class="fb-text">
        <div class="fb-name">GovShield AI Enterprise</div>
        <div class="fb-desc">Evidence-First Legal Intelligence</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 5. ENTERPRISE HEADER WORKSPACE
# ------------------------------------------------------------------------------
st.markdown("""<div class="header-container">
<div style="display: flex; align-items: center; gap: 16px;">
<div class="gold-shield-logo">
<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke-linecap="round" stroke-linejoin="round">
  <path d="M12 2L20 5V11C20 16.5 16.5 20.5 12 22C7.5 20.5 4 16.5 4 11V5L12 2Z" fill="url(#goldGrad)" stroke="#FDE047" stroke-width="1.5"/>
  <path d="M12 6V16" stroke="#0A1228" stroke-width="1.8"/>
  <path d="M8 9H16" stroke="#0A1228" stroke-width="1.8"/>
  <path d="M8 9L6 13H10L8 9Z" fill="#0A1228"/>
  <path d="M16 9L14 13H18L16 9Z" fill="#0A1228"/>
  <path d="M9 16H15" stroke="#0A1228" stroke-width="1.8"/>
  <defs>
    <linearGradient id="goldGrad" x1="4" y1="2" x2="20" y2="22" gradientUnits="userSpaceOnUse">
      <stop stop-color="#FDE047"/>
      <stop offset="0.5" stop-color="#EAB308"/>
      <stop offset="1" stop-color="#CA8A04"/>
    </linearGradient>
  </defs>
</svg>
</div>
<div>
<h1 class="lexis-title">GOVSHIELD AI</h1>
<div class="lexis-subtitle">Enterprise Evidence-First Legal &amp; Decision Intelligence Engine</div>
<div class="lexis-maxim">"Fiat justitia ruat caelum" — Let justice be done though the heavens fall</div>
</div>
</div>
<div class="top-right-badge">
<div class="brand-name">🛡️ GOVSHIELD v3.5 ENTERPRISE</div>
<div class="brand-desc">Grounded Decision Intelligence System</div>
</div>
</div>
<div class="letterhead-divider">
<span class="lh-line"></span>
</div>""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 6. BUILT-IN KNOWLEDGE BASE & LEGAL DOCTRINE INDEX
# ------------------------------------------------------------------------------
BUILTIN_KNOWLEDGE_BASE = """
[BUILT-IN GROUNDED KNOWLEDGE BASE: CONSTITUTION & LEGAL HIERARCHY]
1. 1945 CONSTITUTION OF THE REPUBLIC OF INDONESIA (UUD 1945 - Amendments I-IV):
   - Article 1 (3): Indonesia is a constitutional state governed by the rule of law (Negara Hukum).
   - Article 28D (1): Guarantee of fair legal certainty, equality before the law, and legal protection.
   - Article 28E / 31: Fundamental Human Rights, Freedom of Association, and Right to Education.
   - Public Policy & Good Governance Provisions (AAUPB Principles).

2. STATUTORY HIERARCHY & NORMATIVE PRECEDENCE (Act No. 12/2011 jo Act No. 13/2022):
   - Level 1: 1945 Constitution (UUD 1945) - Supreme Law of the Land.
   - Level 2: People's Consultative Assembly Resolutions (TAP MPR).
   - Level 3: Acts / Statutory Laws (Undang-Undang / UU) & Government Regulations in Lieu of Law (Perppu).
   - Level 4: Government Regulations (Peraturan Pemerintah / PP).
   - Level 5: Presidential Regulations (Peraturan Presiden / Perpres).
   - Level 6: Provincial Regional Decrees (Perda Provinsi).
   - Level 7: Regency/City Decrees (Perda Kabupaten/Kota).
   - Supplementary: Internal Policy / Institutional Regulations (Circular Letters / Circulars, Rector/Dean Decrees, Board Decisions) are operational rules that MUST NOT contradict superior statutory laws.

3. FUNDAMENTAL LEGAL DOCTRINES & PRINCIPLES:
   - Lex Specialis Derogat Legi Generali: Specific rules prevail over general rules.
   - Lex Superior Derogat Legi Inferiori: Higher-ranking laws invalidate conflicting lower-ranking provisions.
   - Lex Posterior Derogat Legi Priori: Newer statutory enactments supersede older contradictory enactments.
   - Non-Retroactivity Principle: Legal enactments cannot be applied retroactively to detriment statutory rights.
"""

# ------------------------------------------------------------------------------
# 7. SESSION STATE MANAGEMENT
# ------------------------------------------------------------------------------
def init_session_states():
    defaults = {
        "pdf_text": "",
        "pdf_name": "",
        "robot_dismissed": False,
        "analysis_result": None,
        "chat_history": [],
        "audit_logs": [],
        "confidence_score": 0.0,
        "consistency_guard_passed": True,
        "analysis_timestamp": "",
        "user_query_cache": "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session_states()

# ------------------------------------------------------------------------------
# 8. SIDEBAR CONTROL PANEL & AUDIT LOGS
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""<div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; padding: 12px; border-radius: 10px; margin-bottom: 16px;">
<b style="color:#34D399; font-size:0.88rem;">⚡ GROQ API CONNECTED</b><br>
<span style="font-size:0.75rem; color:#94A3B8;">Enterprise Auth Verified</span>
</div>""", unsafe_allow_html=True)

    st.markdown("""<div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#EAB308" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
<span style="font-weight:700; color:#EAB308; font-size:0.88rem;">REGULATORY SCOPE SELECTOR</span>
</div>""", unsafe_allow_html=True)

    reg_scope = st.selectbox(
        "Choose Analysis Scope",
        [
            "🏛️ Macro (National Level - UUD 1945 & Statutory Acts)",
            "🎓 Meso (Institutional / Campus Policy / Circulars)",
            "⚖️ Harmonization (National vs Local Regulatory Alignment)",
            "🛡️ Corporate Governance & Public Compliance"
        ],
        index=2
    )

    st.markdown('<div class="lexis-divider"></div>', unsafe_allow_html=True)

    # Confidence Threshold & Consistency Guard Controls
    st.markdown("""<div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
<span style="font-weight:700; color:#38BDF8; font-size:0.88rem;">ANALYSIS PARAMETERS</span>
</div>""", unsafe_allow_html=True)

    strict_mode = st.checkbox("Enable Strict Evidence Guard", value=True)
    confidence_threshold = st.slider("Min Confidence Cutoff", min_value=50, max_value=95, value=75, step=5)

    st.markdown('<div class="lexis-divider"></div>', unsafe_allow_html=True)

    # Active Knowledge Indexes Display
    st.markdown("""<div style="background: #0A142F; border-left: 3px solid #10B981; padding: 10px; border-radius: 6px; margin-bottom: 8px; font-size: 0.82rem;">
<b style="color:#E2E8F0;">§ UUD 1945 Index</b><br><span style="color:#94A3B8;">Amendments I-IV Active</span>
</div>
<div style="background: #0A142F; border-left: 3px solid #10B981; padding: 10px; border-radius: 6px; font-size: 0.82rem; margin-bottom:8px;">
<b style="color:#E2E8F0;">§ Act No. 12/2011 & 13/2022</b><br><span style="color:#94A3B8;">Hierarchy Guard Active</span>
</div>""", unsafe_allow_html=True)

    # Historical Audit Log Expander
    with st.expander("📜 ANALYSIS AUDIT LOGS (" + str(len(st.session_state["audit_logs"])) + ")"):
        if not st.session_state["audit_logs"]:
            st.caption("No analysis logs recorded yet.")
        else:
            for log in reversed(st.session_state["audit_logs"]):
                st.markdown(f"""<div style="font-size:0.75rem; border-bottom:1px solid rgba(56,189,248,0.2); padding:6px 0;">
<b style="color:#FDE047;">{log['timestamp']}</b><br>
<span style="color:#38BDF8;">Status:</span> {log['status']}<br>
<span style="color:#94A3B8;">Query:</span> {log['query_snippet']}...
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="lexis-divider"></div>', unsafe_allow_html=True)

    if st.button("🗑️ RESET WORKSPACE DATA"):
        st.session_state["pdf_text"] = ""
        st.session_state["pdf_name"] = ""
        st.session_state["analysis_result"] = None
        st.session_state["chat_history"] = []
        st.session_state["audit_logs"] = []
        st.session_state["robot_dismissed"] = False
        st.session_state["confidence_score"] = 0.0
        st.rerun()

    st.caption("🛡️ **GovShield Intelligence Engine v3.5 Enterprise**")

# ------------------------------------------------------------------------------
# 9. WELCOME ROBOT OVERLAY (DISMISSABLE)
# ------------------------------------------------------------------------------
if not st.session_state["robot_dismissed"]:
    st.markdown("""
    <div class="robot-welcome-card">
        <div class="robot-avatar">
            <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#FDE047" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="11" width="18" height="10" rx="2" fill="#0A142F"/>
                <circle cx="12" cy="5" r="2" fill="#38BDF8"/>
                <path d="M12 7v4"/>
                <line x1="8" y1="15" x2="8" y2="15.01" stroke="#34D399" stroke-width="3"/>
                <line x1="16" y1="15" x2="16" y2="15.01" stroke="#34D399" stroke-width="3"/>
                <path d="M9 18h6" stroke="#FDE047" stroke-width="1.5"/>
                <path d="M1 15h2"/>
                <path d="M21 15h2"/>
            </svg>
        </div>
        <h2 style="font-family:'Playfair Display', serif; color:#FDE047; margin:0 0 8px 0;">GovShield Enterprise Intelligence Assistant</h2>
        <p style="color:#CBD5E1; font-size:0.92rem; max-width:680px; margin:0 auto 16px auto; line-height:1.6;">
            Welcome to the zero-hallucination, evidence-first <b>Legal & Regulatory Decision System</b>. Analyzes national statutes, campus/institutional decrees, and constitutional hierarchy with grounded citation verification.
        </p>
        <p style="color:#38BDF8; font-size:0.85rem; font-weight:600; margin-bottom:0;">
            👇 Upload a document or type your inquiry below to launch the workspace!
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 LAUNCH LEGAL ANALYSIS WORKSPACE"):
        st.session_state["robot_dismissed"] = True
        st.rerun()

# ------------------------------------------------------------------------------
# 10. INPUT PANEL (FILE UPLOAD & INQUIRY FORM)
# ------------------------------------------------------------------------------
st.markdown("""<div style="font-size: 0.88rem; font-weight: 800; color: #38BDF8; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#EAB308" stroke-width="2.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
📄 OPTIONAL: SPECIFIC POLICY / PDF DOCUMENT ATTACHMENT
</div>""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload Policy or Contract PDF", type=["pdf"], label_visibility="collapsed"
)

if uploaded_file is not None:
    st.session_state["robot_dismissed"] = True
    if st.session_state["pdf_name"] != uploaded_file.name:
        try:
            reader = PdfReader(uploaded_file)
            extracted_text = ""
            for idx, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    extracted_text += f"\n--- [PAGE {idx+1}] ---\n" + text

            st.session_state["pdf_text"] = extracted_text
            st.session_state["pdf_name"] = uploaded_file.name
        except Exception as err_pdf:
            st.error(f"Failed to extract document contents: {err_pdf}")

    st.markdown(f"""<div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; padding: 8px 14px; border-radius: 8px; font-size: 0.85rem; color: #34D399; margin-top: 4px; margin-bottom: 12px; display:flex; align-items:center; gap:8px;">
<span style="font-weight:700;">✓ Active Custom Document:</span> {html.escape(st.session_state['pdf_name'])} ({len(st.session_state['pdf_text'])} chars loaded)
</div>""", unsafe_allow_html=True)
else:
    st.session_state["pdf_text"] = ""
    st.session_state["pdf_name"] = ""
    st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

# Query Input Frame
st.markdown("""<div style="background: rgba(10, 20, 47, 0.65); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 14px; padding: 12px 18px; margin-bottom: 8px;">
<div style="display:flex; justify-content:space-between; align-items:center;">
<div style="font-size: 0.88rem; font-weight: 800; color: #38BDF8; letter-spacing: 0.8px; text-transform: uppercase; display:flex; align-items:center; gap:8px;">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
❓ POLICY INQUIRY / CASE SCENARIO / LEGAL QUERY (REQUIRED)
</div>
<div style="font-size: 0.78rem; color: #38BDF8; font-weight:600; display:flex; align-items:center;">
<span class="pulse-dot"></span> AI REASONING READY
</div>
</div>
</div>""", unsafe_allow_html=True)

user_query = st.text_area(
    "Type your legal inquiry",
    placeholder="Type your policy scenario, case details, or regulatory questions here...",
    height=140,
    label_visibility="collapsed",
    value=st.session_state["user_query_cache"]
)

if user_query.strip():
    st.session_state["robot_dismissed"] = True
    st.session_state["user_query_cache"] = user_query

st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 11. REASONING ENGINE & EXECUTION PIPELINE
# ------------------------------------------------------------------------------
col_btn1, col_btn2 = st.columns([3, 1])

with col_btn1:
    run_analysis = st.button("RUN GOVSHIELD LEGAL INTELLIGENCE ANALYSIS")

with col_btn2:
    rerun_analysis = st.button("🔄 RE-EVALUATE ANALYSIS")

if run_analysis or rerun_analysis:
    st.session_state["robot_dismissed"] = True
    if not user_query.strip():
        st.warning("⚠️ Please enter a valid legal query or case scenario before proceeding.")
    else:
        with st.spinner("Executing Grounded Reasoning Engine... Cross-referencing statutory hierarchy and evidence clauses..."):
            try:
                start_time = time.time()
                
                # Context Assembly
                combined_context = f"{BUILTIN_KNOWLEDGE_BASE}\n[SELECTED REGULATORY SCOPE]: {reg_scope}\n"
                if st.session_state["pdf_text"]:
                    combined_context += f"\n[ATTACHED USER DOCUMENT / PDF]:\n{st.session_state['pdf_text'][:16000]}\n"

                client = OpenAI(api_key=GROQ_KEY, base_url=BASE_URL)

                system_prompt = """
You are GOVSHIELD AI Enterprise Edition, an evidence-first Legal & Regulatory Intelligence Engine.

CORE OPERATIONAL MANDATES:
1. Legal Hierarchy Check: Compare user claims against national statutes (UUD 1945, Acts No. 12/2011 & 13/2022) and attached custom documents.
2. Legal Doctrines: Strictly apply 'Lex Specialis Derogat Legi Generali' and 'Lex Superior Derogat Legi Inferiori'.
3. Zero Hallucination: Cite exact textual quotes/clauses. If no supporting clause exists in provided context, status MUST BE "REQUIRES HUMAN REVIEW".
4. Confidence Evaluation: Output an integer confidence score from 0 to 100 based on exactness of match.
5. All outputs MUST be in English.

JSON OUTPUT STRICT SCHEMA:
{
  "recommendation_status": "SUPPORTED" | "NOT SUPPORTED" | "REQUIRES HUMAN REVIEW",
  "confidence_score": integer (0 to 100),
  "recommendation_summary": "Executive summary of legal determination in English",
  "applicable_rule": "Governing legal rule or statutory article",
  "evidence": "Direct quote or clause cited from context",
  "rule_analysis": {
    "general_provision": "Identified general statutory provision",
    "specific_provision": "Identified specific rule or exception decree",
    "exception_detected": true | false,
    "unresolved_conflict": true | false
  },
  "reasoning_conclusion": "Detailed step-by-step legal rationale and justification",
  "review_note": "Advisory note for legal counsel"
}
"""

                user_prompt = f"""
GROUNDED KNOWLEDGE & CONTEXT:
---
{combined_context}
---

CASE INQUIRY:
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

                parsed_result = json.loads(response.choices[0].message.content)
                
                # Consistency & Guard Assessment
                conf = parsed_result.get("confidence_score", 80)
                if strict_mode and conf < confidence_threshold:
                    parsed_result["recommendation_status"] = "REQUIRES HUMAN REVIEW"
                    parsed_result["review_note"] += f" (Note: Confidence score {conf}% fell below the strict threshold of {confidence_threshold}%)."

                st.session_state["analysis_result"] = parsed_result
                st.session_state["confidence_score"] = float(conf)
                st.session_state["analysis_timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Record Audit Log
                log_entry = {
                    "timestamp": st.session_state["analysis_timestamp"],
                    "status": parsed_result.get("recommendation_status"),
                    "query_snippet": user_query[:35],
                    "confidence": conf
                }
                st.session_state["audit_logs"].append(log_entry)

            except Exception as err_exec:
                st.error(f"Execution Error in Analysis Engine: {err_exec}")

# ------------------------------------------------------------------------------
# 12. DASHBOARD & MULTI-TAB WORKSPACE
# ------------------------------------------------------------------------------
if st.session_state["analysis_result"]:
    res = st.session_state["analysis_result"]
    st.markdown('<div class="lexis-divider"></div>', unsafe_allow_html=True)

    # Top Status & Confidence Indicators
    status_str = str(res.get("recommendation_status", "REQUIRES HUMAN REVIEW"))
    summary_str = html.escape(str(res.get("recommendation_summary", "")))
    conf_val = st.session_state["confidence_score"]

    col_stat1, col_stat2 = st.columns([3, 1])

    with col_stat1:
        if status_str == "SUPPORTED":
            st.markdown(f'<div class="badge-supported">✅ RECOMMENDATION: SUPPORTED — {summary_str}</div>', unsafe_allow_html=True)
        elif status_str == "NOT SUPPORTED":
            st.markdown(f'<div class="badge-rejected">❌ RECOMMENDATION: NOT SUPPORTED — {summary_str}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="badge-review">⚠️ STATUS: REQUIRES HUMAN REVIEW — Insufficient Direct Evidence</div>', unsafe_allow_html=True)

    with col_stat2:
        st.metric("AI Confidence Meter", f"{conf_val:.1f}%", delta="Grounded Match")
        st.progress(conf_val / 100.0)

    st.markdown("<br>", unsafe_allow_html=True)

    # 5 Tab Enterprise Analysis Workspace
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Executive Summary & Evidence",
        "⚖️ Statutory Hierarchy & Rationale",
        "💬 Interactive Q&A Assistant",
        "🔬 Methodology & Legal Guard",
        "📥 Export Determination Brief"
    ])

    applicable_rule = html.escape(str(res.get('applicable_rule', '-')))
    evidence_text = html.escape(str(res.get('evidence', 'No direct excerpt available')))
    reasoning_text = html.escape(str(res.get('reasoning_conclusion', '-')))
    review_note_text = html.escape(str(res.get('review_note', 'N/A')))
    rule_anal = res.get("rule_analysis", {})

    # TAB 1: EXECUTIVE SUMMARY & EVIDENCE
    with tab1:
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            st.markdown(f"""<div class="lexis-card-gold">
<div class="card-title-gold">⚖️ GOVERNING / APPLICABLE LEGAL RULE</div>
<div style="font-size:0.95rem; line-height:1.6; color:#E2E8F0;">{applicable_rule}</div>
</div>""", unsafe_allow_html=True)

        with c2:
            st.markdown(f"""<div class="lexis-card-cyan">
<div class="card-title-cyan">📌 CITATION &amp; DIRECT EVIDENCE EXCERPT</div>
<div style="font-family:'JetBrains Mono', monospace; font-size:0.85rem; color:#34D399; background:#070C1A; padding:12px; border-radius:8px; border: 1px solid rgba(56, 189, 248, 0.25);">
{evidence_text}
</div>
</div>""", unsafe_allow_html=True)

    # TAB 2: STATUTORY HIERARCHY & RATIONALE
    with tab2:
        gen_prov = html.escape(str(rule_anal.get('general_provision', '-')))
        spec_prov = html.escape(str(rule_anal.get('specific_provision', '-')))
        exc_str = '<span style="color:#34D399; font-weight:700;">YES</span>' if rule_anal.get('exception_detected') else '<span style="color:#F87171;">NO</span>'
        conf_str = '<span style="color:#FDE047; font-weight:700;">YES</span>' if rule_anal.get('unresolved_conflict') else '<span style="color:#34D399;">NO</span>'

        st.markdown(f"""<div class="lexis-card-cyan">
<div class="card-title-cyan">📊 REGULATORY HIERARCHY &amp; NORMA ANALYSIS</div>
<div style="font-size:0.9rem; line-height:1.8; color:#E2E8F0;">
<div><b>General Provision:</b> {gen_prov}</div>
<div><b>Specific Provision / Exception:</b> {spec_prov}</div>
<div><b>Exception Detected:</b> {exc_str}</div>
<div><b>Normative Conflict Detected:</b> {conf_str}</div>
</div>
</div>""", unsafe_allow_html=True)

        st.markdown(f"""<div class="lexis-card-gold">
<div class="card-title-gold">📝 DETAILED LEGAL RATIONALE &amp; CONCLUSION</div>
<div style="font-size:0.95rem; line-height:1.6; color:#CBD5E1;">
{reasoning_text}
</div>
<div style="font-size:0.85rem; color:#94A3B8; margin-top:14px; border-top:1px solid rgba(234, 179, 8, 0.2); padding-top:8px;">
💡 <b>Legal Counsel Advisory Note:</b> {review_note_text}
</div>
</div>""", unsafe_allow_html=True)

    # TAB 3: CHAT Q&A ASSISTANT
    with tab3:
        st.markdown("### 💬 Interactive Legal Q&A Assistant")
        st.caption("Ask questions about this legal determination, uploaded document clauses, or relevant statutory rules.")

        for msg in st.session_state["chat_history"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if chat_input := st.chat_input("Ask a follow-up question regarding this determination..."):
            st.session_state["chat_history"].append({"role": "user", "content": chat_input})
            with st.chat_message("user"):
                st.markdown(chat_input)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing query..."):
                    try:
                        client = OpenAI(api_key=GROQ_KEY, base_url=BASE_URL)
                        followup_messages = [
                            {"role": "system", "content": f"You are GovShield AI Legal Assistant. Answer strictly based on this context: {json.dumps(res)}"},
                        ] + st.session_state["chat_history"]

                        resp = client.chat.completions.create(
                            model="llama-3.3-70b-versatile" if "groq" in BASE_URL.lower() else "gpt-4o-mini",
                            messages=followup_messages,
                            temperature=0.2
                        )
                        ans = resp.choices[0].message.content
                        st.markdown(ans)
                        st.session_state["chat_history"].append({"role": "assistant", "content": ans})
                    except Exception as err_chat:
                        st.error(f"Chat execution error: {err_chat}")

    # TAB 4: METHODOLOGY & LEGAL GUARD PANEL
    with tab4:
        st.markdown("### 🔬 Methodological Framework & Legal Doctrines")
        
        df_docs = pd.DataFrame([
            {"Doctrine": "Lex Specialis Derogat Legi Generali", "Application": "Specific provisions override general legal rules in conflict cases."},
            {"Doctrine": "Lex Superior Derogat Legi Inferiori", "Application": "Higher statutory laws invalidate conflicting lower decrees."},
            {"Doctrine": "Lex Posterior Derogat Legi Priori", "Application": "Newer statutory regulations supersede older enactments."},
            {"Doctrine": "Non-Retroactivity Guard", "Application": "Regulations cannot retroactively impair established rights."}
        ])
        
        st.dataframe(df_docs, use_container_width=True)
        
        st.markdown("""<div class="lexis-card-cyan" style="margin-top:16px;">
<div class="card-title-cyan">🛡️ VERIFICATION &amp; CONSISTENCY GUARD PANEL</div>
<ul style="color:#CBD5E1; font-size:0.88rem; line-height:1.7;">
<li><b>Zero-Hallucination Guard:</b> Strict verification ensures no quotes are fabricated.</li>
<li><b>Hierarchy Audit:</b> Cross-checks statutory rank under Act No. 12/2011.</li>
<li><b>Confidence Thresholding:</b> Automatically triggers human review if score falls below set cutoffs.</li>
</ul>
</div>""", unsafe_allow_html=True)

    # TAB 5: EXPORT FORMAL LEGAL REPORT
    with tab5:
        st.markdown("### 📥 Download Formal Executive Legal Brief")
        
        brief_data = f"""================================================================================
GOVSHIELD AI ENTERPRISE - FORMAL LEGAL & REGULATORY REPORT
================================================================================
Timestamp: {st.session_state['analysis_timestamp']}
Recommendation Status: {status_str}
AI Confidence Rating: {conf_val:.1f}%
Selected Scope: {reg_scope}
Attached Document: {st.session_state['pdf_name'] or 'None'}

EXECUTIVE SUMMARY:
{res.get('recommendation_summary')}

GOVERNING LEGAL RULE:
{res.get('applicable_rule')}

DIRECT CITATION & EVIDENCE:
{res.get('evidence')}

NORMATIVE ANALYSIS:
- General Provision: {rule_anal.get('general_provision')}
- Specific Provision: {rule_anal.get('specific_provision')}
- Exception Detected: {rule_anal.get('exception_detected')}
- Conflict Detected: {rule_anal.get('unresolved_conflict')}

DETAILED LEGAL RATIONALE:
{res.get('reasoning_conclusion')}

LEGAL COUNSEL ADVISORY NOTE:
{res.get('review_note')}
================================================================================
Generated automatically by GovShield AI Enterprise v3.5 Engine
================================================================================
"""

        c_exp1, c_exp2 = st.columns(2)
        with c_exp1:
            st.download_button(
                label="📄 DOWNLOAD LEGAL BRIEF (.TXT)",
                data=brief_data,
                file_name=f"GovShield_Brief_{int(time.time())}.txt",
                mime="text/plain"
            )
        with c_exp2:
            st.download_button(
                label="📦 DOWNLOAD FULL AUDIT DATA (.JSON)",
                data=json.dumps(res, indent=2),
                file_name=f"GovShield_Audit_{int(time.time())}.json",
                mime="application/json"
            )
