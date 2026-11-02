# Usa uma imagem leve do Python
FROM python:3.10-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala as ferramentas de sistema (C-bindings) exigidas pelo Google/ChromaDB
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copia os arquivos do projeto para dentro do container
COPY requirements.txt .

# Atualiza o instalador e baixa as bibliotecas
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copia o aplicativo e o banco vetorial
COPY app.py .
COPY chroma_db_olist ./chroma_db_olist

# Expõe a porta padrão do Streamlit
EXPOSE 8501

# Comando atualizado: Desativa o vigia de arquivos e força o modo produção
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.fileWatcherType=none", "--server.headless=true"]
