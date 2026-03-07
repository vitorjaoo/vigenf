"""
VigInfec — Sistema de Vigilância de Infecção Hospitalar
=======================================================
pip install streamlit fpdf2 pandas plotly supabase
streamlit run app.py
"""

# ============================================================
USE_SUPABASE = True
SUPABASE_URL = "https://juzyjqauwujtcsxgsogh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp1enlqcWF1d3VqdGNzeGdzb2doIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3MzE1MjUsImV4cCI6MjA4ODMwNzUyNX0.r90v3aN_lf0Hrf7uyFll4ZQh29WGz8PQKNegBH8p1NY"
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
from fpdf import FPDF
import base64
import io

if USE_SUPABASE:
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── Página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="VigInfec",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .risco-alto  { background:#fee2e2; border-left:5px solid #dc2626; padding:14px 18px; border-radius:8px; margin:8px 0; }
    .risco-medio { background:#fef9c3; border-left:5px solid #ca8a04; padding:14px 18px; border-radius:8px; margin:8px 0; }
    .risco-baixo { background:#dcfce7; border-left:5px solid #16a34a; padding:14px 18px; border-radius:8px; margin:8px 0; }
    .titulo-secao { color:#1e3a5f; font-weight:700; font-size:1.05rem; margin-top:10px; margin-bottom:4px; }
    div[data-testid="stForm"] { background:#f8fafc; padding:18px; border-radius:10px; border:1px solid #e2e8f0; }
    .badge-setor { background:#1e3a5f; color:white; padding:3px 12px; border-radius:99px; font-size:.8rem; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ── Setores e parâmetros por setor ───────────────────────────
SETORES = [
    "UTI Geral",
    "UTI 1",
    "UTI 2",
    "UTI AVC",
    "Area Laranja",
    "Area Vermelha",
    "Internacao A",
    "Internacao B",
    "Internacao C",
]

# Fatores de risco por setor (pesos podem ser ajustados)
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
    "cateter":          "💉 Cateter Venoso Central (CVC)",
    "ventilacao":       "🫁 Ventilação Mecânica Invasiva",
    "cirurgia_recente": "🩹 Cirurgia nos últimos 30 dias",
    "imunossuprimido":  "🛡️ Imunossupressão / Corticoide",
    "antibiotico":      "💊 Em uso de Antibiótico",
    "febre":            "🌡️ Febre (T° > 38°C)",
    "secrecao":         "🔬 Secreção purulenta / Anormal",
    "sedacao":          "💤 Sedação contínua",
    "nutricao_enteral": "🥤 Nutrição Enteral",
    "disfagia":         "🗣️ Disfagia",
    "sonda_vesical":    "🔵 Sonda Vesical de Demora",
    "dreno":            "🩸 Dreno cirúrgico",
}

PESOS = {
    "cateter": 4, "ventilacao": 4, "cirurgia_recente": 3,
    "imunossuprimido": 3, "antibiotico": 2, "febre": 2,
    "secrecao": 2, "sedacao": 2, "nutricao_enteral": 1,
    "disfagia": 1, "sonda_vesical": 2, "dreno": 2,
    "dias_cateter_bonus": 0.3,
    "dias_ventilacao_bonus": 0.4,
}

OPCOES_OBSERVACAO = [
    "Sem intercorrencias",
    "Sinais de infeccao no sitio",
    "Febre persistente em investigacao",
    "Paciente imunossuprimido em observacao",
    "Aguardando resultado de cultura",
    "Em uso de antibiotico de amplo espectro",
    "Dispositivo com sinais de flebite",
    "Outro (ver observacao livre abaixo)",
]

# ── Session State ────────────────────────────────────────────
defaults = {
    "logado": False, "usuario_email": "", "usuario_nome": "",
    "usuario_setor": "", "avaliacoes": [], "contador": 1,
    "editando_id": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Mock data
MOCK_INICIAL = [
    {"id":1,"paciente":"Maria S.","leito":"UTI-01","data":"2025-06-10","score":18,"risco":"Alto",
     "setor":"UTI Geral","cateter":True,"ventilacao":True,"cirurgia_recente":True,"imunossuprimido":False,
     "antibiotico":True,"febre":True,"secrecao":True,"sedacao":True,"nutricao_enteral":False,
     "disfagia":False,"sonda_vesical":False,"dreno":False,
     "dias_cateter":8,"dias_ventilacao":5,"medicacao":"Vancomicina 1g EV 12/12h",
     "temperatura":"38.9","avaliador":"Enf. Demo",
     "observacao_tipo":"Sinais de infeccao no sitio","observacao_livre":"Curativo com secrecao purulenta",
     "prontuario_nome":"","prontuario_b64":""},
]
if not st.session_state.avaliacoes:
    st.session_state.avaliacoes = MOCK_INICIAL.copy()
    st.session_state.contador = 2

# ══════════════════════════════════════════════════════════════
# AUTENTICAÇÃO
# ══════════════════════════════════════════════════════════════
def fazer_login(email, senha):
    if USE_SUPABASE:
        try:
            res = supabase.auth.sign_in_with_password({"email": email, "password": senha})
            meta = res.user.user_metadata or {}
            nome  = meta.get("nome",  email.split("@")[0].title())
            setor = meta.get("setor", SETORES[0])
            return True, nome, setor
        except Exception as e:
            return False, str(e), ""
    else:
        if email and senha:
            return True, email.split("@")[0].title(), SETORES[0]
        return False, "Preencha email e senha.", ""

def fazer_logout():
    if USE_SUPABASE:
        try: supabase.auth.sign_out()
        except: pass
    for k in ["logado","usuario_email","usuario_nome","usuario_setor"]:
        st.session_state[k] = False if k == "logado" else ""

# ── Tela de Login ─────────────────────────────────────────────
if not st.session_state.logado:
    _, col_m, _ = st.columns([1, 1.2, 1])
    with col_m:
        st.markdown("## 🏥 VigInfec")
        st.markdown("**Sistema de Vigilância de Infecção Hospitalar**")
        st.divider()
        with st.form("form_login"):
            st.markdown("### Entrar no sistema")
            email = st.text_input("📧 E-mail", placeholder="seu@email.com")
            senha = st.text_input("🔒 Senha", type="password", placeholder="••••••••")
            entrar = st.form_submit_button("Entrar", use_container_width=True, type="primary")

        if entrar:
            if not email or not senha:
                st.error("Preencha e-mail e senha.")
            else:
                ok, resultado, setor = fazer_login(email, senha)
                if ok:
                    st.session_state.logado       = True
                    st.session_state.usuario_email = email
                    st.session_state.usuario_nome  = resultado
                    st.session_state.usuario_setor = setor
                    st.rerun()
                else:
                    st.error(f"Login inválido: {resultado}")
        if not USE_SUPABASE:
            st.info("🧪 Modo simulação: qualquer e-mail e senha funcionam.")
    st.stop()

# ══════════════════════════════════════════════════════════════
# FUNÇÕES DE DADOS
# ══════════════════════════════════════════════════════════════
def salvar_avaliacao(dados: dict):
    if USE_SUPABASE:
        payload = {k: v for k, v in dados.items() if k != "id"}
        supabase.table("avaliacoes").insert(payload).execute()
    else:
        dados["id"] = st.session_state.contador
        st.session_state.contador += 1
        st.session_state.avaliacoes.append(dados)

def atualizar_avaliacao(av_id, dados: dict):
    if USE_SUPABASE:
        payload = {k: v for k, v in dados.items() if k != "id"}
        supabase.table("avaliacoes").update(payload).eq("id", av_id).execute()
    else:
        for i, a in enumerate(st.session_state.avaliacoes):
            if a["id"] == av_id:
                dados["id"] = av_id
                st.session_state.avaliacoes[i] = dados
                break

def carregar_avaliacoes() -> list:
    if USE_SUPABASE:
        res = supabase.table("avaliacoes").select("*").order("data", desc=True).execute()
        return res.data
    else:
        return list(reversed(st.session_state.avaliacoes))

def deletar_avaliacao(av_id):
    if USE_SUPABASE:
        supabase.table("avaliacoes").delete().eq("id", av_id).execute()
    else:
        st.session_state.avaliacoes = [a for a in st.session_state.avaliacoes if a["id"] != av_id]

# ══════════════════════════════════════════════════════════════
# LÓGICA DE SCORE
# ══════════════════════════════════════════════════════════════
def calcular_score(dados: dict) -> int:
    s = 0
    for campo in PESOS:
        if campo.endswith("_bonus"): continue
        if dados.get(campo): s += PESOS[campo]
    if dados.get("cateter") and dados.get("dias_cateter", 0) > 3:
        s += int((dados["dias_cateter"] - 3) * PESOS["dias_cateter_bonus"])
    if dados.get("ventilacao") and dados.get("dias_ventilacao", 0) > 2:
        s += int((dados["dias_ventilacao"] - 2) * PESOS["dias_ventilacao_bonus"])
    return s

def classificar_risco(score: int) -> tuple:
    if score >= 14: return "Alto",  "risco-alto"
    if score >= 7:  return "Medio", "risco-medio"
    return "Baixo", "risco-baixo"

# ══════════════════════════════════════════════════════════════
# PDF
# ══════════════════════════════════════════════════════════════
def limpar_pdf(texto) -> str:
    if not texto:
        return "-"
    texto = str(texto)
    mapa = {
        "\u2014":"-","\u2013":"-","\u2022":"*","\u2192":"->",
        "\u00e9":"e","\u00ea":"e","\u00e8":"e","\u00eb":"e",
        "\u00e1":"a","\u00e0":"a","\u00e3":"a","\u00e2":"a","\u00e4":"a",
        "\u00ed":"i","\u00ee":"i","\u00ec":"i","\u00ef":"i",
        "\u00f3":"o","\u00f4":"o","\u00f5":"o","\u00f2":"o","\u00f6":"o",
        "\u00fa":"u","\u00fb":"u","\u00f9":"u","\u00fc":"u",
        "\u00e7":"c","\u00f1":"n",
        "\u00c9":"E","\u00ca":"E","\u00c1":"A","\u00c3":"A","\u00c2":"A",
        "\u00cd":"I","\u00d3":"O","\u00d4":"O","\u00d5":"O",
        "\u00da":"U","\u00db":"U","\u00c7":"C","\u00b0":" graus",
    }
    for orig, sub in mapa.items():
        texto = texto.replace(orig, sub)
    return ''.join(c for c in texto if ord(c) < 128)

def gerar_pdf(dados: dict) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)

    # Cabeçalho
    pdf.set_fill_color(30, 58, 95)
    pdf.rect(0, 0, 210, 30, "F")
    pdf.set_font("Helvetica", "B", 15)
    pdf.set_text_color(255, 255, 255)
    pdf.set_y(7)
    pdf.cell(0, 10, "SISTEMA DE VIGILANCIA DE INFECCAO HOSPITALAR", align="C", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "Relatorio de Avaliacao de Risco - VigInfec", align="C", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(36)

    # Identificação
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(226, 232, 240)
    pdf.cell(0, 8, "  IDENTIFICACAO", ln=True, fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(2)

    risco = dados.get("risco","Baixo")
    for label, valor in [
        ("Paciente",      limpar_pdf(dados.get("paciente","-"))),
        ("Leito/Unidade", limpar_pdf(dados.get("leito","-"))),
        ("Setor",         limpar_pdf(dados.get("setor","-"))),
        ("Data",          str(dados.get("data", date.today()))),
        ("Avaliador",     limpar_pdf(dados.get("avaliador","-"))),
        ("Score",         str(dados.get("score","-"))),
        ("Classificacao", limpar_pdf(risco)),
    ]:
        pdf.set_font("Helvetica","B",10)
        pdf.cell(50, 7, f"  {label}:", border=0)
        pdf.set_font("Helvetica","",10)
        if label == "Classificacao":
            cor = (220,38,38) if "alto" in risco.lower() else (202,138,4) if "med" in risco.lower() else (22,163,74)
            pdf.set_text_color(*cor)
            pdf.set_font("Helvetica","B",10)
        pdf.cell(0, 7, valor, ln=True)
        pdf.set_text_color(0,0,0)
    pdf.ln(4)

    # Fatores de risco
    pdf.set_font("Helvetica","B",11)
    pdf.set_fill_color(226,232,240)
    pdf.cell(0, 8, "  FATORES DE RISCO AVALIADOS", ln=True, fill=True)
    pdf.set_font("Helvetica","",10)
    pdf.ln(2)

    setor = dados.get("setor", "UTI Geral")
    fatores_setor = FATORES_POR_SETOR.get(setor, list(LABELS_FATORES.keys()))
    for campo in fatores_setor:
        presente = dados.get(campo, False)
        cor = (220,38,38) if presente else (100,116,139)
        pdf.set_text_color(*cor)
        label_f = limpar_pdf(LABELS_FATORES.get(campo, campo))
        status  = "[SIM]" if presente else "[NAO]"
        linha   = f"   {status}  {label_f}"
        if campo == "cateter" and presente and dados.get("dias_cateter",0) > 0:
            linha += f"  (D{dados['dias_cateter']})"
        if campo == "ventilacao" and presente and dados.get("dias_ventilacao",0) > 0:
            linha += f"  (D{dados['dias_ventilacao']})"
        pdf.cell(0, 6, linha, ln=True)

    pdf.set_text_color(0,0,0)

    # Medicação
    med = limpar_pdf(dados.get("medicacao",""))
    if med and med != "-":
        pdf.ln(2)
        pdf.set_font("Helvetica","B",10)
        pdf.cell(50, 7, "  Medicacao em uso:", border=0)
        pdf.set_font("Helvetica","",10)
        pdf.multi_cell(0, 7, med)

    # Temperatura
    temp = limpar_pdf(dados.get("temperatura",""))
    if temp and temp != "-" and dados.get("febre"):
        pdf.set_font("Helvetica","B",10)
        pdf.cell(50, 7, "  Temperatura registrada:", border=0)
        pdf.set_font("Helvetica","",10)
        pdf.cell(0, 7, f"{temp} graus C", ln=True)

    pdf.ln(4)

    # Observação
    obs_tipo  = limpar_pdf(dados.get("observacao_tipo",""))
    obs_livre = limpar_pdf(dados.get("observacao_livre",""))
    if (obs_tipo and obs_tipo != "-") or (obs_livre and obs_livre != "-"):
        pdf.set_font("Helvetica","B",11)
        pdf.set_fill_color(226,232,240)
        pdf.cell(0, 8, "  OBSERVACOES DO AVALIADOR", ln=True, fill=True)
        pdf.set_font("Helvetica","",10)
        pdf.ln(2)
        if obs_tipo and obs_tipo != "-":
            pdf.set_font("Helvetica","B",10)
            pdf.cell(50, 7, "  Situacao:", border=0)
            pdf.set_font("Helvetica","",10)
            pdf.multi_cell(0, 7, obs_tipo)
        if obs_livre and obs_livre != "-":
            pdf.ln(1)
            pdf.set_font("Helvetica","B",10)
            pdf.cell(0, 7, "  Descricao livre:", ln=True)
            pdf.set_font("Helvetica","",10)
            pdf.set_fill_color(248,250,252)
            pdf.multi_cell(0, 6, f"  {obs_livre}", fill=True)
        pdf.ln(4)

    # Imagem do prontuário
    img_b64 = dados.get("prontuario_b64","")
    if img_b64:
        try:
            pdf.set_font("Helvetica","B",11)
            pdf.set_fill_color(226,232,240)
            pdf.cell(0, 8, "  ANEXO — PRONTUARIO / EVOLUCAO", ln=True, fill=True)
            pdf.ln(2)
            img_bytes = base64.b64decode(img_b64)
            img_buf   = io.BytesIO(img_bytes)
            nome_arq  = dados.get("prontuario_nome","anexo.jpg")
            ext       = nome_arq.split(".")[-1].lower()
            ext_map   = {"jpg":"JPEG","jpeg":"JPEG","png":"PNG"}
            tipo      = ext_map.get(ext,"JPEG")
            pdf.image(img_buf, x=20, w=170, type=tipo)
        except:
            pass

    # Rodapé
    pdf.set_y(-28)
    pdf.set_draw_color(30,58,95)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(2)
    pdf.set_font("Helvetica","I",8)
    pdf.set_text_color(100,116,139)
    pdf.cell(0, 5, f"Gerado em {datetime.now().strftime('%d/%m/%Y as %H:%M')}  |  Avaliador: {limpar_pdf(dados.get('avaliador','-'))}  |  Setor: {limpar_pdf(dados.get('setor','-'))}  |  VigInfec", align="C", ln=True)
    pdf.cell(0, 5, "Instrumento de apoio clinico. Decisoes devem ser validadas por profissional habilitado.", align="C")

    return pdf.output()

# ══════════════════════════════════════════════════════════════
# FORMULÁRIO REUTILIZÁVEL (nova avaliação e edição)
# ══════════════════════════════════════════════════════════════
def renderizar_formulario(prefixo: str, dados_iniciais: dict = None):
    """Renderiza o formulário de avaliação. Retorna os dados preenchidos ou None."""
    d = dados_iniciais or {}
    setor_usuario = st.session_state.usuario_setor or SETORES[0]

    with st.form(f"form_{prefixo}", clear_on_submit=(prefixo=="novo")):

        # Identificação
        st.markdown('<p class="titulo-secao">👤 Identificação do Paciente</p>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([2, 1.5, 1.5])
        with c1:
            paciente = st.text_input("Nome do Paciente *", value=d.get("paciente",""))
        with c2:
            leito = st.text_input("Leito *", value=d.get("leito",""))
        with c3:
            data_val = d.get("data", str(date.today()))
            try:
                data_val = date.fromisoformat(str(data_val))
            except:
                data_val = date.today()
            data_av = st.date_input("Data", value=data_val)

        # Setor (bloqueado ao setor do usuário logado)
        st.markdown('<p class="titulo-secao">🏥 Setor</p>', unsafe_allow_html=True)
        st.info(f"Setor definido pelo seu cadastro: **{setor_usuario}**")
        setor = setor_usuario

        st.divider()

        # Fatores de risco do setor
        st.markdown(f'<p class="titulo-secao">⚠️ Fatores de Risco — {setor}</p>', unsafe_allow_html=True)
        fatores_disponiveis = FATORES_POR_SETOR.get(setor, list(LABELS_FATORES.keys()))

        valores_fatores = {}
        col_esq, col_dir = st.columns(2)
        metade = len(fatores_disponiveis) // 2
        for i, campo in enumerate(fatores_disponiveis):
            col = col_esq if i < metade else col_dir
            with col:
                valores_fatores[campo] = st.checkbox(
                    LABELS_FATORES.get(campo, campo),
                    value=bool(d.get(campo, False)),
                    key=f"{prefixo}_{campo}"
                )

        # Dias de uso condicionais
        dias_cateter = dias_ventilacao = 0
        if valores_fatores.get("cateter") or valores_fatores.get("ventilacao"):
            st.markdown('<p class="titulo-secao">📅 Tempo de Uso do Dispositivo</p>', unsafe_allow_html=True)
            dc1, dc2 = st.columns(2)
            with dc1:
                if valores_fatores.get("cateter"):
                    dias_cateter = st.number_input("Dias com CVC", min_value=0, max_value=365,
                                                    value=int(d.get("dias_cateter",0)), key=f"{prefixo}_dc")
            with dc2:
                if valores_fatores.get("ventilacao"):
                    dias_ventilacao = st.number_input("Dias de VM", min_value=0, max_value=365,
                                                       value=int(d.get("dias_ventilacao",0)), key=f"{prefixo}_dv")

        # Medicação (aparece se antibiótico marcado)
        medicacao = ""
        if valores_fatores.get("antibiotico"):
            st.markdown('<p class="titulo-secao">💊 Medicação em Uso</p>', unsafe_allow_html=True)
            medicacao = st.text_input(
                "Descreva a(s) medicação(ões) — ex: Vancomicina 1g EV 12/12h",
                value=d.get("medicacao",""),
                key=f"{prefixo}_med"
            )

        # Temperatura (aparece se febre marcada)
        temperatura = ""
        if valores_fatores.get("febre"):
            st.markdown('<p class="titulo-secao">🌡️ Temperatura Registrada</p>', unsafe_allow_html=True)
            temperatura = st.text_input(
                "Temperatura em °C — ex: 38.9",
                value=d.get("temperatura",""),
                placeholder="38.5",
                key=f"{prefixo}_temp"
            )

        st.divider()

        # Observação
        st.markdown('<p class="titulo-secao">📝 Observação do Avaliador</p>', unsafe_allow_html=True)
        obs_tipo = st.selectbox(
            "Situação atual",
            options=OPCOES_OBSERVACAO,
            index=OPCOES_OBSERVACAO.index(d.get("observacao_tipo", OPCOES_OBSERVACAO[0]))
                  if d.get("observacao_tipo") in OPCOES_OBSERVACAO else 0,
            key=f"{prefixo}_obs_tipo"
        )
        obs_livre = st.text_area(
            "Descrição livre (aparece no PDF)",
            value=d.get("observacao_livre",""),
            height=90,
            key=f"{prefixo}_obs_livre"
        )

        st.divider()

        # Upload de prontuário
        st.markdown('<p class="titulo-secao">📎 Anexar Prontuário / Evolução (JPG ou PNG)</p>', unsafe_allow_html=True)
        img_upload = st.file_uploader(
            "Selecione uma imagem (opcional)",
            type=["jpg","jpeg","png"],
            key=f"{prefixo}_upload"
        )

        label_btn = "💾 Salvar Alterações" if prefixo != "novo" else "🔍 Calcular Risco e Salvar"
        submitted = st.form_submit_button(label_btn, use_container_width=True, type="primary")

    if submitted:
        if not paciente or not leito:
            st.error("❌ Preencha o nome do paciente e o leito.")
            return None

        # Imagem
        prontuario_b64   = d.get("prontuario_b64","")
        prontuario_nome  = d.get("prontuario_nome","")
        if img_upload:
            prontuario_b64  = base64.b64encode(img_upload.read()).decode("utf-8")
            prontuario_nome = img_upload.name

        dados = dict(
            paciente=paciente, leito=leito, data=str(data_av),
            setor=setor, avaliador=st.session_state.usuario_nome,
            dias_cateter=dias_cateter, dias_ventilacao=dias_ventilacao,
            medicacao=medicacao, temperatura=temperatura,
            observacao_tipo=obs_tipo, observacao_livre=obs_livre,
            prontuario_b64=prontuario_b64, prontuario_nome=prontuario_nome,
        )
        dados.update(valores_fatores)

        score = calcular_score(dados)
        risco, css_class = classificar_risco(score)
        dados.update(score=score, risco=risco)
        return dados, css_class

    return None

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🏥 VigInfec")
    st.markdown(f"👤 **{st.session_state.usuario_nome}**")
    st.caption(st.session_state.usuario_email)
    setor_atual = st.session_state.usuario_setor
    st.markdown(f'<span class="badge-setor">🏥 {setor_atual}</span>', unsafe_allow_html=True)
    st.divider()

    avs = carregar_avaliacoes()
    st.metric("📋 Avaliações", len(avs))
    st.metric("🔴 Risco Alto",  sum(1 for a in avs if "alto"  in str(a.get("risco","")).lower()))
    st.metric("🟡 Risco Médio", sum(1 for a in avs if "med"   in str(a.get("risco","")).lower()))
    st.metric("🟢 Risco Baixo", sum(1 for a in avs if "baixo" in str(a.get("risco","")).lower()))
    st.divider()

    if not USE_SUPABASE:
        st.warning("🧪 Modo simulação")
    if st.button("🚪 Sair", use_container_width=True):
        fazer_logout()
        st.rerun()

# ══════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(["📝  Nova Avaliação", "📊  Dashboard", "📂  Histórico"])

# ── TAB 1 — NOVA AVALIAÇÃO ────────────────────────────────────
with tab1:
    st.subheader("📝 Nova Avaliação de Risco Infeccioso")
    resultado = renderizar_formulario("novo")
    if resultado:
        dados, css_class = resultado
        salvar_avaliacao(dados)
        st.success("✅ Avaliação registrada com sucesso!")
        emoji_r = "🔴" if "alto" in dados["risco"].lower() else "🟡" if "med" in dados["risco"].lower() else "🟢"
        risco_d  = "Médio" if "med" in dados["risco"].lower() else dados["risco"]
        st.markdown(f"""
        <div class="{css_class}">
            <h3>{emoji_r} Risco {risco_d} — Score: {dados['score']} pontos</h3>
            <p><strong>Paciente:</strong> {dados['paciente']} &nbsp;|&nbsp;
               <strong>Leito:</strong> {dados['leito']} &nbsp;|&nbsp;
               <strong>Setor:</strong> {dados['setor']} &nbsp;|&nbsp;
               <strong>Avaliador:</strong> {dados['avaliador']}</p>
        </div>
        """, unsafe_allow_html=True)
        pdf_bytes = gerar_pdf(dados)
        st.download_button(
            "⬇️ Baixar Relatório PDF", data=bytes(pdf_bytes),
            file_name=f"avaliacao_{dados['paciente'].replace(' ','_')}_{dados['data']}.pdf",
            mime="application/pdf", use_container_width=True,
        )

# ── TAB 2 — DASHBOARD ────────────────────────────────────────
with tab2:
    st.subheader("📊 Dashboard de Vigilância")
    avaliacoes = carregar_avaliacoes()

    if not avaliacoes:
        st.info("Nenhuma avaliação registrada ainda.")
    else:
        df = pd.DataFrame(avaliacoes)
        df["risco_display"] = df["risco"].apply(
            lambda r: "Médio" if "med" in str(r).lower() else str(r))

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("📋 Total", len(df))
        m2.metric("🔴 Alto",  int(df["risco"].str.lower().str.contains("alto",na=False).sum()),
                  delta=f"{df['risco'].str.lower().str.contains('alto',na=False).mean()*100:.0f}%",
                  delta_color="inverse")
        m3.metric("🟡 Médio", int(df["risco"].str.lower().str.contains("med",na=False).sum()))
        m4.metric("🟢 Baixo", int(df["risco"].str.lower().str.contains("baixo",na=False).sum()))

        st.divider()
        col1, col2 = st.columns(2)
        cores = {"Alto":"#dc2626","Médio":"#ca8a04","Baixo":"#16a34a"}

        with col1:
            cnt = df["risco_display"].value_counts().reset_index()
            cnt.columns = ["Risco","Qtd"]
            fig = px.pie(cnt, names="Risco", values="Qtd", title="Distribuição por Risco",
                         color="Risco", color_discrete_map=cores, hole=0.4)
            fig.update_layout(margin=dict(t=40,b=0,l=0,r=0))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            if "setor" in df.columns:
                cnt_s = df["setor"].value_counts().reset_index()
                cnt_s.columns = ["Setor","Qtd"]
                fig_s = px.bar(cnt_s, x="Setor", y="Qtd", title="Avaliações por Setor",
                               color="Qtd", color_continuous_scale=["#93c5fd","#1e3a5f"])
                fig_s.update_layout(margin=dict(t=40,b=0), coloraxis_showscale=False)
                st.plotly_chart(fig_s, use_container_width=True)

        cols_f   = [c for c in ["cateter","ventilacao","cirurgia_recente","imunossuprimido",
                                  "antibiotico","febre","secrecao","sedacao","sonda_vesical","dreno"] if c in df.columns]
        labels_f = [LABELS_FATORES.get(c,c).split(" ",1)[-1] for c in cols_f]
        prev     = [int(df[c].sum()) for c in cols_f]
        fig_bar = px.bar(x=labels_f, y=prev, title="Prevalência de Fatores de Risco",
                         labels={"x":"Fator","y":"Pacientes"}, color=prev,
                         color_continuous_scale=["#16a34a","#ca8a04","#dc2626"])
        fig_bar.update_layout(margin=dict(t=40,b=0), coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)

# ── TAB 3 — HISTÓRICO ────────────────────────────────────────
with tab3:
    st.subheader("📂 Histórico de Avaliações")
    avaliacoes = carregar_avaliacoes()

    if not avaliacoes:
        st.info("Nenhuma avaliação registrada ainda.")
    else:
        fc1, fc2, fc3 = st.columns([2, 1, 1])
        with fc1:
            busca = st.text_input("🔍 Buscar", placeholder="Nome, leito ou avaliador...")
        with fc2:
            filtro_risco  = st.selectbox("Risco", ["Todos","Alto","Médio","Baixo"])
        with fc3:
            filtro_setor  = st.selectbox("Setor", ["Todos"] + SETORES)

        filtrados = avaliacoes
        if busca:
            b = busca.lower()
            filtrados = [a for a in filtrados if
                b in str(a.get("paciente","")).lower() or
                b in str(a.get("leito","")).lower() or
                b in str(a.get("avaliador","")).lower()]
        if filtro_risco != "Todos":
            filtrados = [a for a in filtrados if
                (filtro_risco=="Médio" and "med" in str(a.get("risco","")).lower()) or
                (filtro_risco!="Médio" and filtro_risco.lower() in str(a.get("risco","")).lower())]
        if filtro_setor != "Todos":
            filtrados = [a for a in filtrados if a.get("setor","") == filtro_setor]

        st.caption(f"Exibindo {len(filtrados)} de {len(avaliacoes)} avaliações")

        for av in filtrados:
            risco    = str(av.get("risco","Baixo"))
            risco_d  = "Médio" if "med" in risco.lower() else risco
            emoji    = "🔴" if "alto" in risco.lower() else "🟡" if "med" in risco.lower() else "🟢"
            av_id    = av.get("id", 0)
            titulo   = f"{emoji} {av.get('paciente','-')} | {av.get('leito','-')} | {av.get('setor','-')} | Score: {av.get('score','-')} | {av.get('data','-')} | 👤 {av.get('avaliador','-')}"

            with st.expander(titulo):
                # Modo edição
                if st.session_state.editando_id == av_id:
                    st.markdown("#### ✏️ Editando avaliação")
                    resultado_edicao = renderizar_formulario(f"edit_{av_id}", dados_iniciais=av)
                    if resultado_edicao:
                        dados_novos, _ = resultado_edicao
                        atualizar_avaliacao(av_id, dados_novos)
                        st.session_state.editando_id = None
                        st.success("✅ Avaliação atualizada!")
                        st.rerun()
                    if st.button("❌ Cancelar edição", key=f"cancel_{av_id}"):
                        st.session_state.editando_id = None
                        st.rerun()
                else:
                    # Visualização
                    ca, cb = st.columns(2)
                    fatores_av = FATORES_POR_SETOR.get(av.get("setor","UTI Geral"), list(LABELS_FATORES.keys()))
                    metade = len(fatores_av) // 2
                    with ca:
                        st.write(f"**Risco:** {risco_d} | **Score:** {av.get('score','-')}")
                        st.write(f"**Setor:** {av.get('setor','-')}")
                        st.write(f"**Avaliador:** {av.get('avaliador','-')}")
                        for campo in fatores_av[:metade]:
                            presente = av.get(campo, False)
                            extra = ""
                            if campo == "cateter" and presente and av.get("dias_cateter",0):
                                extra = f" (D{av['dias_cateter']})"
                            if campo == "ventilacao" and presente and av.get("dias_ventilacao",0):
                                extra = f" (D{av['dias_ventilacao']})"
                            st.write(f"{'✓' if presente else '✗'} {LABELS_FATORES.get(campo,campo)}{extra}")
                    with cb:
                        for campo in fatores_av[metade:]:
                            presente = av.get(campo, False)
                            st.write(f"{'✓' if presente else '✗'} {LABELS_FATORES.get(campo,campo)}")
                        if av.get("medicacao"):
                            st.write(f"**Medicação:** {av['medicacao']}")
                        if av.get("febre") and av.get("temperatura"):
                            st.write(f"**Temperatura:** {av['temperatura']} °C")

                    obs_t = av.get("observacao_tipo","")
                    obs_l = av.get("observacao_livre","")
                    if obs_t or obs_l:
                        st.markdown("**Observação:**")
                        if obs_t: st.write(f"📌 {obs_t}")
                        if obs_l: st.caption(obs_l)

                    # Mostra imagem se houver
                    if av.get("prontuario_b64"):
                        with st.expander("📎 Ver prontuário anexado"):
                            try:
                                img_bytes = base64.b64decode(av["prontuario_b64"])
                                st.image(img_bytes, caption=av.get("prontuario_nome","Anexo"), use_column_width=True)
                            except:
                                st.warning("Não foi possível exibir a imagem.")

                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    with col_btn1:
                        pdf_bytes = gerar_pdf(av)
                        st.download_button(
                            "⬇️ Baixar PDF",
                            data=bytes(pdf_bytes),
                            file_name=f"relatorio_{str(av.get('paciente','')).replace(' ','_')}_{av.get('data','')}.pdf",
                            mime="application/pdf",
                            key=f"pdf_{av_id}_{av.get('data','')}",
                        )
                    with col_btn2:
                        if st.button("✏️ Editar", key=f"edit_btn_{av_id}"):
                            st.session_state.editando_id = av_id
                            st.rerun()
                    with col_btn3:
                        if st.button("🗑️ Excluir", key=f"del_{av_id}"):
                            deletar_avaliacao(av_id)
                            st.warning("Avaliação excluída.")
                            st.rerun()
