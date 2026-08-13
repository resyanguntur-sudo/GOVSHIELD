import html
import json
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
# 2. READ API KEYS & SECRETS
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

# ---------------------------------------------------------
# 3. UNIVERSAL THEME STYLES (ENTERPRISE DARK THEME + FULL SVG ANIMATIONS)
# ---------------------------------------------------------
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* HEADER & SIDEBAR NAVIGATION BUTTONS */
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

/* BASE BACKGROUND WITH LEGAL SILHOUETTE & TECH GLOW */
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

.stApp::before {
    content: "";
    position: fixed;
    bottom: 0;
    left: 0;
    width: 280px;
    height: 280px;
    pointer-events: none;
    z-index: 1;
    opacity: 0.15;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" fill="none" stroke="%2338BDF8" stroke-width="1"><path d="M20 180 H180 M40 180 V100 M80 180 V100 M120 180 V100 M160 180 V100 M30 100 H170 M100 30 L30 100 M100 30 L170 100"/><circle cx="40" cy="140" r="3" fill="%2338BDF8"/><circle cx="120" cy="120" r="3" fill="%2338BDF8"/><line x1="40" y1="140" x2="120" y2="120" stroke="%23EAB308" stroke-width="0.8"/></svg>');
    background-size: contain;
    background-repeat: no-repeat;
}

.stApp::after {
    content: "";
    position: fixed;
    bottom: 0;
    right: 0;
    width: 280px;
    height: 280px;
    pointer-events: none;
    z-index: 1;
    opacity: 0.15;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" fill="none" stroke="%23EAB308" stroke-width="1.2"><path d="M130 50 L70 110 M60 100 L80 120 M140 160 H180 M20 180 H180"/><circle cx="130" cy="50" r="6" stroke="%2338BDF8"/><path d="M150 30 L170 10 M170 10 H150 M170 10 V30"/></svg>');
    background-size: contain;
    background-repeat: no-repeat;
    background-position: bottom right;
}

/* SIDEBAR STYLING */
section[data-testid="stSidebar"] {
    background-color: #0A1228 !important;
    border-right: 1px solid rgba(56, 189, 248, 0.25) !important;
}

section[data-testid="stSidebar"] * {
    color: #F1F5F9 !important;
}

/* FLOATING TOP-LEFT BADGE */
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
.floating-topleft-badge .fb-text { line-height: 1.15; }
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

.custom-label {
    font-size: 0.88rem !important;
    font-weight: 800 !important;
    color: #38BDF8 !important;
    letter-spacing: 0.8px !important;
    text-transform: uppercase;
    margin-bottom: 8px !important;
    display: flex;
    align-items: center;
    gap: 8px;
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

textarea::placeholder {
    color: #94A3B8 !important;
    opacity: 1 !important;
}

section[data-testid="stFileUploader"] {
    background-color: rgba(10, 20, 47, 0.8) !important;
    border: 1.5px solid #EAB308 !important;
    border-radius: 12px !important;
    padding: 6px 12px !important;
}

.header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
    padding: 0 0 12px 0;
    width: 100%;
    position: relative;
}

.gold-shield-logo {
    background: linear-gradient(135deg, rgba(234, 179, 8, 0.25) 0%, rgba(15, 28, 63, 0.9) 100%);
    padding: 12px;
    border-radius: 16px;
    border: 1.5px solid #FDE047;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 20px rgba(234, 179, 8, 0.4), inset 0 0 10px rgba(254, 224, 71, 0.2);
    position: relative;
}

