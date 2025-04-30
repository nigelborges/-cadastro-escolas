import streamlit as st
import pandas as pd

USUARIO_VALIDO = 'admin'
SENHA_VALIDA = '1234'




import os

SAVE_FILE = 'escolas_salvas.csv'

def salvar_escola_banco(nome, endereco, salas, editar_id=None):
    if 'escolas' not in st.session_state:
        st.session_state['escolas'] = []
    if editar_id is not None:
        st.session_state['escolas'][editar_id] = {'nome': nome, 'endereco': endereco, 'salas': salas}
    else:
        st.session_state['escolas'].append({'nome': nome, 'endereco': endereco, 'salas': salas})

def salvar_backup_csv():
    df = exportar_dados_geral()
    df.to_csv(SAVE_FILE, index=False)
    st.toast("Backup salvo!")

def carregar_escolas():
    if 'escolas' not in st.session_state:
        return pd.DataFrame(columns=['id', 'nome', 'endereco'])
    return pd.DataFrame([{'id': idx, 'id_visivel': idx + 1, 'nome': esc['nome'], 'endereco': esc['endereco']} for idx, esc in enumerate(st.session_state['escolas'])])

def carregar_salas_por_escola(escola_id):
    if 'escolas' not in st.session_state or escola_id >= len(st.session_state['escolas']):
        return pd.DataFrame(columns=['nome_sala', 'bloco', 'andar', 'candidatos_sala'])
    return pd.DataFrame(st.session_state['escolas'][escola_id]['salas'])

def exportar_dados_por_escola(escola_id):
    escola = carregar_escolas().loc[escola_id]
    df_salas = carregar_salas_por_escola(escola_id)
    candidatos = []
    sala_ids = {}
    id_sala_counter = 1
    for i, sala in df_salas.iterrows():
        nome = sala['nome_sala']
        if nome not in sala_ids:
            sala_ids[nome] = id_sala_counter
            id_sala_counter += 1
        id_sala = sala_ids[nome]
        for ordem in range(1, sala['candidatos_sala'] + 1):
            candidatos.append({
                'ID Escola': escola_id,
                'Nome Escola': escola['nome'],
                'Endereco': escola['endereco'],
                'ID Sala': id_sala,
                'Nome da Sala': sala['nome_sala'],
                'Bloco': sala['bloco'],
                'Andar': sala['andar'],
                'Ordem da Sala': i + 1,
                'Numero de Salas': len(df_salas),
                'Ordem do Candidato': ordem
            })
    return pd.DataFrame(candidatos)

def exportar_dados_geral():
    df_escolas = carregar_escolas()
    todos = []
    for _, escola in df_escolas.iterrows():
        df_salas = carregar_salas_por_escola(escola['id'])
        id_sala_counter = 1
        sala_ids = {}
        for i, sala in df_salas.iterrows():
            nome = sala['nome_sala']
            if nome not in sala_ids:
                sala_ids[nome] = id_sala_counter
                id_sala_counter += 1
            id_sala = sala_ids[nome]
            for ordem in range(1, sala['candidatos_sala'] + 1):
                todos.append({
                    'ID Escola': escola['id'],
                    'Nome Escola': escola['nome'],
                    'Endereco': escola['endereco'],
                    'ID Sala': id_sala,
                    'Nome da Sala': sala['nome_sala'],
                    'Bloco': sala['bloco'],
                    'Andar': sala['andar'],
                    'Ordem da Sala': i + 1,
                    'Numero de Salas': len(df_salas),
                    'Ordem do Candidato': ordem
                })
    return pd.DataFrame(todos)

def visualizar():
    st.image("https://www.idecan.org.br/assets/img/logo.png", use_container_width=True)
    st.title("📦 Exportação de Escolas")
    if st.button("📦 Exportar Todas as Escolas", use_container_width=True):
        df_geral = exportar_dados_geral()
        
        st.download_button(
            "⬇️ Baixar CSV Geral",
            df_geral.to_csv(index=False).encode('utf-8'),
            file_name="todas_escolas.csv",
            use_container_width=True
        )

    st.title("📋 Escolas Cadastradas")
    st.divider()
    if 'escolas' not in st.session_state or not st.session_state['escolas']:
        st.info("Nenhuma escola cadastrada.")
        return
    for idx, escola in enumerate(st.session_state['escolas']):
        with st.expander(f"🏫 {escola['nome']} - {escola['endereco']}"):
            st.subheader(f"📄 Salas da escola {escola['nome']}")
            st.caption(f"Endereço: {escola['endereco']}")
            st.markdown("---")
            st.write(f"ID: {idx + 1}")
            df_salas = carregar_salas_por_escola(idx)
            df_salas_visual = df_salas.copy()
            id_sala_counter = 1
            sala_ids = {}
            id_salas = []
            for _, sala in df_salas_visual.iterrows():
                nome = sala['nome_sala']
                if nome not in sala_ids:
                    sala_ids[nome] = id_sala_counter
                    id_sala_counter += 1
                id_salas.append(sala_ids[nome])
            df_salas_visual.insert(0, "ID Sala", id_salas)
            df_salas_visual.insert(0, "ID Escola", idx + 1)
            df_salas_visual.insert(1, "Nome Escola", escola['nome'])
            df_salas_visual.insert(1, "Endereco", escola['endereco'])
            st.dataframe(df_salas_visual)
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button(f"✏️ Editar", key=f"editar_{idx}", use_container_width=True):
                    st.session_state['modo_edicao'] = True
                    st.session_state['escola_em_edicao'] = idx
                    st.session_state['pagina_atual'] = "Cadastrar Escola"
                    st.experimental_rerun()
            with col2:
                if st.button(f"🗑️ Excluir", key=f"excluir_{idx}", use_container_width=True):
                    st.session_state['escolas'].pop(idx)
                    salvar_backup_csv()
                    st.experimental_rerun()
            with col3:
                if st.button(f"📁 Exportar CSV", key=f"botao_exportar_{idx}", use_container_width=True):
                    df_exportar = exportar_dados_por_escola(idx)
                    st.download_button(
                        "⬇️ Baixar CSV",
                        df_exportar.to_csv(index=False).encode('utf-8'),
                        file_name=f"escola_{idx}.csv",
                        key=f"download_{idx}"
                    )

