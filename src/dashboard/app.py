"""
Dashboard Streamlit para monitoramento de fraudes bancarias.
Conecta-se a API FastAPI para exibir metricas em tempo real.
"""
import json
import time
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

# Configuracao da pagina
st.set_page_config(
    page_title="Fraud Detection Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = st.sidebar.text_input(
    "API URL", value="http://api:8000", help="URL da API de deteccao de fraude"
)

st.title("Sistema de Deteccao de Fraudes Bancarias")
st.markdown("Dashboard de monitoramento em tempo real")

# ---------- Sidebar ----------
st.sidebar.header("Controles")

auto_refresh = st.sidebar.checkbox("Auto-refresh (5s)", value=False)
if auto_refresh:
    time.sleep(5)
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("Enviar Transacao de Teste")

with st.sidebar.form("send_transaction"):
    amount = st.number_input("Valor (R$)", min_value=0.0, value=500.0, step=100.0)
    category = st.selectbox(
        "Categoria",
        ["Alimentacao", "Eletronicos", "Vestuario", "Servicos", "Viagem", "Entretenimento"],
    )
    payment = st.selectbox(
        "Pagamento", ["PIX", "CREDIT_CARD", "DEBIT_CARD", "BOLETO"]
    )
    user_country = st.selectbox("Pais Usuario", ["BR", "US", "GB", "FR"])
    merchant_country = st.selectbox("Pais Comerciante", ["BR", "US", "GB", "FR"])
    hour = st.slider("Hora", 0, 23, 14)
    is_weekend = st.checkbox("Fim de semana")

    submitted = st.form_submit_button("Analisar Transacao")

    if submitted:
        payload = {
            "amount": amount,
            "merchant_category": category,
            "payment_method": payment,
            "user_country": user_country,
            "merchant_country": merchant_country,
            "hour": hour,
            "is_weekend": int(is_weekend),
            "is_international": int(user_country != merchant_country),
        }
        try:
            resp = requests.post(
                f"{API_URL}/api/v1/transactions/analyze",
                json=payload,
                timeout=10,
            )
            if resp.status_code == 200:
                result = resp.json()
                if result.get("is_fraud"):
                    st.sidebar.error(
                        f"FRAUDE DETECTADA! Score: {result['fraud_score']:.2%}"
                    )
                else:
                    st.sidebar.success(
                        f"Transacao segura. Score: {result['fraud_score']:.2%}"
                    )
            else:
                st.sidebar.error(f"Erro: {resp.status_code}")
        except requests.exceptions.ConnectionError:
            st.sidebar.error("API indisponivel. Verifique se esta rodando.")


# ---------- Funcoes auxiliares ----------


def fetch_data(endpoint: str):
    """Busca dados da API."""
    try:
        resp = requests.get(f"{API_URL}{endpoint}", timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except requests.exceptions.ConnectionError:
        return None
    return None


# ---------- KPIs ----------

summary = fetch_data("/api/v1/dashboard/summary")

if summary is None:
    st.warning(
        "Nao foi possivel conectar a API. Verifique se ela esta rodando "
        f"em {API_URL}"
    )
    st.info(
        "Para iniciar: `docker-compose up -d` ou "
        "`python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000`"
    )
    st.stop()

kpis = summary.get("kpis", {})

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Transacoes",
        kpis.get("total_transactions", 0),
    )

with col2:
    st.metric(
        "Fraudes Detectadas",
        kpis.get("total_frauds", 0),
    )

with col3:
    fraud_rate = kpis.get("fraud_rate", 0)
    st.metric(
        "Taxa de Fraude",
        f"{fraud_rate:.2%}",
    )

with col4:
    avg_time = kpis.get("avg_processing_time_ms", 0)
    st.metric(
        "Tempo Medio (ms)",
        f"{avg_time:.1f}",
    )

with col5:
    error_rate = kpis.get("error_rate", 0)
    st.metric(
        "Taxa de Erro",
        f"{error_rate:.2%}",
    )

st.markdown("---")

# ---------- Graficos ----------

col_left, col_right = st.columns(2)

# Distribuicao de scores
with col_left:
    st.subheader("Distribuicao de Scores de Fraude")
    score_dist = summary.get("score_distribution", {})
    if any(score_dist.values()):
        fig_scores = go.Figure(
            data=[
                go.Bar(
                    x=["Baixo (0-30%)", "Medio (30-50%)", "Alto (50-80%)", "Critico (80-100%)"],
                    y=[
                        score_dist.get("low_0_30", 0),
                        score_dist.get("medium_30_50", 0),
                        score_dist.get("high_50_80", 0),
                        score_dist.get("critical_80_100", 0),
                    ],
                    marker_color=["#2ecc71", "#f39c12", "#e74c3c", "#8e44ad"],
                )
            ]
        )
        fig_scores.update_layout(
            xaxis_title="Nivel de Risco",
            yaxis_title="Quantidade",
            height=350,
        )
        st.plotly_chart(fig_scores, use_container_width=True)
    else:
        st.info("Envie transacoes para ver a distribuicao de scores")

