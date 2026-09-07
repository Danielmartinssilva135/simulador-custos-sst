import io
import urllib.parse
from datetime import date
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Simulador Financeiro de SST: FAP, RAT e Custos Ocultos",
    page_icon="💼",
    layout="wide"
)

# Estilização CSS Executiva / Power BI Clean
st.markdown("""
<style>
    .stApp {
        background-color: #F8FAFC;
        color: #0F172A;
    }
    .header-box {
        background-color: #FFFFFF;
        padding: 18px 22px;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        border-left: 6px solid #0EA5E9;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .header-title {
        font-size: 22px;
        font-weight: 800;
        color: #0F172A;
        margin: 0;
        text-transform: uppercase;
    }
    .header-sub {
        font-size: 13px;
        color: #64748B;
        margin-top: 4px;
        font-weight: 500;
    }
    .kpi-card {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 14px 10px;
        text-align: center;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        margin-bottom: 12px;
    }
    .kpi-label {
        font-size: 11px;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .kpi-val {
        font-size: 22px;
        font-weight: 800;
    }
    .val-danger { color: #DC2626 !important; }
    .val-success { color: #16A34A !important; }
    .val-info { color: #0284C7 !important; }
    .val-warn { color: #D97706 !important; }
</style>
""", unsafe_allow_html=True)

# Barra Lateral: Parâmetros Financeiros e Acidentários
with st.sidebar:
    st.header("⚙️ Parâmetros da Empresa")
    
    folha_anual = st.number_input(
        "Folha Salarial Bruta Anual (R$):",
        min_value=100000.0,
        value=6000000.0,
        step=500000.0,
        format="%.2f"
    )
    
    grau_risco = st.selectbox(
        "Grau de Risco / Alíquota Base RAT:",
        options=[
            ("Grau 1 - Risco Leve (1,0%)", 0.01),
            ("Grau 2 - Risco Médio (2,0%)", 0.02),
            ("Grau 3 - Risco Grave (3,0%)", 0.03)
        ],
        index=2,
        format_func=lambda x: x[0]
    )[1]
    
    fap_atual = st.slider(
        "FAP Atual da Empresa (0,50 a 2,00):",
        min_value=0.5000,
        max_value=2.0000,
        value=1.4500,
        step=0.0100,
        help="O FAP varia de 0,5 (bônus máximo de 50%) até 2,0 (sobretaxa de 100%)."
    )
    
    st.divider()
    st.subheader("📊 Histórico Recente de Ocorrências")
    acid_afast = st.number_input("Acidentes c/ Afastamento (B91):", min_value=0, value=3, step=1)
    acid_sem_afast = st.number_input("Acidentes s/ Afastamento:", min_value=0, value=8, step=1)
    quase_acidentes = st.number_input("Quase-Acidentes relatados:", min_value=0, value=15, step=1)
    
    st.divider()
    st.subheader("🛡️ Investimento em Prevenção")
    investimento_sst = st.number_input(
        "Orçamento Preventivo Anual Proposto (R$):",
        min_value=5000.0,
        value=65000.0,
        step=5000.0,
        format="%.2f",
        help="Investimento em novos EPCs, treinamentos práticos, adequação ergonômica e auditorias."
    )

# Cálculos Tributários e Previdenciários
rat_ajustado_atual = grau_risco * fap_atual
custo_rat_atual = folha_anual * rat_ajustado_atual

rat_minimo = grau_risco * 0.5000
custo_rat_minimo = folha_anual * rat_minimo
economia_tributaria_maxima = custo_rat_atual - custo_rat_minimo

rat_maximo = grau_risco * 2.0000
custo_rat_maximo = folha_anual * rat_maximo

# Custos Ocultos e Perdas Operacionais (Pirâmide de Bird / Heinrich)
custo_direto_estimado = (acid_afast * 8500.0) + (acid_sem_afast * 1200.0)
# Literatura consagrada: Custos indiretos representam de 4 a 10 vezes os custos médicos/diretos
multiplicador_indireto = 4.5
custos_indiretos_ocultos = custo_direto_estimado * multiplicador_indireto
custo_total_acidentalidade = custo_direto_estimado + custos_indiretos_ocultos

# Retorno sobre o Investimento em Prevenção (ROI de SST)
# Projeção: Redução de 50% nas perdas operacionais + redução gradativa do FAP para 0,80
fap_projetado_sst = 0.8000
economia_fap_projetada = custo_rat_atual - (folha_anual * grau_risco * fap_projetado_sst)
ganho_operacional_projetado = custo_total_acidentalidade * 0.55
beneficio_financeiro_anual = economia_fap_projetada + ganho_operacional_projetado
roi_sst = ((beneficio_financeiro_anual - investimento_sst) / investimento_sst) * 100 if investimento_sst > 0 else 0

# Topo Executivo
st.markdown("""
<div class="header-box">
    <div class="header-title">💼 SIMULADOR FINANCEIRO DE SST: FAP, RAT E RETORNO SOBRE A PREVENÇÃO</div>
    <div class="header-sub">Engenharia Econômica de Segurança • Análise Tributária Previdenciária • Quantificação de Custos Ocultos de Acidentes</div>
</div>
""", unsafe_allow_html=True)

