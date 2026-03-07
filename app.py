"""
VigInfec — Sistema de Vigilância de Infecção Hospitalar
=======================================================
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

# ============================================================
USE_SUPABASE = True
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except:
    SUPABASE_URL = "https://juzyjqauwujtcsxgsogh.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp1enlqcWF1d3VqdGNzeGdzb2doIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3MzE1MjUsImV4cCI6MjA4ODMwNzUyNX0.r90v3aN_lf0Hrf7uyFll4ZQh29WGz8PQKNegBH8p1NY"
# ============================================================

if USE_SUPABASE:
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── Página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="VigInfec",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════
# CSS — Design Clínico Profissional
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

:root {
    --navy:    #0f2342;
    --blue:    #1a3a6b;
    --accent:  #2563eb;
    --accent2: #3b82f6;
    --red:     #dc2626;
    --yellow:  #d97706;
    --green:   #059669;
    --red-bg:  #fef2f2;
    --yel-bg:  #fffbeb;
    --grn-bg:  #f0fdf4;
    --gray-50: #f8fafc;
    --gray-100:#f1f5f9;
    --gray-200:#e2e8f0;
    --gray-400:#94a3b8;
    --gray-600:#475569;
    --gray-800:#1e293b;
    --white:   #ffffff;
    --shadow:  0 1px 3px rgba(0,0,0,.08), 0 4px 16px rgba(0,0,0,.06);
    --shadow-lg: 0 4px 6px rgba(0,0,0,.07), 0 12px 32px rgba(0,0,0,.1);
    --radius:  12px;
    --radius-sm: 8px;
}

* { font-family: 'DM Sans', sans-serif !important; }
code, .stCode { font-family: 'DM Mono', monospace !important; }

/* Reset streamlit defaults */
.main .block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none !important; }
header[data-testid="stHeader"] { display: none !important; }
.stDeployButton { display: none !important; }
footer { display: none !important; }

/* ── TOP NAV ───────────────────────────── */
.viginfec-nav {
    background: var(--navy);
    padding: 0 24px;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 999;
    box-shadow: 0 2px 12px rgba(0,0,0,.2);
}
.nav-brand {
    color: white;
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: -.3px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.nav-brand span { color: #60a5fa; }
.nav-user {
    color: #94a3b8;
    font-size: .8rem;
    display: flex;
    align-items: center;
    gap: 10px;
}
.nav-badge {
    background: rgba(37,99,235,.3);
    color: #93c5fd;
    padding: 3px 10px;
    border-radius: 99px;
    font-size: .72rem;
    font-weight: 600;
    letter-spacing: .3px;
    text-transform: uppercase;
}

/* ── MAIN CONTENT ──────────────────────── */
.page-wrap {
    padding: 24px 20px;
    max-width: 900px;
    margin: 0 auto;
}

/* ── CARDS ─────────────────────────────── */
.card {
    background: var(--white);
    border-radius: var(--radius);
    border: 1px solid var(--gray-200);
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: var(--shadow);
}
.card-header {
    font-size: .7rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--gray-400);
    margin-bottom: 12px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--gray-100);
}

/* ── RISCO ALERTS ──────────────────────── */
.alert {
    border-radius: var(--radius);
    padding: 16px 20px;
    margin: 12px 0;
    display: flex;
    align-items: flex-start;
    gap: 12px;
}
.alert-alto   { background: var(--red-bg); border-left: 4px solid var(--red); }
.alert-medio  { background: var(--yel-bg); border-left: 4px solid var(--yellow); }
.alert-baixo  { background: var(--grn-bg); border-left: 4px solid var(--green); }
.alert-icon   { font-size: 1.4rem; line-height: 1; margin-top: 2px; }
.alert-title  { font-weight: 700; font-size: 1rem; margin-bottom: 2px; }
.alert-sub    { font-size: .85rem; color: var(--gray-600); }

/* ── METRIC CARDS ──────────────────────── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 20px;
}
@media (max-width: 600px) {
    .metric-grid { grid-template-columns: repeat(2, 1fr); }
}
.metric-card {
    background: var(--white);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius);
    padding: 16px;
    text-align: center;
    box-shadow: var(--shadow);
    transition: transform .15s, box-shadow .15s;
}
.metric-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-lg); }
.metric-num  { font-size: 1.8rem; font-weight: 700; line-height: 1; }
.metric-lbl  { font-size: .72rem; color: var(--gray-400); margin-top: 4px; font-weight: 500; letter-spacing: .3px; text-transform: uppercase; }
.metric-alto   .metric-num { color: var(--red); }
.metric-medio  .metric-num { color: var(--yellow); }
.metric-baixo  .metric-num { color: var(--green); }
.metric-total  .metric-num { color: var(--navy); }

/* ── HISTÓRICO CARDS ────────────────────── */
.hcard {
    background: var(--white);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius);
    padding: 16px 18px;
    margin-bottom: 10px;
    box-shadow: var(--shadow);
    border-left: 4px solid var(--gray-200);
    transition: box-shadow .15s;
}
.hcard:hover { box-shadow: var(--shadow-lg); }
.hcard-alto   { border-left-color: var(--red); }
.hcard-medio  { border-left-color: var(--yellow); }
.hcard-baixo  { border-left-color: var(--green); }
.hcard-top    { display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px; }
.hcard-name   { font-size: 1rem; font-weight: 700; color: var(--gray-800); }
.hcard-meta   { font-size: .78rem; color: var(--gray-400); margin-top: 3px; }
.hcard-badge  { padding: 3px 10px; border-radius: 99px; font-size: .72rem; font-weight: 700; letter-spacing: .3px; text-transform: uppercase; white-space: nowrap; }
.badge-alto   { background: #fee2e2; color: var(--red); }
.badge-medio  { background: #fef3c7; color: var(--yellow); }
.badge-baixo  { background: #d1fae5; color: var(--green); }
.hcard-chips  { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
.chip {
    background: var(--gray-100);
    color: var(--gray-600);
    padding: 3px 9px;
    border-radius: 99px;
    font-size: .72rem;
    font-weight: 500;
}
.chip-active { background: #dbeafe; color: var(--accent); }

/* ── SECTION TITLE ─────────────────────── */
.sec-title {
    font-size: .7rem;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: var(--accent);
    margin: 20px 0 10px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.sec-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--gray-200);
}

/* ── SCORE RING ────────────────────────── */
.score-display {
    text-align: center;
    padding: 20px;
}
.score-num {
    font-size: 3rem;
    font-weight: 700;
    line-height: 1;
}
.score-lbl { font-size: .75rem; color: var(--gray-400); text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }

/* ── STREAMLIT OVERRIDES ───────────────── */
div[data-testid="stForm"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}
.stCheckbox > label {
    background: var(--gray-50);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-sm);
    padding: 8px 12px !important;
    width: 100%;
    font-size: .88rem !important;
    transition: background .12s, border-color .12s;
    cursor: pointer;
}
.stCheckbox > label:hover { background: #eff6ff; border-color: var(--accent2); }
div[data-testid="stCheckbox"] { margin-bottom: 6px !important; }
.stTextInput input, .stTextArea textarea, .stSelectbox select,
div[data-baseweb="select"] > div {
    border-radius: var(--radius-sm) !important;
    border-color: var(--gray-200) !important;
    font-size: .9rem !important;
    background: var(--white) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,.1) !important;
}
div[data-testid="stNumberInput"] input {
    border-radius: var(--radius-sm) !important;
    font-size: .9rem !important;
}
.stButton > button {
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    font-size: .88rem !important;
    transition: all .15s !important;
}
.stButton > button[kind="primary"] {
    background: var(--accent) !important;
    border: none !important;
    color: white !important;
}
.stButton > button[kind="primary"]:hover {
    background: #1d4ed8 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(37,99,235,.3) !important;
}
div[data-testid="stTabs"] button {
    font-weight: 600 !important;
    font-size: .85rem !important;
    color: var(--gray-600) !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--accent) !important;
}
.stSuccess, .stError, .stInfo, .stWarning {
    border-radius: var(--radius-sm) !important;
    font-size: .88rem !important;
}
div[data-testid="stExpander"] {
    border: 1px solid var(--gray-200) !important;
    border-radius: var(--radius) !important;
    background: var(--white) !important;
}
label[data-testid="stWidgetLabel"] {
    font-size: .8rem !important;
    font-weight: 600 !important;
    color: var(--gray-600) !important;
    letter-spacing: .2px !important;
    text-transform: uppercase !important;
    margin-bottom: 4px !important;
}

/* ── LOGIN ─────────────────────────────── */
.login-wrap {
    min-height: 100vh;
    background: linear-gradient(135deg, #0f2342 0%, #1a3a6b 50%, #0f2342 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
}
.login-card {
    background: white;
    border-radius: 20px;
    padding: 40px;
    width: 100%;
    max-width: 400px;
    box-shadow: 0 24px 64px rgba(0,0,0,.25);
}
.login-logo {
    text-align: center;
    margin-bottom: 28px;
}
.login-logo-icon {
    width: 60px; height: 60px;
    background: var(--navy);
    border-radius: 16px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 1.8rem;
    margin-bottom: 12px;
}
.login-title { font-size: 1.4rem; font-weight: 700; color: var(--navy); margin-bottom: 4px; }
.login-sub   { font-size: .85rem; color: var(--gray-400); }

/* ── DIVIDER ───────────────────────────── */
.divider { height: 1px; background: var(--gray-200); margin: 16px 0; }

/* ── EMPTY STATE ───────────────────────── */
.empty-state {
    text-align: center;
    padding: 48px 20px;
    color: var(--gray-400);
}
.empty-icon { font-size: 2.5rem; margin-bottom: 12px; }
.empty-text { font-size: .95rem; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# DADOS E CONFIGURAÇÕES
# ══════════════════════════════════════════════════════════════
SETORES = [
    "UTI Geral","UTI 1","UTI 2","UTI AVC",
    "Area Laranja","Area Vermelha",
    "Internacao A","Internacao B","Internacao C",
]

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

LABELS_FATORES = {
    "cateter":          "Cateter Venoso Central",
    "ventilacao":       "Ventilação Mecânica",
    "cirurgia_recente": "Cirurgia < 30 dias",
    "imunossuprimido":  "Imunossupressão",
    "antibiotico":      "Em uso de Antibiótico",
    "febre":            "Febre > 38°C",
    "secrecao":         "Secreção Anormal",
    "sedacao":          "Sedação Contínua",
    "nutricao_enteral": "Nutrição Enteral",
    "disfagia":         "Disfagia",
    "sonda_vesical":    "Sonda Vesical",
    "dreno":            "Dreno Cirúrgico",
}

ICONS_FATORES = {
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

OPCOES_OBSERVACAO = [
    "Sem intercorrencias",
    "Sinais de infeccao no sitio",
    "Febre persistente em investigacao",
    "Paciente imunossuprimido em observacao",
    "Aguardando resultado de cultura",
    "Em uso de antibiotico de amplo espectro",
    "Dispositivo com sinais de flebite",
    "Outro (ver descricao livre)",
]

# ── Session State ────────────────────────────────────────────
defaults = {
    "logado":False,"usuario_email":"","usuario_nome":"","usuario_setor":"",
    "avaliacoes":[],"contador":1,"editando_id":None,"tab_ativa":"nova",
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

MOCK_INICIAL = [
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
]
if not st.session_state.avaliacoes:
    st.session_state.avaliacoes = MOCK_INICIAL.copy()
    st.session_state.contador = 4

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════
def risco_info(risco: str):
    r = str(risco).lower()
    if "alto"  in r: return "Alto",  "alto",  "🔴", "#dc2626"
    if "med"   in r: return "Médio", "medio", "🟡", "#d97706"
    return "Baixo", "baixo", "🟢", "#059669"

def calcular_score(dados):
    s = 0
    for campo, peso in PESOS.items():
        if campo.endswith("_bonus"): continue
        if dados.get(campo): s += peso
    if dados.get("cateter") and dados.get("dias_cateter",0) > 3:
        s += int((dados["dias_cateter"]-3)*PESOS["dias_cateter_bonus"])
    if dados.get("ventilacao") and dados.get("dias_ventilacao",0) > 2:
        s += int((dados["dias_ventilacao"]-2)*PESOS["dias_ventilacao_bonus"])
    return s

def classificar_risco(score):
    if score >= 14: return "Alto",  "alert-alto"
    if score >= 7:  return "Medio", "alert-medio"
    return "Baixo", "alert-baixo"

# ══════════════════════════════════════════════════════════════
# AUTENTICAÇÃO
# ══════════════════════════════════════════════════════════════
def fazer_login(email, senha):
    if USE_SUPABASE:
        try:
            res  = supabase.auth.sign_in_with_password({"email":email,"password":senha})
            meta = res.user.user_metadata or {}
            return True, meta.get("nome",email.split("@")[0].title()), meta.get("setor",SETORES[0])
        except Exception as e:
            return False, str(e), ""
    else:
        if email and senha: return True, email.split("@")[0].title(), SETORES[0]
        return False, "Preencha email e senha.", ""

def fazer_logout():
    if USE_SUPABASE:
        try: supabase.auth.sign_out()
        except: pass
    for k in ["logado","usuario_email","usuario_nome","usuario_setor"]:
        st.session_state[k] = False if k=="logado" else ""

# ── TELA DE LOGIN ─────────────────────────────────────────────
if not st.session_state.logado:
    st.markdown("""
    <div style="min-height:100vh;background:linear-gradient(135deg,#0f2342 0%,#1a3a6b 60%,#0f2342 100%);
    display:flex;align-items:center;justify-content:center;padding:20px;">
    </div>""", unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        st.markdown("""
        <div style="background:white;border-radius:20px;padding:36px 32px;
        box-shadow:0 24px 64px rgba(0,0,0,.3);margin-top:60px;">
            <div style="text-align:center;margin-bottom:24px;">
                <div style="width:56px;height:56px;background:#0f2342;border-radius:14px;
                display:inline-flex;align-items:center;justify-content:center;font-size:1.6rem;margin-bottom:10px;">🏥</div>
                <div style="font-size:1.4rem;font-weight:700;color:#0f2342;font-family:'DM Sans',sans-serif;">VigInfec</div>
                <div style="font-size:.82rem;color:#94a3b8;margin-top:2px;">Vigilância de Infecção Hospitalar</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login"):
            email = st.text_input("E-mail", placeholder="seu@hospital.com")
            senha = st.text_input("Senha", type="password", placeholder="••••••••")
            ok_btn = st.form_submit_button("Entrar →", use_container_width=True, type="primary")

        if ok_btn:
            if not email or not senha:
                st.error("Preencha e-mail e senha.")
            else:
                ok, nome, setor = fazer_login(email, senha)
                if ok:
                    st.session_state.logado        = True
                    st.session_state.usuario_email = email
                    st.session_state.usuario_nome  = nome
                    st.session_state.usuario_setor = setor
                    st.rerun()
                else:
                    st.error(f"Credenciais inválidas")

        if not USE_SUPABASE:
            st.caption("🧪 Modo simulação — qualquer credencial funciona")
    st.stop()

