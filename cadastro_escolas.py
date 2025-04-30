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

def exportar_dados():
    df_escolas = carregar_escolas()
    frames = []
    for _, row in df_escolas.iterrows():
        df_salas = carregar_salas_por_escola(row['id'])
        df_salas['Nome Escola'] = row['nome']
        df_salas['Endereco'] = row['endereco']
        for _, sala in df_salas.iterrows():
            for ordem in range(1, sala['candidatos_sala'] + 1):
                frames.append({
                    'Nome Escola': sala['Nome Escola'],
                    'Endereco': sala['Endereco'],
                    'Nome da Sala': sala['nome_sala'],
                    'Bloco': sala['bloco'],
                    'Andar': sala['andar'],
                    'Ordem da Sala': sala['ordem_sala'],
                    'Numero de Salas': len(df_salas),
                    'Ordem do Candidato': ordem
                })
    return pd.DataFrame(frames)

def form_escola():
    st.image('https://www.idecan.org.br/assets/img/logo.png', use_container_width=True)
    st.markdown("""<h1 style='text-align: center; color: #0E4D92;'>Cadastro de Escola</h1>""", unsafe_allow_html=True)
    st.markdown("""<hr style='border:1px solid #0E4D92'>""", unsafe_allow_html=True)

    editar_id = st.session_state.get("escola_em_edicao")
    nome = ""
    endereco = ""
    num_salas = 1
    salas_existentes = []

    if editar_id:
        df_escolas = carregar_escolas()
        escola = df_escolas[df_escolas['id'] == editar_id].iloc[0]
        nome = escola['nome']
        endereco = escola['endereco']
        salas_existentes = carregar_salas_por_escola(editar_id).to_dict("records")
        num_salas = len(salas_existentes)

    with st.container():
        nome = st.text_input("Nome da Escola", value=nome)
        endereco = st.text_input("Endereço", value=endereco)
        num_salas = st.number_input("Quantidade de Salas", min_value=1, step=1, value=num_salas)
        tipo = st.radio("Todas as salas têm os mesmos dados?", ["Sim", "Não"], index=0 if not salas_existentes else 1)

    salas = []
    if tipo == "Sim":
        col1, col2 = st.columns(2)
        with col1:
            base_nome = st.text_input("Nome base da Sala", value="Sala")
            bloco = st.text_input("Bloco", value="A")
        with col2:
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

    col_salvar, _ = st.columns(2)
    with col_salvar:
        if st.button("💾 Salvar Alterações" if editar_id else "✅ Salvar Cadastro", use_container_width=True):
            if not nome or not endereco or any(not sala['nome_sala'] for sala in salas):
                st.warning("Todos os campos são obrigatórios.")
            else:
                salvar_escola_banco(nome, endereco, salas, editar_id=editar_id)
                st.success("Escola atualizada com sucesso!" if editar_id else "Escola cadastrada com sucesso!")
                st.session_state['modo_edicao'] = False
                st.session_state['escola_em_edicao'] = None

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
                    st.experimental_rerun()
            with col3:
                df_exportar = exportar_dados()
                st.download_button("📁 Exportar CSV", df_exportar.to_csv(index=False).encode('utf-8'), "escolas_export.csv")

def login():
    st.image('https://www.idecan.org.br/assets/img/logo.png', use_container_width=True)
    st.markdown("""<h1 style='text-align: center; color: #0E4D92;'>Login</h1>""", unsafe_allow_html=True)
    st.markdown("""<hr style='border:1px solid #0E4D92'>""", unsafe_allow_html=True)

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("🔐 Entrar"):
        if usuario == USUARIO_VALIDO and senha == SENHA_VALIDA:
            st.session_state['logado'] = True
        else:
            st.error("Usuário ou senha incorretos")

if __name__ == '__main__':
    st.set_page_config(page_title="Cadastro Escolar DB", layout="centered")

    if not st.session_state['logado']:
        login()
    else:
        st.sidebar.title("Menu")
        opcao = st.sidebar.radio("Navegação", ["Cadastrar Escola", "Visualizar Escolas", "Sair"],
                                 index=["Cadastrar Escola", "Visualizar Escolas", "Sair"].index(st.session_state['pagina_atual']))
        st.session_state['pagina_atual'] = opcao

        if opcao == "Cadastrar Escola":
            form_escola()
        elif opcao == "Visualizar Escolas":
            visualizar()
        elif opcao == "Sair":
            st.session_state['logado'] = False