def form_escola():
    st.title("🏫 Cadastro de Escola")
    st.divider()
    editar_id = st.session_state.get("escola_em_edicao")
    nome = ""
    endereco = ""
    num_salas = 1
    salas_existentes = []

    if editar_id and 'escolas' in st.session_state and editar_id < len(st.session_state['escolas']):
        escola = st.session_state['escolas'][editar_id]
        nome = escola['nome']
        endereco = escola['endereco']
        salas_existentes = escola['salas']
        num_salas = len(salas_existentes)

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
        # aplicar ID Sala conforme nome
        id_sala_counter = 1
        sala_ids = {}
        id_salas = []
        for _, sala in df_salas.iterrows():
            nome = sala['nome_sala']
            if nome not in sala_ids:
                sala_ids[nome] = id_sala_counter
                id_sala_counter += 1
            id_salas.append(sala_ids[nome])
        df_salas.insert(0, 'ID Sala', id_salas)
        df_editada = st.data_editor(df_salas, num_rows="dynamic", key="editor_salas")
        salas = df_editada.to_dict("records")

    if st.button("Salvar Alterações" if editar_id else "Salvar Cadastro"):
        if not nome or not endereco or any(not sala['nome_sala'] for sala in salas):
            st.warning("Todos os campos são obrigatórios.")
        else:
            salvar_escola_banco(nome, endereco, salas, editar_id=editar_id)
            st.success("Escola atualizada com sucesso!" if editar_id else "Escola cadastrada com sucesso!")
            st.session_state['modo_edicao'] = False
            salvar_backup_csv()
            st.session_state['escola_em_edicao'] = None

def mostrar_menu():
    st.sidebar.title("Menu")
    opcao = st.sidebar.radio("Navegação", ["Cadastrar Escola", "Visualizar Escolas", "Limpar Todas"], index=0)
    if opcao == "Cadastrar Escola":
        form_escola()
    elif opcao == "Visualizar Escolas":
        visualizar()
    elif opcao == "Limpar Todas":
        st.warning("Esta ação apagará todas as escolas cadastradas.")
        if st.button("⚠️ Confirmar Limpeza Total", type="primary"):
            st.session_state['escolas'] = []
            salvar_backup_csv()
            st.success("Todos os dados foram apagados.")
            st.experimental_rerun()
    

if os.path.exists(SAVE_FILE):
    try:
        df_loaded = pd.read_csv(SAVE_FILE)
        if df_loaded.empty or df_loaded.columns.size == 0:
            raise ValueError("Arquivo vazio ou inválido.")
        escolas_dict = {}
        for _, row in df_loaded.iterrows():
            key = (row['ID Escola'], row['Nome Escola'], row['Endereco'])
            if key not in escolas_dict:
                escolas_dict[key] = []
            escolas_dict[key].append({
                'nome_sala': row['Nome da Sala'],
                'bloco': row['Bloco'],
                'andar': row['Andar'],
                'candidatos_sala': row['Ordem do Candidato']
            })
        st.session_state['escolas'] = [
            {'nome': k[1], 'endereco': k[2], 'salas': v}
            for k, v in escolas_dict.items()
        ]
    except Exception as e:
    if st.session_state.get('escolas'):
        st.warning(f"Erro ao carregar backup: {e}")
    else:
        pass

if __name__ == '__main__':
    # Inicializar session_state com segurança
    if 'modo_edicao' not in st.session_state:
        st.session_state['modo_edicao'] = False
    if 'escola_em_edicao' not in st.session_state:
        st.session_state['escola_em_edicao'] = None
    if 'pagina_atual' not in st.session_state:
        st.session_state['pagina_atual'] = 'Cadastrar Escola'
    
    mostrar_menu()
