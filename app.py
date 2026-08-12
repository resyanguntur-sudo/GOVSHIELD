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
# 2. BACA DARI SECRETS.TOML (DENGAN SAFE CHECK)
# ---------------------------------------------------------
try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    BASE_URL = st.secrets.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
except KeyError:
    st.error("❌ Key 'GROQ_API_KEY' tidak ditemukan di dalam file .streamlit/secrets.toml!")
    st.stop()
except Exception as e:
    st.error(f"❌ Terjadi kesalahan membaca secrets.toml: {e}")
    st.stop()

# ---------------------------------------------------------
# 3. UNIVERSAL THEME STYLES (BACKGROUND SILHOUETTE + TECH DECO)
# ---------------------------------------------------------
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* HEADER & TOMBOL NAVIGATOR SIDEBAR */
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

/* BASE BACKGROUND DENGAN SILUET HUKUM BERPADU DENGAN GLOW TEKNOLOGI */
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
# 4. HEADER TASKBAR DENGAN LOGO TAMENG EMAS + HUKUM
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
<div class="lexis-maxim">"Fiat justitia ruat caelum" — Keadilan harus ditegakkan meski langit runtuh</div>
</div>
</div>
<div class="top-right-badge">
<div class="brand-name">🛡️ GOVSHIELD AI v2.5</div>
<div class="brand-desc">Enterprise Legal Analysis System</div>
</div>
</div>
<div class="letterhead-divider">
<span class="lh-line"></span>
</div>""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. KNOWLEDGE BASE
# ---------------------------------------------------------
BUILTIN_KNOWLEDGE_BASE = """
[BUILT-IN KNOWLEDGE BASE: UUD NR1 1945 & HIERARKI HUKUM INDONESIA]
1. UUD 1945 (Pasal 1 s/d Pasal 37 beserta Amandemen I, II, III, IV):
   - Indonesia adalah negara hukum (Pasal 1 ayat 3).
   - Hak Asasi Manusia, Hak Pendidikan (Pasal 31), Kebijakan Pemerintahan, Hak Pekerjaan, Kebijakan Hukum Organisasi.
   - Hak atas Kepastian Hukum yang Adil dan Perlakuan Sama di Hadapan Hukum (Pasal 28D ayat 1).
2. HIERARKI PERATURAN PERUNDANG-UNDANGAN (UU No. 12 Tahun 2011 jo UU No. 13 Tahun 2022):
   - UUD 1945 > TAP MPR > UU/Perppu > Peraturan Pemerintah (PP) > Peraturan Presiden (Perpres) > Perda Provinsi > Perda Kabupaten/Kota.
   - Aturan Internal (Surat Edaran/Keputusan): Merupakan aturan pelaksanaan/operasional yang TIDAK BOLEH bertentangan dengan peraturan perundang-undangan di atasnya.
3. AZAS-AZAS HUKUM REGULASI:
   - Lex Specialis Derogat Legi Generali: Hukum yang khusus mengesampingkan hukum yang umum.
   - Lex Superior Derogat Legi Inferiori: Hukum yang lebih tinggi mengesampingkan hukum yang rendah.
"""

# ---------------------------------------------------------
# 6. SESSION STATE
# ---------------------------------------------------------
if "pdf_text" not in st.session_state:
    st.session_state["pdf_text"] = ""
if "pdf_name" not in st.session_state:
    st.session_state["pdf_name"] = ""

# ---------------------------------------------------------
# 7. SIDEBAR CONFIG
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""<div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; padding: 12px; border-radius: 10px; margin-bottom: 16px;">
<b style="color:#34D399; font-size:0.88rem;">⚡ SECRETS CONNECTED</b><br>
<span style="font-size:0.75rem; color:#94A3B8;">API Key Terbaca dari secrets.toml</span>
</div>""", unsafe_allow_html=True)

    st.markdown("""<div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#EAB308" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
<span style="font-weight:700; color:#EAB308; font-size:0.88rem;">GROUNDED KNOWLEDGE</span>
</div>""", unsafe_allow_html=True)

    st.markdown("""<div style="background: #0A142F; border-left: 3px solid #10B981; padding: 10px; border-radius: 6px; margin-bottom: 8px; font-size: 0.85rem;">
