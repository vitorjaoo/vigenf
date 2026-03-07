"""
VigInfec — Sistema de Vigilância de Infecção Hospitalar
pip install streamlit fpdf2 pandas plotly supabase Pillow
streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from fpdf import FPDF
import base64, io

# ── Secrets / Config ─────────────────────────────────────────
USE_SUPABASE = True
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except:
    SUPABASE_URL = "https://juzyjqauwujtcsxgsogh.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp1enlqcWF1d3VqdGNzeGdzb2doIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3MzE1MjUsImV4cCI6MjA4ODMwNzUyNX0.r90v3aN_lf0Hrf7uyFll4ZQh29WGz8PQKNegBH8p1NY"

if USE_SUPABASE:
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="VigInfec", page_icon="🏥", layout="wide",
                   initial_sidebar_state="collapsed")

# ══════════════════════════════════════════════════════════════
# DESIGN SYSTEM
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --c-navy:    #0d1f3c;
  --c-blue:    #163d6e;
  --c-accent:  #2461d4;
  --c-red:     #e53e3e;
  --c-amber:   #c07a1a;
  --c-green:   #1a7a4a;
  --c-red-bg:  #fff5f5;
  --c-amb-bg:  #fffaf0;
  --c-grn-bg:  #f0fff4;
  --c-red-br:  #feb2b2;
  --c-amb-br:  #fbd38d;
  --c-grn-br:  #9ae6b4;
  --c-bg:      #f7f8fc;
  --c-surface: #ffffff;
  --c-border:  #e4e8ef;
  --c-muted:   #8a94a6;
  --c-text:    #1a202c;
  --c-text2:   #4a5568;
  --shadow-s:  0 1px 2px rgba(0,0,0,.06), 0 2px 8px rgba(0,0,0,.05);
  --shadow-m:  0 2px 4px rgba(0,0,0,.06), 0 8px 24px rgba(0,0,0,.08);
  --r-sm: 6px; --r-md: 10px; --r-lg: 14px;
}

/* ── RESET ────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.main .block-container  { padding: 0 !important; max-width: 100% !important; background: var(--c-bg); }
section[data-testid="stSidebar"], header[data-testid="stHeader"],
.stDeployButton, footer, #MainMenu { display: none !important; }
.stApp { background: var(--c-bg) !important; }

/* ── TOPBAR ────────────────────────────────── */
.topbar {
  background: var(--c-navy);
  height: 52px; padding: 0 28px;
  display: flex; align-items: center; justify-content: space-between;
  position: sticky; top: 0; z-index: 100;
  border-bottom: 1px solid rgba(255,255,255,.06);
}
.topbar-brand { color: #fff; font-size: .95rem; font-weight: 700; letter-spacing: -.2px; display: flex; align-items: center; gap: 8px; }
.topbar-brand em { color: #60a5fa; font-style: normal; }
.topbar-right { display: flex; align-items: center; gap: 12px; }
.topbar-setor {
  background: rgba(96,165,250,.15); color: #93c5fd;
  padding: 3px 10px; border-radius: 99px;
  font-size: .7rem; font-weight: 600; letter-spacing: .4px; text-transform: uppercase;
}
.topbar-user { color: #94a3b8; font-size: .78rem; }

/* ── PAGE SHELL ────────────────────────────── */
.page { padding: 20px 24px; max-width: 1100px; margin: 0 auto; }

/* ── SECTION LABEL ─────────────────────────── */
.slabel {
  font-size: .65rem; font-weight: 700; letter-spacing: 1.1px;
  text-transform: uppercase; color: var(--c-accent);
  margin: 20px 0 8px; padding-bottom: 6px;
  border-bottom: 1px solid var(--c-border);
}

/* ── SURFACE CARD ──────────────────────────── */
.surf {
  background: var(--c-surface); border: 1px solid var(--c-border);
  border-radius: var(--r-lg); padding: 18px 20px;
  box-shadow: var(--shadow-s); margin-bottom: 12px;
}

/* ── RISK BANNER ───────────────────────────── */
.rbanner {
  border-radius: var(--r-md); padding: 14px 18px;
  display: flex; align-items: center; gap: 14px; margin: 12px 0;
}
.rbanner.r-alto  { background: var(--c-red-bg); border: 1px solid var(--c-red-br); }
.rbanner.r-medio { background: var(--c-amb-bg); border: 1px solid var(--c-amb-br); }
.rbanner.r-baixo { background: var(--c-grn-bg); border: 1px solid var(--c-grn-br); }
.rbanner-icon { font-size: 1.5rem; flex-shrink: 0; }
.rbanner-score {
  font-family: 'JetBrains Mono', monospace;
  font-size: 2rem; font-weight: 700; line-height: 1; flex-shrink: 0;
}
.r-alto  .rbanner-score { color: var(--c-red); }
.r-medio .rbanner-score { color: var(--c-amber); }
.r-baixo .rbanner-score { color: var(--c-green); }
.rbanner-body { flex: 1; }
.rbanner-title { font-size: .95rem; font-weight: 700; color: var(--c-text); }
.rbanner-sub   { font-size: .78rem; color: var(--c-text2); margin-top: 2px; }

/* ── METRIC ROW ────────────────────────────── */
.mrow { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin-bottom: 18px; }
@media(max-width:640px){ .mrow { grid-template-columns: repeat(2,1fr); } }
.mcard {
  background: var(--c-surface); border: 1px solid var(--c-border);
  border-radius: var(--r-md); padding: 14px 16px;
  box-shadow: var(--shadow-s); text-align: center;
}
.mcard-n { font-size: 1.9rem; font-weight: 700; line-height: 1.1; font-family: 'JetBrains Mono', monospace; }
.mcard-l { font-size: .65rem; font-weight: 600; letter-spacing: .5px; text-transform: uppercase; color: var(--c-muted); margin-top: 4px; }
.mn-total { color: var(--c-navy); }
.mn-alto  { color: var(--c-red); }
.mn-medio { color: var(--c-amber); }
.mn-baixo { color: var(--c-green); }

/* ── HISTORY CARD ──────────────────────────── */
.hcard {
  background: var(--c-surface); border: 1px solid var(--c-border);
  border-left: 3px solid var(--c-border);
  border-radius: var(--r-md); padding: 14px 16px;
  margin-bottom: 8px; box-shadow: var(--shadow-s);
  transition: box-shadow .15s, transform .1s;
}
.hcard:hover { box-shadow: var(--shadow-m); transform: translateY(-1px); }
.hcard.h-alto  { border-left-color: var(--c-red); }
.hcard.h-medio { border-left-color: var(--c-amber); }
.hcard.h-baixo { border-left-color: var(--c-green); }
.hcard-row1 { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; flex-wrap: wrap; }
.hcard-name { font-size: .92rem; font-weight: 700; color: var(--c-text); }
.hcard-meta { font-size: .72rem; color: var(--c-muted); margin-top: 2px; }
.hbadge {
  font-size: .67rem; font-weight: 700; padding: 2px 9px;
  border-radius: 99px; letter-spacing: .3px; text-transform: uppercase; white-space: nowrap;
}
.hbadge.b-alto  { background: #fee2e2; color: #b91c1c; }
.hbadge.b-medio { background: #fef3c7; color: #92400e; }
.hbadge.b-baixo { background: #d1fae5; color: #065f46; }
.hscore { font-size: .72rem; color: var(--c-muted); font-family: 'JetBrains Mono',monospace; text-align: right; margin-top: 3px; }
.chips { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 10px; }
.chip {
  font-size: .68rem; padding: 2px 8px; border-radius: 99px;
  background: var(--c-bg); border: 1px solid var(--c-border); color: var(--c-text2);
}
.chip.on { background: #eff6ff; border-color: #bfdbfe; color: var(--c-accent); }

/* ── SETOR OVERVIEW CARD ───────────────────── */
.sov-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 12px; }
@media(max-width:640px){ .sov-grid { grid-template-columns: 1fr; } }
.sov-card {
  background: var(--c-surface); border: 1px solid var(--c-border);
  border-radius: var(--r-lg); padding: 16px; box-shadow: var(--shadow-s);
}
.sov-name { font-size: .82rem; font-weight: 700; color: var(--c-navy); margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid var(--c-border); }
.sov-row  { display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }
.sov-lbl  { font-size: .72rem; color: var(--c-text2); }
.sov-val  { font-size: .72rem; font-weight: 700; font-family: 'JetBrains Mono',monospace; }
.sov-bar-wrap { background: var(--c-bg); border-radius: 99px; height: 4px; margin-top: 8px; overflow: hidden; }
.sov-bar      { height: 4px; border-radius: 99px; background: linear-gradient(90deg,#2461d4,#60a5fa); }
.sov-alerta   { display: flex; align-items: center; gap: 5px; margin-top: 8px; font-size: .68rem; color: var(--c-red); font-weight: 600; }

/* ── STREAMLIT WIDGET OVERRIDES ────────────── */
div[data-testid="stForm"] { background: transparent !important; border: none !important; padding: 0 !important; box-shadow: none !important; }

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
div[data-baseweb="select"] > div:first-child {
  border: 1px solid var(--c-border) !important;
  border-radius: var(--r-sm) !important;
  background: var(--c-surface) !important;
  font-size: .86rem !important;
  color: var(--c-text) !important;
  padding: 7px 11px !important;
  transition: border-color .15s, box-shadow .15s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--c-accent) !important;
  box-shadow: 0 0 0 3px rgba(36,97,212,.1) !important;
  outline: none !important;
}

/* Labels */
div[data-testid="stWidgetLabel"] > label,
div[data-testid="stWidgetLabel"] > p {
  font-size: .7rem !important;
  font-weight: 600 !important;
  letter-spacing: .3px !important;
  text-transform: uppercase !important;
  color: var(--c-text2) !important;
}

/* Checkboxes */
.stCheckbox { margin-bottom: 5px !important; }
.stCheckbox > label {
  display: flex !important; align-items: center !important;
  background: var(--c-bg) !important;
  border: 1px solid var(--c-border) !important;
  border-radius: var(--r-sm) !important;
  padding: 8px 12px !important;
  font-size: .83rem !important;
  color: var(--c-text) !important;
  cursor: pointer !important;
  transition: background .12s, border-color .12s !important;
  width: 100% !important;
}
.stCheckbox > label:hover { background: #eff6ff !important; border-color: #93c5fd !important; }
.stCheckbox input:checked + div + label,
.stCheckbox input:checked ~ label {
  background: #eff6ff !important;
  border-color: var(--c-accent) !important;
  color: var(--c-accent) !important;
  font-weight: 600 !important;
}

/* Number input */
div[data-testid="stNumberInput"] input {
  border: 1px solid var(--c-border) !important;
  border-radius: var(--r-sm) !important;
  font-size: .86rem !important;
}

/* Buttons */
.stButton > button {
  border-radius: var(--r-sm) !important;
  font-size: .82rem !important;
  font-weight: 600 !important;
  padding: 7px 16px !important;
  transition: all .15s !important;
  border: 1px solid var(--c-border) !important;
  background: var(--c-surface) !important;
  color: var(--c-text) !important;
}
.stButton > button:hover { border-color: var(--c-accent) !important; color: var(--c-accent) !important; background: #eff6ff !important; }
.stButton > button[kind="primary"] {
  background: var(--c-accent) !important;
  border-color: var(--c-accent) !important;
  color: #fff !important;
}
.stButton > button[kind="primary"]:hover {
  background: #1a4fb5 !important;
  border-color: #1a4fb5 !important;
  box-shadow: 0 4px 12px rgba(36,97,212,.25) !important;
}

/* Download button */
.stDownloadButton > button {
  border-radius: var(--r-sm) !important;
  font-size: .82rem !important;
  font-weight: 600 !important;
  background: var(--c-navy) !important;
  color: #fff !important;
  border: none !important;
  width: 100% !important;
}

/* Tabs */
div[data-testid="stTabs"] { border-bottom: 1px solid var(--c-border) !important; }
div[data-testid="stTabs"] > div > div > button {
  font-size: .8rem !important;
  font-weight: 600 !important;
  color: var(--c-muted) !important;
  padding: 8px 14px !important;
  border-radius: 0 !important;
  border-bottom: 2px solid transparent !important;
}
div[data-testid="stTabs"] > div > div > button[aria-selected="true"] {
  color: var(--c-accent) !important;
  border-bottom-color: var(--c-accent) !important;
}

/* Expander */
div[data-testid="stExpander"] {
  border: 1px solid var(--c-border) !important;
  border-radius: var(--r-md) !important;
  background: var(--c-surface) !important;
  box-shadow: none !important;
}
div[data-testid="stExpander"] summary {
  font-size: .8rem !important;
  font-weight: 600 !important;
  color: var(--c-text2) !important;
}

/* Alerts */
div[data-testid="stAlert"] { border-radius: var(--r-sm) !important; font-size: .82rem !important; }

/* File uploader */
div[data-testid="stFileUploader"] {
  border: 1.5px dashed var(--c-border) !important;
  border-radius: var(--r-md) !important;
  background: var(--c-bg) !important;
  padding: 12px !important;
}

/* Divider */
hr { border: none !important; border-top: 1px solid var(--c-border) !important; margin: 16px 0 !important; }

/* Info/success/error */
.stSuccess, .stError, .stInfo, .stWarning { border-radius: var(--r-sm) !important; font-size: .82rem !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# DADOS
# ══════════════════════════════════════════════════════════════
SETORES = ["UTI Geral","UTI 1","UTI 2","UTI AVC",
           "Area Laranja","Area Vermelha",
           "Internacao A","Internacao B","Internacao C"]

FATORES_POR_SETOR = {
    "UTI Geral":     ["cateter","ventilacao","cirurgia_recente","imunossuprimido","antibiotico","febre","secrecao","sedacao","nutricao_enteral"],
    "UTI 1":         ["cateter","ventilacao","cirurgia_recente","imunossuprimido","antibiotico","febre","secrecao","sedacao","nutricao_enteral"],
    "UTI 2":         ["cateter","ventilacao","cirurgia_recente","imunossuprimido","antibiotico","febre","secrecao","sedacao","nutricao_enteral"],
    "UTI AVC":       ["cateter","ventilacao","cirurgia_recente","imunossuprimido","antibiotico","febre","secrecao","disfagia","sonda_vesical"],
    "Area Laranja":  ["cateter","cirurgia_recente","imunossuprimido","antibiotico","febre","secrecao","sonda_vesical"],
    "Area Vermelha": ["cateter","ventilacao","cirurgia_recente","imunossuprimido","antibiotico","febre","secrecao","sonda_vesical","dreno"],
    "Internacao A":  ["cateter","cirurgia_recente","imunossuprimido","antibiotico","febre","secrecao","sonda_vesical"],
    "Internacao B":  ["cateter","cirurgia_recente","imunossuprimido","antibiotico","febre","secrecao","sonda_vesical"],
    "Internacao C":  ["cateter","cirurgia_recente","imunossuprimido","antibiotico","febre","secrecao","sonda_vesical"],
}

LABELS = {
    "cateter":"Cateter Venoso Central","ventilacao":"Ventilação Mecânica",
    "cirurgia_recente":"Cirurgia < 30 dias","imunossuprimido":"Imunossupressão",
    "antibiotico":"Antibiótico","febre":"Febre > 38°C","secrecao":"Secreção Anormal",
    "sedacao":"Sedação Contínua","nutricao_enteral":"Nutrição Enteral",
    "disfagia":"Disfagia","sonda_vesical":"Sonda Vesical","dreno":"Dreno Cirúrgico",
}
ICONS = {
    "cateter":"💉","ventilacao":"🫁","cirurgia_recente":"🩹","imunossuprimido":"🛡️",
    "antibiotico":"💊","febre":"🌡️","secrecao":"🔬","sedacao":"💤",
    "nutricao_enteral":"🥤","disfagia":"🗣️","sonda_vesical":"🔵","dreno":"🩸",
}
PESOS = {
    "cateter":4,"ventilacao":4,"cirurgia_recente":3,"imunossuprimido":3,
    "antibiotico":2,"febre":2,"secrecao":2,"sedacao":2,
    "nutricao_enteral":1,"disfagia":1,"sonda_vesical":2,"dreno":2,
    "dias_cateter_bonus":0.3,"dias_ventilacao_bonus":0.4,
}
OBS_OPCOES = [
    "Sem intercorrencias","Sinais de infeccao no sitio",
    "Febre persistente em investigacao","Paciente imunossuprimido em observacao",
    "Aguardando resultado de cultura","Em uso de antibiotico de amplo espectro",
    "Dispositivo com sinais de flebite","Outro (ver descricao livre)",
]

# ── Session state ─────────────────────────────────────────────
for k,v in [("logado",False),("usuario_email",""),("usuario_nome",""),
            ("usuario_setor",""),("avaliacoes",[]),("contador",1),("editando_id",None)]:
    if k not in st.session_state: st.session_state[k] = v

MOCK = [
    {"id":1,"paciente":"Maria Santos","leito":"L-01","data":"2026-03-01","score":18,"risco":"Alto",
     "setor":"UTI Geral","cateter":True,"ventilacao":True,"cirurgia_recente":True,"imunossuprimido":False,
     "antibiotico":True,"febre":True,"secrecao":True,"sedacao":True,"nutricao_enteral":False,
     "disfagia":False,"sonda_vesical":False,"dreno":False,
     "dias_cateter":8,"dias_ventilacao":5,"medicacao":"Vancomicina 1g EV 12/12h",
     "temperatura":"38.9","avaliador":"Enf. Demo","observacao_tipo":"Sinais de infeccao no sitio",
     "observacao_livre":"Curativo com secrecao purulenta","prontuario_nome":"","prontuario_b64":""},
    {"id":2,"paciente":"João Pereira","leito":"L-12","data":"2026-03-02","score":9,"risco":"Medio",
     "setor":"Internacao A","cateter":False,"ventilacao":False,"cirurgia_recente":True,"imunossuprimido":True,
     "antibiotico":False,"febre":True,"secrecao":False,"sedacao":False,"nutricao_enteral":False,
     "disfagia":False,"sonda_vesical":True,"dreno":False,
     "dias_cateter":0,"dias_ventilacao":0,"medicacao":"","temperatura":"38.2",
     "avaliador":"Enf. Demo","observacao_tipo":"Paciente imunossuprimido em observacao",
     "observacao_livre":"","prontuario_nome":"","prontuario_b64":""},
    {"id":3,"paciente":"Ana Lima","leito":"L-03","data":"2026-03-03","score":3,"risco":"Baixo",
     "setor":"Area Laranja","cateter":False,"ventilacao":False,"cirurgia_recente":False,"imunossuprimido":False,
     "antibiotico":False,"febre":False,"secrecao":False,"sedacao":False,"nutricao_enteral":False,
     "disfagia":False,"sonda_vesical":False,"dreno":False,
     "dias_cateter":0,"dias_ventilacao":0,"medicacao":"","temperatura":"",
     "avaliador":"Enf. Demo","observacao_tipo":"Sem intercorrencias",
     "observacao_livre":"","prontuario_nome":"","prontuario_b64":""},
    {"id":4,"paciente":"Carlos Melo","leito":"L-05","data":"2026-03-04","score":14,"risco":"Alto",
     "setor":"UTI AVC","cateter":True,"ventilacao":False,"cirurgia_recente":False,"imunossuprimido":True,
     "antibiotico":True,"febre":True,"secrecao":False,"sedacao":False,"nutricao_enteral":False,
     "disfagia":True,"sonda_vesical":True,"dreno":False,
     "dias_cateter":6,"dias_ventilacao":0,"medicacao":"Meropenem 1g EV 8/8h",
     "temperatura":"39.1","avaliador":"Enf. Demo","observacao_tipo":"Febre persistente em investigacao",
     "observacao_livre":"","prontuario_nome":"","prontuario_b64":""},
]
if not st.session_state.avaliacoes:
    st.session_state.avaliacoes = MOCK.copy()
    st.session_state.contador = 5

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════
def risco_meta(risco):
    r = str(risco).lower()
    if "alto"  in r: return "Alto",  "alto",  "🔴", "#e53e3e"
    if "med"   in r: return "Médio", "medio", "🟡", "#c07a1a"
    return "Baixo", "baixo", "🟢", "#1a7a4a"

def calcular_score(d):
    s = 0
    for c,p in PESOS.items():
        if c.endswith("_bonus"): continue
        if d.get(c): s += p
    if d.get("cateter")   and d.get("dias_cateter",0)   > 3: s += int((d["dias_cateter"]-3)*PESOS["dias_cateter_bonus"])
    if d.get("ventilacao") and d.get("dias_ventilacao",0) > 2: s += int((d["dias_ventilacao"]-2)*PESOS["dias_ventilacao_bonus"])
    return s

def classificar(score):
    if score >= 14: return "Alto"
    if score >= 7:  return "Medio"
    return "Baixo"

# ══════════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════════
def fazer_login(email, senha):
    if USE_SUPABASE:
        try:
            res  = supabase.auth.sign_in_with_password({"email":email,"password":senha})
            meta = res.user.user_metadata or {}
            return True, meta.get("nome",email.split("@")[0].title()), meta.get("setor",SETORES[0])
        except Exception as e:
            return False, str(e), ""
    if email and senha: return True, email.split("@")[0].title(), SETORES[0]
    return False, "Preencha os campos.", ""

def fazer_logout():
    if USE_SUPABASE:
        try: supabase.auth.sign_out()
        except: pass
    for k in ["logado","usuario_email","usuario_nome","usuario_setor"]:
        st.session_state[k] = False if k=="logado" else ""

# ── LOGIN ─────────────────────────────────────────────────────
if not st.session_state.logado:
    st.markdown("""
    <div style="min-height:100vh;background:linear-gradient(160deg,#0d1f3c 0%,#163d6e 100%);
    display:flex;align-items:center;justify-content:center;padding:20px;position:fixed;
    inset:0;z-index:9999;"></div>""", unsafe_allow_html=True)

    _, col, _ = st.columns([1,1,1])
    with col:
        st.markdown("""
        <div style="background:#fff;border-radius:16px;padding:36px 32px 28px;
        box-shadow:0 20px 60px rgba(0,0,0,.28);margin-top:80px;">
          <div style="text-align:center;margin-bottom:24px;">
            <div style="width:52px;height:52px;background:#0d1f3c;border-radius:12px;
            display:inline-flex;align-items:center;justify-content:center;
            font-size:1.5rem;margin-bottom:10px;">🏥</div>
            <div style="font-size:1.3rem;font-weight:700;color:#0d1f3c;letter-spacing:-.3px;">VigInfec</div>
            <div style="font-size:.78rem;color:#8a94a6;margin-top:2px;">Vigilância de Infecção Hospitalar</div>
          </div>
        </div>""", unsafe_allow_html=True)

        with st.form("login_form"):
            email = st.text_input("E-mail", placeholder="enfermeiro@hospital.com")
            senha = st.text_input("Senha", type="password", placeholder="••••••••")
            btn   = st.form_submit_button("Entrar →", use_container_width=True, type="primary")

        if btn:
            if not email or not senha: st.error("Preencha todos os campos.")
            else:
                ok, nome, setor = fazer_login(email, senha)
                if ok:
                    st.session_state.update(logado=True, usuario_email=email,
                                            usuario_nome=nome, usuario_setor=setor)
                    st.rerun()
                else: st.error("Credenciais inválidas.")

        if not USE_SUPABASE:
            st.caption("🧪 Modo simulação — qualquer credencial funciona")
    st.stop()

# ══════════════════════════════════════════════════════════════
# DADOS
# ══════════════════════════════════════════════════════════════
def salvar(d):
    if USE_SUPABASE:
        supabase.table("avaliacoes").insert({k:v for k,v in d.items() if k!="id"}).execute()
    else:
        d["id"] = st.session_state.contador; st.session_state.contador += 1
        st.session_state.avaliacoes.append(d)

def atualizar(av_id, d):
    if USE_SUPABASE:
        supabase.table("avaliacoes").update({k:v for k,v in d.items() if k!="id"}).eq("id",av_id).execute()
    else:
        for i,a in enumerate(st.session_state.avaliacoes):
            if a["id"]==av_id: d["id"]=av_id; st.session_state.avaliacoes[i]=d; break

def carregar():
    if USE_SUPABASE:
        return supabase.table("avaliacoes").select("*").order("data",desc=True).execute().data
    return list(reversed(st.session_state.avaliacoes))

def deletar(av_id):
    if USE_SUPABASE: supabase.table("avaliacoes").delete().eq("id",av_id).execute()
    else: st.session_state.avaliacoes = [a for a in st.session_state.avaliacoes if a["id"]!=av_id]

# ══════════════════════════════════════════════════════════════
# PDF
# ══════════════════════════════════════════════════════════════
def lp(t):
    if not t: return "-"
    t = str(t)
    for o,s in {"\u2014":"-","\u2013":"-","\u00e9":"e","\u00ea":"e","\u00e1":"a","\u00e0":"a",
                "\u00e3":"a","\u00e2":"a","\u00ed":"i","\u00f3":"o","\u00f4":"o","\u00f5":"o",
                "\u00fa":"u","\u00fb":"u","\u00e7":"c","\u00c9":"E","\u00c1":"A","\u00c3":"A",
                "\u00cd":"I","\u00d3":"O","\u00d5":"O","\u00da":"U","\u00c7":"C","\u00b0":" graus"}.items():
        t = t.replace(o,s)
    return ''.join(c for c in t if ord(c)<128)

