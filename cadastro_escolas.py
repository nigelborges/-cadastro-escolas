import streamlit as st
import pandas as pd
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

def form_escola():
    st.markdown("# Cadastro de Escola")
    editar_id = st.session_state.get("escola_em_edicao")
    nome = ""
    endereco = ""
    num_salas = 1
    salas_existentes = []

    if editar_id:
        conn = conectar()
        escola = pd.read_sql_query("SELECT * FROM escolas WHERE id = ?", conn, params=(editar_id,)).iloc[0]
        nome = escola['nome']
        endereco = escola['endereco']
        salas_existentes = pd.read_sql_query("SELECT * FROM salas WHERE escola_id = ?", conn, params=(editar_id,)).to_dict("records")
        num_salas = len(salas_existentes)
        conn.close()

    nome = st.text_input("Nome da Escola", value=nome)
    endereco = st.text_input("Endereço", value=endereco)
    num_salas = st.number_input("Quantidade de Salas", min_value=1, step=1, value=num_salas)
    tipo = st.radio("Todas as salas têm os mesmos dados?", ["Sim", "Não"], index=0 if not salas_existentes else 1)

    salas = []
    if tipo == "Sim":
        base_nome = st.text_input("Nome base da Sala", value="Sala")
        bloco = st.text_input("Bloco", value="A")
        andar = st.text_input("Andar", value="Térreo")
        candidatos = st.number_input("Candidatos por Sala", min_value=1, step=1, value=40)
        for i in range(int(num_salas)):
            salas.append({
                "nome_sala": f"{base_nome} {i+1:02d}",
                "bloco": bloco,
                "andar": andar,
                "candidatos_sala": candidatos
            })
    else:
        if salas_existentes:
            df_salas = pd.DataFrame(salas_existentes)[['nome_sala', 'bloco', 'andar', 'candidatos_sala']]
        else:
            df_salas = pd.DataFrame([{
                "nome_sala": f"Sala {i+1:02d}",
                "bloco": "A",
                "andar": "Térreo",
                "candidatos_sala": 40
            } for i in range(int(num_salas))])
        st.markdown("### Cadastro das Salas")
        df_editada = st.data_editor(df_salas, num_rows="dynamic", key="editor_salas")
        salas = df_editada.to_dict("records")

    if st.button("Salvar Alterações" if editar_id else "Salvar Cadastro"):
        if not nome or not endereco or any(not sala['nome_sala'] for sala in salas):
            st.warning("Todos os campos são obrigatórios.")
        else:
            salvar_escola_banco(nome, endereco, salas, editar_id=editar_id)
            st.success("Escola atualizada com sucesso!" if editar_id else "Escola cadastrada com sucesso!")
            st.session_state['modo_edicao'] = False
            st.session_state['escola_em_edicao'] = None

def login():
    st.markdown("# Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario == USUARIO_VALIDO and senha == SENHA_VALIDA:
            st.session_state['logado'] = True
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos")

def mostrar_menu():
    st.sidebar.title("Menu")
    opcao = st.sidebar.radio("Navegação", ["Cadastrar Escola", "Sair"], index=0)
    if opcao == "Cadastrar Escola":
        form_escola()
    elif opcao == "Sair":
        st.session_state['logado'] = False
        st.experimental_rerun()

if __name__ == '__main__':
    st.set_page_config(page_title="Sistema Escolar - Acesso", layout="centered")
    if not st.session_state['logado']:
        login()
    else:
        mostrar_menu()
