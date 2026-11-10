# Usa uma imagem leve do Python
FROM python:3.10-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala ferramentas base do Linux exigidas pelo ChromaDB
RUN apt-get update && apt-get install -y build-essential sqlite3 && rm -rf /var/lib/apt/lists/*

# Instala as bibliotecas Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copia a aplicação, a base limpa de CSV e o script construtor
COPY app.py .
COPY dados/ ./dados/
COPY build_db.py .

# A MÁGICA: Constrói o banco vetorial dentro da nuvem para evitar erros de arquitetura!
RUN python build_db.py

# Expõe a porta padrão do Streamlit
EXPOSE 8501

# Comando para iniciar o painel
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.fileWatcherType=none", "--server.headless=true"]