def gerar_pdf(d):
    pdf = FPDF(); pdf.add_page(); pdf.set_margins(20,20,20)
    # Header
    pdf.set_fill_color(13,31,60); pdf.rect(0,0,210,28,"F")
    pdf.set_font("Helvetica","B",14); pdf.set_text_color(255,255,255)
    pdf.set_y(6); pdf.cell(0,9,"SISTEMA DE VIGILANCIA DE INFECCAO HOSPITALAR",align="C",ln=True)
    pdf.set_font("Helvetica","",8); pdf.cell(0,5,"Relatorio de Avaliacao de Risco  -  VigInfec",align="C",ln=True)
    pdf.set_text_color(0,0,0); pdf.set_y(34)

    def h2(t):
        pdf.set_font("Helvetica","B",9); pdf.set_fill_color(241,245,249)
        pdf.cell(0,7,f"  {t}",ln=True,fill=True); pdf.ln(1)

    def row(lbl,val,bold_val=False,cor=None):
        pdf.set_font("Helvetica","B",8); pdf.cell(48,5.5,f"  {lbl}:",border=0)
        if cor: pdf.set_text_color(*cor)
        pdf.set_font("Helvetica","B" if bold_val else "",8)
        pdf.cell(0,5.5,lp(val),ln=True)
        pdf.set_text_color(0,0,0)

    rl,_,_,_ = risco_meta(d.get("risco","Baixo"))
    cr = (229,62,62) if "alto" in str(d.get("risco","")).lower() else (192,122,26) if "med" in str(d.get("risco","")).lower() else (26,122,74)

    h2("IDENTIFICACAO")
    row("Paciente",   d.get("paciente","-"))
    row("Leito",      d.get("leito","-"))
    row("Setor",      d.get("setor","-"))
    row("Data",       str(d.get("data",date.today())))
    row("Avaliador",  d.get("avaliador","-"))
    row("Score",      str(d.get("score","-")))
    row("Risco",      rl, bold_val=True, cor=cr)
    pdf.ln(3)

    h2("FATORES DE RISCO")
    setor  = d.get("setor","UTI Geral")
    for c in FATORES_POR_SETOR.get(setor,list(LABELS.keys())):
        pres = d.get(c,False)
        pdf.set_text_color(*(229,62,62) if pres else (138,148,166))
        pdf.set_font("Helvetica","",8)
        ex = ""
        if c=="cateter"   and pres and d.get("dias_cateter",0):   ex=f" (D{d['dias_cateter']})"
        if c=="ventilacao" and pres and d.get("dias_ventilacao",0): ex=f" (D{d['dias_ventilacao']})"
        pdf.cell(0,5.5,f"  {'[SIM]' if pres else '[NAO]'}  {lp(LABELS.get(c,c))}{ex}",ln=True)
    pdf.set_text_color(0,0,0)

    if d.get("medicacao"): pdf.ln(1); row("Medicacao", d["medicacao"])
    if d.get("febre") and d.get("temperatura"): row("Temperatura", f"{d['temperatura']} graus C")
    pdf.ln(3)

    ot = lp(d.get("observacao_tipo",""))
    ol = lp(d.get("observacao_livre",""))
    if (ot and ot!="-") or (ol and ol!="-"):
        h2("OBSERVACOES")
        if ot and ot!="-": row("Situacao",ot)
        if ol and ol!="-":
            pdf.set_font("Helvetica","B",8); pdf.cell(0,5.5,"  Descricao:",ln=True)
            pdf.set_font("Helvetica","",8); pdf.set_fill_color(247,248,252)
            pdf.multi_cell(0,5,f"  {ol}",fill=True)
        pdf.ln(3)

    if d.get("prontuario_b64"):
        try:
            h2("ANEXO - PRONTUARIO")
            ext  = (d.get("prontuario_nome","img.jpg")).split(".")[-1].lower()
            tipo = {"jpg":"JPEG","jpeg":"JPEG","png":"PNG"}.get(ext,"JPEG")
            pdf.image(io.BytesIO(base64.b64decode(d["prontuario_b64"])), x=20, w=170, type=tipo)
        except: pass

    pdf.set_y(-24); pdf.set_draw_color(13,31,60); pdf.line(20,pdf.get_y(),190,pdf.get_y()); pdf.ln(2)
    pdf.set_font("Helvetica","I",7); pdf.set_text_color(138,148,166)
    pdf.cell(0,4,f"Gerado em {datetime.now().strftime('%d/%m/%Y as %H:%M')}  |  Avaliador: {lp(d.get('avaliador','-'))}  |  Setor: {lp(d.get('setor','-'))}  |  VigInfec",align="C",ln=True)
    pdf.cell(0,4,"Instrumento de apoio clinico. Decisoes devem ser validadas por profissional habilitado.",align="C")
    return pdf.output()

