import html
import json
import datetime
import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="GovShield AI | Legal Decision Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# SECRETS
# =============================================================================
try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    BASE_URL = st.secrets.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
except KeyError:
    st.error("Key 'GROQ_API_KEY' was not found in .streamlit/secrets.toml")
    st.stop()
except Exception as e:
    st.error(f"Error reading secrets.toml: {e}")
    st.stop()

# =============================================================================
# THEME PALETTE (single source of truth — no pure white anywhere)
#   base        #05070F  #080C1C  #0A0F24
#   panel       #0C1330  #0F1A3D  #121D44
#   text hi     #E7ECF5  (near-white, never #FFFFFF)
#   text mid    #B7C2D9
#   text low    #7C89A8
#   gold        #E8B33D  #F4CD6E  #B8860F
#   cyan        #37B6E8  #7ED0F2  #1E6FA3
#   emerald     #35C98C
#   rose        #E5636B
#   mono        #6FE3D6
# =============================================================================
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&family=Fraunces:wght@500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg-0:#05070F; --bg-1:#080C1C; --bg-2:#0A0F24;
    --panel-0:#0C1330; --panel-1:#0F1A3D; --panel-2:#121D44;
    --line-soft:rgba(126,208,242,0.14); --line-gold:rgba(232,179,61,0.30); --line-cyan:rgba(55,182,232,0.30);
    --text-hi:#E7ECF5; --text-mid:#B7C2D9; --text-low:#7C89A8;
    --gold:#E8B33D; --gold-soft:#F4CD6E; --gold-deep:#B8860F;
    --cyan:#37B6E8; --cyan-soft:#7ED0F2; --cyan-deep:#1E6FA3;
    --emerald:#35C98C; --rose:#E5636B; --mono:#6FE3D6;
}

html, body, [class*="css"] { font-family: 'Sora', sans-serif !important; color: var(--text-hi); }

/* ---------- kill every trace of Streamlit's default light chrome ---------- */
html, body { background-color: var(--bg-0) !important; color-scheme: dark !important; }

header[data-testid="stHeader"] {
    background: var(--bg-0) !important;
    border-bottom: 1px solid var(--line-soft) !important;
    z-index: 99999 !important;
}
div[data-testid="stToolbar"] { background: transparent !important; }
div[data-testid="stToolbarActions"] button { background: var(--panel-0) !important; color: var(--cyan-soft) !important; }
div[data-testid="stDecoration"] { background: linear-gradient(90deg, var(--gold), var(--cyan)) !important; }
#MainMenu, footer { background-color: var(--bg-0) !important; color: var(--text-mid) !important; }
div[data-testid="stStatusWidget"] { background: var(--panel-0) !important; color: var(--text-hi) !important; }
div[data-testid="stStatusWidget"] svg { fill: var(--cyan-soft) !important; }

button[data-testid="stSidebarCollapseButton"],
button[data-testid="baseButton-headerNoPadding"],
button[data-testid="stBaseButton-headerNoPadding"] {
    background-color: var(--panel-0) !important;
    border: 1px solid var(--line-gold) !important;
    color: var(--gold-soft) !important;
    border-radius: 8px !important;
}
button[data-testid="stSidebarCollapseButton"]:hover,
button[data-testid="baseButton-headerNoPadding"]:hover,
button[data-testid="stBaseButton-headerNoPadding"]:hover {
    border-color: var(--cyan) !important; background-color: var(--panel-1) !important; color: var(--cyan-soft) !important;
}
button[data-testid="stSidebarCollapseButton"] svg,
button[data-testid="baseButton-headerNoPadding"] svg,
button[data-testid="stBaseButton-headerNoPadding"] svg { fill: var(--gold-soft) !important; }

.block-container {
    padding: 1.6rem 2.2rem 3rem 2.2rem !important;
    max-width: 100% !important;
    position: relative; z-index: 2;
}

/* ---------- base app surface ---------- */
.stApp {
    background-color: var(--bg-0) !important;
    background-image:
        radial-gradient(circle at 10% -10%, rgba(232,179,61,0.10) 0%, transparent 42%),
        radial-gradient(circle at 108% 4%, rgba(55,182,232,0.13) 0%, transparent 46%),
        radial-gradient(circle at 50% 108%, rgba(55,182,232,0.08) 0%, transparent 60%),
        radial-gradient(circle at 50% 18%, #0C1330 0%, #080C1C 62%, #05070F 100%) !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
    color: var(--text-hi) !important;
}

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"] {
    background-color: var(--bg-1) !important;
    border-right: 1px solid var(--line-cyan) !important;
}
section[data-testid="stSidebar"] > div { background-color: var(--bg-1) !important; }
section[data-testid="stSidebar"] * { color: var(--text-hi) !important; }
section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] .stMarkdown p { color: var(--text-mid) !important; }
section[data-testid="stSidebar"] hr { border-color: var(--line-soft) !important; }

