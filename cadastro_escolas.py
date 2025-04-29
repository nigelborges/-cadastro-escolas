import streamlit as st
import pandas as pd
import os

# Arquivo de saída
OUTPUT_FILE = 'escolas.csv'

# Usuário e senha fixos
USUARIO_VALIDO = 'admin'
SENHA_VALIDA = '1234'

# Dados na memória
dados = []

# Funções para manipulação dos dados
def salvar_csv():
    df = pd.DataFrame(dados)
    if os.path.exists(OUTPUT_FILE):
        df_existente = pd.read_csv(OUTPUT_FILE)
        df = pd.concat([df_existente, df], ignore_index=True)
    df.to_csv(OUTPUT_FILE, index=False)

def gerar_dados(nome_escola, endereco, num_salas, candidatos_info, blocos_info, andares_info):
    global dados
    id_escola = (max([d['ID Escola'] for d in dados]) + 1) if dados else 1
    for i in range(1, num_salas + 1):
        num_candidatos = candidatos_info[i-1]
        for candidato_ordem in range(1, num_candidatos + 1):
            registro = {
                'ID Escola': id_escola,
                'Nome Escola': nome_escola,
                'Endereco': endereco,
                'ID Sala': i,
                'Bloco': blocos_info[i-1],
                'Andar': andares_info[i-1],
                'Ordem da Sala': i,
                'Numero de Salas': num_salas,
                'Candidatos por Sala': num_candidatos,
                'Ordem do Candidato': candidato_ordem
            }
            dados.append(registro)

# Inicializa o app
if __name__ == "__main__":
    st.set_page_config(page_title="Cadastro de Escolas", layout="centered")
    st.title("Sistema de Cadastro de Escolas e Salas")

    if os.path.exists(OUTPUT_FILE):
        df_existente = pd.read_csv(OUTPUT_FILE)
        dados = df_existente.to_dict('records')

    if 'logado' not in st.session_state:
        st.session_state['logado'] = False

    if not st.session_state['logado']:
        st.subheader("Login")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if usuario == USUARIO_VALIDO and senha == SENHA_VALIDA:
                st.session_state['logado'] = True
                st.success("Login realizado com sucesso!")
            else:
                st.error("Usuário ou senha incorretos.")
    else:
        with st.form("form_cadastro"):
            nome_escola = st.text_input("Nome da Escola")
            endereco = st.text_input("Endereço")
            num_salas = st.number_input("Quantidade de Salas", min_value=1, step=1)

            opcoes = st.radio("Todas as salas têm o mesmo número de candidatos, bloco e andar?", ("Sim", "Não"))

            candidatos_info = []
            blocos_info = []
            andares_info = []

            if opcoes == "Sim":
                candidatos_unico = st.number_input("Candidatos por Sala", min_value=1, step=1)
                bloco_unico = st.text_input("Bloco", value="A")
                andar_unico = st.number_input("Andar", min_value=1, step=1)
                if st.form_submit_button("Cadastrar Escola"):
                    candidatos_info = [candidatos_unico] * num_salas
                    blocos_info = [bloco_unico] * num_salas
                    andares_info = [andar_unico] * num_salas
                    gerar_dados(nome_escola, endereco, num_salas, candidatos_info, blocos_info, andares_info)
                    salvar_csv()
                    st.success(f"Escola cadastrada com sucesso! ({num_salas} salas)")
            else:
                for i in range(1, num_salas + 1):
                    st.markdown(f"### Sala {i}")
                    candidatos = st.number_input(f"Candidatos Sala {i}", min_value=1, step=1, key=f"cand_{i}")
                    bloco = st.text_input(f"Bloco Sala {i}", value="A", key=f"bloco_{i}")
                    andar = st.number_input(f"Andar Sala {i}", min_value=1, step=1, key=f"andar_{i}")
                    candidatos_info.append(candidatos)
                    blocos_info.append(bloco)
                    andares_info.append(andar)
                if st.form_submit_button("Cadastrar Escola"):
                    gerar_dados(nome_escola, endereco, num_salas, candidatos_info, blocos_info, andares_info)
                    salvar_csv()
                    st.success(f"Escola cadastrada com sucesso! ({num_salas} salas)")

        if dados:
            st.subheader("Candidatos Cadastrados")
            df = pd.DataFrame(dados)
            st.dataframe(df)
            st.download_button(
                label="Baixar CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name='escolas.csv',
                mime='text/csv'
            )

        if st.button("Sair"):
            st.session_state['logado'] = False
            st.experimental_rerun()
