import streamlit as st
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 1. Configuração da Página
st.set_page_config(page_title="VoC Intelligence", page_icon="📊", layout="centered")
st.title("📊 Voice of Customer Intelligence")
st.markdown("Exploração inteligente de avaliações do e-commerce com RAG e filtros de Metadados.")

load_dotenv()
if "GOOGLE_API_KEY" not in os.environ:
    st.error("Erro: GOOGLE_API_KEY não encontrada.")
    st.stop()

# 2. Funções com suporte a Filtro de Metadado
def carregar_banco_vetorial(categoria_filtro=None):
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma
    
    embeddings_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    vectordb = Chroma(persist_directory="./chroma_db_olist", embedding_function=embeddings_model)
    
    # Se o usuário escolheu uma categoria específica, aplicamos o filtro no ChromaDB!
    search_kwargs = {"k": 7} # Aumentei para 7 para dar mais contexto
    if categoria_filtro and categoria_filtro != "Todas as Categorias":
        search_kwargs["filter"] = {"product_category_name": categoria_filtro}
        
    return vectordb.as_retriever(search_kwargs=search_kwargs)

def formatar_docs_com_metadados(docs):
    contextos = []
    for d in docs:
        nota = d.metadata.get('review_score', 'N/A')
        categoria = d.metadata.get('product_category_name', 'N/A')
        texto = d.page_content
        contextos.append(f"[Nota: {nota} | Categoria: {categoria}] Comentário: {texto}")
    return "\n\n".join(contextos)

# 3. Interface de Interação (Com Filtro Visual)
col1, col2 = st.columns([2, 1])

with col1:
    pergunta_usuario = st.text_input("O que você deseja saber?", placeholder="Ex: Quais as principais reclamações?")

with col2:
    # Lista com as top categorias do Olist para o painel
    lista_categorias = [
        "Todas as Categorias", "beleza_saude", "cama_mesa_banho", 
        "esporte_lazer", "informatica_acessorios", "moveis_decoracao", 
        "utilidades_domesticas", "relogios_presentes", "brinquedos"
    ]
    categoria_selecionada = st.selectbox("Filtrar por Categoria:", lista_categorias)
    st.caption("💡 Em pedidos com mais de um produto, usamos a categoria do primeiro item. O comentário pode se referir a outro produto do mesmo pedido.")

if st.button("Analisar Sentimento e Avaliações"):
    if pergunta_usuario:
        with st.spinner(f"Analisando base..."):
            try:
                # 1. Inicializa os componentes
                retriever = carregar_banco_vetorial(categoria_selecionada)
                
                # 2. OTIMIZAÇÃO: Faz a busca no banco APENAS UMA VEZ e guarda o resultado
                docs_recuperados = retriever.invoke(pergunta_usuario)
                
                # 3. Formata os documentos guardados e gera a resposta
                contexto_formatado = formatar_docs_com_metadados(docs_recuperados)
                
                # 4. Modificamos o pipeline para aceitar o contexto formatado diretamente
                llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.1)
                template_voc = """
                Você é um analista de Voice of Customer (VoC) de um e-commerce.
                Seu objetivo é responder à pergunta do gestor utilizando estritamente o contexto de avaliações fornecido.

                Regras de negócio:
                1. Responda baseando-se APENAS no contexto abaixo.
                2. Se o contexto não contiver informações suficientes, responda EXATAMENTE: "Não possuo evidências suficientes na base de avaliações para responder a esta pergunta."
                3. Sempre cite as evidências: mencione trechos dos comentários e faça referência à Categoria e à Nota.
                4. Estruture a resposta em tópicos.

                Contexto (Avaliações recuperadas):
                {context}

                Pergunta do gestor: {question}

                Resposta analítica:
                """
                
                prompt = PromptTemplate.from_template(template_voc)
                chain = prompt | llm | StrOutputParser()
                resposta = chain.invoke({"context": contexto_formatado, "question": pergunta_usuario})
                
                st.markdown("### 📋 Análise Gerencial")
                st.write(resposta)
                
                # 5. UX: Título ajustado conforme sugestão do professor, usando a MESMA variável da busca
                with st.expander("🔍 Comentários enviados ao modelo"):
                    for i, doc in enumerate(docs_recuperados, 1):
                        st.markdown(f"**Evidência {i}** (Nota: {doc.metadata.get('review_score')} | Categoria: {doc.metadata.get('product_category_name')})")
                        st.write(f"_{doc.page_content}_")
                        st.divider()
                        
            except Exception as e:
                st.error(f"Erro ao processar: {e}")
    else:
        st.warning("Digite uma pergunta.")