# ══════════════════════════════════════════════════════════════
# FORMULÁRIO
# ══════════════════════════════════════════════════════════════
def formulario(pfx, di=None):
    d     = di or {}
    setor = st.session_state.usuario_setor or SETORES[0]
    fats  = FATORES_POR_SETOR.get(setor, list(LABELS.keys()))

    with st.form(f"f_{pfx}", clear_on_submit=(pfx=="novo")):
        st.markdown('<div class="slabel">Identificação do Paciente</div>', unsafe_allow_html=True)
        c1,c2 = st.columns([2,1])
        with c1: pac  = st.text_input("Nome do Paciente", value=d.get("paciente",""), placeholder="Nome completo")
        with c2: leito= st.text_input("Leito", value=d.get("leito",""), placeholder="Ex: UTI-01")
        c3,c4 = st.columns(2)
        with c3:
            try: dv = date.fromisoformat(str(d.get("data",date.today())))
            except: dv = date.today()
            dtav = st.date_input("Data", value=dv)
        with c4: st.text_input("Setor", value=setor, disabled=True)

        st.markdown(f'<div class="slabel">Fatores de Risco — {setor}</div>', unsafe_allow_html=True)
        vals = {}
        cols = st.columns(2)
        for i,c in enumerate(fats):
            with cols[i%2]:
                vals[c] = st.checkbox(f"{ICONS.get(c,'')} {LABELS.get(c,c)}", value=bool(d.get(c,False)), key=f"{pfx}_{c}")

        dias_cat = dias_vent = 0
        if vals.get("cateter") or vals.get("ventilacao"):
            st.markdown('<div class="slabel">Dias de Uso do Dispositivo</div>', unsafe_allow_html=True)
            dc1,dc2 = st.columns(2)
            with dc1:
                if vals.get("cateter"):
                    dias_cat = st.number_input("Dias com CVC", 0, 365, int(d.get("dias_cateter",0)), key=f"{pfx}_dc")
            with dc2:
                if vals.get("ventilacao"):
                    dias_vent = st.number_input("Dias de VM", 0, 365, int(d.get("dias_ventilacao",0)), key=f"{pfx}_dv")

        med = temp = ""
        if vals.get("antibiotico"):
            st.markdown('<div class="slabel">Medicação em Uso</div>', unsafe_allow_html=True)
            med = st.text_input("Descreva a medicação", value=d.get("medicacao",""),
                                placeholder="Ex: Vancomicina 1g EV 12/12h", key=f"{pfx}_med")
        if vals.get("febre"):
            st.markdown('<div class="slabel">Temperatura</div>', unsafe_allow_html=True)
            temp = st.text_input("Temperatura (°C)", value=d.get("temperatura",""),
                                  placeholder="Ex: 38.9", key=f"{pfx}_temp")

        st.markdown('<div class="slabel">Observação</div>', unsafe_allow_html=True)
        idx = OBS_OPCOES.index(d.get("observacao_tipo",OBS_OPCOES[0])) if d.get("observacao_tipo") in OBS_OPCOES else 0
        obs_t = st.selectbox("Situação atual", OBS_OPCOES, index=idx, key=f"{pfx}_ot")
        obs_l = st.text_area("Descrição adicional", value=d.get("observacao_livre",""),
                              height=80, placeholder="Detalhes para o relatório...", key=f"{pfx}_ol")

        st.markdown('<div class="slabel">Prontuário / Evolução</div>', unsafe_allow_html=True)
        img_up = st.file_uploader("Anexar imagem JPG ou PNG", type=["jpg","jpeg","png"], key=f"{pfx}_img")

        lbl = "💾 Salvar Alterações" if pfx != "novo" else "✓  Registrar Avaliação"
        sub = st.form_submit_button(lbl, use_container_width=True, type="primary")

    if sub:
        if not pac or not leito: st.error("Preencha nome e leito."); return None
        pb64 = d.get("prontuario_b64",""); pnm = d.get("prontuario_nome","")
        if img_up: pb64 = base64.b64encode(img_up.read()).decode(); pnm = img_up.name
        dados = dict(paciente=pac, leito=leito, data=str(dtav), setor=setor,
                     avaliador=st.session_state.usuario_nome,
                     dias_cateter=dias_cat, dias_ventilacao=dias_vent,
                     medicacao=med, temperatura=temp,
                     observacao_tipo=obs_t, observacao_livre=obs_l,
                     prontuario_b64=pb64, prontuario_nome=pnm)
        dados.update(vals)
        sc = calcular_score(dados); risco = classificar(sc)
        dados.update(score=sc, risco=risco)
        return dados
    return None

# ══════════════════════════════════════════════════════════════
# TOPBAR
# ══════════════════════════════════════════════════════════════
avs = carregar()
st.markdown(f"""
<div class="topbar">
  <div class="topbar-brand">🏥 <em>Vig</em>Infec</div>
  <div class="topbar-right">
    <span class="topbar-setor">{st.session_state.usuario_setor}</span>
    <span class="topbar-user">👤 {st.session_state.usuario_nome}</span>
  </div>
</div>""", unsafe_allow_html=True)

# Logout — alinhado à direita via colunas
_, col_out = st.columns([10,1])
with col_out:
    if st.button("Sair", key="logout"):
        fazer_logout(); st.rerun()

st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs(["📝  Nova Avaliação", "🏥  Visão por Setor", "📊  Dashboard", "📂  Histórico"])

# ─────────────────────────────────────────────────────────────
# TAB 1 — NOVA AVALIAÇÃO
# ─────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
    res = formulario("novo")
    if res:
        salvar(res)
        rl,rc,em,cor = risco_meta(res["risco"])
        st.markdown(f"""
        <div class="rbanner r-{rc}">
          <div class="rbanner-icon">{em}</div>
          <div class="rbanner-score">{res['score']}</div>
          <div class="rbanner-body">
            <div class="rbanner-title">Risco {rl}</div>
            <div class="rbanner-sub">{res['paciente']} · Leito {res['leito']} · {res['setor']} · {res['avaliador']}</div>
          </div>
        </div>""", unsafe_allow_html=True)
        st.success("Avaliação registrada com sucesso.")
        pb = gerar_pdf(res)
        st.download_button("⬇️  Baixar Relatório PDF", data=bytes(pb),
            file_name=f"viginfec_{res['paciente'].replace(' ','_')}_{res['data']}.pdf",
            mime="application/pdf", use_container_width=True)

# ─────────────────────────────────────────────────────────────
# TAB 2 — VISÃO POR SETOR
# ─────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
    if not avs:
        st.info("Nenhuma avaliação registrada ainda.")
    else:
        df_sv = pd.DataFrame(avs)

        # Resumo geral primeiro
        total_sv  = len(df_sv)
        altos_sv  = int(df_sv["risco"].str.lower().str.contains("alto",na=False).sum())
        st.markdown(f"""
        <div class="mrow" style="grid-template-columns:repeat(2,1fr);max-width:400px;">
          <div class="mcard"><div class="mcard-n mn-total">{total_sv}</div><div class="mcard-l">Total geral</div></div>
          <div class="mcard"><div class="mcard-n mn-alto">{altos_sv}</div><div class="mcard-l">Alto risco</div></div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="slabel">Situação atual de cada setor</div>', unsafe_allow_html=True)
        st.markdown('<div class="sov-grid">', unsafe_allow_html=True)

        for setor in SETORES:
            avs_set = [a for a in avs if a.get("setor","") == setor]
            n_tot  = len(avs_set)
            n_alt  = sum(1 for a in avs_set if "alto"  in str(a.get("risco","")).lower())
            n_med  = sum(1 for a in avs_set if "med"   in str(a.get("risco","")).lower())
            n_bai  = sum(1 for a in avs_set if "baixo" in str(a.get("risco","")).lower())
            pct_bar = int(n_alt/n_tot*100) if n_tot else 0
            alerta  = n_alt > 0

            alerta_html = '<div class="sov-alerta">⚠️ Atenção — pacientes de alto risco</div>' if alerta else ""
            st.markdown(f"""
            <div class="sov-card">
              <div class="sov-name">🏥 {setor}</div>
              <div class="sov-row"><span class="sov-lbl">Total avaliações</span><span class="sov-val">{n_tot}</span></div>
              <div class="sov-row"><span class="sov-lbl" style="color:#e53e3e">Risco Alto</span><span class="sov-val" style="color:#e53e3e">{n_alt}</span></div>
              <div class="sov-row"><span class="sov-lbl" style="color:#c07a1a">Risco Médio</span><span class="sov-val" style="color:#c07a1a">{n_med}</span></div>
              <div class="sov-row"><span class="sov-lbl" style="color:#1a7a4a">Risco Baixo</span><span class="sov-val" style="color:#1a7a4a">{n_bai}</span></div>
              <div class="sov-bar-wrap"><div class="sov-bar" style="width:{pct_bar}%"></div></div>
              {alerta_html}
            </div>""", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Lista de pacientes por setor (read-only)
        st.markdown('<div class="slabel" style="margin-top:24px;">Pacientes por setor</div>', unsafe_allow_html=True)
        setor_sel = st.selectbox("Selecione o setor", SETORES, key="sv_setor_sel")
        avs_sel   = [a for a in avs if a.get("setor","") == setor_sel]

        if not avs_sel:
            st.caption("Nenhuma avaliação neste setor.")
        else:
            for av in avs_sel:
                rl,rc,em,_ = risco_meta(av.get("risco","Baixo"))
                fats_atv   = [c for c in FATORES_POR_SETOR.get(setor_sel,[]) if av.get(c)]
                chips      = "".join([f'<span class="chip on">{ICONS.get(c,"")} {LABELS.get(c,c)}</span>' for c in fats_atv])
                if not chips: chips = '<span class="chip">Sem fatores ativos</span>'
                st.markdown(f"""
                <div class="hcard h-{rc}">
                  <div class="hcard-row1">
                    <div>
                      <div class="hcard-name">{av.get('paciente','-')} · Leito {av.get('leito','-')}</div>
                      <div class="hcard-meta">📅 {av.get('data','-')} · 👤 {av.get('avaliador','-')}</div>
                    </div>
                    <div>
                      <span class="hbadge b-{rc}">{em} {rl}</span>
                      <div class="hscore">Score {av.get('score','-')}</div>
                    </div>
                  </div>
                  <div class="chips">{chips}</div>
                </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# TAB 3 — DASHBOARD
# ─────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
    if not avs:
        st.info("Nenhuma avaliação registrada ainda.")
    else:
        df = pd.DataFrame(avs)
        df["rd"] = df["risco"].apply(lambda r: "Médio" if "med" in str(r).lower() else str(r))

        tot  = len(df)
        nalt = int(df["risco"].str.lower().str.contains("alto",na=False).sum())
        nmed = int(df["risco"].str.lower().str.contains("med",na=False).sum())
        nbai = int(df["risco"].str.lower().str.contains("baixo",na=False).sum())
        pct  = f"{nalt/tot*100:.0f}%" if tot else "0%"

        st.markdown(f"""
        <div class="mrow">
          <div class="mcard"><div class="mcard-n mn-total">{tot}</div><div class="mcard-l">Total</div></div>
          <div class="mcard"><div class="mcard-n mn-alto">{nalt}</div><div class="mcard-l">Alto · {pct}</div></div>
          <div class="mcard"><div class="mcard-n mn-medio">{nmed}</div><div class="mcard-l">Médio</div></div>
          <div class="mcard"><div class="mcard-n mn-baixo">{nbai}</div><div class="mcard-l">Baixo</div></div>
        </div>""", unsafe_allow_html=True)

        CHART_LAYOUT = dict(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter",size=11,color="#4a5568"),
            margin=dict(t=36,b=8,l=8,r=8),
        )

        c1,c2 = st.columns(2)
        with c1:
            cnt = df["rd"].value_counts().reset_index(); cnt.columns=["Risco","Qtd"]
            fig = px.pie(cnt, names="Risco", values="Qtd", hole=0.58,
                         color="Risco", color_discrete_map={"Alto":"#e53e3e","Médio":"#c07a1a","Baixo":"#1a7a4a"})
            fig.update_layout(**CHART_LAYOUT, title=dict(text="Distribuição por Risco",font=dict(size=12),x=0,y=.97))
            fig.update_traces(textfont=dict(family="Inter"), textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            if "setor" in df.columns:
                cnt_s = df["setor"].value_counts().reset_index(); cnt_s.columns=["Setor","Qtd"]
                fig_s = px.bar(cnt_s, x="Qtd", y="Setor", orientation="h",
                               color="Qtd", color_continuous_scale=["#dbeafe","#163d6e"])
                fig_s.update_layout(**CHART_LAYOUT, title=dict(text="Avaliações por Setor",font=dict(size=12),x=0,y=.97),
                                    coloraxis_showscale=False,
                                    xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
                                    yaxis=dict(tickfont=dict(size=10)))
                st.plotly_chart(fig_s, use_container_width=True)

        colf = [c for c in LABELS if c in df.columns]
        prev = [int(df[c].sum()) for c in colf]
        lblf = [LABELS[c] for c in colf]

        fig_b = go.Figure(go.Bar(
            x=prev, y=lblf, orientation="h",
            marker=dict(color=prev, colorscale=[[0,"#d1fae5"],[.5,"#fef3c7"],[1,"#fee2e2"]], showscale=False),
            text=prev, textposition="outside", textfont=dict(size=10,family="Inter"),
        ))
        fig_b.update_layout(**CHART_LAYOUT,
            title=dict(text="Prevalência de Fatores de Risco",font=dict(size=12),x=0,y=.99),
            xaxis=dict(showgrid=False,showticklabels=False,range=[0,max(prev)*1.15 if prev else 1]),
            yaxis=dict(tickfont=dict(size=10)),
            height=max(260, len(colf)*28),
            margin=dict(t=36,b=8,l=8,r=48),
        )
        st.plotly_chart(fig_b, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# TAB 4 — HISTÓRICO
# ─────────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
    if not avs:
        st.info("Nenhuma avaliação registrada ainda.")
    else:
        # Barra de filtros
        fc1,fc2,fc3 = st.columns([3,1,1])
        with fc1: busca   = st.text_input("", placeholder="🔍  Buscar por paciente, leito ou avaliador...", label_visibility="collapsed")
        with fc2: f_risco = st.selectbox("", ["Todos","Alto","Médio","Baixo"], label_visibility="collapsed")
        with fc3: f_setor = st.selectbox("", ["Todos"]+SETORES, label_visibility="collapsed")

        filt = avs
        if busca:
            b = busca.lower()
            filt = [a for a in filt if b in str(a.get("paciente","")).lower()
                    or b in str(a.get("leito","")).lower() or b in str(a.get("avaliador","")).lower()]
        if f_risco != "Todos":
            filt = [a for a in filt if
                (f_risco=="Médio" and "med" in str(a.get("risco","")).lower()) or
                (f_risco!="Médio" and f_risco.lower() in str(a.get("risco","")).lower())]
        if f_setor != "Todos":
            filt = [a for a in filt if a.get("setor","") == f_setor]

        st.caption(f"{len(filt)} registro{'s' if len(filt)!=1 else ''} encontrado{'s' if len(filt)!=1 else ''}")
        st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

        for av in filt:
            av_id = av.get("id",0)
            rl,rc,em,_ = risco_meta(av.get("risco","Baixo"))
            fat_atv    = [c for c in FATORES_POR_SETOR.get(av.get("setor","UTI Geral"),[]) if av.get(c)]
            chips_h    = "".join([f'<span class="chip on">{ICONS.get(c,"")} {LABELS.get(c,c)}</span>' for c in fat_atv])
            if not chips_h: chips_h = '<span class="chip">Sem fatores ativos</span>'

            st.markdown(f"""
            <div class="hcard h-{rc}">
              <div class="hcard-row1">
                <div>
                  <div class="hcard-name">{av.get('paciente','-')} · Leito {av.get('leito','-')}</div>
                  <div class="hcard-meta">📅 {av.get('data','-')} &nbsp;·&nbsp; 🏥 {av.get('setor','-')} &nbsp;·&nbsp; 👤 {av.get('avaliador','-')}</div>
                </div>
                <div>
                  <span class="hbadge b-{rc}">{em} {rl}</span>
                  <div class="hscore">Score {av.get('score','-')}</div>
                </div>
              </div>
              <div class="chips">{chips_h}</div>
            </div>""", unsafe_allow_html=True)

            with st.expander("Detalhes · Editar · Excluir"):
                if st.session_state.editando_id == av_id:
                    st.markdown("#### ✏️ Editando")
                    res_e = formulario(f"e{av_id}", di=av)
                    if res_e:
                        atualizar(av_id, res_e)
                        st.session_state.editando_id = None
                        st.success("Atualizado!")
                        st.rerun()
                    if st.button("Cancelar", key=f"cx{av_id}"):
                        st.session_state.editando_id = None; st.rerun()
                else:
                    # Info
                    r1,r2 = st.columns(2)
                    with r1:
                        if av.get("medicacao"):    st.write(f"💊 **Medicação:** {av['medicacao']}")
                        if av.get("temperatura"):  st.write(f"🌡️ **Temperatura:** {av['temperatura']} °C")
                    with r2:
                        if av.get("observacao_tipo"): st.write(f"📌 {av['observacao_tipo']}")
                        if av.get("observacao_livre"): st.caption(av["observacao_livre"])

                    if av.get("prontuario_b64"):
                        with st.expander("📎 Ver prontuário"):
                            try:
                                st.image(base64.b64decode(av["prontuario_b64"]),
                                         caption=av.get("prontuario_nome","Anexo"),
                                         use_column_width=True)
                            except: st.warning("Não foi possível exibir o anexo.")

                    ba,bb,bc = st.columns(3)
                    with ba:
                        pb = gerar_pdf(av)
                        st.download_button("⬇️ PDF", data=bytes(pb),
                            file_name=f"viginfec_{str(av.get('paciente','')).replace(' ','_')}_{av.get('data','')}.pdf",
                            mime="application/pdf", key=f"p{av_id}")
                    with bb:
                        if st.button("✏️ Editar", key=f"eb{av_id}"):
                            st.session_state.editando_id = av_id; st.rerun()
                    with bc:
                        if st.button("🗑️ Excluir", key=f"db{av_id}"):
                            deletar(av_id); st.rerun()
