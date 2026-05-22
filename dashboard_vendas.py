import pandas as pd
import streamlit as st
import plotly.express as px
import hashlib
import requests
import io

# ══════════════════════════════════════════════════════════════════
#  UTILIZADORES AUTORIZADOS
#  Para adicionar/remover utilizadores, edita este dicionario.
#  A senha e guardada como hash SHA-256 por seguranca.
#
#  Para gerar o hash de uma nova senha, corre no terminal:
#      python -c "import hashlib; print(hashlib.sha256('TUASENHA'.encode()).hexdigest())"
# ══════════════════════════════════════════════════════════════════
def make_hash(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# Ler utilizadores dos Secrets do Streamlit Cloud
# Em desenvolvimento local, usa o dicionario abaixo como fallback

try:
    UTILIZADORES = {u: make_hash(p) for u, p in st.secrets["utilizadores"].items()}
except Exception:
    UTILIZADORES = {
        "admin":  make_hash("9de304d93bd520081197f916428edea3d6efca19b076746afba9e58a8eaeec62"),
        "gestor": make_hash("f4721d147a10d4c1235cdfe5522fef0cdb3d9079d65dd7c4b944985e850bbeba"),
        "vendas": make_hash("9804ae817bec7d2b84ef26b6c259acdea380772ba27d6d7d4035be46acb4572f"),
    }
# ── Configuração da página ───────────────────────────────────────────
st.set_page_config(page_title="Dashboard de Vendas - B Mussungo & Filhos Comércio Geral Lda", page_icon="📊", layout="wide")

# ── CSS global ───────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stAppViewContainer"], .main { background: #0f1117 !important; }
    [data-testid="stSidebar"] { background: #1a1d27 !important; border-right: 1px solid #2e3250; }
    html, body, [class*="css"], p, span, div, label, h1, h2, h3, h4, h5, h6 { color: #ffffff !important; }
    h1 { color: #00d4aa !important; letter-spacing: -1px; }
    [data-testid="metric-container"] {
        background: #1a1d27 !important;
        border: 1px solid #2e3250;
        border-radius: 12px;
        padding: 16px;
    }
    [data-testid="stMetricValue"] { color: #00d4aa !important; font-size: 1.4rem !important; }
    [data-testid="stMetricLabel"] { color: #c0c8ff !important; }

    /* Inputs de texto */
    [data-testid="stTextInput"] input {
        background-color: #1a1d27 !important;
        color: #ffffff !important;
        border: 1px solid #2e3250 !important;
        border-radius: 8px !important;
    }

    /* Selectbox / Multiselect */
    [data-baseweb="select"] > div { background-color: #1a1d27 !important; border-color: #2e3250 !important; }
    [data-baseweb="select"] span, [data-baseweb="select"] input, [data-baseweb="select"] div { color: #ffffff !important; }
    [data-baseweb="popover"], [data-baseweb="menu"], ul[role="listbox"] { background-color: #1a1d27 !important; border: 1px solid #2e3250 !important; }
    [role="option"] { background-color: #1a1d27 !important; color: #ffffff !important; }
    [role="option"]:hover, [aria-selected="true"] { background-color: #2e3250 !important; color: #00d4aa !important; }
    [data-baseweb="tag"] { background-color: #2e3250 !important; color: #ffffff !important; }

    /* Botao principal */
    [data-testid="stButton"] > button {
        background: linear-gradient(135deg, #00d4aa, #0099cc) !important;
        color: #0f1117 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        width: 100%;
        padding: 0.6rem !important;
        font-size: 1rem !important;
    }
    [data-testid="stButton"] > button:hover {
        opacity: 0.9 !important;
        transform: translateY(-1px);
    }

    /* Card de login */
    .login-box {
        background: linear-gradient(135deg, #1a1d27, #0f1117);
        border: 1px solid #2e3250;
        border-radius: 16px;
        padding: 40px;
        max-width: 420px;
        margin: 80px auto 0 auto;
        box-shadow: 0 8px 40px rgba(0,212,170,0.08);
    }
    .login-title {
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        color: #00d4aa !important;
        margin-bottom: 4px;
    }
    .login-sub {
        text-align: center;
        color: #888 !important;
        margin-bottom: 28px;
        font-size: 0.9rem;
    }

    /* Cards de ano */
    .card-ano {
        background: linear-gradient(135deg, #1a1d27, #2e3250);
        border: 1px solid #f0f0f0;
        border-radius: 12px;
        padding: 16px 20px;
        text-align: center;
        margin-bottom: 8px;
    }
    .card-ano h4 { color: #c0c8ff !important; margin: 0; font-size: 0.85rem; }
    .card-ano h2 { color: #00d4aa !important; margin: 4px 0 0 0; font-size: 1.3rem; }

    [data-testid="stDataFrame"] * { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
#  AUTENTICAÇÃO
# ══════════════════════════════════════════════════════════════════
def verificar_login(utilizador, senha):
    if utilizador in UTILIZADORES:
        return UTILIZADORES[utilizador] == make_hash(senha)
    return False

def tela_login():
    col_l, col_mid, col_r = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<br><br>", unsafe_allow_html=True)

        # Logo da empresa
        try:
            st.image("bmrh.png", use_container_width=True)
        except Exception:
            pass

        st.markdown("""
        <div style="text-align:center; margin: 16px 0 24px 0;">
            <div style="font-size:1.1rem; color:#888;">Dashboard de Vendas</div>
            <div style="font-size:0.85rem; color:#555; margin-top:4px;">
                Acesso restrito — insira as suas credenciais
            </div>
        </div>
        """, unsafe_allow_html=True)

        utilizador = st.text_input("👤 Utilizador", placeholder="nome de utilizador")
        senha      = st.text_input("🔒 Senha", type="password", placeholder="senha")
        entrar     = st.button("Entrar")

        if entrar:
            if verificar_login(utilizador, senha):
                st.session_state["autenticado"] = True
                st.session_state["utilizador"]  = utilizador
                st.rerun()
            else:
                st.error("❌ Utilizador ou senha incorrectos.")

# ── Inicializar sessão ───────────────────────────────────────────────
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)
    tela_login()
    st.stop()

# ══════════════════════════════════════════════════════════════════
#  DASHBOARD (só chega aqui quem fez login)
# ══════════════════════════════════════════════════════════════════

# ── Carregar dados ───────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def carregar_dados():
    # Verifica se SHEET_ID existe nos secrets (Streamlit Cloud)
    if "SHEET_ID" in st.secrets:
        sheet_id = st.secrets["SHEET_ID"]
        gid       = st.secrets.get("SHEET_GID", "0")
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx&gid={gid}"
        st.sidebar.caption(f"A carregar dados do Google Sheets...")
        resp = requests.get(url, timeout=30)
        if resp.status_code != 200:
            st.error(f"Erro HTTP {resp.status_code} ao aceder ao Google Sheets.")
            st.error(f"URL tentado: `{url}`")
            st.info("Verifica: 1) SHEET_ID correcto nos Secrets  2) Folha partilhada como publica  3) SHEET_GID correcto")
            st.stop()
        df = pd.read_excel(io.BytesIO(resp.content))
    else:
        # Ambiente local sem secrets - usa ficheiro Excel
        import os
        if not os.path.exists("bmvendas.xlsx"):
            st.error("Ficheiro bmvendas.xlsx nao encontrado e SHEET_ID nao configurado nos Secrets.")
            st.stop()
        df = pd.read_excel("bmvendas.xlsx")

    df["Data_venda"] = pd.to_datetime(df["Data_venda"], errors="coerce")
    if "Ano" not in df.columns:
        df["Ano"] = df["Data_venda"].dt.year
    if "Mes" not in df.columns:
        col_mes = "Mes" if "Mes" in df.columns else ("Mes" if "Mes" in df.columns else None)
        df["Mes"] = df[col_mes] if col_mes else df["Data_venda"].dt.month
    if "mes_extenso_pt" not in df.columns:
        meses_pt = {1:"Janeiro",2:"Fevereiro",3:"Marco",4:"Abril",5:"Maio",6:"Junho",
                    7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}
        df["mes_extenso_pt"] = df["Mes"].map(meses_pt)
    if "Trimestre" not in df.columns:
        df["Trimestre"] = df["Mes"].apply(lambda m: f"T{(m-1)//3+1}")
    return df

vendas_df = carregar_dados()
if vendas_df is None or vendas_df.empty:
    st.error("Dados vazios. Verifica o Google Sheets.")
    st.stop()

CORES = px.colors.qualitative.Bold
meses_ordem_pt = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
                  "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
mes_ordem_num = {m: i for i, m in enumerate(meses_ordem_pt)}

LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#ffffff"),
    legend=dict(font=dict(color="#ffffff")),
    xaxis=dict(tickfont=dict(color="#ffffff"), title_font=dict(color="#ffffff")),
    yaxis=dict(tickfont=dict(color="#ffffff"), title_font=dict(color="#ffffff")),
)
def graf(fig):
    fig.update_layout(**LAYOUT)
    return fig

# ── BARRA LATERAL ────────────────────────────────────────────────────
st.sidebar.title("Filtros")
st.sidebar.markdown(f"✅ Sessão: **{st.session_state['utilizador']}**")
if st.sidebar.button("🚪 Terminar Sessão"):
    st.session_state["autenticado"] = False
    st.session_state["utilizador"]  = ""
    st.rerun()

st.sidebar.divider()

anos_disp = sorted(vendas_df["Ano"].dropna().unique().tolist())
ano_sel = st.sidebar.multiselect("Ano", options=anos_disp, default=anos_disp)

lojas_disp = sorted(vendas_df["Nome_Loja"].dropna().unique().tolist())
loja_sel = st.sidebar.multiselect("Loja", options=lojas_disp, default=lojas_disp)

meses_no_df = vendas_df["mes_extenso_pt"].dropna().unique().tolist()
meses_disp = [m for m in meses_ordem_pt if m in meses_no_df]
mes_sel = st.sidebar.multiselect("Mes", options=meses_disp, default=meses_disp)

trim_disp = sorted(vendas_df["Trimestre"].dropna().unique().tolist())
trim_sel = st.sidebar.multiselect("Trimestre", options=trim_disp, default=trim_disp)

tem_semana = "Semana" in vendas_df.columns
if tem_semana:
    semanas_disp = sorted(vendas_df["Semana"].dropna().unique().tolist())
    semana_sel = st.sidebar.multiselect("Semana", options=semanas_disp, default=semanas_disp)
else:
    semana_sel = []

# ── Aplicar filtros ──────────────────────────────────────────────────
anos_f  = ano_sel  if ano_sel  else anos_disp
lojas_f = loja_sel if loja_sel else lojas_disp
meses_f = mes_sel  if mes_sel  else meses_disp
trim_f  = trim_sel if trim_sel else trim_disp

mask = (
    vendas_df["Ano"].isin(anos_f) &
    vendas_df["Nome_Loja"].isin(lojas_f) &
    vendas_df["mes_extenso_pt"].isin(meses_f) &
    vendas_df["Trimestre"].isin(trim_f)
)
if tem_semana and semana_sel:
    mask = mask & vendas_df["Semana"].isin(semana_sel)

df = vendas_df[mask].copy()

# ── CABECALHO ────────────────────────────────────────────────────────
st.title("Dashboard de Vendas - B Mussungo & Filhos Comércio Geral Lda")
st.caption(f"A mostrar {len(df):,} registos filtrados de {len(vendas_df):,} totais")
st.divider()

# ── CARDS TOTAIS ─────────────────────────────────────────────────────
st.subheader("Totais de Vendas")
total_geral = df["total_iva"].sum()
media_loja  = df.groupby("Nome_Loja")["total_iva"].sum().mean() if not df.empty else 0
melhor_loja = df.groupby("Nome_Loja")["total_iva"].sum().idxmax() if not df.empty else "s/d"
total_lojas = df["Nome_Loja"].nunique()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Geral (filtrado)", f"{total_geral:,.2f} Kz")
c2.metric("Lojas Activas", total_lojas)
c3.metric("Media por Loja", f"{media_loja:,.2f} Kz")
c4.metric("Melhor Loja", melhor_loja)

st.markdown("<br>", unsafe_allow_html=True)

anos_todos  = sorted(vendas_df["Ano"].dropna().unique().tolist())
total_todos = vendas_df["total_iva"].sum()
cols_anos   = st.columns(len(anos_todos) + 1)

with cols_anos[0]:
    st.markdown(f'<div class="card-ano"><h4>TOTAL GERAL (todos os anos)</h4><h2>{total_todos:,.2f} Kz</h2></div>', unsafe_allow_html=True)
for i, ano in enumerate(anos_todos):
    t = vendas_df[vendas_df["Ano"] == ano]["total_iva"].sum()
    with cols_anos[i + 1]:
        st.markdown(f'<div class="card-ano"><h4>TOTAL {ano}</h4><h2>{t:,.2f} Kz</h2></div>', unsafe_allow_html=True)

st.divider()

# ── GRAFICO 1: Ano + Pizza ───────────────────────────────────────────
st.subheader("Vendas por Ano e Loja")
col_a, col_b = st.columns(2)

with col_a:
    d = df.groupby(["Ano","Nome_Loja"])["total_iva"].sum().reset_index()
    fig = px.bar(d, x="Ano", y="total_iva", color="Nome_Loja", barmode="group",
                 text_auto=".2s", labels={"total_iva":"Total (Kz)","Nome_Loja":"Loja"},
                 color_discrete_sequence=CORES, title="Total por Ano e Loja")
    st.plotly_chart(graf(fig), use_container_width=True)

with col_b:
    d = df.groupby("Nome_Loja")["total_iva"].sum().reset_index()
    fig = px.pie(d, names="Nome_Loja", values="total_iva", hole=0.45,
                 color_discrete_sequence=CORES, title="Quota por Loja")
    fig.update_traces(textfont=dict(color="#ffffff"))
    st.plotly_chart(graf(fig), use_container_width=True)

# ── GRAFICO 2: Evolucao Mensal ───────────────────────────────────────
st.subheader("Evolucao Mensal das Vendas")
d = (df.groupby(["Ano","Mes","mes_extenso_pt","Nome_Loja"])["total_iva"]
     .sum().reset_index().sort_values(["Ano","Mes"]))
d["Periodo"] = d["mes_extenso_pt"] + " " + d["Ano"].astype(str)
fig = px.line(d, x="Periodo", y="total_iva", color="Nome_Loja", markers=True,
              labels={"total_iva":"Total (Kz)","Nome_Loja":"Loja","Periodo":""},
              color_discrete_sequence=CORES)
fig.update_layout(xaxis_tickangle=-45)
st.plotly_chart(graf(fig), use_container_width=True)

# ── GRAFICO 3: Mes ───────────────────────────────────────────────────
st.subheader("Vendas por Mes")
d = df.groupby(["mes_extenso_pt","Nome_Loja"])["total_iva"].sum().reset_index()
d["ordem"] = d["mes_extenso_pt"].map(mes_ordem_num).fillna(99)
d = d.sort_values("ordem")
fig = px.bar(d, x="mes_extenso_pt", y="total_iva", color="Nome_Loja",
             barmode="group", text_auto=".2s",
             labels={"total_iva":"Total (Kz)","mes_extenso_pt":"Mes","Nome_Loja":"Loja"},
             color_discrete_sequence=CORES)
st.plotly_chart(graf(fig), use_container_width=True)

# ── GRAFICO 4: Trimestre + Dia da Semana ────────────────────────────
st.subheader("Vendas por Trimestre e Dia da Semana")
col_c, col_d = st.columns(2)

with col_c:
    d = df.groupby(["Trimestre","Nome_Loja"])["total_iva"].sum().reset_index()
    fig = px.bar(d, x="Trimestre", y="total_iva", color="Nome_Loja",
                 barmode="group", text_auto=".2s",
                 labels={"total_iva":"Total (Kz)","Nome_Loja":"Loja"},
                 color_discrete_sequence=CORES, title="Por Trimestre")
    st.plotly_chart(graf(fig), use_container_width=True)

with col_d:
    if "Dia_da_semana" in df.columns:
        dias_ordem = ["Segunda","Terca","Quarta","Quinta","Sexta","Sabado","Domingo"]
        d = df.groupby(["Dia_da_semana","Nome_Loja"])["total_iva"].sum().reset_index()
        d["Dia_da_semana"] = pd.Categorical(
            d["Dia_da_semana"],
            categories=[x for x in dias_ordem if x in d["Dia_da_semana"].values],
            ordered=True
        )
        fig = px.bar(d.sort_values("Dia_da_semana"), x="Dia_da_semana", y="total_iva",
                     color="Nome_Loja", barmode="group", text_auto=".2s",
                     labels={"total_iva":"Total (Kz)","Dia_da_semana":"Dia","Nome_Loja":"Loja"},
                     color_discrete_sequence=CORES, title="Por Dia da Semana")
        st.plotly_chart(graf(fig), use_container_width=True)

# ── GRAFICO 5: Semana ────────────────────────────────────────────────
if tem_semana:
    st.subheader("Vendas por Semana")
    d = df.groupby(["Semana","Nome_Loja"])["total_iva"].sum().reset_index()
    fig = px.bar(d, x="Semana", y="total_iva", color="Nome_Loja",
                 barmode="group", text_auto=".2s",
                 labels={"total_iva":"Total (Kz)","Semana":"Semana","Nome_Loja":"Loja"},
                 color_discrete_sequence=CORES)
    st.plotly_chart(graf(fig), use_container_width=True)

    st.subheader("Detalhe Semanal por Mes")
    d_sem = (df.groupby(["mes_extenso_pt","Semana","Nome_Loja"])["total_iva"]
             .sum().reset_index())
    d_sem["ordem"] = d_sem["mes_extenso_pt"].map(mes_ordem_num).fillna(99)
    d_sem = d_sem.sort_values("ordem")
    meses_com_dados = [m for m in meses_ordem_pt if m in d_sem["mes_extenso_pt"].values]

    mes_escolhido = st.radio("Selecciona o mes:", options=meses_com_dados, horizontal=True)
    df_sem_mes = d_sem[d_sem["mes_extenso_pt"] == mes_escolhido]
    fig = px.bar(df_sem_mes, x="Semana", y="total_iva", color="Nome_Loja",
                 barmode="group", text_auto=".2s",
                 labels={"total_iva":"Total (Kz)","Semana":"Semana","Nome_Loja":"Loja"},
                 color_discrete_sequence=CORES, title=f"Semanas de {mes_escolhido}")
    st.plotly_chart(graf(fig), use_container_width=True)

# ── TABELA RESUMO ────────────────────────────────────────────────────
st.divider()
st.subheader("Tabela Resumo por Loja e Mes")
tabela = (
    df.groupby(["Nome_Loja","Ano","mes_extenso_pt"])["total_iva"]
    .sum().reset_index()
    .rename(columns={"Nome_Loja":"Loja","mes_extenso_pt":"Mes","total_iva":"Total (Kz)"})
    .sort_values(["Loja","Ano"])
)
tabela["Total (Kz)"] = tabela["Total (Kz)"].map("{:,.2f}".format)
st.dataframe(tabela, use_container_width=True, hide_index=True)