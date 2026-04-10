import streamlit as st
from datetime import date
from fpdf import FPDF

st.set_page_config(page_title="Devoluções", layout="wide")
st.title("📦 Sistema de Devoluções")

# ==================== ESTADO ====================
if "motivos" not in st.session_state:
    st.session_state.motivos = ["Recusado", "Danificado", "Endereço incompleto", "Fora de rota", "Desconhecido", "Outro"]

if "itens" not in st.session_state:
    st.session_state.itens = []

# ==================== ABAS ====================
tab1, tab2 = st.tabs(["📋 Operação", "⚙️ Motivos"])

# ==================== ABA 1 ====================
with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        data_relatorio = st.date_input("Data", value=date.today())
    with col2:
        transportadora = st.text_input("Entregador", value="Honorio/Gabriel - Parque mambucaba")

    st.subheader("Adicionar item")

    with st.form("form_add", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns([1.5, 2, 3, 1.5])

        with c1:
            awb = st.text_input("AWB")
        with c2:
            cliente = st.text_input("Cliente")
        with c3:
            endereco = st.text_input("Endereço")
        with c4:
            tipo = st.selectbox("Tipo", ["CARD", "PCT"])

        motivo = st.selectbox("Motivo (opcional)", [""] + st.session_state.motivos)
        submit = st.form_submit_button("➕ Adicionar")

        if submit and awb.strip():
            st.session_state.itens.append({
                "AWB": awb.strip(),
                "Nome do Cliente": cliente.strip(),
                "Endereço": endereco.strip(),
                "Motivo": motivo.strip(),
                "Tipo": tipo
            })
            st.rerun()

    # --- LISTAGEM DE ITENS (DENTRO DA ABA 1) ---
    st.subheader(f"Itens ({len(st.session_state.itens)})")

    if not st.session_state.itens:
        st.info("Nenhum item adicionado.")
    else:
        for i, item in enumerate(st.session_state.itens):
            with st.expander(f"📦 {item.get('Tipo', 'PCT')} | {item.get('AWB', 'S/N')} - {item.get('Nome do Cliente','')}"):
                
                # Campo para editar o AWB
                item["AWB"] = st.text_input("AWB", value=item.get("AWB", ""), key=f"awb_edit_{i}")

                col_e1, col_e2 = st.columns([3, 1])
                with col_e1:
                    item["Nome do Cliente"] = st.text_input("Cliente", value=item.get("Nome do Cliente",""), key=f"cli_{i}")
                with col_e2:
                    opcoes_tipo = ["CARD", "PCT"]
                    t_idx = opcoes_tipo.index(item["Tipo"]) if item["Tipo"] in opcoes_tipo else 1
                    item["Tipo"] = st.selectbox("Tipo", opcoes_tipo, index=t_idx, key=f"tp_{i}")

                item["Endereço"] = st.text_area("Endereço", value=item.get("Endereço",""), key=f"end_{i}")

                m_lista = [""] + st.session_state.motivos
                m_idx = m_lista.index(item["Motivo"]) if item["Motivo"] in m_lista else 0
                item["Motivo"] = st.selectbox("Motivo", m_lista, index=m_idx, key=f"mot_{i}")

                if st.button("Remover Item", key=f"del_{i}"):
                    st.session_state.itens.pop(i)
                    st.rerun()

    # --- BOTÃO DE PDF (DENTRO DA ABA 1) ---
    if st.session_state.itens:
        st.divider()
        if st.button("Gerar PDF"):
            pdf = FPDF("P", "mm", "A4")
            pdf.add_page()
            
            pdf.set_font("helvetica", "B", 14)
            pdf.cell(0, 10, "RELATÓRIO DE DEVOLUÇÕES", ln=True, align="C")
            
            pdf.set_font("helvetica", "", 10)
            pdf.cell(0, 6, f"Entregador: {transportadora} | Data: {data_relatorio.strftime('%d/%m/%Y')}", ln=True, align="C")
            pdf.ln(5)

            w_awb, w_tipo, w_cli, w_end, w_mot = 35, 15, 45, 55, 40

            pdf.set_font("helvetica", "B", 8)
            pdf.set_fill_color(200, 200, 200)
            pdf.cell(w_awb, 8, "AWB", 1, 0, "C", True)
            pdf.cell(w_tipo, 8, "TIPO", 1, 0, "C", True)
            pdf.cell(w_cli, 8, "CLIENTE", 1, 0, "C", True)
            pdf.cell(w_end, 8, "ENDERECO", 1, 0, "C", True)
            pdf.cell(w_mot, 8, "MOTIVO", 1, 1, "C", True)

            pdf.set_font("helvetica", "", 8)
            for item in st.session_state.itens:
                txt_awb = str(item.get("AWB",""))
                txt_tipo = str(item.get("Tipo",""))
                txt_cli = str(item.get("Nome do Cliente","")).encode('latin-1', 'replace').decode('latin-1')
                txt_end = str(item.get("Endereço","")).encode('latin-1', 'replace').decode('latin-1')
                txt_mot = str(item.get("Motivo","")).encode('latin-1', 'replace').decode('latin-1')

                h = 6
                x, y = pdf.get_x(), pdf.get_y()
                
                pdf.multi_cell(w_awb, h, txt_awb, border=1)
                y_max = pdf.get_y()
                
                pdf.set_xy(x + w_awb, y)
                pdf.multi_cell(w_tipo, h, txt_tipo, border=1, align='C')
                y_max = max(y_max, pdf.get_y())
                
                pdf.set_xy(x + w_awb + w_tipo, y)
                pdf.multi_cell(w_cli, h, txt_cli, border=1)
                y_max = max(y_max, pdf.get_y())
                
                pdf.set_xy(x + w_awb + w_tipo + w_cli, y)
                pdf.multi_cell(w_end, h, txt_end, border=1)
                y_max = max(y_max, pdf.get_y())
                
                pdf.set_xy(x + w_awb + w_tipo + w_cli + w_end, y)
                pdf.multi_cell(w_mot, h, txt_mot, border=1)
                y_max = max(y_max, pdf.get_y())
                
                pdf.set_y(y_max)

            pdf_output = pdf.output(dest="S").encode("latin1")
            st.download_button("📥 Baixar Relatório PDF", pdf_output, "relatorio.pdf", "application/pdf")

# ==================== ABA 2 ====================
with tab2:
    st.subheader("Gerenciar Motivos")
    novo = st.text_input("Novo motivo")
    if st.button("Adicionar motivo"):
        if novo.strip() and novo not in st.session_state.motivos:
            st.session_state.motivos.append(novo.strip())
            st.rerun()

    for i, m in enumerate(st.session_state.motivos):
        c_m1, c_m2 = st.columns([5,1])
        c_m1.write(m)
        if c_m2.button("X", key=f"del_m_{i}"):
            st.session_state.motivos.pop(i)
            st.rerun()