.lexis-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(1.6rem, 4.2vw, 2.4rem);
    font-weight: 800;
    letter-spacing: 1px;
    background: linear-gradient(120deg, #FFFFFF 0%, #FDE047 42%, #EAB308 55%, #FFFFFF 100%);
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
    opacity: 0.85;
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

.ai-search-frame {
    background: rgba(10, 20, 47, 0.65);
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-radius: 14px;
    padding: 14px 18px;
    margin-bottom: 8px;
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

.card-title-cyan {
    font-size: 0.85rem;
    font-weight: 800;
    color: #38BDF8 !important;
    letter-spacing: 1px;
    margin-bottom: 10px;
}

.card-title-gold {
    font-size: 0.85rem;
    font-weight: 800;
    color: #FDE047 !important;
    letter-spacing: 1px;
    margin-bottom: 10px;
}

.badge-supported {
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid #10B981;
    color: #34D399 !important;
    padding: 14px 20px;
    border-radius: 10px;
    font-weight: 700;
}
.badge-review {
    background: rgba(234, 179, 8, 0.15);
    border: 1px solid #EAB308;
    color: #FDE047 !important;
    padding: 14px 20px;
    border-radius: 10px;
    font-weight: 700;
}
.badge-rejected {
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid #EF4444;
    color: #F87171 !important;
    padding: 14px 20px;
    border-radius: 10px;
    font-weight: 700;
}

/* ROBOT WELCOME CARD STYLES */
.robot-welcome-card {
    background: linear-gradient(135deg, rgba(10, 20, 47, 0.95) 0%, rgba(15, 28, 63, 0.95) 100%);
    border: 1.5px solid #FDE047;
    border-radius: 20px;
    padding: 30px;
    text-align: center;
    box-shadow: 0 0 35px rgba(234, 179, 8, 0.25), inset 0 0 15px rgba(56, 189, 248, 0.15);
    margin-bottom: 25px;
}

@keyframes floatRobot {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
    100% { transform: translateY(0px); }
}

.robot-avatar {
    width: 90px;
    height: 90px;
    margin: 0 auto 15px auto;
    animation: floatRobot 3.5s ease-in-out infinite;
}
</style>
""", unsafe_allow_html=True)

# FLOATING BADGE (TOP-LEFT)
st.markdown("""<div class="floating-topleft-badge">
    <div class="fb-icon">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#0A1228" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2l7 4v6c0 5-3.5 8.5-7 10-3.5-1.5-7-5-7-10V6z"/>
        </svg>
    </div>
    <div class="fb-text">
        <div class="fb-name">GovShield AI</div>
        <div class="fb-desc">Evidence-First Legal Intelligence</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. HEADER TASKBAR WITH GOLD SHIELD & LEGAL ICON
# ---------------------------------------------------------
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
<div class="lexis-subtitle">Evidence-First Legal &amp; Regulatory Intelligence Engine</div>
<div class="lexis-maxim">"Fiat justitia ruat caelum" — Let justice be done though the heavens fall</div>
</div>
</div>
<div class="top-right-badge">
<div class="brand-name">🛡️ GOVSHIELD AI v3.0</div>
<div class="brand-desc">Global Legal Analysis System</div>
</div>
</div>
<div class="letterhead-divider">
<span class="lh-line"></span>
</div>""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. BUILT-IN GROUNDED KNOWLEDGE BASE (ENGLISH & INDONESIAN LAW)
# ---------------------------------------------------------
BUILTIN_KNOWLEDGE_BASE = """
[BUILT-IN GROUNDED KNOWLEDGE BASE: CONSTITUTION & LEGAL HIERARCHY]
1. 1945 CONSTITUTION OF THE REPUBLIC OF INDONESIA (UUD 1945 - Amendments I-IV):
   - Article 1 (3): Indonesia is a constitutional state governed by the rule of law.
   - Article 28D (1): Guarantee of fair legal certainty and equal treatment before the law.
   - Article 31: Human Rights & Right to Education.
   - Public Policy & Governance Provisions.
2. STATUTORY HIERARCHY (Act No. 12/2011 & Act No. 13/2022):
   - 1945 Constitution (UUD 1945) > People's Consultative Assembly Resolutions (TAP MPR) > Acts/Laws (UU) / Government Regulations in Lieu of Law (Perppu) > Government Regulations (PP) > Presidential Regulations (Perpres) > Provincial Decrees > Regency/City Regulations.
   - Internal Policies / Institutional Regulations (Circular Letters, Rector/Dean Decrees): Operational rules that MUST NOT contradict superior statutory laws.
3. FUNDAMENTAL LEGAL PRINCIPLES:
   - Lex Specialis Derogat Legi Generali: Specific laws override general laws.
   - Lex Superior Derogat Legi Inferiori: Higher ranking laws override lower ranking laws.
"""

# ---------------------------------------------------------
# 6. SESSION STATE INITIALIZATION
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# 7. SIDEBAR CONFIGURATION (MULTI-TIER SCOPE SELECTOR)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""<div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; padding: 12px; border-radius: 10px; margin-bottom: 16px;">
<b style="color:#34D399; font-size:0.88rem;">⚡ SECRETS CONNECTED</b><br>
<span style="font-size:0.75rem; color:#94A3B8;">GROQ API Key Authenticated</span>
</div>""", unsafe_allow_html=True)

    st.markdown("""<div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#EAB308" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
<span style="font-weight:700; color:#EAB308; font-size:0.88rem;">REGULATORY SCOPE SELECTOR</span>
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

    st.markdown("""<div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
<span style="font-weight:700; color:#38BDF8; font-size:0.88rem;">GROUNDED INDEX ACTIVE</span>
</div>""", unsafe_allow_html=True)

    st.markdown("""<div style="background: #0A142F; border-left: 3px solid #10B981; padding: 10px; border-radius: 6px; margin-bottom: 8px; font-size: 0.85rem;">
<b style="color:#FFFFFF;">§ 1945 Constitution (UUD)</b><br><span style="color:#94A3B8;">Amendments I-IV Indexed</span>
</div>
<div style="background: #0A142F; border-left: 3px solid #10B981; padding: 10px; border-radius: 6px; font-size: 0.85rem;">
<b style="color:#FFFFFF;">§ Statutory Hierarchy</b><br><span style="color:#94A3B8;">Act 12/2011 jo Act 13/2022</span>
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="lexis-divider"></div>', unsafe_allow_html=True)
    
    if st.button("🗑️ RESET WORKSPACE DATA"):
        st.session_state["pdf_text"] = ""
        st.session_state["pdf_name"] = ""
        st.session_state["analysis_result"] = None
        st.session_state["chat_history"] = []
        st.session_state["robot_dismissed"] = False
        st.rerun()

    st.caption("🛡️ **GovShield Intelligence Engine v3.0**")

# ---------------------------------------------------------
# 8. ROBOT WELCOME OVERLAY (CAN BE DISMISSED)
# ---------------------------------------------------------
if not st.session_state["robot_dismissed"]:
    st.markdown("""
    <div class="robot-welcome-card">
        <div class="robot-avatar">
            <svg width="85" height="85" viewBox="0 0 24 24" fill="none" stroke="#FDE047" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
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
        <h2 style="font-family:'Playfair Display', serif; color:#FDE047; margin:0 0 8px 0;">Welcome to GovShield AI Legal Assistant</h2>
        <p style="color:#CBD5E1; font-size:0.95rem; max-width:650px; margin:0 auto 18px auto; line-height:1.6;">
            I am your automated <b>Legal & Policy Intelligence Assistant</b>. I analyze legal cases, institutional regulations, and national constitutions using evidence-first grounded reasoning.
        </p>
        <p style="color:#38BDF8; font-size:0.85rem; font-weight:600; margin-bottom:0;">
            👇 Upload a document or type your inquiry below to launch the analysis workspace!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 LAUNCH LEGAL ANALYSIS WORKSPACE"):
        st.session_state["robot_dismissed"] = True
        st.rerun()

# ---------------------------------------------------------
# 9. INPUT AREA (PDF UPLOAD + QUERY INPUT)
# ---------------------------------------------------------
st.markdown("""<div class="custom-label">
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
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"

            st.session_state["pdf_text"] = extracted_text
            st.session_state["pdf_name"] = uploaded_file.name
        except Exception as err:
            st.error(f"Failed to process PDF document: {err}")

    st.markdown(f"""<div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; padding: 8px 14px; border-radius: 8px; font-size: 0.85rem; color: #34D399; margin-top: 4px; margin-bottom: 12px; display:flex; align-items:center; gap:8px;">
<span style="font-weight:700;">✓ Active Custom Document:</span> {html.escape(st.session_state['pdf_name'])}
</div>""", unsafe_allow_html=True)
else:
    st.session_state["pdf_text"] = ""
    st.session_state["pdf_name"] = ""
    st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

# SEARCH AND QUERY FRAME
st.markdown("""<div class="ai-search-frame">
<div style="display:flex; justify-content:space-between; align-items:center;">
<div class="custom-label" style="margin-bottom: 0 !important;">
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
)

if user_query.strip():
    st.session_state["robot_dismissed"] = True

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 10. EXECUTE BUTTON & AI REASONING LOGIC
# ---------------------------------------------------------
if st.button("RUN GOVSHIELD LEGAL INTELLIGENCE ANALYSIS"):
    st.session_state["robot_dismissed"] = True
    if not user_query.strip():
        st.warning("⚠️ Please enter a legal inquiry or case scenario before proceeding.")
    else:
        with st.spinner("Analyzing legal hierarchy, cross-referencing provisions, and generating evidence-first reasoning..."):
            try:
                combined_context = f"{BUILTIN_KNOWLEDGE_BASE}\n[SELECTED REGULATORY SCOPE]: {reg_scope}\n"
                if st.session_state["pdf_text"]:
                    combined_context += f"\n[ATTACHED USER DOCUMENT / PDF]:\n{st.session_state['pdf_text'][:14000]}\n"

                client = OpenAI(api_key=GROQ_KEY, base_url=BASE_URL)

                system_prompt = """
You are GOVSHIELD AI, an evidence-first enterprise Legal & Regulatory Intelligence Assistant.

CORE MANDATES:
1. Analyze legal hierarchy (1945 Constitution / UUD 1945 vs Statutory Laws vs Institutional/Campus Decrees) based on the user's selected Regulatory Scope.
2. Apply the legal principle "Lex Specialis Derogat Legi Generali" (Specific laws prevail over general laws) and "Lex Superior Derogat Legi Inferiori" (Higher ranking laws override lower laws).
3. Distinguish clearly between General Provisions and Specific Provisions/Exceptions.
4. Provide direct EVIDENCE quotes / clause citations from the 1945 Constitution (UUD 1945) or the uploaded PDF document.
5. IF NO EVIDENCE OR DIRECT CLAUSES EXIST, SET STATUS AS "REQUIRES HUMAN REVIEW" and explicitly state that no corresponding clauses were found. DO NOT HALLUCINATE OR INVENT ARTICLES.
6. RESPOND ENTIRELY IN ENGLISH.

OUTPUT FORMAT (JSON ONLY):
{
  "recommendation_status": "SUPPORTED" | "NOT SUPPORTED" | "REQUIRES HUMAN REVIEW",
  "recommendation_summary": "Executive summary of the legal determination in English",
  "applicable_rule": "The final governing legal rule or supreme constitutional principle applicable",
  "evidence": "Direct textual quote, clause, or article reference serving as legal evidence",
  "rule_analysis": {
    "general_provision": "General rule or statutory provision identified",
    "specific_provision": "Specific rule, exception, or institutional decree identified",
    "exception_detected": true | false,
    "unresolved_conflict": true | false
  },
  "reasoning_conclusion": "Detailed step-by-step legal reasoning and justification",
  "review_note": "Critical analysis note or advice for human legal counsel"
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

            except Exception as e:
                st.error(f"Technical Analysis Error: {e}")

# ---------------------------------------------------------
# 11. OUTPUT DASHBOARD & MULTI-TAB WORKSPACE
# ---------------------------------------------------------
if st.session_state["analysis_result"]:
    result = st.session_state["analysis_result"]
    
    st.markdown('<div class="lexis-divider"></div>', unsafe_allow_html=True)
    st.markdown("""<div style="font-size:1.15rem; font-weight:800; color:#38BDF8; margin-bottom:16px; letter-spacing:1px;">
⚖️ GOVSHIELD INTELLIGENCE ANALYSIS DASHBOARD
</div>""", unsafe_allow_html=True)

    status = str(result.get("recommendation_status", "REQUIRES HUMAN REVIEW"))
    summary = html.escape(str(result.get("recommendation_summary", "")))

    if status == "SUPPORTED":
        st.markdown(f'<div class="badge-supported">✅ RECOMMENDATION: SUPPORTED — {summary}</div>', unsafe_allow_html=True)
    elif status == "NOT SUPPORTED":
        st.markdown(f'<div class="badge-rejected">❌ RECOMMENDATION: NOT SUPPORTED — {summary}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="badge-review">⚠️ STATUS: REQUIRES HUMAN REVIEW — Insufficient Direct Evidence</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # TABULAR DISPLAY FOR DEEP DIVE & UPGRADED WORKSPACE
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

    with tab1:
        r_col1, r_col2 = st.columns(2, gap="medium")
        with r_col1:
            st.markdown(f"""<div class="lexis-card-gold">
<div class="card-title-gold">⚖️ GOVERNING / APPLICABLE RULE</div>
<div style="font-size:0.95rem; line-height:1.6; color:#F1F5F9;">{applicable_rule}</div>
</div>""", unsafe_allow_html=True)

        with r_col2:
            st.markdown(f"""<div class="lexis-card-cyan">
<div class="card-title-cyan">📌 CITATION &amp; DIRECT LEGAL EVIDENCE EXCERPT</div>
<div style="font-family:'JetBrains Mono', monospace; font-size:0.85rem; color:#34D399; background:#070C1A; padding:12px; border-radius:8px; border: 1px solid rgba(56, 189, 248, 0.25);">
{evidence_text}
</div>
</div>""", unsafe_allow_html=True)

    with tab2:
        ra = result.get("rule_analysis", {})
        gen_prov = html.escape(str(ra.get('general_provision', '-')))
        spec_prov = html.escape(str(ra.get('specific_provision', '-')))
        exc_str = '<span style="color:#34D399; font-weight:700;">YES</span>' if ra.get('exception_detected') else '<span style="color:#F87171;">NO</span>'
        conf_str = '<span style="color:#FDE047; font-weight:700;">YES</span>' if ra.get('unresolved_conflict') else '<span style="color:#34D399;">NO</span>'

        st.markdown(f"""<div class="lexis-card-cyan">
<div class="card-title-cyan">📊 REGULATORY HIERARCHY &amp; NORMA ANALYSIS</div>
<div style="font-size:0.9rem; line-height:1.8; color:#F1F5F9;">
<div><b>General Provision:</b> {gen_prov}</div>
<div><b>Specific Provision / Exception:</b> {spec_prov}</div>
<div><b>Exception Detected:</b> {exc_str}</div>
<div><b>Normative Conflict Detected:</b> {conf_str}</div>
</div>
</div>""", unsafe_allow_html=True)

        st.markdown(f"""<div class="lexis-card-gold">
<div class="card-title-gold">📝 DETAILED LEGAL RATIONALE &amp; CONCLUSION</div>
<div style="font-size:0.95rem; line-height:1.6; color:#E2E8F0;">
{reasoning}
</div>
<div style="font-size:0.85rem; color:#94A3B8; margin-top:14px; border-top:1px solid rgba(234, 179, 8, 0.2); padding-top:8px;">
💡 <b>Legal Counsel Advisory Note:</b> {review_note}
</div>
</div>""", unsafe_allow_html=True)

    # TAB 3: INTERACTIVE CHAT WORKSPACE
    with tab3:
        st.markdown("### 💬 Interactive Legal Q&A Assistant")
        st.caption("Ask questions about this legal determination, uploaded document clauses, or relevant statutory rules.")

        for msg in st.session_state["chat_history"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if chat_input := st.chat_input("Ask a follow-up question regarding this case..."):
            st.session_state["chat_history"].append({"role": "user", "content": chat_input})
            with st.chat_message("user"):
                st.markdown(chat_input)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing follow-up legal question..."):
                    try:
                        client = OpenAI(api_key=GROQ_KEY, base_url=BASE_URL)
                        followup_messages = [
                            {"role": "system", "content": f"You are GovShield AI Legal Assistant. Answer strictly based on this legal analysis and ground context: {json.dumps(result)}"},
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

    # TAB 4: DOWNLOAD REPORT
    with tab4:
        st.markdown("### 📥 Download Formal Legal Determination Brief")
        report_text = f"""================================================================================
GOVSHIELD AI - FORMAL LEGAL & REGULATORY DETERMINATION REPORT
================================================================================
Status: {status}
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
Generated automatically by GovShield AI Engine v3.0
================================================================================
"""
        st.download_button(
            label="📄 DOWNLOAD FORMAL LEGAL REPORT (.TXT)",
            data=report_text,
            file_name="GovShield_Executive_Legal_Brief.txt",
            mime="text/plain"
        )
