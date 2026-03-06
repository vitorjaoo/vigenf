"""
Sistema de Vigilância de Infecção Hospitalar — VigInfec
=======================================================
Dependências: pip install streamlit fpdf2 pandas plotly supabase
Rodar: streamlit run app.py
"""

# ============================================================
# CONFIGURAÇÃO PRINCIPAL
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

if USE_SUPABASE:
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── Página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="VigInfec — Vigilância Hospitalar",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
    .risco-alto  { background:#fee2e2; border-left:5px solid #dc2626; padding:14px 18px; border-radius:8px; margin:8px 0; }
    .risco-medio { background:#fef9c3; border-left:5px solid #ca8a04; padding:14px 18px; border-radius:8px; margin:8px 0; }
    .risco-baixo { background:#dcfce7; border-left:5px solid #16a34a; padding:14px 18px; border-radius:8px; margin:8px 0; }
    .titulo-secao { color:#1e3a5f; font-weight:700; font-size:1.05rem; margin-top:10px; margin-bottom:4px; }
    div[data-testid="stForm"] { background:#f8fafc; padding:18px; border-radius:10px; border:1px solid #e2e8f0; }
</style>
""", unsafe_allow_html=True)

# ── Session State ────────────────────────────────────────────
for key, val in [("logado", False), ("usuario_email", ""), ("usuario_nome", ""),
                 ("avaliacoes", []), ("contador", 1)]:
    if key not in st.session_state:
        st.session_state[key] = val

# ── Dados Mock ───────────────────────────────────────────────
MOCK_INICIAL = [
    {"id":1,"paciente":"Maria S.","leito":"UTI-01","data":"2025-06-10","score":18,"risco":"Alto",
     "cateter":True,"ventilacao":True,"cirurgia_recente":True,"imunossuprimido":False,
     "antibiotico":True,"febre":True,"secrecao":True,"dias_cateter":8,"dias_ventilacao":5,
     "avaliador":"Enf. Demo","observacao_tipo":"Sinais de infeccao no sitio","observacao_livre":"Curativo com secrecao purulenta"},
    {"id":2,"paciente":"Joao P.","leito":"ENF-12","data":"2025-06-11","score":9,"risco":"Medio",
     "cateter":False,"ventilacao":False,"cirurgia_recente":True,"imunossuprimido":True,
     "antibiotico":False,"febre":True,"secrecao":False,"dias_cateter":0,"dias_ventilacao":0,
     "avaliador":"Enf. Demo","observacao_tipo":"Paciente imunossuprimido em observacao","observacao_livre":""},
    {"id":3,"paciente":"Ana L.","leito":"UTI-03","data":"2025-06-12","score":4,"risco":"Baixo",
     "cateter":False,"ventilacao":False,"cirurgia_recente":False,"imunossuprimido":False,
     "antibiotico":False,"febre":False,"secrecao":False,"dias_cateter":0,"dias_ventilacao":0,
     "avaliador":"Enf. Demo","observacao_tipo":"Sem intercorrencias","observacao_livre":""},
]

if not st.session_state.avaliacoes:
    st.session_state.avaliacoes = MOCK_INICIAL.copy()
    st.session_state.contador = 4

# ══════════════════════════════════════════════════════════════
# AUTENTICAÇÃO
# ══════════════════════════════════════════════════════════════
def fazer_login(email: str, senha: str) -> tuple[bool, str]:
    if USE_SUPABASE:
        try:
            res = supabase.auth.sign_in_with_password({"email": email, "password": senha})
            nome = res.user.user_metadata.get("nome", email.split("@")[0].title())
            return True, nome
        except Exception as e:
            return False, str(e)
    else:
        if email and senha:
            return True, email.split("@")[0].title()
        return False, "Preencha email e senha."

def fazer_logout():
    if USE_SUPABASE:
        try:
            supabase.auth.sign_out()
        except:
            pass
    for k in ["logado","usuario_email","usuario_nome"]:
        st.session_state[k] = "" if k != "logado" else False

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
                ok, resultado = fazer_login(email, senha)
                if ok:
                    st.session_state.logado = True
                    st.session_state.usuario_email = email
                    st.session_state.usuario_nome = resultado
                    st.rerun()
                else:
                    st.error(f"Login invalido: {resultado}")

        if not USE_SUPABASE:
            st.info("Modo simulacao: qualquer e-mail e senha funcionam.")
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

def carregar_avaliacoes() -> list:
    if USE_SUPABASE:
        res = supabase.table("avaliacoes").select("*").order("data", desc=True).execute()
        return res.data
    else:
        return list(reversed(st.session_state.avaliacoes))

# ══════════════════════════════════════════════════════════════
# LÓGICA DE SCORE
# ══════════════════════════════════════════════════════════════
PESOS = {
    "cateter": 4, "ventilacao": 4, "cirurgia_recente": 3,
    "imunossuprimido": 3, "antibiotico": 2, "febre": 2, "secrecao": 2,
    "dias_cateter_bonus": 0.3,
    "dias_ventilacao_bonus": 0.4,
}

def calcular_score(dados: dict) -> int:
    s = 0
    for campo in ["cateter","ventilacao","cirurgia_recente","imunossuprimido","antibiotico","febre","secrecao"]:
        if dados.get(campo):
            s += PESOS[campo]
    if dados.get("cateter") and dados.get("dias_cateter", 0) > 3:
        s += int((dados["dias_cateter"] - 3) * PESOS["dias_cateter_bonus"])
    if dados.get("ventilacao") and dados.get("dias_ventilacao", 0) > 2:
        s += int((dados["dias_ventilacao"] - 2) * PESOS["dias_ventilacao_bonus"])
    return s

def classificar_risco(score: int) -> tuple[str, str]:
    if score >= 14: return "Alto", "risco-alto"
    if score >= 7:  return "Medio", "risco-medio"
    return "Baixo", "risco-baixo"

# ══════════════════════════════════════════════════════════════
# GERADOR DE PDF
# ══════════════════════════════════════════════════════════════
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

def limpar_pdf(texto: str) -> str:
    mapa = {
        "\u2014":"-", "\u2013":"-", "\u2022":"*", "\u2192":"->",
        "\u00e9":"e", "\u00ea":"e", "\u00e8":"e", "\u00eb":"e",
        "\u00e1":"a", "\u00e0":"a", "\u00e3":"a", "\u00e2":"a", "\u00e4":"a",
        "\u00ed":"i", "\u00ee":"i", "\u00ec":"i", "\u00ef":"i",
        "\u00f3":"o", "\u00f4":"o", "\u00f5":"o", "\u00f2":"o", "\u00f6":"o",
        "\u00fa":"u", "\u00fb":"u", "\u00f9":"u", "\u00fc":"u",
        "\u00e7":"c", "\u00f1":"n",
        "\u00c9":"E", "\u00ca":"E", "\u00c1":"A", "\u00c3":"A", "\u00c2":"A",
        "\u00cd":"I", "\u00d3":"O", "\u00d4":"O", "\u00d5":"O",
        "\u00da":"U", "\u00db":"U", "\u00c7":"C",
        "\u00b0":" graus",
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

    risco = dados.get("risco", "Baixo")
    campos_id = [
        ("Paciente",       limpar_pdf(dados.get("paciente", "-"))),
        ("Leito/Unidade",  limpar_pdf(dados.get("leito", "-"))),
        ("Data",           dados.get("data", str(date.today()))),
        ("Avaliador",      limpar_pdf(dados.get("avaliador", "-"))),
        ("Score de Risco", str(dados.get("score", "-"))),
        ("Classificacao",  limpar_pdf(risco)),
    ]
    for label, valor in campos_id:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(50, 7, f"  {label}:", border=0)
        pdf.set_font("Helvetica", "", 10)
        if label == "Classificacao":
            cor = (220,38,38) if "alto" in risco.lower() else (202,138,4) if "med" in risco.lower() else (22,163,74)
            pdf.set_text_color(*cor)
            pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, valor, ln=True)
        pdf.set_text_color(0, 0, 0)

    pdf.ln(4)

    # Fatores de Risco
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(226, 232, 240)
    pdf.cell(0, 8, "  FATORES DE RISCO AVALIADOS", ln=True, fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(2)

    fatores = [
        ("Cateter Venoso Central (CVC)", "cateter",          "dias_cateter"),
        ("Ventilacao Mecanica Invasiva",  "ventilacao",       "dias_ventilacao"),
        ("Cirurgia Recente (<30 dias)",   "cirurgia_recente", None),
        ("Imunossupressao / Corticoide",  "imunossuprimido",  None),
        ("Uso de Antibiotico",            "antibiotico",      None),
        ("Febre (>38 graus C)",           "febre",            None),
        ("Secrecao Purulenta / Anormal",  "secrecao",         None),
    ]
    for label, campo, campo_dias in fatores:
        presente = dados.get(campo, False)
        cor = (220, 38, 38) if presente else (100, 116, 139)
        pdf.set_text_color(*cor)
        status = "[SIM]" if presente else "[NAO]"
        linha = f"   {status}  {label}"
        if campo_dias and presente and dados.get(campo_dias, 0) > 0:
            linha += f"  (D{dados[campo_dias]})"
        pdf.cell(0, 6, linha, ln=True)

    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    # Observação
    obs_tipo  = limpar_pdf(dados.get("observacao_tipo", ""))
    obs_livre = limpar_pdf(dados.get("observacao_livre", ""))

    if obs_tipo or obs_livre:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_fill_color(226, 232, 240)
        pdf.cell(0, 8, "  OBSERVACOES DO AVALIADOR", ln=True, fill=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.ln(2)

        if obs_tipo:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(50, 7, "  Situacao:", border=0)
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 7, obs_tipo)

        if obs_livre:
            pdf.ln(1)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 7, "  Descricao livre:", ln=True)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_fill_color(248, 250, 252)
            pdf.multi_cell(0, 6, f"  {obs_livre}", fill=True)

        pdf.ln(4)

    # Rodapé
    pdf.set_y(-28)
    pdf.set_draw_color(30, 58, 95)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 5, f"Gerado em {datetime.now().strftime('%d/%m/%Y as %H:%M')}  |  Avaliador: {limpar_pdf(dados.get('avaliador','-'))}  |  VigInfec", align="C", ln=True)
    pdf.cell(0, 5, "Instrumento de apoio clinico. Decisoes devem ser validadas por profissional habilitado.", align="C")

    return pdf.output()

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🏥 VigInfec")
    st.markdown(f"👤 **{st.session_state.usuario_nome}**")
    st.caption(st.session_state.usuario_email)
    st.divider()

    avaliacoes_side = carregar_avaliacoes()
    total  = len(avaliacoes_side)
    altos  = sum(1 for a in avaliacoes_side if "alto" in a.get("risco","").lower())
    medios = sum(1 for a in avaliacoes_side if "med" in a.get("risco","").lower())
    baixos = sum(1 for a in avaliacoes_side if "baixo" in a.get("risco","").lower())

    st.metric("📋 Avaliações", total)
    st.metric("🔴 Risco Alto",  altos)
    st.metric("🟡 Risco Médio", medios)
    st.metric("🟢 Risco Baixo", baixos)
    st.divider()

    if not USE_SUPABASE:
        st.warning("🧪 Modo simulação ativo")

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

    with st.form("form_avaliacao", clear_on_submit=True):

        st.markdown('<p class="titulo-secao">👤 Identificação do Paciente</p>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([2, 1.5, 1.5])
        with c1:
            paciente = st.text_input("Nome do Paciente *", placeholder="Ex.: Maria da Silva")
        with c2:
            leito = st.text_input("Leito / Unidade *", placeholder="Ex.: UTI-01")
        with c3:
            data_av = st.date_input("Data da Avaliação", value=date.today())

        st.divider()

        st.markdown('<p class="titulo-secao">⚠️ Fatores de Risco — Marque os presentes</p>', unsafe_allow_html=True)
        c4, c5 = st.columns(2)
        with c4:
            cateter     = st.checkbox("💉 Cateter Venoso Central (CVC)")
            ventilacao  = st.checkbox("🫁 Ventilação Mecânica Invasiva")
            cirurgia    = st.checkbox("🩹 Cirurgia nos últimos 30 dias")
            imunossup   = st.checkbox("🛡️ Imunossupressão / Corticoide")
        with c5:
            antibiotico = st.checkbox("💊 Em uso de Antibiótico")
            febre       = st.checkbox("🌡️ Febre (T° > 38°C nas últimas 24h)")
            secrecao    = st.checkbox("🔬 Secreção purulenta / Anormal")

        dias_cateter = dias_ventilacao = 0
        if cateter or ventilacao:
            st.markdown('<p class="titulo-secao">📅 Tempo de Uso do Dispositivo</p>', unsafe_allow_html=True)
            dc1, dc2 = st.columns(2)
            with dc1:
                if cateter:
                    dias_cateter = st.number_input("Dias com CVC", min_value=0, max_value=365, value=0)
            with dc2:
                if ventilacao:
                    dias_ventilacao = st.number_input("Dias de Ventilação Mecânica", min_value=0, max_value=365, value=0)

        st.divider()

        st.markdown('<p class="titulo-secao">📝 Observação do Avaliador</p>', unsafe_allow_html=True)
        obs_tipo = st.selectbox("Situação atual do paciente", options=OPCOES_OBSERVACAO)
        obs_livre = st.text_area(
            "Descrição livre (opcional — aparece no PDF)",
            placeholder="Descreva detalhes relevantes para o relatório...",
            height=100,
        )

        st.divider()
        submitted = st.form_submit_button("🔍 Calcular Risco e Salvar", use_container_width=True, type="primary")

    if submitted:
        if not paciente or not leito:
            st.error("❌ Preencha o nome do paciente e o leito.")
        else:
            dados = dict(
                paciente=paciente, leito=leito, data=str(data_av),
                avaliador=st.session_state.usuario_nome,
                cateter=cateter, ventilacao=ventilacao,
                cirurgia_recente=cirurgia, imunossuprimido=imunossup,
                antibiotico=antibiotico, febre=febre, secrecao=secrecao,
                dias_cateter=dias_cateter, dias_ventilacao=dias_ventilacao,
                observacao_tipo=obs_tipo,
                observacao_livre=obs_livre,
            )
            score = calcular_score(dados)
            risco, css_class = classificar_risco(score)
            dados.update(score=score, risco=risco)
            salvar_avaliacao(dados)

            st.success("✅ Avaliação registrada com sucesso!")
            emoji_r = "🔴" if risco=="Alto" else "🟡" if "med" in risco.lower() else "🟢"
            risco_display = "Médio" if risco == "Medio" else risco
            st.markdown(f"""
            <div class="{css_class}">
                <h3>{emoji_r} Risco {risco_display} — Score: {score} pontos</h3>
                <p><strong>Paciente:</strong> {paciente} &nbsp;|&nbsp;
                   <strong>Leito:</strong> {leito} &nbsp;|&nbsp;
                   <strong>Avaliador:</strong> {st.session_state.usuario_nome}</p>
            </div>
            """, unsafe_allow_html=True)

            pdf_bytes = gerar_pdf(dados)
            st.download_button(
                label="⬇️ Baixar Relatório PDF",
                data=bytes(pdf_bytes),
                file_name=f"avaliacao_{paciente.replace(' ','_')}_{data_av}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

# ── TAB 2 — DASHBOARD ────────────────────────────────────────
with tab2:
    st.subheader("📊 Dashboard de Vigilância")
    avaliacoes = carregar_avaliacoes()

    if not avaliacoes:
        st.info("Nenhuma avaliação registrada ainda.")
    else:
        df = pd.DataFrame(avaliacoes)
        df["risco_display"] = df["risco"].apply(lambda r: "Médio" if "med" in str(r).lower() else r)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("📋 Total", len(df))
        m2.metric("🔴 Risco Alto",  int(df["risco"].str.lower().str.contains("alto").sum()),
                  delta=f"{df['risco'].str.lower().str.contains('alto').mean()*100:.0f}% do total",
                  delta_color="inverse")
        m3.metric("🟡 Risco Médio", int(df["risco"].str.lower().str.contains("med").sum()))
        m4.metric("🟢 Risco Baixo", int(df["risco"].str.lower().str.contains("baixo").sum()))

        st.divider()
        col1, col2 = st.columns(2)

        with col1:
            contagem = df["risco_display"].value_counts().reset_index()
            contagem.columns = ["Risco", "Qtd"]
            cores = {"Alto":"#dc2626","Médio":"#ca8a04","Baixo":"#16a34a"}
            fig_pie = px.pie(contagem, names="Risco", values="Qtd",
                             title="Distribuição por Nível de Risco",
                             color="Risco", color_discrete_map=cores, hole=0.4)
            fig_pie.update_layout(margin=dict(t=40,b=0,l=0,r=0))
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            cols_f  = ["cateter","ventilacao","cirurgia_recente","imunossuprimido","antibiotico","febre","secrecao"]
            labels_f = ["CVC","Ventilação","Cirurgia","Imunosup.","Antibiótico","Febre","Secreção"]
            prev = [int(df[c].sum()) for c in cols_f if c in df.columns]
            fig_bar = px.bar(x=labels_f[:len(prev)], y=prev,
                             title="Prevalência de Fatores de Risco",
                             labels={"x":"Fator","y":"Pacientes"},
                             color=prev,
                             color_continuous_scale=["#16a34a","#ca8a04","#dc2626"])
            fig_bar.update_layout(margin=dict(t=40,b=0), coloraxis_showscale=False)
            st.plotly_chart(fig_bar, use_container_width=True)

        df_t = df.copy()
        df_t["data"] = pd.to_datetime(df_t["data"])
        hover = ["paciente","leito"]
        if "avaliador" in df_t.columns:
            hover.append("avaliador")
        fig_sc = px.scatter(df_t.sort_values("data"), x="data", y="score",
                            color="risco_display", size="score", size_max=18,
                            title="Score por Paciente ao Longo do Tempo",
                            color_discrete_map={"Alto":"#dc2626","Médio":"#ca8a04","Baixo":"#16a34a"},
                            hover_data=hover)
        fig_sc.add_hline(y=14, line_dash="dot", line_color="#dc2626", annotation_text="Limiar Alto (14)")
        fig_sc.add_hline(y=7,  line_dash="dot", line_color="#ca8a04", annotation_text="Limiar Médio (7)")
        st.plotly_chart(fig_sc, use_container_width=True)

# ── TAB 3 — HISTÓRICO ────────────────────────────────────────
with tab3:
    st.subheader("📂 Histórico de Avaliações")
    avaliacoes = carregar_avaliacoes()

    if not avaliacoes:
        st.info("Nenhuma avaliação registrada ainda.")
    else:
        fc1, fc2 = st.columns([2, 1])
        with fc1:
            busca = st.text_input("🔍 Buscar por nome, leito ou avaliador", placeholder="Digite para filtrar...")
        with fc2:
            filtro = st.selectbox("Filtrar por risco", ["Todos","Alto","Médio","Baixo"])

        filtrados = avaliacoes
        if busca:
            b = busca.lower()
            filtrados = [a for a in filtrados if
                         b in a.get("paciente","").lower() or
                         b in a.get("leito","").lower() or
                         b in a.get("avaliador","").lower()]
        if filtro != "Todos":
            filtrados = [a for a in filtrados if
                         (filtro == "Médio" and "med" in a.get("risco","").lower()) or
                         (filtro != "Médio" and filtro.lower() in a.get("risco","").lower())]

        st.caption(f"Exibindo {len(filtrados)} de {len(avaliacoes)} avaliações")

        for av in filtrados:
            risco = av.get("risco","Baixo")
            risco_display = "Médio" if "med" in risco.lower() else risco
            emoji = "🔴" if "alto" in risco.lower() else "🟡" if "med" in risco.lower() else "🟢"
            avaliador = av.get("avaliador", "-")
            titulo = f"{emoji} {av.get('paciente','-')} | {av.get('leito','-')} | Score: {av.get('score','-')} | {av.get('data','-')} | 👤 {avaliador}"

            with st.expander(titulo):
                ca, cb = st.columns(2)
                with ca:
                    st.write(f"**Risco:** {risco_display}")
                    st.write(f"**Avaliador:** {avaliador}")
                    dias_cat  = f"({av.get('dias_cateter')} dias)"   if av.get('cateter')    else ""
                    dias_vent = f"({av.get('dias_ventilacao')} dias)" if av.get('ventilacao') else ""
                    st.write(f"**Cateter:** {'✓' if av.get('cateter') else '✗'} {dias_cat}")
                    st.write(f"**Ventilação:** {'✓' if av.get('ventilacao') else '✗'} {dias_vent}")
                    st.write(f"**Cirurgia recente:** {'✓' if av.get('cirurgia_recente') else '✗'}")
                with cb:
                    st.write(f"**Imunossuprimido:** {'✓' if av.get('imunossuprimido') else '✗'}")
                    st.write(f"**Antibiótico:** {'✓' if av.get('antibiotico') else '✗'}")
                    st.write(f"**Febre:** {'✓' if av.get('febre') else '✗'}")
                    st.write(f"**Secreção:** {'✓' if av.get('secrecao') else '✗'}")

                obs_t = av.get("observacao_tipo","")
                obs_l = av.get("observacao_livre","")
                if obs_t or obs_l:
                    st.markdown("**Observação:**")
                    if obs_t: st.write(f"📌 {obs_t}")
                    if obs_l: st.caption(obs_l)

                pdf_bytes = gerar_pdf(av)
                st.download_button(
                    f"⬇️ PDF — {av.get('paciente','-')}",
                    data=bytes(pdf_bytes),
                    file_name=f"relatorio_{av.get('paciente','').replace(' ','_')}_{av.get('data','')}.pdf",
                    mime="application/pdf",
                    key=f"pdf_{av.get('id',0)}_{av.get('data','')}",
                )