# ══════════════════════════════════════════════════════════════
# FUNÇÕES DE DADOS
# ══════════════════════════════════════════════════════════════
def salvar_avaliacao(dados):
    if USE_SUPABASE:
        payload = {k:v for k,v in dados.items() if k!="id"}
        supabase.table("avaliacoes").insert(payload).execute()
    else:
        dados["id"] = st.session_state.contador
        st.session_state.contador += 1
        st.session_state.avaliacoes.append(dados)

def atualizar_avaliacao(av_id, dados):
    if USE_SUPABASE:
        payload = {k:v for k,v in dados.items() if k!="id"}
        supabase.table("avaliacoes").update(payload).eq("id",av_id).execute()
    else:
        for i,a in enumerate(st.session_state.avaliacoes):
            if a["id"]==av_id:
                dados["id"]=av_id
                st.session_state.avaliacoes[i]=dados; break

def carregar_avaliacoes():
    if USE_SUPABASE:
        res = supabase.table("avaliacoes").select("*").order("data",desc=True).execute()
        return res.data
    return list(reversed(st.session_state.avaliacoes))

def deletar_avaliacao(av_id):
    if USE_SUPABASE:
        supabase.table("avaliacoes").delete().eq("id",av_id).execute()
    else:
        st.session_state.avaliacoes = [a for a in st.session_state.avaliacoes if a["id"]!=av_id]

