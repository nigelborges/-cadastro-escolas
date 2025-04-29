import streamlit as st
import pandas as pd
import os

OUTPUT_FILE = 'escolas.csv'
USUARIO_VALIDO = 'admin'
SENHA_VALIDA = '1234'

if 'logado' not in st.session_state:
    st.session_state['logado'] = False
if 'modo_edicao' not in st.session_state:
    st.session_state['modo_edicao'] = False
if 'escola_em_edicao' not in st.session_state:
    st.session_state['escola_em_edicao'] = None

def carregar_dados():
    if os.path.exists(OUTPUT_FILE):
        return pd.read_csv(OUTPUT_FILE)
    return pd.DataFrame(columns=[
        'ID Escola', 'Nome Escola', 'Endereco', 'ID Sala', 'Bloco', 'Andar',
        'Ordem da Sala', 'Numero de Salas', 'Candidatos por Sala', 'Ordem do Candidato'])

def salvar_dados(df):
    df.to_csv(OUTPUT_FILE, index=False)

def gerar_candidatos(id_escola, nome, endereco, num_salas, candidatos_info, blocos_info, andares_info):
    linhas = []
    for i in range(1, num_salas + 1):
        for c in range(1, candidatos_info[i-1] + 1):
            linhas.append({
                'ID Escola': id_escola,
                'Nome Escola': nome,
                'Endereco': endereco,
                'ID Sala': i,
                'Bloco': blocos_info[i-1],
                'Andar': andares_info[i-1],
                'Ordem da Sala': i,
                'Numero de Salas': num_salas,
                'Candidatos por Sala': candidatos_info[i-1],
                'Ordem do Candidato': c
            })
    return pd.DataFrame(linhas)

def form_escola():
    st.subheader("Cadastro de Escola")
    nome = st.text_input("Nome da Escola")
    endereco = st.text_input("Endereço")
    num_salas = st.number_input("Quantidade de Salas", min_value=1, step=1, key='num_salas')

    tipo = st.radio("Todas as salas têm mesmos dados?", ["Sim", "Não"])

    candidatos_info, blocos_info, andares_info = [], [], []

    if tipo == "Sim":
        candidatos = st.number_input("Candidatos por Sala", min_value=1, step=1)
        bloco = st.text_input("Bloco", value="A")
        andar = st.number_input("Andar", min_value=1, step=1)
        candidatos_info = [candidatos] * num_salas
        blocos_info = [bloco] * num_salas
        andares_info = [andar] * num_salas
    else:
        for i in range(1, num_salas + 1):
            st.markdown(f"#### Sala {i}")
            candidatos = st.number_input(f"Candidatos Sala {i}", min_value=1, step=1, key=f"cand_{i}")
            bloco = st.text_input(f"Bloco Sala {i}", value="A", key=f"bloco_{i}")
            andar = st.number_input(f"Andar Sala {i}", min_value=1, step=1, key=f"andar_{i}")
            candidatos_info.append(candidatos)
            blocos_info.append(bloco)
            andares_info.append(andar)

    if st.button("Salvar Cadastro"):
        df = carregar_dados()
        id_escola = df['ID Escola'].max() + 1 if not df.empty else 1
        nova_escola = gerar_candidatos(id_escola, nome, endereco, num_salas, candidatos_info, blocos_info, andares_info)
        df = pd.concat([df, nova_escola], ignore_index=True)
        salvar_dados(df)
        st.success("Escola cadastrada com sucesso!")
        st.experimental_rerun()

def excluir_escola(id_escola):
    df = carregar_dados()
    df = df[df['ID Escola'] != id_escola]
    salvar_dados(df)
    st.success("Escola excluída com sucesso!")
    st.experimental_rerun()

def mostrar_escolas():
    df = carregar_dados()
    for id_escola in sorted(df['ID Escola'].unique()):
        escola_df = df[df['ID Escola'] == id_escola]
        with st.expander(f"{escola_df['Nome Escola'].iloc[0]} - ID {id_escola}"):
            st.dataframe(escola_df)
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Excluir ID {id_escola}"):
                    excluir_escola(id_escola)
            with col2:
                st.markdown("(Editar: versão futura)")

def login():
    st.title("Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario == USUARIO_VALIDO and senha == SENHA_VALIDA:
            st.session_state['logado'] = True
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos")

if __name__ == '__main__':
    st.set_page_config(page_title="Cadastro Escolar Avançado")

    if not st.session_state['logado']:
        login()
    else:
        st.sidebar.title("Menu")
        op = st.sidebar.radio("Navegação", ["Cadastrar Escola", "Visualizar Escolas", "Baixar CSV", "Sair"])

        if op == "Cadastrar Escola":
            form_escola()

        elif op == "Visualizar Escolas":
            mostrar_escolas()

        elif op == "Baixar CSV":
            df = carregar_dados()
            st.download_button("Baixar Arquivo CSV", df.to_csv(index=False).encode('utf-8'), "escolas.csv")

        elif op == "Sair":
            st.session_state['logado'] = False
            st.experimental_rerun()
