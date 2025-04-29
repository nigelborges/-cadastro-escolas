import streamlit as st
import pandas as pd
import os

OUTPUT_FILE = 'escolas.csv'
USUARIO_VALIDO = 'admin'
SENHA_VALIDA = '1234'

if 'logado' not in st.session_state:
    st.session_state['logado'] = False

def carregar_dados():
    if os.path.exists(OUTPUT_FILE):
        return pd.read_csv(OUTPUT_FILE)
    return pd.DataFrame(columns=[
        'ID Escola', 'Nome Escola', 'Endereco', 'ID Sala', 'Nome da Sala', 'Bloco', 'Andar',
        'Ordem da Sala', 'Numero de Salas', 'Ordem do Candidato'
    ])

def salvar_dados(df_novo):
    if os.path.exists(OUTPUT_FILE):
        df_existente = pd.read_csv(OUTPUT_FILE)
        df = pd.concat([df_existente, df_novo], ignore_index=True)
    else:
        df = df_novo
    df.to_csv(OUTPUT_FILE, index=False)

def gerar_candidatos(id_escola, nome, endereco, num_salas, candidatos_info, blocos_info, andares_info):
    linhas = []
    for i in range(1, num_salas + 1):
        for ordem_candidato in range(1, candidatos_info[i-1] + 1):
            linha = {
                'ID Escola': id_escola,
                'Nome Escola': nome,
                'Endereco': endereco,
                'ID Sala': i,
                'Nome da Sala': f"Sala {i:02d}",
                'Bloco': blocos_info[i-1],
                'Andar': andares_info[i-1],
                'Ordem da Sala': i,
                'Numero de Salas': num_salas,
                'Ordem do Candidato': ordem_candidato
            }
            linhas.append(linha)
    return pd.DataFrame(linhas)

def form_escola():
    st.image('https://www.idecan.org.br/assets/img/logo.png', use_column_width=True)
    st.markdown("""<h1 style='text-align: center; color: #0E4D92;'>Sistema de Cadastro de Escolas</h1>""", unsafe_allow_html=True)
    st.markdown("""<hr style='border:1px solid #0E4D92'>""", unsafe_allow_html=True)
    
    with st.form("formulario_cadastro"):
        st.subheader("Cadastro de Escola")
        nome = st.text_input("Nome da Escola")
        endereco = st.text_input("Endereço")
        num_salas = st.number_input("Quantidade de Salas", min_value=1, step=1)

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

        submit = st.form_submit_button("Salvar Cadastro")
        if submit:
            df = carregar_dados()
            id_escola = df['ID Escola'].max() + 1 if not df.empty else 1
            nova_escola = gerar_candidatos(id_escola, nome, endereco, num_salas, candidatos_info, blocos_info, andares_info)
            salvar_dados(nova_escola)
            st.success("Escola cadastrada com sucesso!")


def mostrar_escolas():
    st.image('https://www.idecan.org.br/assets/img/logo.png', use_column_width=True)
    st.markdown("""<h1 style='text-align: center; color: #0E4D92;'>Escolas Cadastradas</h1>""", unsafe_allow_html=True)
    st.markdown("""<hr style='border:1px solid #0E4D92'>""", unsafe_allow_html=True)
    
    df = carregar_dados()
    if df.empty:
        st.info("Nenhuma escola cadastrada.")
        return
    for id_escola in sorted(df['ID Escola'].unique()):
        escola_df = df[df['ID Escola'] == id_escola]
        with st.expander(f"{escola_df['Nome Escola'].iloc[0]} - ID {id_escola}"):
            st.dataframe(escola_df)
            if st.button(f"Excluir ID {id_escola}"):
                excluir_escola(id_escola)

def excluir_escola(id_escola):
    df = carregar_dados()
    df = df[df['ID Escola'] != id_escola]
    df.to_csv(OUTPUT_FILE, index=False)
    st.success("Escola excluída com sucesso!")


def login():
    st.image('https://www.idecan.org.br/assets/img/logo.png', use_column_width=True)
    st.markdown("""<h1 style='text-align: center; color: #0E4D92;'>Login</h1>""", unsafe_allow_html=True)
    st.markdown("""<hr style='border:1px solid #0E4D92'>""", unsafe_allow_html=True)
    
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario == USUARIO_VALIDO and senha == SENHA_VALIDA:
            st.session_state['logado'] = True
        else:
            st.error("Usuário ou senha incorretos")

if __name__ == '__main__':
    st.set_page_config(page_title="Cadastro Escolar Avançado", layout="centered")

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
