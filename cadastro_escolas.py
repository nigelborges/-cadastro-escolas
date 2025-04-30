import streamlit as st
import pandas as pd
import os
import sqlite3

DB_FILE = 'escolas.db'
USUARIO_VALIDO = 'admin'
SENHA_VALIDA = '1234'

if 'logado' not in st.session_state:
    st.session_state['logado'] = False
if 'modo_edicao' not in st.session_state:
    st.session_state['modo_edicao'] = False
if 'escola_em_edicao' not in st.session_state:
    st.session_state['escola_em_edicao'] = None
if 'pagina_atual' not in st.session_state:
    st.session_state['pagina_atual'] = 'Cadastrar Escola'

def conectar():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS escolas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            endereco TEXT NOT NULL
        )""")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS salas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            escola_id INTEGER,
            nome_sala TEXT,
            bloco TEXT,
            andar TEXT,
            ordem_sala INTEGER,
            candidatos_sala INTEGER,
            ordem_candidato INTEGER,
            FOREIGN KEY (escola_id) REFERENCES escolas(id)
        )""")
    return conn

def salvar_escola_banco(nome, endereco, salas, editar_id=None):
    conn = conectar()
    cur = conn.cursor()
    if editar_id:
        cur.execute("DELETE FROM salas WHERE escola_id = ?", (editar_id,))
        cur.execute("UPDATE escolas SET nome = ?, endereco = ? WHERE id = ?", (nome, endereco, editar_id))
        escola_id = editar_id
    else:
        cur.execute("INSERT INTO escolas (nome, endereco) VALUES (?, ?)", (nome, endereco))
        escola_id = cur.lastrowid
    for i, sala in enumerate(salas):
        cur.execute("""
            INSERT INTO salas (
                escola_id, nome_sala, bloco, andar, ordem_sala, candidatos_sala, ordem_candidato
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (escola_id, sala['nome_sala'], sala['bloco'], sala['andar'], i + 1, sala['candidatos_sala'], 1))
    conn.commit()
    conn.close()

def carregar_escolas():
    conn = conectar()
    df_escolas = pd.read_sql_query("SELECT * FROM escolas", conn)
    conn.close()
    return df_escolas

def carregar_salas_por_escola(escola_id):
    conn = conectar()
    df_salas = pd.read_sql_query("SELECT * FROM salas WHERE escola_id = ?", conn, params=(escola_id,))
    conn.close()
    return df_salas

def excluir_escola(escola_id):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM salas WHERE escola_id = ?", (escola_id,))
    cur.execute("DELETE FROM escolas WHERE id = ?", (escola_id,))
    conn.commit()
    conn.close()

def exportar_dados_por_escola(escola_id):
    df_escolas = carregar_escolas()
    escola = df_escolas[df_escolas['id'] == escola_id].iloc[0]
    df_salas = carregar_salas_por_escola(escola_id)
    candidatos = []
    id_sala_counter = 1
    sala_ids = {}
    for _, sala in df_salas.iterrows():
        nome = sala['nome_sala']
        if nome not in sala_ids:
            sala_ids[nome] = id_sala_counter
            id_sala_counter += 1
        id_sala = sala_ids[nome]
        for ordem in range(1, sala['candidatos_sala'] + 1):
            candidatos.append({
                'ID Escola': escola['id'],
                'Nome Escola': escola['nome'],
                'Endereco': escola['endereco'],
                'ID Sala': id_sala,
                'Nome da Sala': sala['nome_sala'],
                'Bloco': sala['bloco'],
                'Andar': sala['andar'],
                'Ordem da Sala': sala['ordem_sala'],
                'Numero de Salas': len(df_salas),
                'Ordem do Candidato': ordem
            })
    return pd.DataFrame(candidatos)

def visualizar():
    st.markdown("# Escolas Cadastradas")
    df = carregar_escolas()
    if df.empty:
        st.info("Nenhuma escola cadastrada.")
        return
    for _, row in df.iterrows():
        with st.expander(f"🏫 {row['nome']} - {row['endereco']}"):
            st.write(f"ID: {row['id']}")
            df_salas = carregar_salas_por_escola(row['id'])
            st.dataframe(df_salas)
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"✏️ Editar ID {row['id']}"):
                    st.session_state['modo_edicao'] = True
                    st.session_state['escola_em_edicao'] = row['id']
                    st.session_state['pagina_atual'] = "Cadastrar Escola"
            with col2:
                if st.button(f"🗑️ Excluir ID {row['id']}"):
                    excluir_escola(row['id'])
                    st.rerun()
            with col3:
                if st.button(f"📁 Exportar CSV {row['id']}", key=f"botao_exportar_{row['id']}"):
                    df_exportar = exportar_dados_por_escola(row['id'])
                    st.download_button(
                        "⬇️ Baixar CSV",
                        df_exportar.to_csv(index=False).encode('utf-8'),
                        file_name=f"escola_{row['id']}.csv",
                        key=f"download_{row['id']}"
                    )