<b style="color:#FFFFFF;">§ UUD 1945 &amp; Amandemen I-IV</b><br><span style="color:#94A3B8;">Active Index</span>
</div>
<div style="background: #0A142F; border-left: 3px solid #10B981; padding: 10px; border-radius: 6px; font-size: 0.85rem;">
<b style="color:#FFFFFF;">§ Hierarki Hukum Indonesia</b><br><span style="color:#94A3B8;">UU 12/2011 jo UU 13/2022</span>
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="lexis-divider"></div>', unsafe_allow_html=True)
    st.caption("🛡️ **GovShield Intelligence Engine**")

# ---------------------------------------------------------
# 8. INPUT AREA
# ---------------------------------------------------------
st.markdown("""<div class="custom-label">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#EAB308" stroke-width="2.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
📄 OPSIONAL: DOKUMEN KHUSUS (UPLOAD PDF REGULASI / KONTRAK)
</div>""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload Dokumen PDF", type=["pdf"], label_visibility="collapsed"
)

if uploaded_file is not None:
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
            st.error(f"Gagal memproses file PDF: {err}")

    st.markdown(f"""<div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; padding: 8px 14px; border-radius: 8px; font-size: 0.85rem; color: #34D399; margin-top: 4px; margin-bottom: 12px; display:flex; align-items:center; gap:8px;">
<span style="font-weight:700;">✓ Dokumen Khusus Aktif:</span> {html.escape(st.session_state['pdf_name'])}
</div>""", unsafe_allow_html=True)
else:
    st.session_state["pdf_text"] = ""
    st.session_state["pdf_name"] = ""
    st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

# AREA PENCARIAN & KASUS
st.markdown("""<div class="ai-search-frame">
<div style="display:flex; justify-content:space-between; align-items:center;">
<div class="custom-label" style="margin-bottom: 0 !important;">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
❓ PERTANYAAN / SKENARIO KASUS / INSTRUKSI ANALISIS (WAJIB)
</div>
<div style="font-size: 0.78rem; color: #38BDF8; font-weight:600; display:flex; align-items:center;">
<span class="pulse-dot"></span> AI REASONING READY
</div>
</div>
</div>""", unsafe_allow_html=True)

user_query = st.text_area(
    "Ketik skenario hukum",
    placeholder="Ketik skenario kasus, analisis pasal dari PDF, atau instruksi analisis hukum di sini...",
    height=140,
    label_visibility="collapsed",
)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 9. EXECUTE BUTTON & LEGAL AI REASONING
# ---------------------------------------------------------
if st.button("PROSES ANALISIS HUKUM (RUN GOVSHIELD AI)"):
    if not user_query.strip():
        st.warning("⚠️ Mohon ketik skenario kasus atau instruksi analisis hukum kamu terlebih dahulu.")
    else:
        with st.spinner("Memproses Analisis Lexis Decision Intelligence..."):
            try:
                combined_context = f"{BUILTIN_KNOWLEDGE_BASE}\n"
                if st.session_state["pdf_text"]:
                    combined_context += f"\n[DOKUMEN SPESIFIK USER / UPLOAD]:\n{st.session_state['pdf_text'][:14000]}\n"

                client = OpenAI(api_key=GROQ_KEY, base_url=BASE_URL)

                system_prompt = """
Anda adalah GOVSHIELD AI, sistem intelligence analisis regulasi berbasis bukti (Evidence-First Legal Decision Support System).

PRINSIP WAJIB:
1. Analisis hirarki hukum (UUD 1945 vs Aturan Khusus/Dokumen Upload) dan terapkan azas "Lex Specialis Derogat Legi Generali".
2. Bedakan Aturan Umum (General Provision) dan Aturan Khusus/Pengecualian (Specific Provision/Exception).
3. Tunjukkan EVIDENCE berupa kutipan asli/nomor pasal/bab dari UUD 1945 maupun Dokumen PDF.
4. JIKA PERTANYAAN TIDAK MEMILIKI BUKTI ATAU PASAL TERKAIT, JAWAB STATUS SEBAGAI "REQUIRES HUMAN REVIEW" dan sebutkan bahwa pasal tidak ditemukan. JANGAN MENGARANG PASAL.

FORMAT KELUARAN JSON:
{
  "recommendation_status": "SUPPORTED" | "NOT SUPPORTED" | "REQUIRES HUMAN REVIEW",
  "recommendation_summary": "Ringkasan keputusan dalam Bahasa Indonesia",
  "applicable_rule": "Ketentuan akhir yang paling berlaku berdasarkan prinsip Lex Specialis atau Konstitusi",
  "evidence": "Kutipan teks asli/pasal/bab dari dokumen sebagai bukti kuat",
  "rule_analysis": {
    "general_provision": "Ketentuan umum yang ditemukan",
    "specific_provision": "Ketentuan khusus/pengecualian yang ditemukan",
    "exception_detected": true | false,
    "unresolved_conflict": true | false
  },
  "reasoning_conclusion": "Analisis logis hukum secara rinci",
  "review_note": "Catatan kritis analis hukum manusia"
}
Jawab HANYA JSON.
"""

                user_prompt = f"""
KUMPULAN REGULASI & DOKUMEN:
---
{combined_context}
---

PERTANYAAN / KASUS:
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

                result = json.loads(response.choices[0].message.content)

                # ---------------------------------------------------------
                # 10. OUTPUT DASHBOARD
                # ---------------------------------------------------------
                st.markdown('<div class="lexis-divider"></div>', unsafe_allow_html=True)
                st.markdown("""<div style="font-size:1.15rem; font-weight:800; color:#38BDF8; margin-bottom:16px; letter-spacing:1px;">
⚖️ HASIL ANALISIS: GOVSHIELD INTELLIGENCE
</div>""", unsafe_allow_html=True)

                status = str(result.get("recommendation_status", "REQUIRES HUMAN REVIEW"))
                summary = html.escape(str(result.get("recommendation_summary", "")))

                if status == "SUPPORTED":
                    st.markdown(f'<div class="badge-supported">✅ RECOMMENDATION: SUPPORTED — {summary}</div>', unsafe_allow_html=True)
                elif status == "NOT SUPPORTED":
                    st.markdown(f'<div class="badge-rejected">❌ RECOMMENDATION: NOT SUPPORTED — {summary}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="badge-review">⚠️ STATUS: REQUIRES HUMAN REVIEW — Bukti Kurang Spesifik</div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                r_col1, r_col2 = st.columns(2, gap="medium")

                applicable_rule = html.escape(str(result.get('applicable_rule', '-')))
                evidence_text = html.escape(str(result.get('evidence', 'Tidak ada bukti langsung')))
                reasoning = html.escape(str(result.get('reasoning_conclusion', '-')))
                review_note = html.escape(str(result.get('review_note', 'N/A')))

                with r_col1:
                    st.markdown(f"""<div class="lexis-card-gold">
<div class="card-title-gold">⚖️ APPLICABLE RULE (ATURAN BERLAKU)</div>
<div style="font-size:0.95rem; line-height:1.6; color:#F1F5F9;">{applicable_rule}</div>
</div>
<div class="lexis-card-cyan">
<div class="card-title-cyan">📌 BUKTI VALID (EVIDENCE EXCERPT)</div>
<div style="font-family:'JetBrains Mono', monospace; font-size:0.85rem; color:#34D399; background:#070C1A; padding:12px; border-radius:8px; border: 1px solid rgba(56, 189, 248, 0.25);">
{evidence_text}
</div>
</div>""", unsafe_allow_html=True)

                with r_col2:
                    ra = result.get("rule_analysis", {})
                    gen_prov = html.escape(str(ra.get('general_provision', '-')))
                    spec_prov = html.escape(str(ra.get('specific_provision', '-')))
                    exc_str = '<span style="color:#34D399; font-weight:700;">YA</span>' if ra.get('exception_detected') else '<span style="color:#F87171;">TIDAK</span>'
                    conf_str = '<span style="color:#FDE047; font-weight:700;">YA</span>' if ra.get('unresolved_conflict') else '<span style="color:#34D399;">TIDAK</span>'

                    st.markdown(f"""<div class="lexis-card-cyan">
<div class="card-title-cyan">📊 ANALISIS STRUKTUR REGULASI</div>
<div style="font-size:0.9rem; line-height:1.8; color:#F1F5F9;">
<div><b>Ketentuan Umum:</b> {gen_prov}</div>
<div><b>Ketentuan Khusus:</b> {spec_prov}</div>
<div><b>Pengecualian Terdeteksi:</b> {exc_str}</div>
<div><b>Konflik Norma:</b> {conf_str}</div>
</div>
</div>""", unsafe_allow_html=True)

                st.markdown(f"""<div class="lexis-card-gold">
<div class="card-title-gold">📝 RASIONALISASI &amp; KESIMPULAN HUKUM</div>
<div style="font-size:0.95rem; line-height:1.6; color:#E2E8F0;">
{reasoning}
</div>
<div style="font-size:0.85rem; color:#94A3B8; margin-top:14px; border-top:1px solid rgba(234, 179, 8, 0.2); padding-top:8px;">
💡 <b>Catatan Analis:</b> {review_note}
</div>
</div>""", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Terjadi kesalahan teknis: {e}")