# Cartões de Métricas
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">RAT Efetivo Atual</div><div class="kpi-val val-info">{rat_ajustado_atual*100:.2f}%</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Custo Tributário RAT / Ano</div><div class="kpi-val val-danger">R$ {custo_rat_atual:,.2f}</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Economia Tributária c/ FAP 0.5</div><div class="kpi-val val-success">R$ {economia_tributaria_maxima:,.2f}</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Custos Ocultos de Acidentes</div><div class="kpi-val val-warn">R$ {custos_indiretos_ocultos:,.2f}</div></div>', unsafe_allow_html=True)
with k5:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">ROI Projetado de Prevenção</div><div class="kpi-val val-success">{roi_sst:.1f}%</div></div>', unsafe_allow_html=True)

st.write("")

# Gráficos de Apoio à Tomada de Decisão
g1, g2 = st.columns([1.1, 0.9])
config_limpo = {"displayModeBar": False}

with g1:
    cenarios_df = pd.DataFrame({
        "Cenário": ["Melhor Caso (FAP 0.5)", "Cenário Projetado (Gestão SST)", "Cenário Atual", "Pior Caso (FAP 2.0)"],
        "Custo Anual (R$)": [custo_rat_minimo, folha_anual * grau_risco * fap_projetado_sst, custo_rat_atual, custo_rat_maximo],
        "Tipo": ["Meta Otimizada", "Com Ações Preventivas", "Atual", "Sobretaxa Máxima"]
    })
    
    fig_cenarios = px.bar(
        cenarios_df,
        x="Cenário",
        y="Custo Anual (R$)",
        color="Cenário",
        text_auto=".2s",
        title="<b>Impacto do FAP no Custo Anual do Seguro Acidentário (RAT)</b>",
        color_discrete_sequence=["#16A34A", "#0EA5E9", "#F59E0B", "#DC2626"]
    )
    fig_cenarios.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=20, r=20, t=50, b=30),
        showlegend=False,
        yaxis=dict(gridcolor="#F1F5F9", title="Custo em R$"),
        xaxis=dict(title=None)
    )
    st.plotly_chart(fig_cenarios, config=config_limpo, use_container_width=True)

with g2:
    fig_donut = go.Figure(data=[go.Pie(
        labels=["Custos Diretos (Médicos/Hospitalares)", "Custos Ocultos (Paradas, Perícias e Treinamento)"],
        values=[custo_direto_estimado, custos_indiretos_ocultos],
        hole=0.55,
        marker=dict(colors=["#94A3B8", "#EA580C"])
    )])
    fig_donut.update_layout(
        title="<b>Composição das Perdas por Acidentes (Ratio de Bird)</b>",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_donut, config=config_limpo, use_container_width=True)

st.write("")

# Síntese Executiva para Envio Direto ao WhatsApp (Diretoria / Financeiro)
msg_cfo = f"💼 *RELATÓRIO DE ENGENHARIA ECONÔMICA & IMPACTO DO FAP/RAT* 💼%0A%0A"
msg_cfo += f"Empresa / Folha Salarial Anual: R$ {folha_anual:,.2f}%0A"
msg_cfo += f"Alíquota Atual do RAT Efetivo: {rat_ajustado_atual*100:.2f}% (FAP {fap_atual:.2f})%0A"
msg_cfo += f"Custo Previdenciário Acidentário Atual: R$ {custo_rat_atual:,.2f}/ano%0A%0A"
msg_cfo += f"🎯 *Potencial de Redução com Gestão Ativa de SST:*%0A"
msg_cfo += f"- Economia Tributária Potencial: até R$ {economia_tributaria_maxima:,.2f}/ano%0A"
msg_cfo += f"- Perdas Ocultas com Acidentes no Período: R$ {custo_total_acidentalidade:,.2f}%0A"
msg_cfo += f"- Retorno Projetado sobre o Investimento em SST (ROI): {roi_sst:.1f}%%0A%0A"
msg_cfo += "Acesse a simulação completa interativa: https://simulador-custos-sst.streamlit.app"

link_zap_cfo = f"https://api.whatsapp.com/send?text={msg_cfo}"

st.markdown(f"""
    <div style="display: flex; justify-content: flex-end; margin-bottom: 20px;">
        <a href="{link_zap_cfo}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #25D366; color: white; padding: 12px 20px; border-radius: 6px; font-weight: 700; font-size: 14px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                📲 Compartilhar Sumário Executivo com Diretoria / Financeiro
            </div>
        </a>
    </div>
""", unsafe_allow_html=True)

# Detalhamento Metodológico e Normativo
with st.expander("📚 Fundamentação Técnica e Normativa do Modelo"):
    st.markdown("""
    * **RAT (Riscos Ambientais do Trabalho):** Alíquota de 1%, 2% ou 3% incidente sobre a folha de salários para custear os benefícios acidentários e aposentadorias especiais concedidas pelo INSS (Lei nº 8.212/91).
    * **FAP (Fator Acidentário de Prevenção):** Multiplicador instituído pela Lei nº 10.666/2003 que bonifica (reduzindo a alíquota à metade) ou sobretaxa (dobrando a alíquota) as empresas com base nos índices de frequência, gravidade e custo dos acidentes da subclasse CNAE.
    * **Custos Ocultos (Teoria da Proporção de Acidentes de Frank Bird Jr.):** Demonstra que as indenizações e despesas médicas imediatas representam apenas a ponta do iceberg, enquanto o tempo perdido por equipes de apoio, consertos mecânicos, perícias técnicas e contratações temporárias compõem a maior fatia do prejuízo empresarial.
    """)
