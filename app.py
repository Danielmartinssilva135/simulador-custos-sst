# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import urllib.parse

st.set_page_config(
    page_title="Simulador Financeiro de SST: FAP, RAT e Custos Ocultos",
    page_icon="📊",
    layout="wide"
)

# Estilização visual customizada com contraste forçado para modo claro e escuro
st.markdown("""
<style>
    /* Força os cards do st.metric a terem fundo executivo e texto legível */
    [data-testid="stMetric"] {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        padding: 18px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.25) !important;
    }
    
    /* Cor do rótulo/título da métrica */
    [data-testid="stMetricLabel"] p {
        color: #94A3B8 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    
    /* Cor do valor financeiro principal (R$) */
    [data-testid="stMetricValue"] div {
        color: #F8FAFC !important;
        font-weight: 800 !important;
        font-size: 26px !important;
    }
</style>
""", unsafe_allow_html=True)

# Título e Cabeçalho Executivo
st.title("💼 Simulador Financeiro de SST: FAP, RAT e Retorno sobre Prevenção")
st.markdown("""
Quantifique o impacto dos acidentes e do FAP diretamente na folha de pagamento da sua empresa.
Converta indicadores técnicos de SST em valor econômico e projeção de ROI para apresentação à Diretoria.
""")
st.markdown("---")

# Barra Lateral - Parâmetros da Empresa
st.sidebar.markdown("## ⚙️ Parâmetros da Empresa")

folha_mensal = st.sidebar.number_input(
    "Folha Salarial Mensal Bruta (R$):", 
    min_value=10000.0, 
    value=350000.0, 
    step=25000.0,
    format="%.2f"
)

folha_anual = folha_mensal * 12

rat_aliquota = st.sidebar.selectbox(
    "Alíquota RAT / Grau de Risco (CNAE):",
    options=[0.01, 0.02, 0.03],
    index=1,
    format_func=lambda x: f"{int(x*100)}% — Risco {'Leve' if x==0.01 else 'Médio' if x==0.02 else 'Grave'}"
)

fap_atual = st.sidebar.slider(
    "FAP Atual da Empresa (0.5 a 2.0):",
    min_value=0.5000,
    max_value=2.0000,
    value=1.2500,
    step=0.0100
)

fap_alvo = st.sidebar.slider(
    "FAP Alvo Projetado (Meta de Gestão SST):",
    min_value=0.5000,
    max_value=2.0000,
    value=0.7000,
    step=0.0100
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🚑 Histórico de Acidentes (Últimos 12 Meses)")

acid_sem_afast = st.sidebar.number_input("Acidentes Sem Afastamento (< 15 dias):", min_value=0, value=6, step=1)
acid_com_afast = st.sidebar.number_input("Acidentes Com Afastamento (B91 / > 15 dias):", min_value=0, value=2, step=1)
custo_direto_medio = st.sidebar.number_input("Custo Médico/Hospitalar Direto Médio por Ocorrência (R$):", min_value=0.0, value=2500.0, step=500.0)

# Cálculos Previdenciários (FAP e RAT Ajustado)
rat_ajustado_atual = rat_aliquota * fap_atual
rat_ajustado_alvo = rat_aliquota * fap_alvo
rat_ajustado_minimo = rat_aliquota * 0.50
rat_ajustado_maximo = rat_aliquota * 2.00

custo_rat_atual = folha_anual * rat_ajustado_atual
custo_rat_alvo = folha_anual * rat_ajustado_alvo
custo_rat_minimo = folha_anual * rat_ajustado_minimo
custo_rat_maximo = folha_anual * rat_ajustado_maximo

economia_tributaria = custo_rat_atual - custo_rat_alvo

# Metodologia Pirâmide de Bird (Custos Ocultos / Indiretos)
# Relação clássica estimada de 1:4.5 em perdas de produtividade, paradas e retrabalho
total_acidentes = acid_sem_afast + acid_com_afast
custos_diretos_totais = total_acidentes * custo_direto_medio
custos_indiretos_totais = custos_diretos_totais * 4.5

impacto_total_atual = custo_rat_atual + custos_diretos_totais + custos_indiretos_totais

# 4 Cards de Métricas Principais
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Custo Anual RAT Vigente",
        value=f"R$ {custo_rat_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        delta=f"Alíquota: {rat_ajustado_atual*100:.2f}%",
        delta_color="inverse"
    )

with col2:
    st.metric(
        label="Economia Tributária Projetada",
        value=f"R$ {economia_tributaria:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        delta=f"FAP: {fap_atual:.2f} ➔ {fap_alvo:.2f}"
    )

with col3:
    st.metric(
        label="Custos Ocultos Estimados (Bird)",
        value=f"R$ {custos_indiretos_totais:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        delta=f"{total_acidentes} ocorrências",
        delta_color="off"
    )

with col4:
    potencial_total_recuperacao = economia_tributaria + (custos_indiretos_totais * 0.50)
    st.metric(
        label="Potencial Total de Retorno (SST)",
        value=f"R$ {potencial_total_recuperacao:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        delta="Economia + Mitigação"
    )

st.markdown("---")

# Seção de Gráficos Executivos (Visual compatível com Dark e Light mode)
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("📊 Comparativo de Cenários Tributários (RAT Anual)")
    
    df_cenarios = pd.DataFrame({
        "Cenário": ["Melhor Caso (FAP 0.5)", "Meta Projetada (Gestão SST)", "Cenário Atual", "Pior Caso (FAP 2.0)"],
        "Custo_R$": [custo_rat_minimo, custo_rat_alvo, custo_rat_atual, custo_rat_maximo],
        "Rotulo": [
            f"R$ {custo_rat_minimo/1000:.0f}k",
            f"R$ {custo_rat_alvo/1000:.0f}k",
            f"R$ {custo_rat_atual/1000:.0f}k",
            f"R$ {custo_rat_maximo/1000:.0f}k"
        ]
    })
    
    cores = ["#16A34A", "#0284C7", "#D97706", "#DC2626"]
    
    fig_bar = px.bar(
        df_cenarios,
        x="Cenário",
        y="Custo_R$",
        text="Rotulo",
        color="Cenário",
        color_discrete_sequence=cores
    )
    
    fig_bar.update_traces(
        textposition="outside",
        textfont=dict(size=14, color="#E2E8F0", family="Arial Black")
    )
    
    fig_bar.update_layout(
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94A3B8", size=13),
        xaxis=dict(
            tickfont=dict(color="#CBD5E1", size=11),
            title=None,
            showgrid=False
        ),
        yaxis=dict(
            tickfont=dict(color="#CBD5E1", size=12),
            title=dict(text="Custo Anual em R$", font=dict(color="#CBD5E1")),
            showgrid=True,
            gridcolor="#334155"
        ),
        margin=dict(t=30, l=10, r=10, b=40)
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)

with col_g2:
    st.subheader("🎯 Composição das Perdas por Ocorrências (Bird)")
    
    df_pizza = pd.DataFrame({
        "Tipo": ["Custos Ocultos (Paradas, Perícias e Treinamento)", "Custos Diretos (Médicos/Hospitalares)"],
        "Valor": [custos_indiretos_totais, custos_diretos_totais]
    })
    
    fig_donut = px.pie(
        df_pizza,
        names="Tipo",
        values="Valor",
        hole=0.55,
        color_discrete_sequence=["#EA580C", "#64748B"]
    )
    
    fig_donut.update_traces(
        textinfo="percent",
        textfont=dict(size=14, color="#FFFFFF", family="Arial Black"),
        marker=dict(line=dict(color='#0F172A', width=2))
    )
    
    fig_donut.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94A3B8", size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(color="#CBD5E1", size=11)
        ),
        margin=dict(t=30, l=10, r=10, b=50)
    )
    
    st.plotly_chart(fig_donut, use_container_width=True)

st.markdown("---")

# Seção de Compartilhamento via WhatsApp (Texto Completo e Codificado)
st.subheader("📲 Compartilhar Diagnóstico Executivo")

msg_whatsapp = f"""*RELATÓRIO DE ENGENHARIA ECONÔMICA & SST* 📊
----------------------------------------
🏢 *Diagnóstico Financeiro de FAP/RAT e Ocorrências*

💰 *Folha Salarial Anual:* R$ {folha_anual:,.2f}
📉 *FAP Vigente:* {fap_atual:.2f} ➔ *FAP Alvo Proposto:* {fap_alvo:.2f}

📌 *RESULTADOS APURADOS:*
• Custo Anual RAT Atual: R$ {custo_rat_atual:,.2f}
• Economia Tributária Potencial: R$ {economia_tributaria:,.2f}/ano
• Custos Indiretos/Ocultos Estimados: R$ {custos_indiretos_totais:,.2f}
• *Potencial Total de Retorno (SST): R$ {potencial_total_recuperacao:,.2f}*

Simulação realizada via: https://simulador-custos-sst.streamlit.app
Consultoria Técnica: Daniel Martins (Engenheiro de Segurança do Trabalho)
""".replace(",", "X").replace(".", ",").replace("X", ".")

link_whatsapp = f"https://api.whatsapp.com/send?text={urllib.parse.quote_plus(msg_whatsapp)}"

st.markdown(
    f"""
    <a href="{link_whatsapp}" target="_blank" style="text-decoration:none;">
        <button style="
            background-color: #25D366;
            color: white;
            border: none;
            padding: 14px 28px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        ">
            📲 Compartilhar Sumário Executivo com Diretoria / Financeiro via WhatsApp
        </button>
    </a>
    """,
    unsafe_allow_html=True
)