/* ---------- generic text ---------- */
p, span, div, li, label, h1, h2, h3, h4, h5, h6 { color: var(--text-hi); }
a, a:visited { color: var(--cyan-soft) !important; text-decoration: none; }
a:hover { color: var(--gold-soft) !important; text-decoration: underline; }
hr { border-color: var(--line-soft) !important; }
::selection { background: rgba(232,179,61,0.32); color: #0A0F24; }

::-webkit-scrollbar { width: 9px; height: 9px; }
::-webkit-scrollbar-track { background: var(--bg-1); }
::-webkit-scrollbar-thumb { background: linear-gradient(180deg, var(--cyan), var(--gold)); border-radius: 8px; }

/* ---------- header identity block ---------- */
.brand-row { display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px; padding:2px 0 14px 0; }
.brand-left { display:flex; align-items:center; gap:16px; }
.brand-mark {
    width:52px; height:52px; border-radius:14px; display:flex; align-items:center; justify-content:center;
    background: linear-gradient(135deg, rgba(232,179,61,0.22) 0%, var(--panel-1) 100%);
    border:1.5px solid var(--gold-soft);
    box-shadow: 0 0 22px rgba(232,179,61,0.22), inset 0 0 10px rgba(244,205,110,0.14);
}
.brand-title {
    font-family:'Fraunces', serif; font-weight:700; letter-spacing:0.5px;
    font-size:clamp(1.5rem, 3.6vw, 2.15rem); margin:0; text-transform:uppercase;
    background: linear-gradient(120deg, var(--text-hi) 0%, var(--gold-soft) 45%, var(--gold) 60%, var(--text-hi) 100%);
    background-size: 220% auto; -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.brand-subtitle { font-size:0.83rem; color: var(--text-mid) !important; font-weight:500; margin-top:2px; }
.brand-maxim { font-family:'Fraunces', serif; font-style:italic; font-size:0.72rem; color: var(--gold) !important; opacity:0.88; margin-top:3px; }
.brand-tag {
    background: var(--panel-1); border:1px solid var(--line-cyan); border-radius:10px; padding:8px 16px; text-align:right;
    box-shadow: 0 0 14px rgba(55,182,232,0.12);
}
.brand-tag .t-name { font-size:0.9rem; font-weight:800; color: var(--gold-soft) !important; letter-spacing:0.4px; }
.brand-tag .t-desc { font-size:0.72rem; color: var(--cyan-soft) !important; font-weight:600; }
.brand-divider {
    height:1px; margin:4px 0 22px 0;
    background: linear-gradient(90deg, transparent, var(--gold), var(--cyan), transparent);
    opacity:0.7;
}
.section-divider {
    height:1px; margin:10px 0 20px 0;
    background: linear-gradient(90deg, var(--cyan) 0%, var(--gold) 55%, transparent 100%);
    opacity:0.55;
}

/* ---------- section label ---------- */
.field-label {
    font-size:0.82rem !important; font-weight:700 !important; color: var(--cyan-soft) !important;
    letter-spacing:0.6px !important; text-transform:uppercase; margin-bottom:8px !important;
    display:flex; align-items:center; gap:9px;
}
.field-label .mark { color: var(--gold); font-weight:800; }

/* ---------- text inputs ---------- */
textarea, .stTextArea textarea {
    background-color: var(--panel-0) !important;
    color: var(--text-hi) !important;
    font-size:0.97rem !important; font-weight:450 !important;
    border:1.4px solid var(--line-cyan) !important; border-radius:12px !important;
    padding:14px !important; caret-color: var(--gold) !important;
}
textarea:focus, .stTextArea textarea:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 3px rgba(232,179,61,0.14) !important;
    background-color: var(--panel-1) !important;
}
textarea::placeholder { color: var(--text-low) !important; opacity:1 !important; }

input[type="text"], input[type="number"], input[type="password"], .stTextInput input, .stNumberInput input {
    background-color: var(--panel-0) !important; color: var(--text-hi) !important;
    border:1.4px solid var(--line-cyan) !important; border-radius:10px !important; caret-color: var(--gold) !important;
}
.stTextInput input:focus, .stNumberInput input:focus { border-color: var(--gold) !important; box-shadow: 0 0 0 3px rgba(232,179,61,0.14) !important; }
input::placeholder { color: var(--text-low) !important; opacity:1 !important; }
.stNumberInput button { background-color: var(--panel-1) !important; border-color: var(--line-cyan) !important; color: var(--cyan-soft) !important; }

/* ---------- file uploader ---------- */
section[data-testid="stFileUploader"] {
    background-color: var(--panel-0) !important; border:1.4px solid var(--line-gold) !important;
    border-radius:12px !important; padding:6px 12px !important;
}
section[data-testid="stFileUploader"] section { background-color: var(--panel-0) !important; border:1px dashed var(--line-gold) !important; color: var(--text-mid) !important; }
section[data-testid="stFileUploader"] small { color: var(--text-low) !important; }
section[data-testid="stFileUploader"] button { background-color: var(--panel-1) !important; color: var(--gold-soft) !important; border:1px solid var(--line-gold) !important; }
div[data-testid="stFileUploaderDropzone"] { background-color: var(--panel-0) !important; }
div[data-testid="stFileUploaderDropzoneInstructions"] span, div[data-testid="stFileUploaderDropzoneInstructions"] small { color: var(--text-mid) !important; }
div[data-testid="stFileUploaderFile"] { background-color: var(--panel-1) !important; color: var(--text-hi) !important; border-radius:8px; }

/* ---------- selectbox / dropdown ---------- */
div[data-baseweb="select"] > div { background-color: var(--panel-0) !important; border:1.4px solid var(--line-cyan) !important; color: var(--text-hi) !important; border-radius:10px !important; }
div[data-baseweb="select"] span { color: var(--text-hi) !important; }
div[data-baseweb="popover"] { background-color: var(--panel-1) !important; }
ul[data-testid="stSelectboxVirtualDropdown"] { background-color: var(--panel-1) !important; border:1px solid var(--line-cyan) !important; }
ul[data-testid="stSelectboxVirtualDropdown"] li { background-color: var(--panel-1) !important; color: var(--text-hi) !important; }
ul[data-testid="stSelectboxVirtualDropdown"] li:hover { background-color: var(--panel-2) !important; color: var(--gold-soft) !important; }
div[data-baseweb="tag"] { background-color: var(--cyan-deep) !important; color: var(--text-hi) !important; }

/* ---------- buttons ---------- */
div.stButton > button, div.stDownloadButton > button, div.stFormSubmitButton > button {
    background: linear-gradient(135deg, var(--cyan-deep) 0%, #123456 100%) !important;
    color: var(--text-hi) !important; font-weight:700 !important; font-size:0.9rem !important;
    border:1px solid var(--cyan) !important; border-radius:10px !important; padding:13px 26px !important;
    width:100% !important; letter-spacing:0.4px; text-transform:uppercase;
    transition: all 0.18s ease-in-out;
}
div.stButton > button:hover, div.stDownloadButton > button:hover, div.stFormSubmitButton > button:hover {
    border-color: var(--gold) !important; box-shadow: 0 0 20px rgba(232,179,61,0.30) !important; color: var(--gold-soft) !important;
}
div.stButton > button:disabled { background: var(--panel-0) !important; color: var(--text-low) !important; border-color:#1B2340 !important; }
div.stButton > button p, div.stDownloadButton > button p { color: inherit !important; }
button[kind="secondary"] { background: var(--panel-0) !important; color: var(--cyan-soft) !important; border:1.4px solid var(--line-cyan) !important; box-shadow:none !important; }
button[kind="secondary"]:hover { background: var(--panel-1) !important; border-color: var(--gold) !important; color: var(--gold-soft) !important; }

/* ---------- checkbox / radio / toggle ---------- */
.stCheckbox label, .stRadio label, .stCheckbox p, .stRadio p { color: var(--text-hi) !important; }
[data-testid="stWidgetLabel"] p { color: var(--text-mid) !important; font-weight:600 !important; }
.stCheckbox [data-baseweb="checkbox"] > div:first-child { background-color: var(--panel-0) !important; border-color: var(--cyan) !important; }
.stCheckbox [data-baseweb="checkbox"] input:checked ~ div { background-color: var(--gold) !important; border-color: var(--gold) !important; }
[data-baseweb="radio"] div:first-child { background-color: var(--panel-0) !important; border-color: var(--cyan) !important; }
.stToggle [data-baseweb="checkbox"] span { background-color: var(--panel-0) !important; }
.stToggle [aria-checked="true"] { background-color: var(--gold) !important; }

/* ---------- slider ---------- */
div[data-testid="stSlider"] div[role="slider"] { background-color: var(--gold-soft) !important; border:2px solid var(--gold) !important; box-shadow: 0 0 8px rgba(232,179,61,0.5) !important; }
div[data-testid="stSlider"] > div > div > div { background: var(--panel-0) !important; }
div[data-testid="stSlider"] > div > div > div > div { background: linear-gradient(90deg, var(--cyan-deep), var(--cyan)) !important; }
div[data-testid="stTickBarMin"], div[data-testid="stTickBarMax"] { color: var(--text-low) !important; }
div[data-testid="stThumbValue"] { background-color: var(--panel-1) !important; color: var(--gold-soft) !important; border:1px solid var(--line-gold) !important; }

/* ---------- progress bar ---------- */
div[data-testid="stProgress"] > div { background-color: var(--panel-0) !important; border-radius:8px; }
div[data-testid="stProgress"] > div > div { background: linear-gradient(90deg, var(--gold), var(--cyan)) !important; border-radius:8px; }

/* ---------- metric ---------- */
div[data-testid="stMetric"] { background-color: var(--panel-0) !important; border:1px solid var(--line-cyan) !important; border-radius:12px !important; padding:14px 16px !important; }
div[data-testid="stMetricLabel"] { color: var(--text-low) !important; font-weight:700 !important; }
div[data-testid="stMetricValue"] { color: var(--gold-soft) !important; font-weight:800 !important; }
div[data-testid="stMetricDelta"] { color: var(--emerald) !important; }
div[data-testid="stMetricDelta"] svg { fill: var(--emerald) !important; }

/* ---------- expander ---------- */
details[data-testid="stExpander"] { background-color: var(--panel-0) !important; border:1px solid var(--line-gold) !important; border-radius:12px !important; }
details[data-testid="stExpander"] summary { background-color: var(--panel-0) !important; color: var(--gold-soft) !important; font-weight:700 !important; border-radius:12px !important; }
details[data-testid="stExpander"] summary:hover { color: var(--cyan-soft) !important; }
details[data-testid="stExpander"] summary svg { fill: var(--gold-soft) !important; }
details[data-testid="stExpander"] > div { background-color: var(--bg-1) !important; border-top:1px solid var(--line-gold) !important; color: var(--text-hi) !important; }

/* ---------- dataframe / table ---------- */
div[data-testid="stDataFrame"], div[data-testid="stTable"] { background-color: var(--panel-0) !important; border:1px solid var(--line-cyan) !important; border-radius:10px !important; }
div[data-testid="stDataFrame"] * { color: var(--text-hi) !important; }
.stDataFrame [data-testid="stElementToolbar"] { background-color: var(--panel-1) !important; }
table { background-color: var(--panel-0) !important; color: var(--text-hi) !important; }
thead tr th { background-color: var(--panel-1) !important; color: var(--gold-soft) !important; border-color: var(--line-cyan) !important; }
tbody tr td { background-color: var(--panel-0) !important; color: var(--text-hi) !important; border-color: var(--line-soft) !important; }
tbody tr:hover td { background-color: var(--panel-1) !important; }

/* ---------- code block ---------- */
code { background-color: var(--panel-0) !important; color: var(--mono) !important; border-radius:4px; padding:2px 6px; font-family:'JetBrains Mono', monospace !important; }
pre, div[data-testid="stCodeBlock"] { background-color: #060913 !important; border:1px solid var(--line-cyan) !important; border-radius:10px !important; }
pre code { background-color: transparent !important; color: var(--mono) !important; }
div[data-testid="stCodeBlock"] button { background-color: var(--panel-1) !important; color: var(--cyan-soft) !important; }

/* ---------- tooltip ---------- */
div[data-baseweb="tooltip"] { background-color: var(--panel-1) !important; color: var(--gold-soft) !important; border:1px solid var(--line-gold) !important; border-radius:8px !important; }
[data-testid="stTooltipIcon"] svg, [data-testid="stTooltipHoverTarget"] svg { fill: var(--cyan-soft) !important; }

/* ---------- tabs ---------- */
button[data-baseweb="tab"] { background-color: var(--panel-0) !important; color: var(--text-low) !important; border-radius:8px 8px 0 0 !important; font-weight:650 !important; }
button[data-baseweb="tab"]:hover { color: var(--cyan-soft) !important; background-color: var(--panel-1) !important; }
button[data-baseweb="tab"][aria-selected="true"] { background-color: var(--panel-1) !important; color: var(--gold-soft) !important; border-bottom:2px solid var(--gold) !important; }
div[data-baseweb="tab-highlight"] { background-color: var(--gold) !important; }
div[data-baseweb="tab-border"] { background-color: var(--line-soft) !important; }

/* ---------- alerts / toast / spinner ---------- */
div[data-testid="stAlert"] { border-radius:10px !important; }
div[data-testid="stAlertContentInfo"] { background-color: rgba(55,182,232,0.10) !important; color: var(--cyan-soft) !important; }
div[data-testid="stAlertContentSuccess"] { background-color: rgba(53,201,140,0.12) !important; color: var(--emerald) !important; }
div[data-testid="stAlertContentWarning"] { background-color: rgba(232,179,61,0.12) !important; color: var(--gold-soft) !important; }
div[data-testid="stAlertContentError"] { background-color: rgba(229,99,107,0.12) !important; color: var(--rose) !important; }
div[data-testid="stAlert"] p, div[data-testid="stAlert"] span { color: inherit !important; }
div[data-testid="stToast"] { background-color: var(--panel-1) !important; color: var(--text-hi) !important; border:1px solid var(--line-gold) !important; }
div[data-testid="stSpinner"] > div { color: var(--gold-soft) !important; }
div[data-testid="stSpinner"] svg { color: var(--cyan-soft) !important; }

/* ---------- chat ---------- */
div[data-testid="stChatMessage"] { background-color: var(--panel-0) !important; border:1px solid var(--line-cyan) !important; border-radius:12px !important; color: var(--text-hi) !important; }
div[data-testid="stChatMessage"] p { color: var(--text-hi) !important; }
div[data-testid="stChatInput"] { background-color: var(--panel-0) !important; border:1.4px solid var(--line-cyan) !important; border-radius:12px !important; }
div[data-testid="stChatInput"] textarea { background-color: transparent !important; color: var(--text-hi) !important; }
div[data-testid="stChatInput"] button { background-color: var(--cyan-deep) !important; }
div[data-testid="stChatInputSubmitButton"] svg { fill: var(--text-hi) !important; }
div[data-testid="stBottomBlockContainer"], div[data-testid="stBottom"] { background-color: var(--bg-0) !important; }

/* ---------- popover ---------- */
div[data-testid="stPopover"] button { background-color: var(--panel-0) !important; color: var(--gold-soft) !important; border:1px solid var(--line-gold) !important; }
ul[role="listbox"] { background-color: var(--panel-1) !important; }
li[role="option"] { color: var(--text-hi) !important; }
li[role="option"]:hover { background-color: var(--panel-2) !important; color: var(--gold-soft) !important; }

/* ---------- caption ---------- */
.stCaption, [data-testid="stCaptionContainer"] { color: var(--text-low) !important; }

/* ---------- cards ---------- */
.panel-frame { background: var(--panel-0); border:1px solid var(--line-cyan); border-radius:14px; padding:14px 18px; margin-bottom:8px; }
.status-dot { width:7px; height:7px; background-color: var(--emerald); border-radius:50%; box-shadow: 0 0 6px var(--emerald); display:inline-block; margin-right:7px; }

.card {
    background: var(--panel-1); border-radius:14px; padding:20px; margin-bottom:16px; color: var(--text-hi) !important;
    border:1px solid var(--line-soft);
}
.card.gold { border-color: var(--line-gold); }
.card.cyan { border-color: var(--line-cyan); }
.card.emerald { border-color: rgba(53,201,140,0.32); }
.card-head { font-size:0.78rem; font-weight:800; letter-spacing:1px; margin-bottom:10px; text-transform:uppercase; }
.card-head.gold { color: var(--gold-soft) !important; }
.card-head.cyan { color: var(--cyan-soft) !important; }
.card-head.emerald { color: var(--emerald) !important; }

.status-banner { padding:14px 20px; border-radius:10px; font-weight:700; font-size:0.92rem; }
.status-banner.supported { background: rgba(53,201,140,0.12); border:1px solid var(--emerald); color: var(--emerald) !important; }
.status-banner.review { background: rgba(232,179,61,0.12); border:1px solid var(--gold); color: var(--gold-soft) !important; }
.status-banner.rejected { background: rgba(229,99,107,0.12); border:1px solid var(--rose); color: var(--rose) !important; }

/* ---------- confidence meter ---------- */
.confidence-box { background: var(--panel-0); border:1px solid var(--line-cyan); border-radius:12px; padding:16px 18px; margin-bottom:16px; }
.confidence-top { display:flex; justify-content:space-between; align-items:baseline; margin-bottom:8px; }
.confidence-tag { font-size:0.76rem; font-weight:800; letter-spacing:0.6px; color: var(--cyan-soft) !important; text-transform:uppercase; }
.confidence-num { font-size:1.02rem; font-weight:800; }
.confidence-track { width:100%; height:9px; background-color:#060913; border-radius:999px; overflow:hidden; border:1px solid var(--line-soft); }
.confidence-fill { height:100%; border-radius:999px; }
.confidence-note { font-size:0.73rem; color: var(--text-low) !important; margin-top:6px; }

/* ---------- consistency guard rows ---------- */
.guard-row { display:flex; align-items:flex-start; gap:10px; padding:9px 12px; border-radius:8px; background-color:#060913; margin-bottom:6px; border-left:3px solid #263256; }
.guard-row.ok { border-left-color: var(--emerald); }
.guard-row.warn { border-left-color: var(--gold); }
.guard-row.bad { border-left-color: var(--rose); }
.guard-mark { font-family:'JetBrains Mono', monospace; font-size:0.75rem; font-weight:700; flex-shrink:0; padding-top:1px; }
.guard-row.ok .guard-mark { color: var(--emerald); }
.guard-row.warn .guard-mark { color: var(--gold-soft); }
.guard-row.bad .guard-mark { color: var(--rose); }
.guard-text { font-size:0.84rem; color: var(--text-mid) !important; line-height:1.5; }
.guard-text b { color: var(--text-hi) !important; }

/* ---------- history ---------- */
.history-card { background-color: var(--panel-0); border:1px solid var(--line-cyan); border-radius:10px; padding:10px 14px; margin-bottom:8px; }
.history-time { font-size:0.68rem; color: var(--text-low) !important; font-family:'JetBrains Mono', monospace; }
.history-query { font-size:0.84rem; color: var(--text-mid) !important; margin:4px 0; line-height:1.4; }
.history-status { font-size:0.68rem; font-weight:800; letter-spacing:0.4px; padding:2px 10px; border-radius:999px; display:inline-block; }

/* ---------- methodology ---------- */
.method-row { display:flex; gap:12px; padding:10px 0; border-bottom:1px solid var(--line-soft); }
.method-row:last-child { border-bottom:none; }
.method-index { flex-shrink:0; width:24px; height:24px; border-radius:7px; background: linear-gradient(135deg, var(--gold), var(--gold-deep)); color:#0A0F24 !important; font-weight:800; font-size:0.74rem; display:flex; align-items:center; justify-content:center; font-family:'JetBrains Mono', monospace; }
.method-title { color: var(--cyan-soft) !important; font-size:0.87rem; font-weight:700; }
.method-desc { color: var(--text-mid) !important; font-size:0.81rem; margin:2px 0 0 0; line-height:1.5; }

/* ---------- welcome panel ---------- */
.welcome-panel { background: linear-gradient(135deg, var(--panel-0) 0%, var(--panel-1) 100%); border:1.5px solid var(--line-gold); border-radius:18px; padding:32px; text-align:center; margin-bottom:24px; }
.welcome-title { font-family:'Fraunces', serif; color: var(--gold-soft) !important; margin:0 0 8px 0; font-weight:700; font-size:1.5rem; }
.welcome-body { color: var(--text-mid) !important; font-size:0.93rem; max-width:640px; margin:0 auto 16px auto; line-height:1.65; }
.welcome-cta { color: var(--cyan-soft) !important; font-size:0.83rem; font-weight:600; }

/* ---------- footer strip ---------- */
.footer-strip { margin-top:36px; padding:16px 20px; border-top:1px solid var(--line-soft); text-align:center; color: var(--text-low) !important; font-size:0.72rem; }
.footer-strip b { color: var(--text-mid) !important; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# HEADER IDENTITY BLOCK
# =============================================================================
st.markdown("""<div class="brand-row">
<div class="brand-left">
<div class="brand-mark">
<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke-linecap="round" stroke-linejoin="round">
  <path d="M12 2L20 5V11C20 16.5 16.5 20.5 12 22C7.5 20.5 4 16.5 4 11V5L12 2Z" fill="url(#gg)" stroke="#F4CD6E" stroke-width="1.4"/>
  <path d="M12 6V16M8 9H16M9 16H15" stroke="#0A0F24" stroke-width="1.6"/>
  <defs><linearGradient id="gg" x1="4" y1="2" x2="20" y2="22" gradientUnits="userSpaceOnUse">
    <stop stop-color="#F4CD6E"/><stop offset="0.5" stop-color="#E8B33D"/><stop offset="1" stop-color="#B8860F"/>
  </linearGradient></defs>
</svg>
</div>
<div>
<h1 class="brand-title">GovShield AI</h1>
<div class="brand-subtitle">Evidence-First Legal &amp; Regulatory Intelligence Engine</div>
<div class="brand-maxim">"Fiat justitia ruat caelum" — let justice be done though the heavens fall</div>
</div>
</div>
<div class="brand-tag">
<div class="t-name">GovShield AI · v5.0</div>
<div class="t-desc">Global Legal Analysis System</div>
</div>
</div>
<div class="brand-divider"></div>""", unsafe_allow_html=True)

# =============================================================================
# BUILT-IN GROUNDED KNOWLEDGE BASE
# =============================================================================
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

METHODOLOGY_STEPS = [
    ("Context Assembly", "Combine the constitutional knowledge base, selected regulatory scope, and any uploaded document text into one grounded context window."),
    ("Hierarchy Mapping", "Rank every identified provision by statutory hierarchy, from UUD 1945 down to institutional decrees."),
    ("Principle Application", "Apply Lex Specialis Derogat Legi Generali and Lex Superior Derogat Legi Inferiori to resolve overlaps between general and specific provisions."),
    ("Evidence Extraction", "Pull clause-level citations only from the grounded context — the model is instructed never to invent articles."),
    ("Consistency Guard", "Cross-check the structured JSON output for internal contradictions before it is rendered."),
    ("Confidence Scoring", "Derive a heuristic confidence score from evidence presence, conflict flags, and output completeness."),
]

# =============================================================================
# SESSION STATE
# =============================================================================
DEFAULT_STATE = {
    "pdf_text": "",
    "pdf_name": "",
    "welcome_dismissed": False,
    "analysis_result": None,
    "chat_history": [],
    "analysis_history": [],
    "last_query": "",
    "last_scope": "",
    "rerun_requested": False,
    "show_methodology": False,
}
for key, default_val in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = list(default_val) if isinstance(default_val, list) else default_val

# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown("""<div style="background:rgba(53,201,140,0.12); border:1px solid #35C98C; padding:12px; border-radius:10px; margin-bottom:16px;">
<b style="color:#35C98C; font-size:0.85rem;">Secrets connected</b><br>
<span style="font-size:0.73rem; color:#7C89A8;">GROQ API key authenticated</span>
</div>""", unsafe_allow_html=True)

    st.markdown("""<div class="field-label"><span class="mark">01</span> Regulatory scope</div>""", unsafe_allow_html=True)
    scope_options = [
        "Macro — National Level (UUD 1945 & Acts)",
        "Meso — Institutional / Campus Policy",
        "Harmonization — National vs Local Alignment",
    ]
    reg_scope = st.selectbox("Choose analysis scope", scope_options, index=2, label_visibility="collapsed")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    st.markdown("""<div class="field-label"><span class="mark">02</span> Grounded index</div>""", unsafe_allow_html=True)
    st.markdown("""<div style="background:#0C1330; border-left:3px solid #35C98C; padding:10px; border-radius:6px; margin-bottom:8px; font-size:0.83rem;">
<b style="color:#E7ECF5;">1945 Constitution (UUD)</b><br><span style="color:#7C89A8;">Amendments I–IV indexed</span>
</div>
<div style="background:#0C1330; border-left:3px solid #35C98C; padding:10px; border-radius:6px; font-size:0.83rem;">
<b style="color:#E7ECF5;">Statutory hierarchy</b><br><span style="color:#7C89A8;">Act 12/2011 jo. Act 13/2022</span>
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    st.markdown("""<div class="field-label"><span class="mark">03</span> Methodology panel</div>""", unsafe_allow_html=True)
    st.session_state["show_methodology"] = st.toggle(
        "Show reasoning methodology", value=st.session_state["show_methodology"]
    )

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    st.markdown("""<div class="field-label"><span class="mark">04</span> Analysis history</div>""", unsafe_allow_html=True)

    history = st.session_state["analysis_history"]
    if not history:
        st.markdown("""<div style="font-size:0.76rem; color:#7C89A8; padding:6px 2px;">
No analyses run yet this session. Completed runs will appear here for recall and re-run.
</div>""", unsafe_allow_html=True)
    else:
        status_style = {
            "SUPPORTED": ("#35C98C", "rgba(53,201,140,0.16)"),
            "NOT SUPPORTED": ("#E5636B", "rgba(229,99,107,0.16)"),
            "REQUIRES HUMAN REVIEW": ("#F4CD6E", "rgba(232,179,61,0.16)"),
        }
        for idx, item in enumerate(reversed(history[-8:])):
            real_idx = len(history) - 1 - idx
            st_status = item.get("status", "REQUIRES HUMAN REVIEW")
            color, bg = status_style.get(st_status, ("#F4CD6E", "rgba(232,179,61,0.16)"))
            short_q = html.escape(item.get("query", "")[:68])
            if len(item.get("query", "")) > 68:
                short_q += "…"
            st.markdown(f"""<div class="history-card">
<div class="history-time">{item.get('timestamp','')}</div>
<div class="history-query">{short_q}</div>
<span class="history-status" style="background:{bg}; color:{color};">{st_status}</span>
</div>""", unsafe_allow_html=True)
            if st.button("Re-run this query", key=f"rerun_{real_idx}", use_container_width=True):
                st.session_state["rerun_requested"] = True
                st.session_state["pending_rerun_query"] = item.get("query", "")
                st.rerun()

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    if st.button("Reset workspace"):
        st.session_state["pdf_text"] = ""
        st.session_state["pdf_name"] = ""
        st.session_state["analysis_result"] = None
        st.session_state["chat_history"] = []
        st.session_state["welcome_dismissed"] = False
        st.rerun()

    st.caption("GovShield Intelligence Engine · v5.0")

# =============================================================================
# WELCOME PANEL
# =============================================================================
if not st.session_state["welcome_dismissed"]:
    st.markdown("""
    <div class="welcome-panel">
        <h2 class="welcome-title">Welcome to GovShield AI</h2>
        <p class="welcome-body">
            Your automated <b style="color:#E7ECF5;">legal &amp; policy intelligence assistant</b>.
            It analyzes legal cases, institutional regulations, and national constitutions using
            evidence-first grounded reasoning — never inventing an article that isn't in context.
        </p>
        <p class="welcome-cta">Upload a document or type your inquiry below to begin.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Launch analysis workspace"):
        st.session_state["welcome_dismissed"] = True
        st.rerun()

# =============================================================================
# METHODOLOGY PANEL (sidebar toggle)
# =============================================================================
if st.session_state["show_methodology"]:
    with st.expander("Reasoning methodology — how GovShield AI reaches a determination", expanded=True):
        rows = ""
        for i, (title, desc) in enumerate(METHODOLOGY_STEPS, start=1):
            rows += f"""<div class="method-row">
<div class="method-index">{i:02d}</div>
<div><div class="method-title">{html.escape(title)}</div><p class="method-desc">{html.escape(desc)}</p></div>
</div>"""
        st.markdown(f'<div class="card gold">{rows}</div>', unsafe_allow_html=True)
        st.markdown("""<div style="font-size:0.76rem; color:#7C89A8;">
This engine performs evidence-first retrieval reasoning, not independent legal judgment.
All outputs require review by qualified legal counsel before formal reliance.
</div>""", unsafe_allow_html=True)

# =============================================================================
# INPUT — DOCUMENT ATTACHMENT
# =============================================================================
st.markdown("""<div class="field-label"><span class="mark">A</span> Optional — policy or contract PDF</div>""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload policy or contract PDF", type=["pdf"], label_visibility="collapsed")

if uploaded_file is not None:
    st.session_state["welcome_dismissed"] = True
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

    char_note = ""
    if st.session_state["pdf_text"]:
        char_note = f' <span style="color:#7C89A8;">· {len(st.session_state["pdf_text"]):,} characters extracted</span>'

    st.markdown(f"""<div style="background:rgba(53,201,140,0.12); border:1px solid #35C98C; padding:8px 14px; border-radius:8px; font-size:0.83rem; color:#35C98C; margin:4px 0 12px 0;">
<span style="font-weight:700;">Active document:</span> {html.escape(st.session_state['pdf_name'])}{char_note}
</div>""", unsafe_allow_html=True)
else:
    st.session_state["pdf_text"] = ""
    st.session_state["pdf_name"] = ""
    st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

# =============================================================================
# INPUT — QUERY
# =============================================================================
st.markdown("""<div class="panel-frame">
<div style="display:flex; justify-content:space-between; align-items:center;">
<div class="field-label" style="margin-bottom:0 !important;"><span class="mark">B</span> Policy inquiry / case scenario — required</div>
<div style="font-size:0.74rem; color:#37B6E8; font-weight:600; display:flex; align-items:center;">
<span class="status-dot"></span>Reasoning engine ready
</div>
</div>
</div>""", unsafe_allow_html=True)

default_query_value = ""
if st.session_state.get("rerun_requested"):
    default_query_value = st.session_state.get("pending_rerun_query", "")
    st.info("Re-running a previous query from history — edit it below before executing again.")
    st.session_state["rerun_requested"] = False

user_query = st.text_area(
    "Type your legal inquiry",
    value=default_query_value,
    placeholder="Describe the policy scenario, case details, or regulatory question here…",
    height=140,
    label_visibility="collapsed",
)

if user_query.strip():
    st.session_state["welcome_dismissed"] = True

st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

# =============================================================================
# HELPERS — CONFIDENCE SCORING & CONSISTENCY GUARD
# =============================================================================

def compute_confidence(result: dict) -> tuple[int, str]:
    """Heuristic confidence score (0-100) from structured output signals."""
    score = 50
    status = str(result.get("recommendation_status", "")).upper()
    ra = result.get("rule_analysis", {}) or {}
    evidence = str(result.get("evidence", "")).strip()
    applicable_rule = str(result.get("applicable_rule", "")).strip()

    if status == "SUPPORTED":
        score += 20
    elif status == "NOT SUPPORTED":
        score += 12
    else:
        score -= 15

    if evidence and evidence.lower() not in ("-", "n/a", "none", "no direct text excerpt available"):
        score += 15
    else:
        score -= 20

    if applicable_rule and applicable_rule != "-":
        score += 8
    if ra.get("exception_detected"):
        score -= 4
    if ra.get("unresolved_conflict"):
        score -= 14

    score = max(5, min(97, score))
    if score >= 75:
        label = "High confidence"
    elif score >= 45:
        label = "Moderate confidence"
    else:
        label = "Low confidence — review advised"
    return score, label


def run_consistency_guard(result: dict) -> list[tuple[str, str]]:
    """Cross-checks the structured JSON for internal contradictions."""
    checks = []
    status = str(result.get("recommendation_status", "")).upper()
    ra = result.get("rule_analysis", {}) or {}
    evidence = str(result.get("evidence", "")).strip().lower()
    summary = str(result.get("recommendation_summary", "")).strip()
    reasoning = str(result.get("reasoning_conclusion", "")).strip()

    if status in ("SUPPORTED", "NOT SUPPORTED"):
        if not evidence or evidence in ("-", "n/a", "none", "no direct text excerpt available"):
            checks.append(("bad", f"Status is <b>{status}</b> but no direct evidence excerpt was returned — grounding inconsistency."))
        else:
            checks.append(("ok", f"Status <b>{status}</b> is backed by a direct evidence excerpt."))
    else:
        checks.append(("ok", "Status is Requires Human Review, consistent with absent or insufficient evidence."))

    if ra.get("unresolved_conflict") and status == "SUPPORTED":
        checks.append(("warn", "An unresolved normative conflict was detected, yet the recommendation is Supported — review the hierarchy reasoning."))
    elif ra.get("unresolved_conflict"):
        checks.append(("warn", "Unresolved normative conflict detected between provisions."))
    else:
        checks.append(("ok", "No unresolved normative conflict detected between general and specific provisions."))

    if len(summary) < 15:
        checks.append(("warn", "Executive summary is unusually short — may indicate incomplete reasoning."))
    if len(reasoning) < 25:
        checks.append(("warn", "Detailed rationale is unusually short relative to a formal legal determination."))
    if len(summary) >= 15 and len(reasoning) >= 25:
        checks.append(("ok", "Executive summary and detailed rationale both meet minimum completeness thresholds."))

    if ra.get("exception_detected") and (not ra.get("specific_provision") or str(ra.get("specific_provision")).strip() in ("-", "")):
        checks.append(("bad", "An exception was flagged as detected, but no specific provision was cited to support it."))
    elif ra.get("exception_detected"):
        checks.append(("ok", "Exception detected and supported by a cited specific provision."))

    return checks


def confidence_color(score: int) -> str:
    if score >= 75:
        return "#35C98C"
    elif score >= 45:
        return "#F4CD6E"
    return "#E5636B"


# =============================================================================
# EXECUTE
# =============================================================================
run_col1, run_col2 = st.columns([3, 1])
with run_col1:
    run_clicked = st.button("Run legal intelligence analysis")
with run_col2:
    quick_rerun_clicked = False
    if st.session_state["analysis_result"] is not None:
        quick_rerun_clicked = st.button("Re-run last", use_container_width=True)

trigger_analysis = run_clicked or quick_rerun_clicked

if trigger_analysis:
    st.session_state["welcome_dismissed"] = True
    effective_query = user_query.strip()
    if quick_rerun_clicked and not effective_query:
        effective_query = st.session_state.get("last_query", "")

    if not effective_query:
        st.warning("Please enter a legal inquiry or case scenario before proceeding.")
    else:
        with st.spinner("Analyzing legal hierarchy, cross-referencing provisions, and generating evidence-first reasoning…"):
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
{effective_query}
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
                st.session_state["analysis_result"] = parsed_result
                st.session_state["last_query"] = effective_query
                st.session_state["last_scope"] = reg_scope
                st.session_state["chat_history"] = []

                st.session_state["analysis_history"].append({
                    "timestamp": datetime.datetime.now().strftime("%H:%M · %d %b"),
                    "query": effective_query,
                    "scope": reg_scope,
                    "status": str(parsed_result.get("recommendation_status", "REQUIRES HUMAN REVIEW")).upper(),
                })

            except Exception as e:
                st.error(f"Technical analysis error: {e}")

# =============================================================================
# OUTPUT DASHBOARD
# =============================================================================
if st.session_state["analysis_result"]:
    result = st.session_state["analysis_result"]

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("""<div style="font-size:1.05rem; font-weight:800; color:#37B6E8; margin-bottom:16px; letter-spacing:0.6px; text-transform:uppercase;">
Analysis dashboard
</div>""", unsafe_allow_html=True)

    status = str(result.get("recommendation_status", "REQUIRES HUMAN REVIEW"))
    summary = html.escape(str(result.get("recommendation_summary", "")))

    if status == "SUPPORTED":
        st.markdown(f'<div class="status-banner supported">Recommendation: Supported — {summary}</div>', unsafe_allow_html=True)
    elif status == "NOT SUPPORTED":
        st.markdown(f'<div class="status-banner rejected">Recommendation: Not Supported — {summary}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-banner review">Status: Requires Human Review — insufficient direct evidence</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # ---------------- confidence meter + metrics ----------------
    conf_score, conf_label = compute_confidence(result)
    bar_color = confidence_color(conf_score)

    conf_col, metric_col1, metric_col2 = st.columns([2, 1, 1])
    with conf_col:
        st.markdown(f"""<div class="confidence-box">
<div class="confidence-top">
<span class="confidence-tag">Determination confidence</span>
<span class="confidence-num" style="color:{bar_color};">{conf_score}/100 · {conf_label}</span>
</div>
<div class="confidence-track"><div class="confidence-fill" style="width:{conf_score}%; background:linear-gradient(90deg, {bar_color}, {bar_color}CC);"></div></div>
<div class="confidence-note">Heuristic score from evidence presence, hierarchy conflicts, and output completeness — not a substitute for legal review.</div>
</div>""", unsafe_allow_html=True)
    with metric_col1:
        scope_short = reg_scope.split("—", 1)[0].strip() if "—" in reg_scope else reg_scope
        st.metric("Regulatory scope", scope_short)
    with metric_col2:
        ra_preview = result.get("rule_analysis", {}) or {}
        st.metric("Unresolved conflict", "Yes" if ra_preview.get("unresolved_conflict") else "No")

    # ---------------- consistency guard ----------------
    with st.expander("Consistency guard — internal contradiction check", expanded=(conf_score < 45)):
        guard_results = run_consistency_guard(result)
        mark = {"ok": "OK", "warn": "!!", "bad": "XX"}
        for severity, message in guard_results:
            st.markdown(f"""<div class="guard-row {severity}">
<span class="guard-mark">[{mark.get(severity, "--")}]</span>
<span class="guard-text">{message}</span>
</div>""", unsafe_allow_html=True)
        bad_count = sum(1 for s, _ in guard_results if s == "bad")
        warn_count = sum(1 for s, _ in guard_results if s == "warn")
        if bad_count:
            st.markdown(f'<div style="margin-top:10px; font-size:0.78rem; color:#E5636B;">{bad_count} critical inconsistency detected — treat as Requires Human Review regardless of stated status.</div>', unsafe_allow_html=True)
        elif warn_count:
            st.markdown(f'<div style="margin-top:10px; font-size:0.78rem; color:#F4CD6E;">{warn_count} soft warning(s) detected — a second read-through is recommended.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="margin-top:10px; font-size:0.78rem; color:#35C98C;">No structural inconsistencies detected in this output.</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # ---------------- tabs ----------------
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Summary & evidence",
        "Statutory reasoning",
        "Follow-up assistant",
        "Export brief",
        "Methodology & audit",
    ])

    applicable_rule = html.escape(str(result.get('applicable_rule', '-')))
    evidence_text = html.escape(str(result.get('evidence', 'No direct text excerpt available')))
    reasoning = html.escape(str(result.get('reasoning_conclusion', '-')))
    review_note = html.escape(str(result.get('review_note', 'N/A')))
    ra = result.get("rule_analysis", {})

    with tab1:
        r_col1, r_col2 = st.columns(2, gap="medium")
        with r_col1:
            st.markdown(f"""<div class="card gold">
<div class="card-head gold">Governing / applicable rule</div>
<div style="font-size:0.93rem; line-height:1.6; color:#E7ECF5;">{applicable_rule}</div>
</div>""", unsafe_allow_html=True)
        with r_col2:
            st.markdown(f"""<div class="card cyan">
<div class="card-head cyan">Citation &amp; direct legal evidence</div>
<div style="font-family:'JetBrains Mono', monospace; font-size:0.83rem; color:#6FE3D6; background:#060913; padding:12px; border-radius:8px; border:1px solid rgba(55,182,232,0.25);">{evidence_text}</div>
</div>""", unsafe_allow_html=True)

        st.markdown(f"""<div class="card emerald">
<div class="card-head emerald">Confidence &amp; scope snapshot</div>
<div style="font-size:0.86rem; line-height:1.7; color:#E7ECF5;">
<div><b>Confidence score:</b> {conf_score}/100 ({conf_label})</div>
<div><b>Regulatory scope applied:</b> {html.escape(reg_scope)}</div>
<div><b>Source document:</b> {html.escape(st.session_state['pdf_name']) if st.session_state['pdf_name'] else 'None — constitutional knowledge base only'}</div>
</div>
</div>""", unsafe_allow_html=True)

    with tab2:
        gen_prov = html.escape(str(ra.get('general_provision', '-')))
        spec_prov = html.escape(str(ra.get('specific_provision', '-')))
        exc_str = '<span style="color:#35C98C; font-weight:700;">Yes</span>' if ra.get('exception_detected') else '<span style="color:#E5636B; font-weight:700;">No</span>'
        conf_flag_str = '<span style="color:#F4CD6E; font-weight:700;">Yes</span>' if ra.get('unresolved_conflict') else '<span style="color:#35C98C; font-weight:700;">No</span>'

        st.markdown(f"""<div class="card cyan">
<div class="card-head cyan">Regulatory hierarchy &amp; norma analysis</div>
<div style="font-size:0.88rem; line-height:1.8; color:#E7ECF5;">
<div><b>General provision:</b> {gen_prov}</div>
<div><b>Specific provision / exception:</b> {spec_prov}</div>
<div><b>Exception detected:</b> {exc_str}</div>
<div><b>Normative conflict detected:</b> {conf_flag_str}</div>
</div>
</div>""", unsafe_allow_html=True)

        st.markdown(f"""<div class="card gold">
<div class="card-head gold">Detailed legal rationale &amp; conclusion</div>
<div style="font-size:0.92rem; line-height:1.6; color:#E7ECF5;">{reasoning}</div>
<div style="font-size:0.82rem; color:#B7C2D9; margin-top:14px; border-top:1px solid rgba(232,179,61,0.22); padding-top:8px;">
<b style="color:#E7ECF5;">Legal counsel advisory note:</b> {review_note}
</div>
</div>""", unsafe_allow_html=True)

        with st.expander("Applied legal principles — Lex Specialis / Lex Superior"):
            st.markdown("""<div style="font-size:0.84rem; line-height:1.8; color:#E7ECF5;">
<div><b style="color:#7ED0F2;">Lex Specialis Derogat Legi Generali:</b> a specific rule governing a particular situation overrides a general rule that would otherwise apply.</div>
<div><b style="color:#7ED0F2;">Lex Superior Derogat Legi Inferiori:</b> a rule issued by a higher-ranking authority overrides a conflicting rule issued by a lower-ranking authority.</div>
</div>""", unsafe_allow_html=True)

    with tab3:
        st.markdown("#### Interactive legal Q&A assistant")
        st.caption("Ask questions about this legal determination, uploaded document clauses, or relevant statutory rules.")

        for msg in st.session_state["chat_history"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if chat_input := st.chat_input("Ask a follow-up question regarding this case…"):
            st.session_state["chat_history"].append({"role": "user", "content": chat_input})
            with st.chat_message("user"):
                st.markdown(chat_input)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing follow-up legal question…"):
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

    with tab4:
        st.markdown("#### Download formal legal determination brief")
        guard_export = run_consistency_guard(result)
        guard_lines = "\n".join(
            f"  [{sev.upper()}] {msg.replace('<b>', '').replace('</b>', '')}" for sev, msg in guard_export
        )
        report_text = f"""================================================================================
GOVSHIELD AI - FORMAL LEGAL & REGULATORY DETERMINATION REPORT
================================================================================
Status: {status}
Confidence Score: {conf_score}/100 ({conf_label})
Regulatory Scope: {reg_scope}
Attached Document: {st.session_state['pdf_name'] or 'None'}
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

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

CONSISTENCY GUARD REPORT:
{guard_lines}

LEGAL COUNSEL ADVISORY NOTE:
{result.get('review_note')}
================================================================================
Generated automatically by GovShield AI Engine v5.0
================================================================================
"""
        st.download_button(
            label="Download formal legal report (.txt)",
            data=report_text,
            file_name="GovShield_Executive_Legal_Brief.txt",
            mime="text/plain"
        )

        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
        st.markdown("""<div class="card cyan">
<div class="card-head cyan">Export notes</div>
<div style="font-size:0.84rem; line-height:1.6; color:#B7C2D9;">
The exported brief includes the full consistency guard report so reviewing counsel can see exactly which automated checks passed, warned, or failed for this determination.
</div>
</div>""", unsafe_allow_html=True)

    with tab5:
        st.markdown("#### Methodology & audit trail")
        st.caption("A transparent record of how this determination was produced, plus the running session history.")

        rows = ""
        for i, (title, desc) in enumerate(METHODOLOGY_STEPS, start=1):
            rows += f"""<div class="method-row">
<div class="method-index">{i:02d}</div>
<div><div class="method-title">{html.escape(title)}</div><p class="method-desc">{html.escape(desc)}</p></div>
</div>"""
        st.markdown(f'<div class="card gold">{rows}</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="field-label" style="color:#7ED0F2 !important;">Session audit trail</div>', unsafe_allow_html=True)

        audit_history = st.session_state["analysis_history"]
        if not audit_history:
            st.info("No prior analyses logged yet in this session.")
        else:
            status_style = {
                "SUPPORTED": ("#35C98C", "rgba(53,201,140,0.16)"),
                "NOT SUPPORTED": ("#E5636B", "rgba(229,99,107,0.16)"),
                "REQUIRES HUMAN REVIEW": ("#F4CD6E", "rgba(232,179,61,0.16)"),
            }
            for i, item in enumerate(reversed(audit_history), start=1):
                st_status = item.get("status", "REQUIRES HUMAN REVIEW")
                color, bg = status_style.get(st_status, ("#F4CD6E", "rgba(232,179,61,0.16)"))
                st.markdown(f"""<div class="history-card">
<div class="history-time">#{len(audit_history) - i + 1} · {item.get('timestamp','')} · {html.escape(item.get('scope',''))}</div>
<div class="history-query">{html.escape(item.get('query','')[:160])}</div>
<span class="history-status" style="background:{bg}; color:{color};">{st_status}</span>
</div>""", unsafe_allow_html=True)

# =============================================================================
# FOOTER
# =============================================================================
st.markdown(f"""<div class="footer-strip">
<b>GovShield AI Intelligence Engine v5.0</b> — evidence-first grounded legal reasoning. Outputs are decision-support only and require review by qualified legal counsel.<br>
Session analyses logged: {len(st.session_state["analysis_history"])}
</div>""", unsafe_allow_html=True)