# ══════════════════════════════════════════════════════════════
# PDF
# ══════════════════════════════════════════════════════════════
def limpar_pdf(texto) -> str:
    if not texto: return "-"
    texto = str(texto)
    mapa = {
        "\u2014":"-","\u2013":"-","\u00e9":"e","\u00ea":"e","\u00e1":"a","\u00e0":"a",
        "\u00e3":"a","\u00e2":"a","\u00ed":"i","\u00f3":"o","\u00f4":"o","\u00f5":"o",
        "\u00fa":"u","\u00fb":"u","\u00e7":"c","\u00c9":"E","\u00c1":"A","\u00c3":"A",
        "\u00cd":"I","\u00d3":"O","\u00d5":"O","\u00da":"U","\u00c7":"C","\u00b0":" graus",
    }
    for o,s in mapa.items(): texto=texto.replace(o,s)
    return ''.join(c for c in texto if ord(c)<128)

def gerar_pdf(dados):
    pdf = FPDF(); pdf.add_page(); pdf.set_margins(20,20,20)
    pdf.set_fill_color(15,35,66); pdf.rect(0,0,210,30,"F")
    pdf.set_font("Helvetica","B",15); pdf.set_text_color(255,255,255)
    pdf.set_y(7); pdf.cell(0,10,"SISTEMA DE VIGILANCIA DE INFECCAO HOSPITALAR",align="C",ln=True)
    pdf.set_font("Helvetica","",9)
    pdf.cell(0,6,"Relatorio de Avaliacao de Risco - VigInfec",align="C",ln=True)
    pdf.set_text_color(0,0,0); pdf.set_y(36)

    def secao(titulo):
        pdf.set_font("Helvetica","B",10); pdf.set_fill_color(241,245,249)
        pdf.cell(0,7,f"  {titulo}",ln=True,fill=True); pdf.ln(2)

    def campo(label,valor,cor=None):
        pdf.set_font("Helvetica","B",9); pdf.cell(52,6,f"  {label}:",border=0)
        pdf.set_font("Helvetica","",9)
        if cor: pdf.set_text_color(*cor); pdf.set_font("Helvetica","B",9)
        pdf.cell(0,6,limpar_pdf(valor),ln=True); pdf.set_text_color(0,0,0)

    risco = dados.get("risco","Baixo")
    rl,_,_,_ = risco_info(risco)
    cor_risco = (220,38,38) if "alto" in risco.lower() else (202,138,4) if "med" in risco.lower() else (22,163,74)

    secao("IDENTIFICACAO")
    campo("Paciente",    dados.get("paciente","-"))
    campo("Leito",       dados.get("leito","-"))
    campo("Setor",       dados.get("setor","-"))
    campo("Data",        str(dados.get("data",date.today())))
    campo("Avaliador",   dados.get("avaliador","-"))
    campo("Score",       str(dados.get("score","-")))
    campo("Classificacao", rl, cor=cor_risco)
    pdf.ln(3)

    secao("FATORES DE RISCO")
    setor     = dados.get("setor","UTI Geral")
    fat_list  = FATORES_POR_SETOR.get(setor, list(LABELS_FATORES.keys()))
    for campo_f in fat_list:
        presente = dados.get(campo_f,False)
        cor_f    = (220,38,38) if presente else (148,163,184)
        pdf.set_text_color(*cor_f)
        status = "[SIM]" if presente else "[NAO]"
        label_f = limpar_pdf(LABELS_FATORES.get(campo_f,campo_f))
        extra   = ""
        if campo_f=="cateter"   and presente and dados.get("dias_cateter",0):   extra=f" (D{dados['dias_cateter']})"
        if campo_f=="ventilacao" and presente and dados.get("dias_ventilacao",0): extra=f" (D{dados['dias_ventilacao']})"
        pdf.set_font("Helvetica","",9)
        pdf.cell(0,6,f"  {status}  {label_f}{extra}",ln=True)
    pdf.set_text_color(0,0,0)

    if dados.get("medicacao"):
        pdf.ln(2); pdf.set_font("Helvetica","B",9)
        pdf.cell(52,6,"  Medicacao:",border=0)
        pdf.set_font("Helvetica","",9)
        pdf.multi_cell(0,6,limpar_pdf(dados["medicacao"]))

    if dados.get("febre") and dados.get("temperatura"):
        pdf.set_font("Helvetica","B",9); pdf.cell(52,6,"  Temperatura:",border=0)
        pdf.set_font("Helvetica","",9)
        pdf.cell(0,6,f"{limpar_pdf(dados['temperatura'])} graus C",ln=True)

    pdf.ln(3)

    obs_tipo  = limpar_pdf(dados.get("observacao_tipo",""))
    obs_livre = limpar_pdf(dados.get("observacao_livre",""))
    if (obs_tipo and obs_tipo!="-") or (obs_livre and obs_livre!="-"):
        secao("OBSERVACOES")
        if obs_tipo and obs_tipo!="-":
            pdf.set_font("Helvetica","B",9); pdf.cell(52,6,"  Situacao:",border=0)
            pdf.set_font("Helvetica","",9); pdf.multi_cell(0,6,obs_tipo)
        if obs_livre and obs_livre!="-":
            pdf.set_font("Helvetica","B",9); pdf.cell(0,6,"  Descricao:",ln=True)
            pdf.set_font("Helvetica","",9)
            pdf.set_fill_color(248,250,252)
            pdf.multi_cell(0,5,f"  {obs_livre}",fill=True)
        pdf.ln(3)

    if dados.get("prontuario_b64"):
        try:
            secao("ANEXO - PRONTUARIO")
            img_bytes = base64.b64decode(dados["prontuario_b64"])
            ext = (dados.get("prontuario_nome","img.jpg")).split(".")[-1].lower()
            tipo = {"jpg":"JPEG","jpeg":"JPEG","png":"PNG"}.get(ext,"JPEG")
            pdf.image(io.BytesIO(img_bytes), x=20, w=170, type=tipo)
        except: pass

    pdf.set_y(-26); pdf.set_draw_color(15,35,66)
    pdf.line(20,pdf.get_y(),190,pdf.get_y()); pdf.ln(2)
    pdf.set_font("Helvetica","I",7); pdf.set_text_color(148,163,184)
    pdf.cell(0,4,f"Gerado em {datetime.now().strftime('%d/%m/%Y as %H:%M')}  |  Avaliador: {limpar_pdf(dados.get('avaliador','-'))}  |  Setor: {limpar_pdf(dados.get('setor','-'))}  |  VigInfec",align="C",ln=True)
    pdf.cell(0,4,"Instrumento de apoio clinico. Decisoes devem ser validadas por profissional habilitado.",align="C")
    return pdf.output()

