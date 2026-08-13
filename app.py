import html
import json
import time
import random
import datetime
import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

# ===========================================================
# 1. PAGE CONFIG
# ===========================================================
st.set_page_config(
    page_title="GOVSHIELD AI | Legal Decision Intelligence",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ===========================================================
# 2. READ API KEYS & SECRETS
# ===========================================================
try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    BASE_URL = st.secrets.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
except KeyError:
    st.error("❌ Key 'GROQ_API_KEY' was not found in .streamlit/secrets.toml!")
    st.stop()
except Exception as e:
    st.error(f"❌ Error reading secrets.toml: {e}")
    st.stop()

# ===========================================================
# 3. UNIVERSAL THEME STYLES
# ===========================================================
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

* {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

html, body {
    color: #F1F5F9 !important;
}

/* ===================== HEADER & NAV ===================== */
header[data-testid="stHeader"] {
    background: #040711 !important;
    background-color: #040711 !important;
    z-index: 99999 !important;
    border-bottom: 1px solid rgba(56, 189, 248, 0.15);
}

div[data-testid="stToolbar"] {
    background: transparent !important;
}

div[data-testid="stDecoration"] {
    background: linear-gradient(90deg, #EAB308, #38BDF8) !important;
}

button[data-testid="stSidebarCollapseButton"],
button[data-testid="baseButton-headerNoPadding"],
button[data-testid="stBaseButton-headerNoPadding"] {
    background-color: #0A142F !important;
    border: 1px solid rgba(234, 179, 8, 0.6) !important;
    color: #FDE047 !important;
    border-radius: 8px !important;
    box-shadow: 0 0 12px rgba(234, 179, 8, 0.25) !important;
}

button[data-testid="stSidebarCollapseButton"]:hover,
button[data-testid="baseButton-headerNoPadding"]:hover,
button[data-testid="stBaseButton-headerNoPadding"]:hover {
    border-color: #38BDF8 !important;
    background-color: #0D1B3E !important;
    color: #7DD3FC !important;
}

button[data-testid="stSidebarCollapseButton"] svg,
button[data-testid="baseButton-headerNoPadding"] svg,
button[data-testid="stBaseButton-headerNoPadding"] svg {
    fill: #FDE047 !important;
    color: #FDE047 !important;
}

#MainMenu, footer {
    background-color: #040711 !important;
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
    position: relative;
    z-index: 2;
}

/* ===================== BASE BACKGROUND ===================== */
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
    color: #F1F5F9 !important;
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

/* ===================== SIDEBAR ===================== */
section[data-testid="stSidebar"] {
    background-color: #0A1228 !important;
    border-right: 1px solid rgba(56, 189, 248, 0.25) !important;
}

section[data-testid="stSidebar"] > div {
    background-color: #0A1228 !important;
}

section[data-testid="stSidebar"] * {
    color: #F1F5F9 !important;
}

section[data-testid="stSidebar"] label {
    color: #CBD5E1 !important;
}

section[data-testid="stSidebar"] .stMarkdown p {
    color: #CBD5E1 !important;
}

section[data-testid="stSidebar"] hr {
    border-color: rgba(56, 189, 248, 0.2) !important;
}

/* ===================== GENERIC TEXT ELEMENTS ===================== */
p, span, div, li, label, h1, h2, h3, h4, h5, h6 {
    color: #F1F5F9;
}

a, a:visited {
    color: #7DD3FC !important;
    text-decoration: none;
}
a:hover {
    color: #FDE047 !important;
    text-decoration: underline;
}

hr {
    border-color: rgba(56, 189, 248, 0.2) !important;
}

::selection {
    background: rgba(234, 179, 8, 0.35);
    color: #0A1228;
}

/* Scrollbars */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}
::-webkit-scrollbar-track {
    background: #080E21;
}
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #38BDF8, #EAB308);
    border-radius: 8px;
}
::-webkit-scrollbar-thumb:hover {
    background: #FDE047;
}

/* ===================== BADGE / LABELS ===================== */
.floating-topleft-badge {
    position: fixed;
    top: 50px;
    left: 16px;
    z-index: 9999;
    display: flex;
    align-items: center;
    gap: 9px;
    background: #080E21;
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

/* ===================== INPUTS: TEXTAREA / TEXT INPUT ===================== */
textarea, .stTextArea textarea {
    background-color: #0A142F !important;
    color: #F1F5F9 !important;
    font-size: 0.98rem !important;
    font-weight: 500 !important;
    border: 1.5px solid #38BDF8 !important;
    border-radius: 12px !important;
    padding: 14px !important;
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.25) !important;
    caret-color: #FDE047 !important;
}

textarea:focus, .stTextArea textarea:focus {
    border-color: #FDE047 !important;
    box-shadow: 0 0 22px rgba(253, 224, 71, 0.4) !important;
    background-color: #0D1B3E !important;
}

textarea::placeholder {
    color: #7C8AA6 !important;
    opacity: 1 !important;
}

input[type="text"], input[type="number"], input[type="password"],
.stTextInput input, .stNumberInput input {
    background-color: #0A142F !important;
    color: #F1F5F9 !important;
    border: 1.5px solid #38BDF8 !important;
    border-radius: 10px !important;
    caret-color: #FDE047 !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #FDE047 !important;
    box-shadow: 0 0 16px rgba(253, 224, 71, 0.35) !important;
}
input::placeholder {
    color: #7C8AA6 !important;
    opacity: 1 !important;
}

.stNumberInput button {
    background-color: #0D1B3E !important;
    border-color: #38BDF8 !important;
    color: #7DD3FC !important;
}

