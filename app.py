import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import locale

# Título dinâmico por mês
try:
    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
except:
    pass
mes_atual = datetime.now().strftime("%B").upper()

st.set_page_config(page_title=f"Study Quest - {mes_atual}", page_icon="🎯", layout="wide")

# --- CONEXÃO COM GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    # ttl=0 garante que ele busque o dado fresco sempre que atualizar
    return conn.read(ttl=0)

df = carregar_dados()

# --- CÁLCULOS DE METAS ---
entrega_atual = df[df['status'] == True]['pontos_entrega'].sum()
entrega_total = 120 # Meta fixa conforme seu plano
nota_atual = df['nota'].sum()
nota_minima_req = 35.0

# --- INTERFACE VISUAL ---
st.title(f"🚀 STUDY QUEST // {mes_atual}")

c1, c2, c3 = st.columns(3)
c1.metric("PONTOS DE ENTREGA", f"{entrega_atual} / {entrega_total}")
c2.metric("QUALIDADE ACUMULADA", f"{nota_atual:.1f} / 50.0")
c3.metric("STATUS", "LIBERADO" if (entrega_atual >= 120 and nota_atual >= 35) else "BLOQUEADO")

# Barras de Progresso
st.write("### 📊 Progresso da Jornada")
st.progress(min(entrega_atual / entrega_total, 1.0))
st.caption(f"Faltam {max(entrega_total - entrega_atual, 0)} pontos de entrega")

st.progress(min(nota_atual / 50.0, 1.0))
st.caption(f"Faltam {max(nota_minima_req - nota_atual, 0.0):.1f} pontos de nota para a média 7")

if entrega_atual >= 120 and nota_atual >= 35:
    st.balloons()
    st.success("💰 RECOMPENSA DESBLOQUEADA!")

st.divider()

# --- MURAL DE MISSÕES ---
for index, row in df.iterrows():
    with st.expander(f"{'✅' if row['status'] else '👾'} {row['tarefa']} — {row['pontos_entrega']} pts"):
        st.write(f"**TEMA:** {row['tema']}")
        st.write(f"**DETALHES:** {row['detalhes']}")
        if row['status']:
            st.info(f"Nota: {row['nota']}")

# --- PAINEL DO MENTOR (SIDEBAR) ---
with st.sidebar:
    st.header("🔐 Admin")
    senha = st.text_input("Senha", type="password")
    if senha == st.secrets["admin_password"]:
        tarefa_sel = st.selectbox("Editar Missão", df['tarefa'].tolist())
        idx = df[df['tarefa'] == tarefa_sel].index[0]
        
        new_tema = st.text_input("Novo Tema", df.at[idx, 'tema'])
        new_detalhes = st.text_area("Novos Detalhes", df.at[idx, 'detalhes'])
        new_status = st.checkbox("Entregue?", value=bool(df.at[idx, 'status']))
        new_nota = st.slider("Nota", 0.0, 10.0, float(df.at[idx, 'nota']))
        
        if st.button("💾 Salvar no Google Sheets"):
            # Atualiza o DataFrame local
            df.at[idx, 'tema'] = new_tema
            df.at[idx, 'detalhes'] = new_detalhes
            df.at[idx, 'status'] = new_status
            df.at[idx, 'nota'] = new_nota
            
            # Persiste no Google Sheets
            conn.update(data=df)
            st.success("Planilha Atualizada!")
            st.rerun()