# ══════════════════════════════════════════════════════════════
# FORMULÁRIO
# ══════════════════════════════════════════════════════════════
def renderizar_formulario(prefixo, dados_iniciais=None):
    d = dados_iniciais or {}
    setor = st.session_state.usuario_setor or SETORES[0]
    fatores = FATORES_POR_SETOR.get(setor, list(LABELS_FATORES.keys()))

    with st.form(f"form_{prefixo}", clear_on_submit=(prefixo=="novo")):

        st.markdown('<div class="sec-title">👤 Identificação</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([2,1])
        with c1: paciente = st.text_input("Nome do Paciente", value=d.get("paciente",""), placeholder="Nome completo")
        with c2: leito    = st.text_input("Leito", value=d.get("leito",""), placeholder="Ex: UTI-01")

        c3, c4 = st.columns([1,1])
        with c3:
            try: dval = date.fromisoformat(str(d.get("data",date.today())))
            except: dval = date.today()
            data_av = st.date_input("Data da Avaliação", value=dval)
        with c4:
            st.text_input("Setor", value=setor, disabled=True)

        st.markdown(f'<div class="sec-title">⚠️ Fatores de Risco — {setor}</div>', unsafe_allow_html=True)

        valores = {}
        cols = st.columns(2)
        for i, campo in enumerate(fatores):
            with cols[i % 2]:
                icon = ICONS_FATORES.get(campo,"")
                valores[campo] = st.checkbox(
                    f"{icon} {LABELS_FATORES.get(campo,campo)}",
                    value=bool(d.get(campo,False)),
                    key=f"{prefixo}_{campo}"
                )

        dias_cateter = dias_ventilacao = 0
        if valores.get("cateter") or valores.get("ventilacao"):
            st.markdown('<div class="sec-title">📅 Dias de Uso</div>', unsafe_allow_html=True)
            dc1, dc2 = st.columns(2)
            with dc1:
                if valores.get("cateter"):
                    dias_cateter = st.number_input("Dias com CVC", min_value=0, max_value=365,
                                                    value=int(d.get("dias_cateter",0)), key=f"{prefixo}_dc")
            with dc2:
                if valores.get("ventilacao"):
                    dias_ventilacao = st.number_input("Dias de VM", min_value=0, max_value=365,
                                                       value=int(d.get("dias_ventilacao",0)), key=f"{prefixo}_dv")

        medicacao = ""
        if valores.get("antibiotico"):
            st.markdown('<div class="sec-title">💊 Medicação</div>', unsafe_allow_html=True)
            medicacao = st.text_input(
                "Medicação em uso",
                value=d.get("medicacao",""),
                placeholder="Ex: Vancomicina 1g EV 12/12h",
                key=f"{prefixo}_med"
            )

        temperatura = ""
        if valores.get("febre"):
            st.markdown('<div class="sec-title">🌡️ Temperatura</div>', unsafe_allow_html=True)
            temperatura = st.text_input(
                "Temperatura (°C)",
                value=d.get("temperatura",""),
                placeholder="Ex: 38.9",
                key=f"{prefixo}_temp"
            )

        st.markdown('<div class="sec-title">📝 Observação</div>', unsafe_allow_html=True)
        idx_obs = OPCOES_OBSERVACAO.index(d.get("observacao_tipo",OPCOES_OBSERVACAO[0])) \
                  if d.get("observacao_tipo") in OPCOES_OBSERVACAO else 0
        obs_tipo  = st.selectbox("Situação", options=OPCOES_OBSERVACAO, index=idx_obs, key=f"{prefixo}_ot")
        obs_livre = st.text_area("Descrição adicional (aparece no PDF)", value=d.get("observacao_livre",""),
                                  height=80, key=f"{prefixo}_ol", placeholder="Detalhes relevantes...")

        st.markdown('<div class="sec-title">📎 Prontuário / Evolução</div>', unsafe_allow_html=True)
        img_up = st.file_uploader("Anexar imagem (JPG ou PNG)", type=["jpg","jpeg","png"], key=f"{prefixo}_img")

        lbl = "💾 Salvar Alterações" if prefixo != "novo" else "✓ Registrar Avaliação"
        submitted = st.form_submit_button(lbl, use_container_width=True, type="primary")

    if submitted:
        if not paciente or not leito:
            st.error("Preencha o nome do paciente e o leito.")
            return None

        pb64  = d.get("prontuario_b64","")
        pnome = d.get("prontuario_nome","")
        if img_up:
            pb64  = base64.b64encode(img_up.read()).decode()
            pnome = img_up.name

        dados = dict(
            paciente=paciente, leito=leito, data=str(data_av),
            setor=setor, avaliador=st.session_state.usuario_nome,
            dias_cateter=dias_cateter, dias_ventilacao=dias_ventilacao,
            medicacao=medicacao, temperatura=temperatura,
            observacao_tipo=obs_tipo, observacao_livre=obs_livre,
            prontuario_b64=pb64, prontuario_nome=pnome,
        )
        dados.update(valores)
        score = calcular_score(dados)
        risco, _ = classificar_risco(score)
        dados.update(score=score, risco=risco)
        return dados
    return None

# ══════════════════════════════════════════════════════════════
# NAV BAR
# ══════════════════════════════════════════════════════════════
avs_all = carregar_avaliacoes()

st.markdown(f"""
<div class="viginfec-nav">
    <div class="nav-brand">🏥 <span>Vig</span>Infec</div>
    <div class="nav-user">
        <span class="nav-badge">{st.session_state.usuario_setor}</span>
        <span>👤 {st.session_state.usuario_nome}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Botão logout fora da nav (streamlit limitation)
col_logout = st.columns([6,1])[1]
with col_logout:
    if st.button("Sair", key="logout_btn"):
        fazer_logout(); st.rerun()

# ══════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(["📝  Nova Avaliação", "📊  Dashboard", "📂  Histórico"])

# ─────────────────────────────────────────────────────────────
# TAB 1 — NOVA AVALIAÇÃO
# ─────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    resultado = renderizar_formulario("novo")
    if resultado:
        salvar_avaliacao(resultado)
        rl, rc, emoji, cor = risco_info(resultado["risco"])
        st.markdown(f"""
        <div class="alert alert-{rc}">
            <div class="alert-icon">{emoji}</div>
            <div>
                <div class="alert-title" style="color:{cor}">Risco {rl} — Score {resultado['score']} pontos</div>
                <div class="alert-sub">{resultado['paciente']} · {resultado['leito']} · {resultado['setor']} · {resultado['avaliador']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.success("✅ Avaliação registrada com sucesso!")
        pdf_b = gerar_pdf(resultado)
        st.download_button(
            "⬇️ Baixar Relatório PDF", data=bytes(pdf_b),
            file_name=f"avaliacao_{resultado['paciente'].replace(' ','_')}_{resultado['data']}.pdf",
            mime="application/pdf", use_container_width=True,
        )

# ─────────────────────────────────────────────────────────────
# TAB 2 — DASHBOARD
# ─────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    if not avs_all:
        st.markdown('<div class="empty-state"><div class="empty-icon">📊</div><div class="empty-text">Nenhuma avaliação registrada ainda.</div></div>', unsafe_allow_html=True)
    else:
        df = pd.DataFrame(avs_all)
        df["risco_d"] = df["risco"].apply(lambda r: "Médio" if "med" in str(r).lower() else str(r))

        total  = len(df)
        n_alto = int(df["risco"].str.lower().str.contains("alto",na=False).sum())
        n_med  = int(df["risco"].str.lower().str.contains("med",na=False).sum())
        n_bai  = int(df["risco"].str.lower().str.contains("baixo",na=False).sum())
        pct    = f"{n_alto/total*100:.0f}%" if total else "0%"

        st.markdown(f"""
        <div class="metric-grid">
            <div class="metric-card metric-total">
                <div class="metric-num">{total}</div>
                <div class="metric-lbl">Total</div>
            </div>
            <div class="metric-card metric-alto">
                <div class="metric-num">{n_alto}</div>
                <div class="metric-lbl">Risco Alto · {pct}</div>
            </div>
            <div class="metric-card metric-medio">
                <div class="metric-num">{n_med}</div>
                <div class="metric-lbl">Risco Médio</div>
            </div>
            <div class="metric-card metric-baixo">
                <div class="metric-num">{n_bai}</div>
                <div class="metric-lbl">Risco Baixo</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            cnt = df["risco_d"].value_counts().reset_index()
            cnt.columns = ["Risco","Qtd"]
            fig = px.pie(cnt, names="Risco", values="Qtd",
                         color="Risco", hole=0.55,
                         color_discrete_map={"Alto":"#dc2626","Médio":"#d97706","Baixo":"#059669"})
            fig.update_layout(
                title=dict(text="Distribuição por Risco", font=dict(size=13, family="DM Sans"), x=0),
                margin=dict(t=40,b=10,l=0,r=0),
                legend=dict(font=dict(family="DM Sans",size=11)),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Sans"),
            )
            fig.update_traces(textfont=dict(family="DM Sans"))
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            if "setor" in df.columns:
                cnt_s = df["setor"].value_counts().reset_index()
                cnt_s.columns = ["Setor","Qtd"]
                fig_s = px.bar(cnt_s, x="Qtd", y="Setor", orientation="h",
                               color="Qtd", color_continuous_scale=["#bfdbfe","#1a3a6b"])
                fig_s.update_layout(
                    title=dict(text="Avaliações por Setor", font=dict(size=13,family="DM Sans"),x=0),
                    margin=dict(t=40,b=10,l=0,r=0),
                    coloraxis_showscale=False,
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="DM Sans"),
                    yaxis=dict(tickfont=dict(size=11)),
                )
                st.plotly_chart(fig_s, use_container_width=True)

        # Barras de prevalência
        cols_f   = [c for c in list(LABELS_FATORES.keys()) if c in df.columns]
        labels_f = [LABELS_FATORES[c] for c in cols_f]
        prev     = [int(df[c].sum()) for c in cols_f]
        fig_bar  = go.Figure(go.Bar(
            x=prev, y=labels_f, orientation="h",
            marker=dict(
                color=prev,
                colorscale=[[0,"#d1fae5"],[0.5,"#fef3c7"],[1,"#fee2e2"]],
                showscale=False,
            ),
            text=prev, textposition="outside",
        ))
        fig_bar.update_layout(
            title=dict(text="Prevalência de Fatores de Risco", font=dict(size=13,family="DM Sans"),x=0),
            margin=dict(t=40,b=10,l=0,r=40),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans"),
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(tickfont=dict(size=11)),
            height=max(280, len(cols_f)*32),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# TAB 3 — HISTÓRICO
# ─────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    if not avs_all:
        st.markdown('<div class="empty-state"><div class="empty-icon">📂</div><div class="empty-text">Nenhuma avaliação registrada ainda.</div></div>', unsafe_allow_html=True)
    else:
        # Filtros compactos
        fc1, fc2, fc3 = st.columns([3,1,1])
        with fc1: busca = st.text_input("", placeholder="🔍  Buscar paciente, leito ou avaliador...", label_visibility="collapsed")
        with fc2: f_risco = st.selectbox("", ["Todos","Alto","Médio","Baixo"], label_visibility="collapsed")
        with fc3: f_setor = st.selectbox("", ["Todos"]+SETORES, label_visibility="collapsed")

        filtrados = avs_all
        if busca:
            b = busca.lower()
            filtrados = [a for a in filtrados if b in str(a.get("paciente","")).lower()
                         or b in str(a.get("leito","")).lower() or b in str(a.get("avaliador","")).lower()]
        if f_risco != "Todos":
            filtrados = [a for a in filtrados if
                (f_risco=="Médio" and "med" in str(a.get("risco","")).lower()) or
                (f_risco!="Médio" and f_risco.lower() in str(a.get("risco","")).lower())]
        if f_setor != "Todos":
            filtrados = [a for a in filtrados if a.get("setor","") == f_setor]

        st.caption(f"{len(filtrados)} registro{'s' if len(filtrados)!=1 else ''}")
        st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

        for av in filtrados:
            av_id   = av.get("id",0)
            rl, rc, emoji_r, cor_r = risco_info(av.get("risco","Baixo"))
            score   = av.get("score","-")
            fat_av  = FATORES_POR_SETOR.get(av.get("setor","UTI Geral"), list(LABELS_FATORES.keys()))
            ativos  = [c for c in fat_av if av.get(c)]

            # Card do histórico
            chips_html = "".join([
                f'<span class="chip chip-active">{ICONS_FATORES.get(c,"")} {LABELS_FATORES.get(c,c)}</span>'
                for c in ativos
            ])
            if not chips_html:
                chips_html = '<span class="chip">Nenhum fator ativo</span>'

            st.markdown(f"""
            <div class="hcard hcard-{rc}">
                <div class="hcard-top">
                    <div>
                        <div class="hcard-name">{av.get('paciente','-')} · {av.get('leito','-')}</div>
                        <div class="hcard-meta">📅 {av.get('data','-')} &nbsp;·&nbsp; 🏥 {av.get('setor','-')} &nbsp;·&nbsp; 👤 {av.get('avaliador','-')}</div>
                    </div>
                    <div>
                        <span class="hcard-badge badge-{rc}">{emoji_r} {rl}</span>
                        <div style="text-align:right;font-size:.78rem;color:#64748b;margin-top:4px;font-family:'DM Mono',monospace;">Score {score}</div>
                    </div>
                </div>
                <div class="hcard-chips">{chips_html}</div>
            </div>
            """, unsafe_allow_html=True)

            # Ações expandíveis
            with st.expander("Ver detalhes / Editar"):
                if st.session_state.editando_id == av_id:
                    st.markdown("#### ✏️ Editando avaliação")
                    res_edit = renderizar_formulario(f"edit_{av_id}", dados_iniciais=av)
                    if res_edit:
                        atualizar_avaliacao(av_id, res_edit)
                        st.session_state.editando_id = None
                        st.success("✅ Atualizado!")
                        st.rerun()
                    if st.button("Cancelar", key=f"cancel_{av_id}"):
                        st.session_state.editando_id = None; st.rerun()
                else:
                    # Detalhes
                    if av.get("medicacao"):
                        st.write(f"💊 **Medicação:** {av['medicacao']}")
                    if av.get("febre") and av.get("temperatura"):
                        st.write(f"🌡️ **Temperatura:** {av['temperatura']} °C")
                    if av.get("observacao_tipo"):
                        st.write(f"📌 **Obs:** {av['observacao_tipo']}")
                    if av.get("observacao_livre"):
                        st.caption(av["observacao_livre"])
                    if av.get("prontuario_b64"):
                        try:
                            img_b = base64.b64decode(av["prontuario_b64"])
                            st.image(img_b, caption=av.get("prontuario_nome","Anexo"), use_column_width=True)
                        except: st.warning("Não foi possível exibir o anexo.")

                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        pdf_b = gerar_pdf(av)
                        st.download_button(
                            "⬇️ PDF", data=bytes(pdf_b),
                            file_name=f"rel_{str(av.get('paciente','')).replace(' ','_')}_{av.get('data','')}.pdf",
                            mime="application/pdf", key=f"pdf_{av_id}",
                        )
                    with col_b:
                        if st.button("✏️ Editar", key=f"edit_{av_id}"):
                            st.session_state.editando_id = av_id; st.rerun()
                    with col_c:
                        if st.button("🗑️ Excluir", key=f"del_{av_id}"):
                            deletar_avaliacao(av_id); st.rerun()