/* ===================== FILE UPLOADER ===================== */
section[data-testid="stFileUploader"] {
    background-color: #0A142F !important;
    border: 1.5px solid #EAB308 !important;
    border-radius: 12px !important;
    padding: 6px 12px !important;
}
section[data-testid="stFileUploader"] section {
    background-color: #0A142F !important;
    border: 1px dashed rgba(234, 179, 8, 0.5) !important;
    color: #CBD5E1 !important;
}
section[data-testid="stFileUploader"] small {
    color: #94A3B8 !important;
}
section[data-testid="stFileUploader"] button {
    background-color: #0D1B3E !important;
    color: #FDE047 !important;
    border: 1px solid #EAB308 !important;
}
div[data-testid="stFileUploaderDropzone"] {
    background-color: #0A142F !important;
}
div[data-testid="stFileUploaderDropzoneInstructions"] span,
div[data-testid="stFileUploaderDropzoneInstructions"] small {
    color: #CBD5E1 !important;
}
div[data-testid="stFileUploaderFile"] {
    background-color: #0D1B3E !important;
    color: #F1F5F9 !important;
    border-radius: 8px;
}

/* ===================== SELECTBOX / MULTISELECT ===================== */
div[data-baseweb="select"] > div {
    background-color: #0A142F !important;
    border: 1.5px solid #38BDF8 !important;
    color: #F1F5F9 !important;
    border-radius: 10px !important;
}
div[data-baseweb="select"] span {
    color: #F1F5F9 !important;
}
div[data-baseweb="popover"] {
    background-color: #0D1B3E !important;
}
ul[data-testid="stSelectboxVirtualDropdown"] {
    background-color: #0D1B3E !important;
    border: 1px solid rgba(56, 189, 248, 0.4) !important;
}
ul[data-testid="stSelectboxVirtualDropdown"] li {
    background-color: #0D1B3E !important;
    color: #F1F5F9 !important;
}
ul[data-testid="stSelectboxVirtualDropdown"] li:hover {
    background-color: #12234A !important;
    color: #FDE047 !important;
}
div[data-baseweb="tag"] {
    background-color: #0284C7 !important;
    color: #F1F5F9 !important;
}

