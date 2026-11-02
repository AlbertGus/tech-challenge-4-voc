import pandas as pd
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

print("Iniciando a construção do Banco Vetorial na nuvem...")

# 1. Carrega a base limpa (que é super leve)
df = pd.read_csv('base_conhecimento_limpa.csv')

# 2. Transforma em documentos
documentos = []
for _, row in df.iterrows():
    doc = Document(
        page_content=str(row['texto_completo']),
        metadata={
            "review_id": str(row['review_id']),
            "order_id": str(row['order_id']),
            "review_score": int(row['review_score']),
            "product_category_name": str(row['product_category_name']),
            "ano_mes": str(row['ano_mes'])
        }
    )
    documentos.append(doc)

# 3. Baixa o modelo multilingue
embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# 4. Cria e salva o banco diretamente no Linux do Railway!
vectordb = Chroma.from_documents(
    documents=documentos,
    embedding=embeddings_model,
    persist_directory="./chroma_db_olist"
)

print("Banco vetorial construído com sucesso!")
