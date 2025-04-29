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
if 'pagina_atual' not in st.session_state:
    st.session_state['pagina_atual'] = 'Cadastrar Escola'

def carregar_dados():
    if os.path.exists(OUTPUT_FILE):
        return pd.read_csv(OUTPUT_FILE)
    return pd.DataFrame(columns=[
        'ID Escola', 'Nome Escola', 'Endereco', 'ID Sala', 'Nome da Sala', 'Bloco', 'Andar',
        'Ordem da Sala', 'Numero de Salas', 'Ordem do Candidato'
    ])

def salvar_dados(df_novo, id_editar=None):
    if os.path.exists(OUTPUT_FILE):
        df_existente = pd.read_csv(OUTPUT_FILE)
        if id_editar is not None:
            nome_ref = df_novo['Nome Escola'].iloc[0]
            endereco_ref = df_novo['Endereco'].iloc[0]

            escola_antiga = df_existente[
                (df_existente['Nome Escola'] == nome_ref) &
                (df_existente['Endereco'] == endereco_ref)
            ]
            df_existente = df_existente[~(
                (df_existente['Nome Escola'] == nome_ref) &
                (df_existente['Endereco'] == endereco_ref)
            )]

            nomes_antigos = escola_antiga.drop_duplicates(subset='Nome da Sala')
            mapa_ids = {row['Nome da Sala']: row['ID Sala'] for _, row in nomes_antigos.iterrows()}
            usados = set()
            id_atual = 1
            for i, row in df_novo.iterrows():
                nome = row['Nome da Sala']
                if nome in mapa_ids:
                    novo_id = mapa_ids[nome]
                else:
                    while id_atual in usados or id_atual in mapa_ids.values():
                        id_atual += 1
                    novo_id = id_atual
                usados.add(novo_id)
                df_novo.at[i, 'ID Sala'] = novo_id
                df_novo.at[i, 'Ordem da Sala'] = novo_id

        df = pd.concat([df_existente, df_novo], ignore_index=True)
    else:
        df = df_novo
    df = reindexar_escolas(df)
    df.to_csv(OUTPUT_FILE, index=False)

def reindexar_escolas(df):
    if df.empty:
        return df
    df_sorted = df.sort_values(by=["Nome Escola", "Endereco", "ID Sala"]).reset_index(drop=True)
    nova_df = []
    escolas_agrupadas = df_sorted.groupby(['Nome Escola', 'Endereco'])
    for novo_id, ((nome_escola, endereco), grupo) in enumerate(escolas_agrupadas, start=1):
        grupo = grupo.copy().reset_index(drop=True)
        grupo['ID Escola'] = novo_id
        grupo['Numero de Salas'] = grupo['ID Sala'].nunique()
        nova_df.append(grupo)
    return pd.concat(nova_df, ignore_index=True)

def gerar_candidatos(id_escola, nome, endereco, num_salas, nomes_salas_info, candidatos_info, blocos_info, andares_info):
    linhas = []
    for i in range(1, num_salas + 1):
        for ordem_candidato in range(1, candidatos_info[i-1] + 1):
            linha = {
                'ID Escola': id_escola,
                'Nome Escola': nome,
                'Endereco': endereco,
                'ID Sala': i,
                'Nome da Sala': nomes_salas_info[i-1],
                'Bloco': blocos_info[i-1],
                'Andar': andares_info[i-1],
                'Ordem da Sala': i,
                'Numero de Salas': num_salas,
                'Ordem do Candidato': ordem_candidato
            }
            linhas.append(linha)
    return pd.DataFrame(linhas)

