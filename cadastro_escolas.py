import streamlit as st
import pandas as pd
import os
import sqlite3

DB_FILE = 'escolas.db'
USUARIO_VALIDO = 'admin'
SENHA_VALIDA = '1234'


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

def login():
    st.image('https://www.idecan.org.br/assets/img/logo.png', use_container_width=True)
    st.markdown("""<h1 style='text-align: center; color: #0E4D92;'>Login</h1>""", unsafe_allow_html=True)
    st.markdown("""<hr style='border:1px solid #0E4D92'>""", unsafe_allow_html=True)

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("🔐 Entrar"):
        if usuario == USUARIO_VALIDO and senha == SENHA_VALIDA:
            st.session_state['logado'] = True
            st.success("Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")

def mostrar_menu():
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
        st.rerun()

# Garantir chave 'logado' inicializada
if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if __name__ == '__main__':
    st.set_page_config(page_title="Sistema Escolar - Acesso", layout="centered")
    if not st.session_state['logado']:
        login()
    else:
        mostrar_menu()