/* ===================== BUTTONS ===================== */
div.stButton > button, div.stDownloadButton > button, div.stFormSubmitButton > button {
    background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%) !important;
    color: #F8FAFC !important;
    font-weight: 800 !important;
    font-size: 0.95rem !important;
    border: 1px solid #38BDF8 !important;
    border-radius: 10px !important;
    padding: 14px 28px !important;
    box-shadow: 0 0 20px rgba(56, 189, 248, 0.4) !important;
    width: 100% !important;
    text-transform: uppercase;
    transition: all 0.2s ease-in-out;
}
div.stButton > button:hover, div.stDownloadButton > button:hover, div.stFormSubmitButton > button:hover {
    background: linear-gradient(135deg, #0369A1 0%, #0284C7 100%) !important;
    border-color: #FDE047 !important;
    box-shadow: 0 0 26px rgba(253, 224, 71, 0.45) !important;
    color: #FDE047 !important;
}
div.stButton > button:disabled {
    background: #0D1B3E !important;
    color: #64748B !important;
    border-color: #1E293B !important;
    box-shadow: none !important;
}
div.stButton > button p, div.stDownloadButton > button p {
    color: inherit !important;
}

button[kind="secondary"] {
    background: #0A142F !important;
    color: #7DD3FC !important;
    border: 1.5px solid rgba(56, 189, 248, 0.5) !important;
    box-shadow: none !important;
}
button[kind="secondary"]:hover {
    background: #0D1B3E !important;
    border-color: #FDE047 !important;
    color: #FDE047 !important;
}

/* ===================== CHECKBOX / RADIO / TOGGLE ===================== */
.stCheckbox label, .stRadio label {
    color: #F1F5F9 !important;
}
.stCheckbox p, .stRadio p {
    color: #F1F5F9 !important;
}
[data-testid="stCheckbox"] svg {
    fill: #38BDF8 !important;
}
.stCheckbox [data-baseweb="checkbox"] > div:first-child {
    background-color: #0A142F !important;
    border-color: #38BDF8 !important;
}
.stCheckbox [data-baseweb="checkbox"] input:checked ~ div {
    background-color: #EAB308 !important;
    border-color: #EAB308 !important;
}
.stRadio [role="radiogroup"] label span:first-child {
    background-color: #0A142F !important;
    border-color: #38BDF8 !important;
}
[data-testid="stWidgetLabel"] p {
    color: #CBD5E1 !important;
    font-weight: 600 !important;
}
[data-baseweb="radio"] div:first-child {
    background-color: #0A142F !important;
    border-color: #38BDF8 !important;
}

.stToggle [data-baseweb="checkbox"] span {
    background-color: #0A142F !important;
}
.stToggle [aria-checked="true"] {
    background-color: #EAB308 !important;
}

/* ===================== SLIDER ===================== */
div[data-testid="stSlider"] div[role="slider"] {
    background-color: #FDE047 !important;
    border: 2px solid #EAB308 !important;
    box-shadow: 0 0 10px rgba(253, 224, 71, 0.6) !important;
}
div[data-testid="stSlider"] > div > div > div {
    background: #0A142F !important;
}
div[data-testid="stSlider"] > div > div > div > div {
    background: linear-gradient(90deg, #0284C7, #38BDF8) !important;
}
div[data-testid="stTickBar"] {
    background: transparent !important;
}
div[data-testid="stTickBarMin"], div[data-testid="stTickBarMax"] {
    color: #94A3B8 !important;
}
div[data-testid="stThumbValue"] {
    background-color: #0D1B3E !important;
    color: #FDE047 !important;
    border: 1px solid #EAB308 !important;
}

/* ===================== PROGRESS BAR ===================== */
div[data-testid="stProgress"] > div {
    background-color: #0A142F !important;
    border-radius: 8px;
}
div[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #EAB308, #38BDF8) !important;
    border-radius: 8px;
}

/* ===================== METRIC ===================== */
div[data-testid="stMetric"] {
    background-color: #0A142F !important;
    border: 1px solid rgba(56, 189, 248, 0.35) !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
    box-shadow: 0 0 14px rgba(56, 189, 248, 0.12);
}
div[data-testid="stMetricLabel"] {
    color: #94A3B8 !important;
    font-weight: 700 !important;
}
div[data-testid="stMetricValue"] {
    color: #FDE047 !important;
    font-weight: 800 !important;
}
div[data-testid="stMetricDelta"] {
    color: #34D399 !important;
}
div[data-testid="stMetricDelta"] svg {
    fill: #34D399 !important;
}

/* ===================== EXPANDER ===================== */
details[data-testid="stExpander"], .streamlit-expanderHeader {
    background-color: #0A142F !important;
    border: 1px solid rgba(234, 179, 8, 0.35) !important;
    border-radius: 12px !important;
}
details[data-testid="stExpander"] summary {
    background-color: #0A142F !important;
    color: #FDE047 !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
}
details[data-testid="stExpander"] summary:hover {
    color: #38BDF8 !important;
}
details[data-testid="stExpander"] summary svg {
    fill: #FDE047 !important;
}
details[data-testid="stExpander"] > div {
    background-color: #080E21 !important;
    border-top: 1px solid rgba(234, 179, 8, 0.2) !important;
    color: #F1F5F9 !important;
}

/* ===================== DATAFRAME / TABLE ===================== */
div[data-testid="stDataFrame"], div[data-testid="stTable"] {
    background-color: #0A142F !important;
    border: 1px solid rgba(56, 189, 248, 0.3) !important;
    border-radius: 10px !important;
}
div[data-testid="stDataFrame"] * {
    color: #F1F5F9 !important;
}
.stDataFrame [data-testid="stElementToolbar"] {
    background-color: #0D1B3E !important;
}
table {
    background-color: #0A142F !important;
    color: #F1F5F9 !important;
}
thead tr th {
    background-color: #0D1B3E !important;
    color: #FDE047 !important;
    border-color: rgba(56, 189, 248, 0.25) !important;
}
tbody tr td {
    background-color: #0A142F !important;
    color: #F1F5F9 !important;
    border-color: rgba(56, 189, 248, 0.15) !important;
}
tbody tr:hover td {
    background-color: #0D1B3E !important;
}

/* ===================== CODE BLOCK ===================== */
code {
    background-color: #0A142F !important;
    color: #67E8F9 !important;
    border-radius: 4px;
    padding: 2px 6px;
    font-family: 'JetBrains Mono', monospace !important;
}
pre {
    background-color: #070C1A !important;
    border: 1px solid rgba(56, 189, 248, 0.25) !important;
    border-radius: 10px !important;
}
pre code {
    background-color: transparent !important;
    color: #67E8F9 !important;
}
div[data-testid="stCodeBlock"] {
    background-color: #070C1A !important;
    border: 1px solid rgba(56, 189, 248, 0.25) !important;
    border-radius: 10px !important;
}
div[data-testid="stCodeBlock"] button {
    background-color: #0D1B3E !important;
    color: #7DD3FC !important;
}

/* ===================== TOOLTIP ===================== */
div[data-baseweb="tooltip"] {
    background-color: #0D1B3E !important;
    color: #FDE047 !important;
    border: 1px solid rgba(234, 179, 8, 0.5) !important;
    border-radius: 8px !important;
}
[data-testid="stTooltipIcon"] svg {
    fill: #38BDF8 !important;
}
[data-testid="stTooltipHoverTarget"] svg {
    fill: #38BDF8 !important;
}

/* ===================== TABS ===================== */
button[data-baseweb="tab"] {
    background-color: #0A142F !important;
    color: #94A3B8 !important;
    border-radius: 8px 8px 0 0 !important;
    font-weight: 700 !important;
}
button[data-baseweb="tab"]:hover {
    color: #7DD3FC !important;
    background-color: #0D1B3E !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background-color: #0D1B3E !important;
    color: #FDE047 !important;
    border-bottom: 2px solid #EAB308 !important;
}
div[data-baseweb="tab-highlight"] {
    background-color: #EAB308 !important;
}
div[data-baseweb="tab-border"] {
    background-color: rgba(56, 189, 248, 0.2) !important;
}
div[data-testid="stTabs"] {
    color: #F1F5F9 !important;
}

/* ===================== ALERTS / TOAST / SPINNER ===================== */
div[data-testid="stAlert"] {
    border-radius: 10px !important;
}
div[data-testid="stAlertContentInfo"], div[data-baseweb="notification"] {
    background-color: rgba(56, 189, 248, 0.12) !important;
    color: #7DD3FC !important;
}
div[data-testid="stAlertContentSuccess"] {
    background-color: rgba(16, 185, 129, 0.14) !important;
    color: #34D399 !important;
}
div[data-testid="stAlertContentWarning"] {
    background-color: rgba(234, 179, 8, 0.14) !important;
    color: #FDE047 !important;
}
div[data-testid="stAlertContentError"] {
    background-color: rgba(239, 68, 68, 0.14) !important;
    color: #F87171 !important;
}
div[data-testid="stAlert"] p, div[data-testid="stAlert"] span {
    color: inherit !important;
}
div[data-testid="stToast"] {
    background-color: #0D1B3E !important;
    color: #F1F5F9 !important;
    border: 1px solid rgba(234, 179, 8, 0.4) !important;
}
div[data-testid="stSpinner"] > div {
    color: #FDE047 !important;
}
div[data-testid="stSpinner"] svg {
    color: #38BDF8 !important;
}

/* ===================== CHAT ELEMENTS ===================== */
div[data-testid="stChatMessage"] {
    background-color: #0A142F !important;
    border: 1px solid rgba(56, 189, 248, 0.25) !important;
    border-radius: 12px !important;
    color: #F1F5F9 !important;
}
div[data-testid="stChatMessage"] p {
    color: #F1F5F9 !important;
}
div[data-testid="stChatInput"] {
    background-color: #0A142F !important;
    border: 1.5px solid #38BDF8 !important;
    border-radius: 12px !important;
}
div[data-testid="stChatInput"] textarea {
    background-color: transparent !important;
    color: #F1F5F9 !important;
}
div[data-testid="stChatInput"] button {
    background-color: #0284C7 !important;
}
div[data-testid="stChatInputSubmitButton"] svg {
    fill: #F1F5F9 !important;
}
div[data-testid="stBottomBlockContainer"] {
    background-color: #040711 !important;
}
div[data-testid="stBottom"] {
    background-color: #040711 !important;
}

/* ===================== POPOVER / MENU ===================== */
div[data-testid="stPopover"] button {
    background-color: #0A142F !important;
    color: #FDE047 !important;
    border: 1px solid rgba(234, 179, 8, 0.4) !important;
}
ul[role="listbox"] {
    background-color: #0D1B3E !important;
}
li[role="option"] {
    color: #F1F5F9 !important;
}
li[role="option"]:hover {
    background-color: #12234A !important;
    color: #FDE047 !important;
}

/* ===================== CAPTION / SMALL TEXT ===================== */
.stCaption, [data-testid="stCaptionContainer"] {
    color: #7C8AA6 !important;
}

/* ===================== HEADER TASKBAR ===================== */
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
    background: linear-gradient(120deg, #E2E8F0 0%, #FDE047 42%, #EAB308 55%, #E2E8F0 100%);
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
    background: #0E1A38;
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

.ai-search-frame {
    background: #0A142F;
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
    animation: pulseDot 1.6s ease-in-out infinite;
}
@keyframes pulseDot {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.35; }
}

.lexis-card-cyan {
    background: #0E1A38;
    border: 1px solid rgba(56, 189, 248, 0.4);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
    color: #F1F5F9 !important;
}

.lexis-card-gold {
    background: #0E1A38;
    border: 1px solid rgba(234, 179, 8, 0.4);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
    color: #F1F5F9 !important;
}

.lexis-card-emerald {
    background: #0E1A38;
    border: 1px solid rgba(16, 185, 129, 0.4);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
    color: #F1F5F9 !important;
}

.lexis-card-rose {
    background: #0E1A38;
    border: 1px solid rgba(239, 68, 68, 0.4);
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

.card-title-emerald {
    font-size: 0.85rem;
    font-weight: 800;
    color: #34D399 !important;
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

/* ===================== CONFIDENCE METER ===================== */
.confidence-wrap {
    background: #0A142F;
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 16px;
}
.confidence-label-row {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 8px;
}
.confidence-label {
    font-size: 0.82rem;
    font-weight: 800;
    letter-spacing: 0.6px;
    color: #38BDF8 !important;
    text-transform: uppercase;
}
.confidence-value {
    font-size: 1.05rem;
    font-weight: 800;
}
.confidence-track {
    width: 100%;
    height: 10px;
    background-color: #070C1A;
    border-radius: 999px;
    overflow: hidden;
    border: 1px solid rgba(56, 189, 248, 0.2);
}
.confidence-fill {
    height: 100%;
    border-radius: 999px;
}
.confidence-caption {
    font-size: 0.75rem;
    color: #94A3B8 !important;
    margin-top: 6px;
}

/* ===================== CONSISTENCY GUARD ===================== */
.guard-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 12px;
    border-radius: 8px;
    background-color: #070C1A;
    margin-bottom: 6px;
    border-left: 3px solid #334155;
}
.guard-row.ok { border-left-color: #10B981; }
.guard-row.warn { border-left-color: #EAB308; }
.guard-row.bad { border-left-color: #EF4444; }
.guard-icon { font-size: 1rem; flex-shrink: 0; }
.guard-text { font-size: 0.85rem; color: #E2E8F0 !important; }
.guard-text b { color: #F8FAFC !important; }

/* ===================== HISTORY PANEL ===================== */
.history-item {
    background-color: #0A142F;
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 8px;
}
.history-item .h-time {
    font-size: 0.7rem;
    color: #7C8AA6 !important;
    font-family: 'JetBrains Mono', monospace;
}
.history-item .h-query {
    font-size: 0.85rem;
    color: #E2E8F0 !important;
    margin: 4px 0;
}
.history-item .h-status {
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.4px;
    padding: 2px 10px;
    border-radius: 999px;
    display: inline-block;
}

/* ===================== METHODOLOGY PANEL ===================== */
.method-step {
    display: flex;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid rgba(56, 189, 248, 0.12);
}
.method-step:last-child { border-bottom: none; }
.method-num {
    flex-shrink: 0;
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: linear-gradient(135deg, #EAB308, #CA8A04);
    color: #0A1228 !important;
    font-weight: 800;
    font-size: 0.78rem;
    display: flex;
    align-items: center;
    justify-content: center;
}
.method-body b {
    color: #7DD3FC !important;
    font-size: 0.88rem;
}
.method-body p {
    color: #CBD5E1 !important;
    font-size: 0.82rem;
    margin: 2px 0 0 0;
    line-height: 1.5;
}

/* ===================== ROBOT WELCOME CARD ===================== */
.robot-welcome-card {
    background: linear-gradient(135deg, #0A142F 0%, #0F1C3F 100%);
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

/* ===================== FOOTER STRIP ===================== */
.gov-footer {
    margin-top: 40px;
    padding: 18px 20px;
    border-top: 1px solid rgba(56, 189, 248, 0.2);
    text-align: center;
    color: #64748B !important;
    font-size: 0.75rem;
}
.gov-footer b { color: #94A3B8 !important; }
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

# ===========================================================
# 4. HEADER TASKBAR WITH GOLD SHIELD & LEGAL ICON
# ===========================================================
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
<div class="brand-name">🛡️ GOVSHIELD AI v4.0</div>
<div class="brand-desc">Global Legal Analysis System</div>
</div>
</div>
<div class="letterhead-divider">
<span class="lh-line"></span>
</div>""", unsafe_allow_html=True)

# ===========================================================
# 5. BUILT-IN GROUNDED KNOWLEDGE BASE
# ===========================================================
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
    ("Context Assembly", "Combine the built-in constitutional knowledge base, the selected regulatory scope, and any uploaded PDF text into one grounded context window."),
    ("Hierarchy Mapping", "Rank every identified provision by statutory hierarchy (UUD 1945 → TAP MPR → UU/Perppu → PP → Perpres → regional/institutional decrees)."),
    ("Principle Application", "Apply Lex Specialis Derogat Legi Generali and Lex Superior Derogat Legi Inferiori to resolve any apparent overlap between general and specific provisions."),
    ("Evidence Extraction", "Pull direct clause-level citations only from the grounded context — the model is instructed never to invent articles."),
    ("Consistency Guard", "Cross-check the model's structured JSON output for internal contradictions before it is rendered (see Consistency Guard panel)."),
    ("Confidence Scoring", "Derive a heuristic confidence score from evidence presence, conflict flags, and recommendation status."),
]

# ===========================================================
# 6. SAFE SESSION STATE INITIALIZATION (FIXED BUG)
# ===========================================================
DEFAULT_STATE = {
    "pdf_text": "",
    "pdf_name": "",
    "robot_dismissed": False,
    "analysis_result": None,
    "chat_history": [],
    "analysis_history": [],
    "last_query": "",
    "last_scope": "",
    "rerun_requested": False,
    "pending_rerun_query": "",
    "pending_rerun_scope": "",
    "show_methodology": False,
}

for key, default_val in DEFAULT_STATE.items():
    if key not in st.session_state:
        if isinstance(default_val, list):
            st.session_state[key] = list(default_val)
        elif isinstance(default_val, dict):
            st.session_state[key] = dict(default_val)
        else:
            st.session_state[key] = default_val

# ===========================================================
# 7. SIDEBAR CONFIGURATION
# ===========================================================
with st.sidebar:
    st.markdown("""<div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; padding: 12px; border-radius: 10px; margin-bottom: 16px;">
<b style="color:#34D399; font-size:0.88rem;">⚡ SECRETS CONNECTED</b><br>
<span style="font-size:0.75rem; color:#94A3B8;">GROQ API Key Authenticated</span>
</div>""", unsafe_allow_html=True)

    st.markdown("""<div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#EAB308" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
<span style="font-weight:700; color:#EAB308; font-size:0.88rem;">REGULATORY SCOPE SELECTOR</span>
</div>""", unsafe_allow_html=True)

    scope_options = [
        "🏛️ Macro (National Level - UUD 1945 & Acts)",
        "🎓 Meso (Institutional / Campus Policy)",
        "⚖️ Harmonization (National vs Local Alignment)"
    ]
    reg_scope = st.selectbox(
        "Choose Analysis Scope",
        scope_options,
        index=2
    )

    st.markdown('<div class="lexis-divider"></div>', unsafe_allow_html=True)

    st.markdown("""<div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
<span style="font-weight:700; color:#38BDF8; font-size:0.88rem;">GROUNDED INDEX ACTIVE</span>
</div>""", unsafe_allow_html=True)

    st.markdown("""<div style="background: #0A142F; border-left: 3px solid #10B981; padding: 10px; border-radius: 6px; margin-bottom: 8px; font-size: 0.85rem;">
<b style="color:#F1F5F9;">§ 1945 Constitution (UUD)</b><br><span style="color:#94A3B8;">Amendments I-IV Indexed</span>
</div>
<div style="background: #0A142F; border-left: 3px solid #10B981; padding: 10px; border-radius: 6px; font-size: 0.85rem;">
<b style="color:#F1F5F9;">§ Statutory Hierarchy</b><br><span style="color:#94A3B8;">Act 12/2011 jo Act 13/2022</span>
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="lexis-divider"></div>', unsafe_allow_html=True)

    st.markdown("""<div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FDE047" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
<span style="font-weight:700; color:#FDE047; font-size:0.88rem;">METHODOLOGY PANEL</span>
</div>""", unsafe_allow_html=True)

    st.session_state["show_methodology"] = st.toggle(
        "Show reasoning methodology",
        value=st.session_state.get("show_methodology", False),
    )

    st.markdown('<div class="lexis-divider"></div>', unsafe_allow_html=True)

    st.markdown("""<div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#7DD3FC" stroke-width="2"><path d="M3 3v5h5"/><path d="M3.05 13A9 9 0 1 0 6 5.3L3 8"/><path d="M12 7v5l4 2"/></svg>
<span style="font-weight:700; color:#7DD3FC; font-size:0.88rem;">ANALYSIS HISTORY</span>
</div>""", unsafe_allow_html=True)

    history = st.session_state.get("analysis_history", [])
    if not history:
        st.markdown("""<div style="font-size:0.78rem; color:#7C8AA6; padding:8px 2px;">
No analyses run yet this session. Completed runs will appear here for quick recall and re-run.
</div>""", unsafe_allow_html=True)
    else:
        status_color_map = {
            "SUPPORTED": ("#34D399", "rgba(16,185,129,0.18)"),
            "NOT SUPPORTED": ("#F87171", "rgba(239,68,68,0.18)"),
            "REQUIRES HUMAN REVIEW": ("#FDE047", "rgba(234,179,8,0.18)"),
        }
        for idx, item in enumerate(reversed(history[-8:])):
            real_idx = len(history) - 1 - idx
            st_status = item.get("status", "REQUIRES HUMAN REVIEW")
            color, bg = status_color_map.get(st_status, ("#FDE047", "rgba(234,179,8,0.18)"))
            short_q = html.escape(item.get("query", "")[:70])
            if len(item.get("query", "")) > 70:
                short_q += "…"
            st.markdown(f"""<div class="history-item">
<div class="h-time">{html.escape(item.get('timestamp',''))}</div>
<div class="h-query">{short_q}</div>
<span class="h-status" style="background:{bg}; color:{color};">{html.escape(st_status)}</span>
</div>""", unsafe_allow_html=True)
            if st.button(f"↺ Re-run this query", key=f"rerun_{real_idx}", use_container_width=True):
                st.session_state["rerun_requested"] = True
                st.session_state["pending_rerun_query"] = item.get("query", "")
                st.session_state["pending_rerun_scope"] = item.get("scope", scope_options[2])
                st.rerun()

    st.markdown('<div class="lexis-divider"></div>', unsafe_allow_html=True)

    if st.button("🗑️ RESET WORKSPACE DATA"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.caption("🛡️ **GovShield Intelligence Engine v4.0**")

# ===========================================================
# 8. ROBOT WELCOME OVERLAY
# ===========================================================
if not st.session_state.get("robot_dismissed", False):
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
            I am your automated <b style="color:#F1F5F9;">Legal &amp; Policy Intelligence Assistant</b>. I analyze legal cases, institutional regulations, and national constitutions using evidence-first grounded reasoning.
        </p>
        <p style="color:#38BDF8; font-size:0.85rem; font-weight:600; margin-bottom:0;">
            👇 Upload a document or type your inquiry below to launch the analysis workspace!
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 LAUNCH LEGAL ANALYSIS WORKSPACE"):
        st.session_state["robot_dismissed"] = True
        st.rerun()

# ===========================================================
# 8B. METHODOLOGY PANEL
# ===========================================================
if st.session_state.get("show_methodology", False):
    with st.expander("🧭 REASONING METHODOLOGY — HOW GOVSHIELD AI ARRIVES AT A DETERMINATION", expanded=True):
        steps_html = ""
        for i, (title, desc) in enumerate(METHODOLOGY_STEPS, start=1):
            steps_html += f"""<div class="method-step">
<div class="method-num">{i}</div>
<div class="method-body"><b>{html.escape(title)}</b><p>{html.escape(desc)}</p></div>
</div>"""
        st.markdown(f'<div class="lexis-card-gold">{steps_html}</div>', unsafe_allow_html=True)
        st.markdown("""<div style="font-size:0.78rem; color:#94A3B8;">
⚠️ This engine performs evidence-first retrieval reasoning, not independent legal judgment. All outputs require review by qualified legal counsel before being relied upon in formal proceedings.
</div>""", unsafe_allow_html=True)

# ===========================================================
# 9. INPUT AREA (SAFE PDF EXTRATION)
# ===========================================================
st.markdown("""<div class="custom-label">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#EAB308" stroke-width="2.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
📄 OPTIONAL: SPECIFIC POLICY / PDF DOCUMENT ATTACHMENT
</div>""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload Policy or Contract PDF", type=["pdf"], label_visibility="collapsed"
)

if uploaded_file is not None:
    st.session_state["robot_dismissed"] = True
    if st.session_state.get("pdf_name") != uploaded_file.name:
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
            st.error(f"❌ Failed to process PDF document: {err}")
            st.session_state["pdf_text"] = ""
            st.session_state["pdf_name"] = ""

    page_count_note = ""
    if st.session_state.get("pdf_text"):
        approx_chars = len(st.session_state["pdf_text"])
        page_count_note = f' <span style="color:#7C8AA6;">· {approx_chars:,} characters extracted</span>'

    st.markdown(f"""<div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; padding: 8px 14px; border-radius: 8px; font-size: 0.85rem; color: #34D399; margin-top: 4px; margin-bottom: 12px; display:flex; align-items:center; gap:8px;">
<span style="font-weight:700;">✓ Active Custom Document:</span> {html.escape(st.session_state.get('pdf_name', ''))}{page_count_note}
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

# Prefill query safely if rerun was triggered
default_query_value = ""
if st.session_state.get("rerun_requested"):
    default_query_value = st.session_state.get("pending_rerun_query", "")
    st.info("↺ Re-running a previous query from history. You can edit it below before executing again.")
    st.session_state["rerun_requested"] = False  # Reset flag safely

user_query = st.text_area(
    "Type your legal inquiry",
    value=default_query_value,
    placeholder="Type your policy scenario, case details, or regulatory questions here...",
    height=140,
    label_visibility="collapsed",
)

if user_query.strip():
    st.session_state["robot_dismissed"] = True

st.markdown("<br>", unsafe_allow_html=True)

# ===========================================================
# 10. HELPER FUNCTIONS
# ===========================================================

def compute_confidence(result: dict) -> tuple[int, str]:
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
        label = "HIGH CONFIDENCE"
    elif score >= 45:
        label = "MODERATE CONFIDENCE"
    else:
        label = "LOW CONFIDENCE — HUMAN REVIEW ADVISED"
    return score, label


def run_consistency_guard(result: dict) -> list[tuple[str, str]]:
    checks = []
    status = str(result.get("recommendation_status", "")).upper()
    ra = result.get("rule_analysis", {}) or {}
    evidence = str(result.get("evidence", "")).strip().lower()
    summary = str(result.get("recommendation_summary", "")).strip()
    reasoning = str(result.get("reasoning_conclusion", "")).strip()

    if status in ("SUPPORTED", "NOT SUPPORTED"):
        if not evidence or evidence in ("-", "n/a", "none", "no direct text excerpt available"):
            checks.append(("bad", f"Status is <b>{status}</b> but no direct evidence excerpt was returned — this is a grounding inconsistency."))
        else:
            checks.append(("ok", f"Status <b>{status}</b> is backed by a direct evidence excerpt."))
    else:
        checks.append(("ok", "Status is REQUIRES HUMAN REVIEW, consistent with absent/insufficient evidence."))

    if ra.get("unresolved_conflict") and status == "SUPPORTED":
        checks.append(("warn", "An unresolved normative conflict was detected, yet the recommendation is SUPPORTED — review the hierarchy reasoning carefully."))
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


def confidence_bar_color(score: int) -> str:
    if score >= 75:
        return "#34D399"
    elif score >= 45:
        return "#FDE047"
    return "#F87171"


# ===========================================================
# 11. EXECUTE BUTTON & AI REASONING LOGIC
# ===========================================================
run_col1, run_col2 = st.columns([3, 1])
with run_col1:
    run_clicked = st.button("RUN GOVSHIELD LEGAL INTELLIGENCE ANALYSIS")
with run_col2:
    quick_rerun_clicked = False
    if st.session_state.get("analysis_result") is not None:
        quick_rerun_clicked = st.button("↺ RE-RUN LAST", use_container_width=True)

trigger_analysis = run_clicked or quick_rerun_clicked

if trigger_analysis:
    st.session_state["robot_dismissed"] = True

    effective_query = user_query.strip()
    if quick_rerun_clicked and not effective_query:
        effective_query = st.session_state.get("last_query", "")

    if not effective_query:
        st.warning("⚠️ Please enter a legal inquiry or case scenario before proceeding.")
    else:
        with st.spinner("Analyzing legal hierarchy, cross-referencing provisions, and generating evidence-first reasoning..."):
            try:
                combined_context = f"{BUILTIN_KNOWLEDGE_BASE}\n[SELECTED REGULATORY SCOPE]: {reg_scope}\n"
                if st.session_state.get("pdf_text"):
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

                # Safe logging to analysis history
                if "analysis_history" not in st.session_state:
                    st.session_state["analysis_history"] = []

                st.session_state["analysis_history"].append({
                    "timestamp": datetime.datetime.now().strftime("%H:%M:%S · %d %b"),
                    "query": effective_query,
                    "scope": reg_scope,
                    "status": str(parsed_result.get("recommendation_status", "REQUIRES HUMAN REVIEW")).upper(),
                })

            except Exception as e:
                st.error(f"Technical Analysis Error: {e}")

# ===========================================================
# 12. OUTPUT DASHBOARD & MULTI-TAB WORKSPACE
# ===========================================================
if st.session_state.get("analysis_result"):
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

    # ---------------- CONFIDENCE METER ----------------
    conf_score, conf_label = compute_confidence(result)
    bar_color = confidence_bar_color(conf_score)

    conf_col, metric_col1, metric_col2 = st.columns([2, 1, 1])
    with conf_col:
        st.markdown(f"""<div class="confidence-wrap">
<div class="confidence-label-row">
<span class="confidence-label">🎯 Determination Confidence</span>
<span class="confidence-value" style="color:{bar_color};">{conf_score}/100 · {conf_label}</span>
</div>
<div class="confidence-track">
<div class="confidence-fill" style="width:{conf_score}%; background:linear-gradient(90deg, {bar_color}, {bar_color}CC);"></div>
</div>
<div class="confidence-caption">Heuristic score derived from evidence presence, hierarchy conflicts, and completeness of the structured output — not a substitute for legal review.</div>
</div>""", unsafe_allow_html=True)
    with metric_col1:
        st.metric("Regulatory Scope", reg_scope.split(" ", 1)[1] if " " in reg_scope else reg_scope, delta=None)
    with metric_col2:
        ra_preview = result.get("rule_analysis", {}) or {}
        conflict_flag = "Yes" if ra_preview.get("unresolved_conflict") else "No"
        st.metric("Unresolved Conflict", conflict_flag)

    # ---------------- CONSISTENCY GUARD ----------------
    with st.expander("🛡️ CONSISTENCY GUARD — INTERNAL CONTRADICTION CHECK", expanded=(conf_score < 45)):
        guard_results = run_consistency_guard(result)
        severity_icon = {"ok": "✅", "warn": "⚠️", "bad": "⛔"}
        for severity, message in guard_results:
            st.markdown(f"""<div class="guard-row {severity}">
<span class="guard-icon">{severity_icon.get(severity, "•")}</span>
<span class="guard-text">{message}</span>
</div>""", unsafe_allow_html=True)
        bad_count = sum(1 for s, _ in guard_results if s == "bad")
        warn_count = sum(1 for s, _ in guard_results if s == "warn")
        if bad_count > 0:
            st.markdown(f"""<div style="margin-top:10px; font-size:0.8rem; color:#F87171;">
{bad_count} critical inconsistency(ies) detected. Treat this output as REQUIRES HUMAN REVIEW regardless of the stated status.
</div>""", unsafe_allow_html=True)
        elif warn_count > 0:
            st.markdown(f"""<div style="margin-top:10px; font-size:0.8rem; color:#FDE047;">
{warn_count} soft warning(s) detected. Recommend a second read-through before relying on this determination.
</div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div style="margin-top:10px; font-size:0.8rem; color:#34D399;">
No structural inconsistencies detected in this output.
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # TABULAR DISPLAY
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Executive Summary & Evidence",
        "⚖️ Statutory Structure & Legal Reasoning",
        "💬 Interactive Follow-up Q&A Assistant",
        "📥 Export Executive Legal Brief",
        "🧭 Methodology & Audit Trail",
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
<div style="font-family:'JetBrains Mono', monospace; font-size:0.85rem; color:#67E8F9; background:#070C1A; padding:12px; border-radius:8px; border: 1px solid rgba(56, 189, 248, 0.25);">
{evidence_text}
</div>
</div>""", unsafe_allow_html=True)

        st.markdown(f"""<div class="lexis-card-emerald">
<div class="card-title-emerald">🎯 CONFIDENCE &amp; SCOPE SNAPSHOT</div>
<div style="font-size:0.88rem; line-height:1.7; color:#E2E8F0;">
<div><b style="color:#F1F5F9;">Confidence Score:</b> {conf_score}/100 ({conf_label})</div>
<div><b style="color:#F1F5F9;">Regulatory Scope Applied:</b> {html.escape(reg_scope)}</div>
<div><b style="color:#F1F5F9;">Source Document:</b> {html.escape(st.session_state.get('pdf_name', '')) if st.session_state.get('pdf_name') else 'None — constitutional knowledge base only'}</div>
</div>
</div>""", unsafe_allow_html=True)

    with tab2:
        ra = result.get("rule_analysis", {}) or {}
        gen_prov = html.escape(str(ra.get('general_provision', '-')))
        spec_prov = html.escape(str(ra.get('specific_provision', '-')))
        exc_str = '<span style="color:#34D399; font-weight:700;">YES</span>' if ra.get('exception_detected') else '<span style="color:#F87171; font-weight:700;">NO</span>'
        conf_str = '<span style="color:#FDE047; font-weight:700;">YES</span>' if ra.get('unresolved_conflict') else '<span style="color:#34D399; font-weight:700;">NO</span>'

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
💡 <b style="color:#F1F5F9;">Legal Counsel Advisory Note:</b> {review_note}
</div>
</div>""", unsafe_allow_html=True)

        with st.expander("🔍 View applied legal principles (Lex Specialis / Lex Superior)"):
            st.markdown("""<div style="font-size:0.85rem; line-height:1.8; color:#E2E8F0;">
<div><b style="color:#7DD3FC;">Lex Specialis Derogat Legi Generali:</b> A specific rule governing a particular situation overrides a general rule that would otherwise apply.</div>
<div><b style="color:#7DD3FC;">Lex Superior Derogat Legi Inferiori:</b> A rule issued by a higher-ranking authority overrides a conflicting rule issued by a lower-ranking authority.</div>
</div>""", unsafe_allow_html=True)

    # TAB 3: INTERACTIVE CHAT WORKSPACE
    with tab3:
        st.markdown("### 💬 Interactive Legal Q&A Assistant")
        st.caption("Ask questions about this legal determination, uploaded document clauses, or relevant statutory rules.")

        chat_history = st.session_state.get("chat_history", [])
        for msg in chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if chat_input := st.chat_input("Ask a follow-up question regarding this case..."):
            if "chat_history" not in st.session_state:
                st.session_state["chat_history"] = []
            
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
        ra = result.get("rule_analysis", {}) or {}
        guard_results_export = run_consistency_guard(result)
        guard_lines = "\n".join(
            f"  [{sev.upper()}] {msg.replace('<b>', '').replace('</b>', '')}" for sev, msg in guard_results_export
        )
        report_text = f"""================================================================================
GOVSHIELD AI - FORMAL LEGAL & REGULATORY DETERMINATION REPORT
================================================================================
Status: {status}
Confidence Score: {conf_score}/100 ({conf_label})
Regulatory Scope: {reg_scope}
Attached Document: {st.session_state.get('pdf_name') or 'None'}
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
Generated automatically by GovShield AI Engine v4.0
================================================================================
"""
        st.download_button(
            label="📄 DOWNLOAD FORMAL LEGAL REPORT (.TXT)",
            data=report_text,
            file_name="GovShield_Executive_Legal_Brief.txt",
            mime="text/plain"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""<div class="lexis-card-cyan">
<div class="card-title-cyan">📦 EXPORT NOTES</div>
<div style="font-size:0.85rem; line-height:1.6; color:#CBD5E1;">
The exported brief includes the full Consistency Guard report so reviewing counsel can see exactly which automated checks passed, warned, or failed for this determination.
</div>
</div>""", unsafe_allow_html=True)

    # TAB 5: METHODOLOGY & AUDIT TRAIL
    with tab5:
        st.markdown("### 🧭 Methodology &amp; Audit Trail")
        st.caption("A transparent record of how this specific determination was produced, plus the running session history.")

        steps_html = ""
        for i, (title, desc) in enumerate(METHODOLOGY_STEPS, start=1):
            steps_html += f"""<div class="method-step">
<div class="method-num">{i}</div>
<div class="method-body"><b>{html.escape(title)}</b><p>{html.escape(desc)}</p></div>
</div>"""
        st.markdown(f'<div class="lexis-card-gold">{steps_html}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""<div class="custom-label" style="color:#7DD3FC !important;">📜 SESSION AUDIT TRAIL</div>""", unsafe_allow_html=True)

        audit_history = st.session_state.get("analysis_history", [])
        if not audit_history:
            st.info("No prior analyses logged yet in this session.")
        else:
            status_color_map = {
                "SUPPORTED": ("#34D399", "rgba(16,185,129,0.18)"),
                "NOT SUPPORTED": ("#F87171", "rgba(239,68,68,0.18)"),
                "REQUIRES HUMAN REVIEW": ("#FDE047", "rgba(234,179,8,0.18)"),
            }
            for i, item in enumerate(reversed(audit_history), start=1):
                st_status = item.get("status", "REQUIRES HUMAN REVIEW")
                color, bg = status_color_map.get(st_status, ("#FDE047", "rgba(234,179,8,0.18)"))
                st.markdown(f"""<div class="history-item">
<div class="h-time">#{len(audit_history) - i + 1} · {html.escape(item.get('timestamp',''))} · {html.escape(item.get('scope',''))}</div>
<div class="h-query">{html.escape(item.get('query','')[:160])}</div>
<span class="h-status" style="background:{bg}; color:{color};">{html.escape(st_status)}</span>
</div>""", unsafe_allow_html=True)

# ===========================================================
# 13. FOOTER
# ===========================================================
st.markdown(f"""<div class="gov-footer">
🛡️ <b>GovShield AI Intelligence Engine v4.0</b> — Evidence-first grounded legal reasoning. Outputs are decision-support only and require review by qualified legal counsel before formal reliance.<br>
Session analyses logged: {len(st.session_state.get("analysis_history", []))} · Built for macro/meso/harmonization regulatory scope analysis.
</div>""", unsafe_allow_html=True)