def form_escola():
    st.image('https://www.idecan.org.br/assets/img/logo.png', use_container_width=True)
    if st.session_state['modo_edicao']:
        st.markdown("""<h1 style='text-align: center; color: #0E4D92;'>Editar Escola</h1>""", unsafe_allow_html=True)
    else:
        st.markdown("""<h1 style='text-align: center; color: #0E4D92;'>Sistema de Cadastro de Escolas</h1>""", unsafe_allow_html=True)
    st.markdown("""<hr style='border:1px solid #0E4D92'>""", unsafe_allow_html=True)

    df = carregar_dados()
    nome = ""
    endereco = ""
    num_salas = 1
    tipo = "Sim"

    nomes_salas_info, candidatos_info, blocos_info, andares_info = [], [], [], []

    if st.session_state['modo_edicao'] and st.session_state['escola_em_edicao']:
        escola_df = df[df['ID Escola'] == st.session_state['escola_em_edicao']]
        nome = escola_df['Nome Escola'].iloc[0]
        endereco = escola_df['Endereco'].iloc[0]
        num_salas = escola_df['Numero de Salas'].iloc[0]
        for i in range(1, num_salas + 1):
            sala = escola_df[escola_df['ID Sala'] == i]
            if not sala.empty:
                nomes_salas_info.append(sala['Nome da Sala'].iloc[0])
                blocos_info.append(sala['Bloco'].iloc[0])
                andares_info.append(sala['Andar'].iloc[0])
                candidatos_info.append(int(sala['Ordem do Candidato'].max()))

    nome = st.text_input("Nome da Escola", value=nome)
    endereco = st.text_input("Endereço", value=endereco)
    num_salas = st.number_input("Quantidade de Salas", min_value=1, step=1, value=num_salas)
    tipo = st.radio("Todas as salas têm mesmos dados?", ["Sim", "Não"], key="tipo_salas")

    with st.form("formulario_cadastro"):
        st.subheader("Cadastro de Salas")

        nomes_salas_info_form, candidatos_info_form, blocos_info_form, andares_info_form = [], [], [], []

        if tipo == "Sim":
            candidatos = st.number_input("Candidatos por Sala", min_value=1, step=1)
            bloco = st.text_input("Bloco", value="Bloco A")
            andar = st.text_input("Andar", value="Térreo")
            for i in range(1, num_salas + 1):
                nome_sala = st.text_input(f"Nome da Sala {i}", value=(nomes_salas_info[i-1] if i <= len(nomes_salas_info) else f"Sala {i:02d}"), key=f"nome_sala_{i}")
                nomes_salas_info_form.append(nome_sala)
                candidatos_info_form.append(candidatos)
                blocos_info_form.append(bloco)
                andares_info_form.append(andar)
        else:
            for i in range(1, num_salas + 1):
                st.markdown(f"#### Sala {i}")
                nome_sala = st.text_input(f"Nome da Sala {i}", value=(nomes_salas_info[i-1] if i <= len(nomes_salas_info) else f"Sala {i:02d}"), key=f"nome_sala_{i}")
                candidatos = st.number_input(f"Candidatos Sala {i}", min_value=1, step=1, value=(candidatos_info[i-1] if i <= len(candidatos_info) else 1), key=f"cand_{i}")
                bloco = st.text_input(f"Bloco Sala {i}", value=(blocos_info[i-1] if i <= len(blocos_info) else "Bloco A"), key=f"bloco_{i}")
                andar = st.text_input(f"Andar Sala {i}", value=(andares_info[i-1] if i <= len(andares_info) else "Térreo"), key=f"andar_{i}")
                nomes_salas_info_form.append(nome_sala)
                candidatos_info_form.append(candidatos)
                blocos_info_form.append(bloco)
                andares_info_form.append(andar)

        submit = st.form_submit_button("Salvar Alterações" if st.session_state['modo_edicao'] else "Salvar Cadastro")
        if submit:
            id_escola = st.session_state['escola_em_edicao'] if st.session_state['modo_edicao'] else (df['ID Escola'].max() + 1 if not df.empty else 1)
            nova_escola = gerar_candidatos(id_escola, nome, endereco, num_salas, nomes_salas_info_form, candidatos_info_form, blocos_info_form, andares_info_form)
            salvar_dados(nova_escola, id_editar=st.session_state['escola_em_edicao'] if st.session_state['modo_edicao'] else None)
            st.success("Escola atualizada com sucesso!" if st.session_state['modo_edicao'] else "Escola cadastrada com sucesso!")
            st.session_state['modo_edicao'] = False
            st.session_state['escola_em_edicao'] = None


def mostrar_escolas():
    st.image('https://www.idecan.org.br/assets/img/logo.png', use_container_width=True)
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
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Editar ID {id_escola}"):
                    st.session_state['modo_edicao'] = True
                    st.session_state['escola_em_edicao'] = id_escola
                    st.session_state['pagina_atual'] = "Cadastrar Escola"
            with col2:
                if st.button(f"Excluir ID {id_escola}"):
                    excluir_escola(id_escola)


def excluir_escola(id_escola):
    df = carregar_dados()
    df = df[df['ID Escola'] != id_escola]
    df = reindexar_escolas(df)
    df.to_csv(OUTPUT_FILE, index=False)
    st.success("Escola excluída com sucesso!")

def login():
    st.image('https://www.idecan.org.br/assets/img/logo.png', use_container_width=True)
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
        op = st.sidebar.radio("Navegação", ["Cadastrar Escola", "Visualizar Escolas", "Baixar CSV", "Sair"],
                              index=["Cadastrar Escola", "Visualizar Escolas", "Baixar CSV", "Sair"].index(st.session_state['pagina_atual']))
        st.session_state['pagina_atual'] = op

        if op == "Cadastrar Escola":
            form_escola()

        elif op == "Visualizar Escolas":
            mostrar_escolas()

        elif op == "Baixar CSV":
            df = carregar_dados()
            st.download_button("Baixar Arquivo CSV", df.to_csv(index=False).encode('utf-8'), "escolas.csv")

        elif op == "Sair":
            st.session_state['logado'] = False
