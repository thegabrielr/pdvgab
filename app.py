import streamlit as st
from datetime import date
from fpdf import FPDF
import json
import os

# Configuração da página
st.set_page_config(page_title="Devoluções - Histórico", layout="wide")

# ==================== FUNÇÕES DE PERSISTÊNCIA ====================
DB_FILE = "historico_devolucoes.json"

def salvar_dados():
    dados = {
        "itens": st.session_state.itens,
        "motivos": st.session_state.motivos
    }
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def carregar_dados():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# ==================== INICIALIZAÇÃO DO ESTADO ====================
dados_salvos = carregar_dados()

if "motivos" not in st.session_state:
    st.session_state.motivos = dados_salvos["motivos"] if dados_salvos else [
        "Recusado", "Danificado", "Endereço incompleto", "Fora de rota", "Desconhecido", "Outro"
    ]

if "itens" not in st.session_state:
    st.session_state.itens = dados_salvos["itens"] if dados_salvos else []

# ==================== TÍTULO E ABAS ====================
st.title("📦 Sistema de Devoluções com Histórico")

tab1, tab2 = st.tabs(["📋 Operação Atual", "⚙️ Configurações"])

# ==================== ABA 1: OPERAÇÃO ====================
with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        data_relatorio = st.date_input("Data", value=date.today())
    with col2:
        transportadora = st.text_input("Entregador", value="Honorio/Gabriel - Parque mambucaba")

    st.subheader("Adicionar item")
    with st.form("form_add", clear_on_submit=True):
        c1, c2, c3 = st.columns([1, 2, 3])
        with c1: awb = st.text_input("AWB")
        with c2: cliente = st.text_input("Cliente")
        with c3: endereco = st.text_input("CARD/NORMAL")
        
        motivo = st.selectbox("Motivo (opcional)", [""] + st.session_state.motivos)
        submit = st.form_submit_button("➕ Adicionar à Lista")

        if submit and awb.strip():
            st.session_state.itens.append({
                "AWB": awb.strip(),
                "Nome do Cliente": cliente.strip(),
                "Endereço": endereco.strip(),
                "Motivo": motivo.strip()
            })
            salvar_dados() # Salva no arquivo imediatamente
            st.rerun()

    st.divider()
    
    # Listagem de Itens
    st.subheader(f"Itens na Lista ({len(st.session_state.itens)})")
    
    if not st.session_state.itens:
        st.info("A lista está vazia.")
    else:
        # Loop de exibição e edição
        for i, item in enumerate(st.session_state.itens):
            with st.expander(f"📦 {item['AWB']} - {item.get('Nome do Cliente','')}"):
                col_ed1, col_ed2 = st.columns(2)
                
                with col_ed1:
                    new_cli = st.text_input("Cliente", value=item["Nome do Cliente"], key=f"cli_{i}")
                    new_end = st.text_area("Endereço", value=item["Endereço"], key=f"end_{i}")
                
                with col_ed2:
                    new_mot = st.selectbox("Motivo", [""] + st.session_state.motivos, 
                                         index=(st.session_state.motivos.index(item["Motivo"]) + 1) 
                                         if item["Motivo"] in st.session_state.motivos else 0,
                                         key=f"mot_{i}")
                    
                    if st.button("🗑️ Remover", key=f"del_{i}"):
                        st.session_state.itens.pop(i)
                        salvar_dados()
                        st.rerun()
                
                # Atualiza o estado se houver mudança
                if new_cli != item["Nome do Cliente"] or new_end != item["Endereço"] or new_mot != item["Motivo"]:
                    st.session_state.itens[i].update({"Nome do Cliente": new_cli, "Endereço": new_end, "Motivo": new_mot})
                    salvar_dados()

        # Ações da Lista
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("⚠️ Limpar Tudo", use_container_width=True):
                st.session_state.itens = []
                salvar_dados()
                st.rerun()

        # Geração do PDF
        with col_btn2:
            if st.button("📄 Gerar PDF", type="primary", use_container_width=True):
                pdf = FPDF("P", "mm", "A4")
                pdf.add_page()
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 8, "RELATÓRIO DE DEVOLUÇÕES", ln=True, align="C")
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 6, f"{transportadora} | {data_relatorio.strftime('%d/%m/%Y')}", ln=True, align="C")
                pdf.ln(5)

                # Cabeçalho da Tabela
                pdf.set_font("Arial", "B", 9)
                pdf.set_fill_color(220, 220, 220)
                w = [35, 50, 70, 35] # Larguras das colunas
                pdf.cell(w[0], 7, "AWB", 1, 0, "C", True)
                pdf.cell(w[1], 7, "CLIENTE", 1, 0, "C", True)
                pdf.cell(w[2], 7, "CARD/NORMAL", 1, 0, "C", True)
                pdf.cell(w[3], 7, "MOTIVO", 1, 1, "C", True)

                # Corpo da Tabela
                pdf.set_font("Arial", "", 8)
                for row in st.session_state.itens:
                    # Cálculo de altura dinâmica para evitar quebra de texto
                    x_start, y_start = pdf.get_x(), pdf.get_y()
                    pdf.multi_cell(w[0], 6, str(row['AWB']), border=1)
                    h = pdf.get_y() - y_start
                    
                    pdf.set_xy(x_start + w[0], y_start)
                    pdf.multi_cell(w[1], 6, str(row['Nome do Cliente']), border=1)
                    h = max(h, pdf.get_y() - y_start)

                    pdf.set_xy(x_start + w[0] + w[1], y_start)
                    pdf.multi_cell(w[2], 6, str(row['Endereço']), border=1)
                    h = max(h, pdf.get_y() - y_start)

                    pdf.set_xy(x_start + w[0] + w[1] + w[2], y_start)
                    pdf.multi_cell(w[3], 6, str(row['Motivo']), border=1)
                    h = max(h, pdf.get_y() - y_start)
                    
                    pdf.set_xy(x_start, y_start + h)

                try:
                    pdf_output = pdf.output(dest="S").encode("latin1")
                    st.download_button("📥 Baixar Relatório", pdf_output, 
                                     file_name=f"devolucao_{data_relatorio}.pdf", 
                                     mime="application/pdf", use_container_width=True)
                except Exception as e:
                    st.error("Erro ao gerar PDF: Caracteres especiais não suportados pelo Arial padrão.")

# ==================== ABA 2: MOTIVOS ====================
with tab2:
    st.subheader("Gerenciar Motivos de Devolução")
    novo = st.text_input("Novo motivo")
    if st.button("Adicionar motivo"):
        if novo.strip() and novo not in st.session_state.motivos:
            st.session_state.motivos.append(novo.strip())
            salvar_dados()
            st.rerun()

    for i, m in enumerate(st.session_state.motivos):
        c_m1, c_m2 = st.columns([5, 1])
        c_m1.write(m)
        if c_m2.button("X", key=f"del_m_{i}"):
            st.session_state.motivos.pop(i)
            salvar_dados()
            st.rerun()
