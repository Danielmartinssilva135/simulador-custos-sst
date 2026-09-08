# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import urllib.parse
import io
from datetime import date

# Importações do ReportLab para o relatório formal em PDF
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

st.set_page_config(
    page_title="Simulador Financeiro de SST: FAP, RAT e Custos Ocultos",
    page_icon="📊",
    layout="wide"
)

# Estilização visual customizada com contraste forçado
st.markdown("""
<style>
    [data-testid="stMetric"] {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        padding: 18px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.25) !important;
    }
    [data-testid="stMetricLabel"] p {
        color: #94A3B8 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    [data-testid="stMetricValue"] div {
        color: #F8FAFC !important;
        font-weight: 800 !important;
        font-size: 26px !important;
    }
</style>
""", unsafe_allow_html=True)

# Função Geradora do Laudo / Relatório Executivo em PDF
def gerar_relatorio_executivo_pdf(dados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    estilo_titulo = ParagraphStyle(
        'Titulo',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F172A'),
        alignment=0
    )
    
    estilo_sub = ParagraphStyle(
        'Subtitulo',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B'),
        alignment=0
    )
    
    estilo_secao = ParagraphStyle(
        'Secao',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0284C7'),
        alignment=0
    )
    
    estilo_corpo = ParagraphStyle(
        'Corpo',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#334155')
    )

    estilo_destaque = ParagraphStyle(
        'Destaque',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#16A34A')
    )

    estilo_rodape = ParagraphStyle(
        'Rodape',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#94A3B8'),
        alignment=1
    )

    story = []

    # Cabeçalho Executivo
    story.append(Paragraph("RELATÓRIO DE ENGENHARIA ECONÔMICA & IMPACTO FINANCEIRO EM SST", estilo_titulo))
    story.append(Paragraph(f"Diagnóstico Tributário FAP/RAT, Metodologia Bird e Potencial de Retorno • Emissão: {dados['data_emissao']}", estilo_sub))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284C7"), spaceAfter=15))

    # Seção 1: Dados Base da Operação
    story.append(Paragraph("1. PARÂMETROS DA OPERAÇÃO E CENÁRIO ATUAL", estilo_secao))
    story.append(Spacer(1, 8))
    
    tabela_base = [
        [Paragraph("<b>Folha Salarial Anual Bruta:</b>", estilo_corpo), Paragraph(f"R$ {dados['folha_anual']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), estilo_corpo)],
        [Paragraph("<b>Alíquota Base do RAT (CNAE):</b>", estilo_corpo), Paragraph(f"{dados['rat_base']*100:.1f}%", estilo_corpo)],
        [Paragraph("<b>FAP Atual da Empresa:</b>", estilo_corpo), Paragraph(f"{dados['fap_atual']:.2f}", estilo_corpo)],
        [Paragraph("<b>RAT Ajustado Atual (RAT × FAP):</b>", estilo_corpo), Paragraph(f"{dados['rat_ajustado_atual']*100:.2f}%", estilo_corpo)],
        [Paragraph("<b>Meta FAP Projetada (Gestão Ativa):</b>", estilo_corpo), Paragraph(f"<b>{dados['fap_alvo']:.2f}</b>", estilo_destaque)],
    ]
    t1 = Table(tabela_base, colWidths=[240, 290])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t1)
    story.append(Spacer(1, 18))

    # Seção 2: Apuração Tributária Previdenciária
    story.append(Paragraph("2. IMPACTO TRIBUTÁRIO PREVIDENCIÁRIO (FAP / RAT)", estilo_secao))
    story.append(Spacer(1, 8))

    tabela_trib = [
        [Paragraph("<b>Indicador Previdenciário</b>", estilo_corpo), Paragraph("<b>Valor Vigente / Atual</b>", estilo_corpo), Paragraph("<b>Cenário Otimizado</b>", estilo_corpo)],
        [Paragraph("Custo Anual RAT", estilo_corpo), Paragraph(f"R$ {dados['custo_rat_atual']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), estilo_corpo), Paragraph(f"R$ {dados['custo_rat_alvo']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), estilo_corpo)],
        [Paragraph("<b>Economia Tributária Líquida Anual</b>", estilo_corpo), Paragraph("-", estilo_corpo), Paragraph(f"<b>R$ {dados['economia_tributaria']:,.2f}</b>".replace(",", "X").replace(".", ",").replace("X", "."), estilo_destaque)]
    ]
    t2 = Table(tabela_trib, colWidths=[200, 165, 165])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t2)
    story.append(Spacer(1, 18))

    # Seção 3: Custos Ocultos e Perdas Indiretas (Bird)
    story.append(Paragraph("3. PERDAS INDIRETAS E CUSTOS OCULTOS (RATIO DE BIRD)", estilo_secao))
    story.append(Spacer(1, 8))

    tabela_bird = [
        [Paragraph("<b>Histórico de Ocorrências (12 meses):</b>", estilo_corpo), Paragraph(f"{dados['total_acid']} ocorrência(s) ({dados['acid_sem']} sem afastamento e {dados['acid_com']} com afastamento)", estilo_corpo)],
        [Paragraph("<b>Custos Diretos Estimados (Médico/Hospitalar):</b>", estilo_corpo), Paragraph(f"R$ {dados['custos_diretos']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), estilo_corpo)],
        [Paragraph("<b>Custos Ocultos / Indiretos Estimados:</b><br/><i>(Paradas, reposições, horas improdutivas e passivos)</i>", estilo_corpo), Paragraph(f"R$ {dados['custos_indiretos']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), estilo_corpo)],
    ]
    t3 = Table(tabela_bird, colWidths=[260, 270])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t3)
    story.append(Spacer(1, 18))

    # Seção 4: Conclusão e Parecer
    story.append(Paragraph("4. PARECER TÉCNICO E RETORNO SOBRE O INVESTIMENTO (ROI)", estilo_secao))
    story.append(Spacer(1, 8))

    parecer_texto = f"""
    A implementação de um plano estruturado de conformidade e mitigação de riscos (PGR, treinamentos normativos e controle de afastamentos) apresenta um <b>Potencial Total de Recuperação de R$ {dados['potencial_total']:,.2f}</b> por ano.
    <br/><br/>
    Cada R$ 1,00 investido na prevenção técnica em SST viabiliza retorno financeiro mensurável na preservação do caixa da companhia, blindando a organização contra perdas operacionais e recolhimentos tributários majorados no FAP.
    """.replace(",", "X").replace(".", ",").replace("X", ".")
    
    story.append(Paragraph(parecer_texto, estilo_corpo))
    story.append(Spacer(1, 35))

    # Assinatura
    tabela_assinatura = [
        [Paragraph("____________________________________________________________<br/><b>Daniel Martins</b><br/>Engenheiro de Segurança do Trabalho • Especialista em SST & Economia Ocupacional", estilo_rodape)]
    ]
    t_ass = Table(tabela_assinatura, colWidths=[530])
    t_ass.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(t_ass)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Título Principal do App
st.title("💼 Simulador Financeiro de SST: FAP, RAT e Retorno sobre Prevenção")
st.markdown("""
Quantifique o impacto dos acidentes e do FAP diretamente na folha de pagamento da sua empresa.
Converta indicadores técnicos de SST em valor econômico e gere o **Relatório Executivo Formal** para a Diretoria.
""")
st.markdown("---")

# Barra Lateral
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

# Cálculos Previdenciários
rat_ajustado_atual = rat_aliquota * fap_atual
rat_ajustado_alvo = rat_aliquota * fap_alvo
rat_ajustado_minimo = rat_aliquota * 0.50
rat_ajustado_maximo = rat_aliquota * 2.00

custo_rat_atual = folha_anual * rat_ajustado_atual
custo_rat_alvo = folha_anual * rat_ajustado_alvo
custo_rat_minimo = folha_anual * rat_ajustado_minimo
custo_rat_maximo = folha_anual * rat_ajustado_maximo

economia_tributaria = custo_rat_atual - custo_rat_alvo

# Metodologia Pirâmide de Bird
total_acidentes = acid_sem_afast + acid_com_afast
custos_diretos_totais = total_acidentes * custo_direto_medio
custos_indiretos_totais = custos_diretos_totais * 4.5

potencial_total_recuperacao = economia_tributaria + (custos_indiretos_totais * 0.50)

# Métricas Principais
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
    st.metric(
        label="Potencial Total de Retorno (SST)",
        value=f"R$ {potencial_total_recuperacao:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        delta="Economia + Mitigação"
    )

st.markdown("---")

# Gráficos
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

# Seção de Exportação Executiva (WhatsApp + Laudo em PDF)
st.subheader("📑 Exportação & Compartilhamento Executivo")

col_btn1, col_btn2 = st.columns(2)

# Botão 1: Laudo Formal em PDF
dados_relatorio_pdf = {
    "data_emissao": date.today().strftime("%d/%m/%Y"),
    "folha_anual": folha_anual,
    "rat_base": rat_aliquota,
    "fap_atual": fap_atual,
    "fap_alvo": fap_alvo,
    "rat_ajustado_atual": rat_ajustado_atual,
    "custo_rat_atual": custo_rat_atual,
    "custo_rat_alvo": custo_rat_alvo,
    "economia_tributaria": economia_tributaria,
    "total_acid": total_acidentes,
    "acid_sem": acid_sem_afast,
    "acid_com": acid_com_afast,
    "custos_diretos": custos_diretos_totais,
    "custos_indiretos": custos_indiretos_totais,
    "potencial_total": potencial_total_recuperacao
}

pdf_bytes = gerar_relatorio_executivo_pdf(dados_relatorio_pdf)

with col_btn1:
    st.download_button(
        label="📄 Baixar Relatório Executivo Formal (PDF)",
        data=pdf_bytes,
        file_name=f"Relatorio_Economia_SST_{date.today().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

# Botão 2: Envio Rápido via WhatsApp
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

with col_btn2:
    st.markdown(
        f"""
        <a href="{link_whatsapp}" target="_blank" style="text-decoration:none;">
            <button style="
                background-color: #25D366;
                color: white;
                border: none;
                padding: 11px 20px;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                cursor: pointer;
                width: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            ">
                📲 Compartilhar no WhatsApp
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )
