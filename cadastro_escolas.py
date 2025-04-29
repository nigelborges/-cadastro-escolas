import streamlit as st
import pandas as pd
import os

# Arquivo CSV de saída
OUTPUT_FILE = 'escolas_salas.csv'

# Dados na memória
dados = []

# Funções para manipulação dos dados
def salvar_csv():
    df = pd.DataFrame(dados)
    df.to_csv(OUTPUT_FILE, index=False)

def gerar_dados(nome_escola, endereco, num_salas, candidatos_por_sala):
    global dados
    id_escola = len(dados) // num_salas + 1
    for i in range(1, num_salas + 1):
        registro = {
            'ID Escola': id_escola,
            'Nome Escola': nome_escola,
            'Endereco': endereco,
            'ID Sala': i,
            'Bloco': 'A',
            'Andar': 1,
            'Ordem da Sala': i,
            'Numero de Salas': num_salas,
            'Candidatos por Sala': candidatos_por_sala
        }
        dados.append(registro)

# Inicializa o app
if __name__ == "__main__":
    st.set_page_config(page_title="Cadastro de Escolas", layout="centered")
    st.title("Cadastro de Escolas e Salas")

    if os.path.exists(OUTPUT_FILE):
        df_existente = pd.read_csv(OUTPUT_FILE)
        dados = df_existente.to_dict('records')

    with st.form("form_cadastro"):
        nome_escola = st.text_input("Nome da Escola")
        endereco = st.text_input("Endereço")
        num_salas = st.number_input("Quantidade de Salas", min_value=1, step=1)
        candidatos_por_sala = st.number_input("Candidatos por Sala", min_value=1, step=1)

        submitted = st.form_submit_button("Gerar Cadastro")

        if submitted:
            if not nome_escola or not endereco:
                st.error("Preencha todos os campos corretamente.")
            else:
                gerar_dados(nome_escola, endereco, num_salas, candidatos_por_sala)
                salvar_csv()
                st.success(f"Cadastro gerado com sucesso! ({num_salas} salas)")

    if dados:
        st.subheader("Cadastros Realizados")
        df = pd.DataFrame(dados)
        st.dataframe(df)
        st.download_button(
            label="Baixar CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name='escolas_salas.csv',
            mime='text/csv'
        )