# Fraudes por categoria
with col_right:
    st.subheader("Transacoes por Categoria")
    cat_dist = summary.get("category_distribution", {})
    cat_frauds = summary.get("category_fraud_counts", {})
    if cat_dist:
        categories = list(cat_dist.keys())
        totals = [cat_dist.get(c, 0) for c in categories]
        frauds = [cat_frauds.get(c, 0) for c in categories]
        legits = [t - f for t, f in zip(totals, frauds)]

        fig_cat = go.Figure(
            data=[
                go.Bar(name="Legitimas", x=categories, y=legits, marker_color="#2ecc71"),
                go.Bar(name="Fraudes", x=categories, y=frauds, marker_color="#e74c3c"),
            ]
        )
        fig_cat.update_layout(
            barmode="stack",
            xaxis_title="Categoria",
            yaxis_title="Quantidade",
            height=350,
        )
        st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.info("Envie transacoes para ver por categoria")

# ---------- Pagamento e Modelo ----------

col_pay, col_model = st.columns(2)

with col_pay:
    st.subheader("Metodos de Pagamento")
    pay_dist = summary.get("payment_distribution", {})
    if pay_dist:
        fig_pay = px.pie(
            names=list(pay_dist.keys()),
            values=list(pay_dist.values()),
            hole=0.4,
        )
        fig_pay.update_layout(height=350)
        st.plotly_chart(fig_pay, use_container_width=True)
    else:
        st.info("Envie transacoes para ver metodos de pagamento")

with col_model:
    st.subheader("Feature Importance do Modelo")
    fi_data = fetch_data("/api/v1/model/feature-importance")
    if fi_data and isinstance(fi_data, dict) and fi_data:
        features = list(fi_data.keys())
        importances = list(fi_data.values())
        fig_fi = go.Figure(
            data=[
                go.Bar(
                    x=importances,
                    y=features,
                    orientation="h",
                    marker_color="#3498db",
                )
            ]
        )
        fig_fi.update_layout(
            xaxis_title="Importancia",
            yaxis_title="Feature",
            height=350,
        )
        st.plotly_chart(fig_fi, use_container_width=True)
    else:
        st.info("Modelo nao carregado ou sem feature importance")

st.markdown("---")

# ---------- Tabela de transacoes recentes ----------

st.subheader("Transacoes Recentes")

recent = summary.get("recent_transactions", [])
if recent:
    df = pd.DataFrame(recent)

    # Estilizar colunas
    display_cols = [
        "transaction_id",
        "amount",
        "merchant_category",
        "payment_method",
        "fraud_score",
        "risk_level",
        "recommended_action",
        "processing_time_ms",
    ]
    available_cols = [c for c in display_cols if c in df.columns]
    df_display = df[available_cols].copy()

    if "fraud_score" in df_display.columns:
        df_display["fraud_score"] = df_display["fraud_score"].apply(
            lambda x: f"{x:.2%}"
        )
    if "amount" in df_display.columns:
        df_display["amount"] = df_display["amount"].apply(
            lambda x: f"R$ {x:,.2f}"
        )

    st.dataframe(df_display, use_container_width=True, height=400)
else:
    st.info(
        "Nenhuma transacao processada ainda. Use a barra lateral para "
        "enviar transacoes de teste."
    )

# ---------- Alertas ----------

st.subheader("Alertas de Fraude")

alerts = summary.get("recent_alerts", [])
if alerts:
    for alert in reversed(alerts):
        with st.expander(
            f"ALERTA - Score: {alert['fraud_score']:.2%} | "
            f"R$ {alert['amount']:,.2f} | {alert['risk_level']}",
            expanded=False,
        ):
            st.json(alert)
else:
    st.success("Nenhum alerta de fraude ativo")

# ---------- Data Quality ----------

st.markdown("---")
st.subheader("Relatorio de Data Quality")

dq_data = fetch_data("/api/v1/data-quality/report")
if dq_data and dq_data.get("status") != "no_data":
    checks = dq_data.get("checks", [])
    stats = dq_data.get("statistics", {})

    col_dq1, col_dq2 = st.columns(2)

    with col_dq1:
        st.markdown("**Verificacoes de Qualidade:**")
        for check in checks:
            icon = "✅" if check["passed"] else "❌"
            st.markdown(f"{icon} **{check['rule']}**: {check['details']}")

    with col_dq2:
        st.markdown("**Estatisticas:**")
        if stats:
            st.markdown(f"- Media de valor: R$ {stats.get('amount_mean', 0):,.2f}")
            st.markdown(f"- Mediana de valor: R$ {stats.get('amount_median', 0):,.2f}")
            st.markdown(f"- Desvio padrao: R$ {stats.get('amount_stddev', 0):,.2f}")
            st.markdown(f"- Valor minimo: R$ {stats.get('amount_min', 0):,.2f}")
            st.markdown(f"- Valor maximo: R$ {stats.get('amount_max', 0):,.2f}")
            st.markdown(f"- Taxa de fraude: {stats.get('fraud_rate', 0):.2%}")
else:
    st.info("Processe transacoes para gerar o relatorio de qualidade")

# ---------- Footer ----------

st.markdown("---")
st.markdown(
    "*Sistema de Deteccao de Fraudes Bancarias - "
    "Azure Cloud Native Architecture | v1.0.0*"
)
